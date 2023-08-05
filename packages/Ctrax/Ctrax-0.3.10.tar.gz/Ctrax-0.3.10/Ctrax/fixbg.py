# fixbg.py
# region-of-interest modification dialog for background modeling
# JAB 7/30/11 (made from a previously pasted-and-modified version of roi.py)

import wx
import numpy as num
import scipy.ndimage.morphology as morph

import imagesk
import roi


class FixBG (roi.ROI):
    def __init__( self, parent, bgmodel ):
        roi.ROI.__init__( self, parent, bgmodel, init_polygons=bgmodel.fixbg_polygons )

        self.bgcenter = bgmodel.center.copy()
        self.bgdev = bgmodel.dev.copy()
        self.bgcenter0 = self.bgcenter.copy()
        self.bgdev0 = self.bgdev.copy()

        self.undo_data = bgmodel.fixbg_undo_data

        self.displaymode_choice.SetString( 1, "Background Deviation" )
        self.frame.SetTitle( "Fix Background Model" )


    def make_instruction_text( self ):
        """Get default (ROI) user instructions and modify them for bg-fixing."""
        lines = roi.ROI.make_instruction_text( self )
        for ll in range( len( lines ) ):
            line = lines[ll]
            if line[0:2] == '1.':
                line = '1. Click to select a polygonal region of background image to fix.'
            elif line[0:2] == '4.':
                line = '4. Background within polygon will be interpolated from boundaries.'
            elif line[0:2] == '5.':
                line = '5. Push "Save" button to save the current background model.'
            lines[ll] = line
        return lines


    def AddPolygon(self):
        wx.BeginBusyCursor()
        wx.Yield()
        self.currpolygon = num.r_[self.currpolygon,num.reshape(self.currpolygon[0,:],(1,2))]
        self.polygons.append(self.currpolygon)
        
        isin = self.fix_hole(self.bgcenter,self.bgcenter,self.currpolygon)
        undo_bg_coords = isin
        isin = self.fix_hole(self.bgdev,self.bgdev,self.currpolygon,isin=isin)
        undo_dev_coords = isin

        # save data for later undo
        undo_bg = self.bgcenter0[undo_bg_coords]
        undo_dev = self.bgdev0[undo_dev_coords]
        self.undo_data.append( {'bg_data': undo_bg, 'bg_coords': undo_bg_coords,
                                'dev_data': undo_dev, 'dev_coords': undo_dev_coords} )

        self.issaved = False
        wx.EndBusyCursor()

        
    def OnSave(self,evt=None):
        self.bgmodel.SetCenter(self.bgcenter)
        self.bgmodel.SetDev(self.bgdev)
        self.bgmodel.SetFixBgPolygons(self.polygons,self.undo_data)
        
        self.issaved = True


    def undo_last( self ):
        lastpolygon = self.polygons.pop()
        self.RemovePolygon(lastpolygon)


    def get_image_to_show( self ):
        if self.displaymode_choice.GetSelection() == 0:
            return imagesk.double2mono8(self.bgcenter,donormalize=True)
        else:
            return imagesk.double2mono8(self.bgdev,donormalize=True)


    def RemovePolygon(self,poly):
        wx.BeginBusyCursor()
        wx.Yield()
        #isin = self.undo_fix_hole(self.bgcenter0,self.bgcenter,poly)
        #isin = self.undo_fix_hole(self.bgdev0,self.bgdev,poly,isin=isin)
        undo_data = self.undo_data.pop()
        self.bgcenter[undo_data['bg_coords']] = undo_data['bg_data']
        self.bgdev[undo_data['dev_coords']] = undo_data['dev_data']
        self.issaved = False
        wx.EndBusyCursor()


    def fix_hole(self,im,out,polygon,isin=None):
        # get points on the inside of the polygon
        if isin is None:
            isin = roi.point_inside_polygon(self.X,self.Y,polygon)
        
        return fix_holes(im,out,isin)
    

    def undo_fix_hole(self,im0,im,polygon,isin=None):
        if isin is None:
            isin = roi.point_inside_polygon(self.X,self.Y,polygon)
        im[isin] = im0[isin]    
        return isin

        
def fix_holes(im,out,isin):

    if isin.all():
        raise ValueError('Cannot fix holes. All pixels are labeled as holes.')

    isout = (isin == False)

    # strel for eroding
    se = num.ones((3,3),bool)

    # store dilated version here
    isout1 = num.zeros(isout.shape,dtype=bool)

    # loop, dilating known regions
    while not isout.all():
        
        # get pixels just inside the border
        morph.binary_dilation(isout,se,output=isout1)
        border = isout1 & num.logical_not(isout)
        (yb,xb) = num.nonzero(border)
        yn = num.vstack([yb-1,
                         yb-1,
                         yb-1,
                         yb,
                         yb,
                         yb+1,
                         yb+1,
                         yb+1])
        xn = num.vstack([xb-1,
                         xb,
                         xb+1,
                         xb-1,
                         xb+1,
                         xb-1,
                         xb,
                         xb+1])
        badidx = num.logical_or(yn >= im.shape[0],
                                num.logical_or(yn < 0,
                                               num.logical_or(xn >= im.shape[1],
                                                              xn < 0)))
        yn = yn[badidx == False]
        xn = xn[badidx == False]
        #print "xn = " + str(xn)
        #print "yn = " + str(yn)
        #print "isout[yn,xn] = " + str(isout[yn,xn].astype(int))
        out[yb,xb] = num.average(out[yn,xn],axis=0,weights=isout[yn,xn].astype(float))

#        plt.subplot(121)
#        plt.imshow(isout)
#        plt.subplot(122)
#        plt.imshow(out)
#        plt.show()
        
        # swap isout, isout1x
        isout2 = isout1
        isout1 = isout
        isout = isout2

    return isin


def fix_hole(im,out,polygon,isin=None,X=None,Y=None):

    s = num.ones((3,3),bool)        

    # get points on the inside of the polygon
    if isin is None:
        if X is None or Y is None:
            (Y,X) = num.mgrid[0:im.shape[0],0:im.shape[1]]
        isin = roi.point_inside_polygon(X,Y,polygon)
        
    (y_isin,x_isin) = num.nonzero(isin)

    # get points on the outside boundary of the polygon
    isboundary = num.logical_and(morph.binary_dilation(isin,s),
                                 ~isin)

    (y_isboundary,x_isboundary) = num.nonzero(isboundary)

    # for each point inside the polygon, get an average from
    # all the boundary points
    for i in range(len(y_isin)):
        x = x_isin[i]
        y = y_isin[i]
        d = num.sqrt((y_isboundary-y)**2+(x_isboundary-x)**2)
        w = num.exp(-d)
        out[y,x] = num.sum(im[isboundary] * w) / num.sum(w)

    return isin
