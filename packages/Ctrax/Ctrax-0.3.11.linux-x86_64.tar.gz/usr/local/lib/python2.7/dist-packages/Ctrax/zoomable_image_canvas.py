# zoomable_image_canvas.py
# JAB 10/25/11

# extension to wxvideo's DynamicImageCanvas, allowing drag-to-zoom

import numpy as num
from scipy.misc.pilutil import imresize
import wx

from motmot.wxvideo.wxvideo import DynamicImageCanvas

from imagesk import double2mono8
from params import params

#######################################################################
# ZoomableImageCanvas
#######################################################################
class ZoomableImageCanvas (DynamicImageCanvas):
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, parent=None, id_val=wx.ID_ANY ):
        DynamicImageCanvas.__init__( self, parent, id_val )
        self.set_resize( True )

        self.Bind( wx.EVT_LEFT_DOWN, self.OnMouseDown )
        self.Bind( wx.EVT_MOTION, self.OnMouseMoved )
        self.Bind( wx.EVT_LEFT_UP, self.OnMouseUp )
        self.Bind( wx.EVT_LEFT_DCLICK, self.OnMouseDoubleClick )
        self.zoom_dragging = False
        self.zoom_drag_roi_scale = 1.

        self.current_source = None


    ###################################################################
    # update_image_and_drawings()
    ###################################################################
    def update_image_and_drawings( self, source_name, img, **kwargs ):
        """Override superclass's version to support zooming."""

        if self.current_source != source_name:
            # add some hackery to allow variable image shapes
            # as long as they're identified with a new source name
            self.full_image_numpy = None
            self.id_val = None

        if img.dtype != num.dtype('uint8'):
            img = double2mono8( img, donormalize=False )

        self.current_source = source_name
        self.current_img = img
        self.current_drawings = kwargs
        self.redraw()


    ###################################################################
    # wind2img()
    ###################################################################
    def wind2img( self, x0w, y0w, x1w, y1w ):
        """
        Calculate image coordinates from window coordinates.
        Input window coordinates are fractional window sizes (0:1).
        x0 is left, y0 is top, etc.
        """
        
        size = self.current_img.shape
        hi = float( size[0] ) # image height
        wi = float( size[1] ) # image width

        hw = float( self.GetSize()[1] ) # window height
        ww = float( self.GetSize()[0] ) # window width
        
        ri = hi/wi
        rw = hw/ww

        if ri > rw:
            x0i = x0w*(ri/rw)*wi
            y0i = y0w*hi
            x1i = x1w*(ri/rw)*wi
            y1i = y1w*hi
        else:
            x0i = x0w*wi
            y0i = y0w*(rw/ri)*hi - wi*(rw - ri)
            x1i = x1w*wi
            y1i = y1w*(rw/ri)*hi - wi*(rw - ri)

        return x0i, y0i, x1i, y1i


    ###################################################################
    # redraw()
    ###################################################################
    def redraw( self ):
        """Redraw everything, zooming as approprate."""
        if not hasattr( self, 'current_img' ): return
        
        img = self.current_img.copy()
        size = img.shape
        height = float( size[0] )
        width = float( size[1] )

        if self.current_drawings.has_key( 'linesegs' ) and self.current_drawings.has_key( 'lineseg_colors' ):
            lines_to_draw = self.current_drawings['linesegs'][:]
            line_colors = self.current_drawings['lineseg_colors'][:]
        else:
            lines_to_draw = []
            line_colors = []

        if hasattr( self, 'zoom_drag_roi' ):
            # calculate scale to maintain aspect ratio
            x0, y0, x1, y1 = self.wind2img( *self.zoom_drag_roi )
            left = int( round( x0 ) )
            top = int( round( y0 ) )
            right = int( round( x1 ) )
            bottom = int( round( y1 ) )
            resizew = width/max( float( right - left ), 0.01 )
            resizeh = height/max( float( bottom - top ), 0.01 )
            self.zoom_drag_roi_scale = min( resizew, resizeh )

            # nudge scale to fill image shape
            extrah = height/self.zoom_drag_roi_scale - (bottom - top)
            if extrah > 0.:
                topoff = min( top, int( num.floor( extrah/2. ) ) )
                top -= topoff
                bottom += extrah - topoff
                bottomoff = bottom - height
                if bottomoff > 0:
                    bottom -= bottomoff
                    top -= bottomoff
                    top = max( 0, top )
            else:
                extraw = width/self.zoom_drag_roi_scale - (right - left)
                leftoff = min( left, int( num.floor( extraw/2. ) ) )
                left -= leftoff
                right += extraw - leftoff
                rightoff = right - width
                if rightoff > 0:
                    right -= rightoff
                    left -= rightoff
                    left = max( 0, left )
            self.zoom_drag_roi = (float( left )/width, float( top )/height,
                                  float( right )/width, float( bottom )/height)
            
            # resize the image
            img = img[top:bottom,left:right]
            try:
                new_img = imresize( img, self.zoom_drag_roi_scale )
            except ValueError:
                return # "tile cannot extend outside image", seems to be harmless
            new_img = new_img[:height,:width]

            # fill in with gray at margins
            img = num.ones( (size[0], size[1]), dtype=num.uint8 )*127
            img[:new_img.shape[0],:new_img.shape[1]] = new_img

        if self.zoom_dragging:
            x0, y0, x1, y1 = self.wind2img( self.zoom_drag_origin[0],
                                            self.zoom_drag_origin[1],
                                            self.zoom_drag_current[0],
                                            self.zoom_drag_current[1] )
            lines_to_draw.extend( [(x0,y0, x0,y1), (x0,y1, x1,y1),
                                   (x1,y1, x1,y0), (x1,y0, x0,y0)] )
            line_colors.extend( [params.zoom_drag_rectangle_color,
                                 params.zoom_drag_rectangle_color,
                                 params.zoom_drag_rectangle_color,
                                 params.zoom_drag_rectangle_color] )
        
        # scale the drawings
        if hasattr( self, 'zoom_drag_roi' ):
            for si in range( len( lines_to_draw ) ):
                orig_seg = lines_to_draw[si]
                new_seg = ((orig_seg[0] - left)*self.zoom_drag_roi_scale,
                           (orig_seg[1] - top)*self.zoom_drag_roi_scale,
                           (orig_seg[2] - left)*self.zoom_drag_roi_scale,
                           (orig_seg[3] - top)*self.zoom_drag_roi_scale)
                lines_to_draw[si] = new_seg

        kwargs = self.current_drawings.copy()
        kwargs['linesegs'] = lines_to_draw
        kwargs['lineseg_colors'] = line_colors

        DynamicImageCanvas.update_image_and_drawings( self, self.current_source, img, **kwargs )
        self.Refresh( eraseBackground=False )


    ###################################################################
    # OnMouseDown()
    ###################################################################
    def OnMouseDown( self, evt ):
        self.zoom_dragging = True
        self.zoom_drag_origin = (float( evt.GetX() )/self.GetSize()[0],
                                 1. - float( evt.GetY() )/self.GetSize()[1])
        if hasattr( self, 'zoom_drag_roi' ):
            self.zoom_drag_origin = (self.zoom_drag_origin[0]/self.zoom_drag_roi_scale + self.zoom_drag_roi[0],
                                     self.zoom_drag_origin[1]/self.zoom_drag_roi_scale + self.zoom_drag_roi[1])
        self.zoom_drag_current = self.zoom_drag_origin

        self.redraw()
        evt.Skip()


    ###################################################################
    # OnMouseMoved()
    ###################################################################
    def OnMouseMoved( self, evt ):
        if self.zoom_dragging:
            if not evt.LeftIsDown():
                # in drag mode, but left mouse button is not down anymore...
                self.OnMouseUp( evt )
                return

            # set to draw bounding box
            self.zoom_drag_current = (float( evt.GetX() - self.GetPosition()[0] )/self.GetSize()[0],
                                      1. - float( evt.GetY() - self.GetPosition()[1] )/self.GetSize()[1])
            if hasattr( self, 'zoom_drag_roi' ):
                self.zoom_drag_current = (self.zoom_drag_current[0]/self.zoom_drag_roi_scale + self.zoom_drag_roi[0],
                                          self.zoom_drag_current[1]/self.zoom_drag_roi_scale + self.zoom_drag_roi[1])
            self.redraw()

        evt.Skip()


    ###################################################################
    # OnMouseUp()
    ###################################################################
    def OnMouseUp( self, evt ):
        evt.Skip()

        needs_refresh = self.zoom_dragging
        self.zoom_dragging = False

        if needs_refresh:
            if self.zoom_drag_origin[0] == self.zoom_drag_current[0] or \
               self.zoom_drag_origin[1] == self.zoom_drag_current[1]:
                return

            left = max( min( self.zoom_drag_origin[0],
                             self.zoom_drag_current[0] ), 0. )
            top = max( min( self.zoom_drag_origin[1],
                            self.zoom_drag_current[1] ), 0. )
            right = min( max( self.zoom_drag_origin[0],
                              self.zoom_drag_current[0] ), 1. )
            bottom = min( max( self.zoom_drag_origin[1],
                               self.zoom_drag_current[1] ), 1. )
            self.zoom_drag_roi = (left, top, right, bottom)
            self.redraw()
            

    ###################################################################
    # OnMouseDoubleClick()
    ###################################################################
    def OnMouseDoubleClick( self, evt ):
        if hasattr( self, 'zoom_drag_roi' ):
            delattr( self, 'zoom_drag_roi' )
        self.zoom_drag_roi_scale = 1.
        self.redraw()
