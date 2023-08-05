# draw.py
# KMB 11/10/08

import os
import pdb
import sys

import matplotlib
#matplotlib.use( 'WXAgg' )
matplotlib.interactive( True )
import matplotlib.backends.backend_wxagg
import matplotlib.figure
import matplotlib.cm
import matplotlib.pyplot as plt
if hasattr( plt, 'tight_layout' ): # matplotlib >= 1.1
    HAS_TIGHTLAYOUT = True
else:
    HAS_TIGHTLAYOUT = False
import matplotlib.transforms as mtransforms
import numpy as num
import wx
from wx import xrc

import motmot.wxvalidatedtext.wxvalidatedtext as wxvt # part of Motmot

from params import params


#######################################################################
# PlotConstants
#######################################################################
class PlotConstants:
    def __init__( self ):
        self.vel_bins = 100
        self.vel_x_min=self.vel_x_max=self.vel_y_min=self.vel_y_max = 'a'
        self.dth_bins = 100
        self.dth_x_min=self.dth_x_max=self.dth_y_min=self.dth_y_max = 'a'
##        self.orn_bins = 90
##        self.orn_x_min=self.orn_x_max=self.orn_y_min=self.orn_y_max = 'a'
##        self.space_bins = 50
##        self.space_x_min=self.space_x_max=self.space_y_min=self.space_y_max = 'a'
        self.pos_binsize = 50
        self.pos_x_min=self.pos_x_max=self.pos_y_min=self.pos_y_max = 'a'

        self.filepath = None
const = PlotConstants()


#######################################################################
# PlotPanel
#######################################################################
# class from http://www.scipy.org/Matplotlib_figure_in_a_wx_panel
# although menu/right-click/save functionality was added here
class PlotPanel(wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a 
    flag, and the actually redrawing of the figure is triggered by an Idle event."""
    ###################################################################
    # __init__()
    ###################################################################
    def __init__(self, parent, id = -1, color = None,\
        dpi = None, style = wx.NO_FULL_REPAINT_ON_RESIZE, **kwargs):
        wx.Panel.__init__(self, parent, id = id, style = style, **kwargs)
        self.figure = matplotlib.figure.Figure(None, dpi)
        self.canvas = matplotlib.backends.backend_wxagg.FigureCanvasWxAgg( self, -1, self.figure )
        self.SetColor(color)
        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)
        self._resizeflag = True
        self._SetSize()

        self.canvas.Bind( wx.EVT_RIGHT_UP, self.OnRightMouseButton )

        self.canvas.mpl_connect( 'draw_event', self.post_draw )
            

    ###################################################################
    # OnRightMouseButton()
    ###################################################################
    def OnRightMouseButton( self, evt ):
        """Right mouse button pressed; pop up save menu."""
        menu = wx.Menu()
        file_save_item = wx.MenuItem( menu, wx.ID_ANY, "Save as..." )
        menu.AppendItem( file_save_item )
        self.canvas.Bind( wx.EVT_MENU, self.OnMenuSave )
        self.canvas.PopupMenu( menu )


    ###################################################################
    # OnMenuSave()
    ###################################################################
    def OnMenuSave( self, evt ):
        """User has chosen to save this figure as an image file.
        Prompt for filename and save."""
        # the extension on filename determines file format
        # create text list of allowed file extensions
        extensions = {'.eps': 'encapsulated postscript (*.eps)',
                      '.png': 'portable network graphics (*.png)',
                      '.pdf': 'portable data format (*.pdf)'}
        dialog_str = ''
        ext_list = []
        for ext, txt in extensions.iteritems():
            dialog_str += txt + '|*' + ext + '|'
            ext_list.append( ext )
        dialog_str = dialog_str[:-1]

        # make default filename
        (dirname, filename) = os.path.split( const.filepath )
        (basename, ext) = os.path.splitext( filename )
        if self.__class__.__name__ == 'TrajectoryPlotPanel':
            if '_trajplot' not in basename:
                basename += '_trajplot'
        elif self.__class__.__name__ == 'PosHistPanel':
            if '_posplot' not in basename:
                basename += '_posplot'
        elif self.__class__.__name__ == 'VelPlotPanel':
            if '_velplot' not in basename:
                basename += '_velplot'
        elif self.__class__.__name__ == 'TurnPlotPanel':
            if '_turnplot' not in basename:
                basename += '_turnplot'

        # show dialog
        dlg = wx.FileDialog( self.canvas, "Save as image...", dirname, basename, wildcard=dialog_str, style=wx.SAVE )
        if dlg.ShowModal() == wx.ID_OK:
            # get entered filename and extension
            const.filepath = dlg.GetPath()
            selected_ext = ext_list[dlg.GetFilterIndex()]
            if not const.filepath.endswith( selected_ext ):
                const.filepath += selected_ext
            print "saving to", const.filepath
            try:
                self.figure.savefig( const.filepath )
            except IOError:
                wx.MessageBox( "Miscellaneous error while saving",
                               "Write error", wx.ICON_ERROR )
                # everybody loves a "miscellaneous error" message

        dlg.Destroy()


    ###################################################################
    # SetColor()
    ###################################################################
    def SetColor(self, rgbtuple):
        """Set figure and canvas colours to be the same."""
        if not rgbtuple:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        col = [c/255.0 for c in rgbtuple]
        self.figure.set_facecolor(col)
        self.figure.set_edgecolor(col)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))


    ###################################################################
    # _onSize()
    ###################################################################
    def _onSize(self, event):
        self._resizeflag = True


    ###################################################################
    # _onIdle()
    ###################################################################
    def _onIdle(self, evt):
        if self._resizeflag:
            self._resizeflag = False
            self._SetSize()
            self.draw()


    ###################################################################
    # _SetSize()
    ###################################################################
    def _SetSize(self, pixels=None):
        """This method can be called to force the Plot to be a desired size,
        which defaults to the ClientSize of the panel."""

        if not pixels:
            pixels = self.GetClientSize()
        self.canvas.SetSize(pixels)
        self.figure.set_size_inches(pixels[0]/self.figure.get_dpi(),
                                    pixels[1]/self.figure.get_dpi())


    ###################################################################
    # draw()
    ###################################################################
    def draw( self ):
        """Drawing events handled here. Create subplots, label axes, plot."""
        pass
    

    ###################################################################
    # post_draw()
    ###################################################################
    def post_draw( self, evt ):
        """Post-drawing events handled here. Rescale plots to fit in panel."""
        if HAS_TIGHTLAYOUT and False:
            plt.tight_layout()
            
        else:
            # http://matplotlib.sourceforge.net/faq/howto_faq.html#automatically-make-room-for-tick-labels
            # http://stackoverflow.com/questions/4018860/text-box-in-matplotlib
            bboxes = []
            # Cycle through all artists in all the axes in the figure
            for ax in self.figure.axes:
                for artist in ax.get_children():
                    # If it's a text artist, grab its bounding box...
                    if isinstance(artist, matplotlib.text.Text):
                        bbox = artist.get_window_extent()

                        # the figure transform goes from relative->pixels and
                        # we want the inverse of that
                        bboxi = bbox.inverse_transformed(self.figure.transFigure)
                        bboxes.append(bboxi)
                # cycle through all tick labels, too
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    bbox = label.get_window_extent()
                    bboxi = bbox.inverse_transformed(self.figure.transFigure)
                    bboxes.append(bboxi)

            # this is the bbox that bounds all the bboxes, again in
            # relative figure coords
            if len( bboxes ) == 0: return
            size = mtransforms.Bbox.union(bboxes)
            margins = self.figure.subplotpars

            vspace = size.height - (margins.top - margins.bottom)
            if size.height > 0.8:
                self.figure.subplots_adjust( bottom=margins.bottom + vspace/2.,
                                             top=margins.top - vspace/2. )
            elif size.height < 0.5:
                self.figure.subplots_adjust( bottom=margins.bottom - vspace/2.,
                                             top=margins.top + vspace/2. )
            hspace = size.width - (margins.right - margins.left)
            if size.width > 0.8:
                self.figure.subplots_adjust( left=margins.left + hspace/2.,
                                             right=margins.right - hspace/2. )
            elif size.width < 0.5:
                self.figure.subplots_adjust( left=margins.left - hspace/2.,
                                             right=margins.right + hspace/2. )

            # Temporarily disconnect any callbacks to the draw event...
            # (To avoid recursion)
            func_handles = self.figure.canvas.callbacks.callbacks[evt.name]
            self.figure.canvas.callbacks.callbacks[evt.name] = {}
            # Re-draw the figure..
            self.figure.canvas.draw()
            # Reset the draw event callbacks
            self.figure.canvas.callbacks.callbacks[evt.name] = func_handles


#######################################################################
# TrajectoryPlotPanel
#######################################################################
class TrajectoryPlotPanel (PlotPanel):
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, parent, data ):
        """Initialize a trajectory plot panel with data."""
        PlotPanel.__init__( self, parent )

        self.x = num.zeros( (len( data ),len( data[0] )), dtype=num.float32 )
        self.y = num.zeros( self.x.shape, dtype=num.float32 )
        for fi, frame in enumerate( data ):
            for ei, ellipse in frame.iteritems():
                if ei >= self.x.shape[1]: break
                self.x[fi,ei] = ellipse.center.x
                self.y[fi,ei] = ellipse.center.y
        
        
    ###################################################################
    # draw()
    ###################################################################
    def draw( self ):
        """Draw the data."""
        if not hasattr( self, 'subplot' ):
            self.subplot = self.figure.add_subplot( 111, aspect='equal' )
            self.subplot.set_title( "Positions in first %d frames"%self.x.shape[0], fontsize=12 )
            self.subplot.set_xlabel( "x (pixels)" )
            self.subplot.set_ylabel( "y (pixels)" )

        self.subplot.plot( self.x, self.y )


#######################################################################
# VelocityPlotPanel
#######################################################################
class VelocityPlotPanel (PlotPanel):
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, parent, data ):
        """Initialize a velocity plot panel with data."""
        PlotPanel.__init__( self, parent )

        self.x = num.zeros( (len( data ) - 1,), dtype=num.float32 )
        self.y = num.zeros( (len( data ) - 1,len( data[0] )), dtype=num.float32 )
        for fi in range( len( data ) - 1 ):
            self.x[fi] = fi
            for ei in range( self.y.shape[1] ):
                if data[fi].hasItem( ei ) and data[fi + 1].hasItem( ei ):
                    pos = data[fi][ei]
                    next_pos = data[fi + 1][ei]
                    self.y[fi,ei] = pos.Euc_dist( next_pos )

        self.y_mn = num.mean( self.y, 1 )
        self.y_st = num.std( self.y, 1 )
        #self.y_env = num.hstack( (self.y_mn + self.y_st,
        #                          self.y_mn[::-1] - self.y_st[::-1]) )
        #self.x_env = num.hstack( (self.x, self.x[::-1]) )
        
        
    ###################################################################
    # draw()
    ###################################################################
    def draw( self ):
        """Draw the data."""
        if not hasattr( self, 'subplot' ):
            self.subplot = self.figure.add_subplot( 111 )
            self.subplot.set_title( "Velocities in first %d frames"%self.x.shape[0], fontsize=12 )
            self.subplot.set_xlabel( "frame" )
            self.subplot.set_ylabel( "velocity (pixels/frame)\nmean +/- S.D." )

        self.subplot.plot( self.x, self.y_mn, 'k' )
        self.subplot.fill_between( self.x, self.y_mn + self.y_st, self.y_mn - self.y_st, alpha=0.5, edgecolor='none', facecolor='k' )
        if self.y.shape[1] < 10:
            self.subplot.plot( self.x, self.y )
        

#######################################################################
# PosHistPanel
#######################################################################
class PosHistPanel( PlotPanel ):
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, frame, data, width, height ):
        PlotPanel.__init__( self, frame )
        self.data = data

        # fill grid
        self.grid = num.zeros( (width/const.pos_binsize+1, height/const.pos_binsize+1) )
        for frame in data:
            for fly in frame.itervalues():
                fly_x = fly.center.x
                fly_y = fly.center.y
                try: self.grid[int(fly_x/const.pos_binsize),int(fly_y/const.pos_binsize)] += 1
                except IndexError:
                    print "error adding", fly_x, fly_y, "to bin", fly_x/const.pos_binsize, fly_y/const.pos_binsize, "(size is", self.grid.shape, "\b)"
                # increment grid
            # for each fly
        # for each frame

        self.xticks = range( 0, self.grid.shape[0], max( 200/const.pos_binsize, 1 ) )
        self.xticklabels = []
        for xx in self.xticks:
            self.xticklabels.append( str(xx*const.pos_binsize) )
        self.yticks = range( 0, self.grid.shape[1], max( 200/const.pos_binsize, 1 ) )
        self.yticklabels = []
        for yy in self.yticks:
            self.yticklabels.append( str(yy*const.pos_binsize) )


    ###################################################################
    # draw()
    ###################################################################
    def draw( self ):
        first = False
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot( 111, aspect='equal' )
            self.subplot.set_title("Position histogram for first %d frames"%len( self.data ), fontsize = 12)
            self.subplot.set_xlabel( "x (pixels)" )
            self.subplot.set_ylabel( "y (pixels)" )
            self.subplot.set_xticks( self.xticks )
            self.subplot.set_yticks( self.yticks )
            self.subplot.set_xticklabels( self.xticklabels )
            self.subplot.set_yticklabels( self.yticklabels )
            first = True

        # 2D histogram
        self.subplot.imshow( self.grid.T, cmap=matplotlib.cm.hot )

        if first:
            self.subplot.invert_yaxis()


#######################################################################
# VelPlotPanel
#######################################################################
class VelPlotPanel( PlotPanel ):
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, frame, data ):
        PlotPanel.__init__( self, frame )
        self.data = data

        self.vels = []
        for ff in range( len(self.data)-1 ):
            for fly in self.data[ff].iterkeys():
                if self.data[ff+1].hasItem(fly):
                    vel = self.data[ff][fly].Euc_dist( self.data[ff+1][fly] )
                    if True:#vel < max_jump:
                        self.vels.append( vel )
                # calculate velocity
            # for each fly
        # for each pair of consecutive frames in data
        self.vels = num.array( self.vels )


    ###################################################################
    # draw()
    ###################################################################
    def draw( self ):
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)
            self.subplot.set_title("Velocity histogram for first %d frames"%len( self.data ), fontsize = 12)
            self.subplot.set_xlabel( "fly velocity (pixels/frame)" )
            self.subplot.set_ylabel( "bin count" )

        # histogram
        self.subplot.hist( self.vels, const.vel_bins )
        
        if const.vel_x_min != 'a':
            self.subplot.axis( xmin=const.vel_x_min )
        if const.vel_x_max != 'a':
            self.subplot.axis( xmax=const.vel_x_max )
        if const.vel_y_min != 'a':
            self.subplot.axis( ymin=const.vel_y_min )
        if const.vel_y_max != 'a':
            self.subplot.axis( ymax=const.vel_y_max )


#######################################################################
# TurnPlotPanel
#######################################################################
class TurnPlotPanel( PlotPanel ):
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, frame, data ):
        PlotPanel.__init__( self, frame )
        self.data = data

        self.turns = []
        for ff in range( len(self.data)-1 ):
            for fly in self.data[ff].iterkeys():
                if self.data[ff+1].hasItem(fly):
                    turn = self.data[ff][fly].angle - self.data[ff+1][fly].angle
                    if abs( turn ) < num.pi:
                        self.turns.append( turn )
                # calculate dtheta
            # for each fly
        # for each pair of consecutive frames in data
        self.turns = num.array( self.turns )


    ###################################################################
    # draw()
    ###################################################################
    def draw( self ):
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)
            self.subplot.set_title("Turn histogram for first %d frames"%len( self.data ), fontsize = 12)
            self.subplot.set_xlabel( "turn velocity (rad/frame)" )
            self.subplot.set_ylabel( "bin count" )

        # histogram
        self.subplot.hist( self.turns, const.dth_bins )
        self.subplot.axis( xmin=-num.pi, xmax=num.pi )
        
        if const.dth_x_min != 'a':
            self.subplot.axis( xmin=const.dth_x_min )
        if const.dth_x_max != 'a':
            self.subplot.axis( xmax=const.dth_x_max )
        if const.dth_y_min != 'a':
            self.subplot.axis( ymin=const.dth_y_min )
        if const.dth_y_max != 'a':
            self.subplot.axis( ymax=const.dth_y_max )


class OrnPlotPanel( PlotPanel ):
    def __init__( self, frame, data, title ):
        PlotPanel.__init__( self, frame )
        self.data = data
        self.title = title

        self.orns = []
        for frame in self.data:
            for fly in frame.itervalues():
                self.orns.append( fly.angle )
                # grab angle
            # for each ellipse
        # for each frame in data
        self.orns = num.array( self.orns )
        
    def draw( self ):
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)

        # histogram
        self.subplot.hist( self.orns, const.orn_bins )
        
        #Set some plot attributes
        self.subplot.set_title(self.title, fontsize = 12)
        self.subplot.set_xlabel( "fly orientation (rad)" )
        self.subplot.set_ylabel( "bin count" )
        
class SpacePlotPanel( PlotPanel ):
    def __init__( self, frame, data, title ):
        PlotPanel.__init__( self, frame )
        self.data = data
        self.title = title
        
        self.dists = []
        for frame in self.data:
            for fly1 in frame.iterkeys():
                for fly2 in frame.iterkeys():
                    if fly1 < fly2:
                        self.dists.append( frame[fly1].Euc_dist( frame[fly2] ) )
                    # calculate distance
                # for each pair of ellipses
        # for each frame in data
        self.dists = num.array( self.dists )

    def draw( self ):
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)

        # histogram
        self.subplot.hist( self.dists, const.space_bins )
        
        #Set some plot attributes
        self.subplot.set_title(self.title, fontsize = 12)
        self.subplot.set_xlabel( "distance between flies (pixels)" )
        self.subplot.set_ylabel( "bin count" )
        

class DrawSettingsDialog:
    def __init__( self, parent=None ):
        rsrc = xrc.XmlResource( RSRC_FILE )
        self.frame = rsrc.LoadFrame( parent, "frame_Ctrax_settings" )

        # input box handles
        self.vel_bins_box = xrc.XRCCTRL( self.frame, "text_vel_bins" )
        self.orn_bins_box = xrc.XRCCTRL( self.frame, "text_orn_bins" )
        self.space_bins_box = xrc.XRCCTRL( self.frame, "text_space_bins" )
        self.pos_binsize_box = xrc.XRCCTRL( self.frame, "text_pos_binsize" )
        self.vel_axes_box = xrc.XRCCTRL( self.frame, "text_vel_axes" )
        self.orn_axes_box = xrc.XRCCTRL( self.frame, "text_orn_axes" )
        self.space_axes_box = xrc.XRCCTRL( self.frame, "text_space_axes" )
        self.pos_axes_box = xrc.XRCCTRL( self.frame, "text_pos_axes" )

        # initial values
        self.vel_bins_box.SetValue( str(const.vel_bins) )
        self.orn_bins_box.SetValue( str(const.orn_bins) )
        self.space_bins_box.SetValue( str(const.space_bins) )
        self.pos_binsize_box.SetValue( str(const.pos_binsize) )
        self.vel_axes_box.SetValue( "a,a,a,a" )
        self.orn_axes_box.SetValue( "a,a,a,a" )
        self.space_axes_box.SetValue( "a,a,a,a" )
        self.pos_axes_box.SetValue( "a,a,a,a" )

        # bind to wxvalidatedtext
        wxvt.setup_validated_integer_callback( self.vel_bins_box,
                                               xrc.XRCID("text_vel_bins"),
                                               self.OnTextValidated,
                                               pending_color=params.wxvt_bg )
        wxvt.setup_validated_integer_callback( self.orn_bins_box,
                                               xrc.XRCID("text_orn_bins"),
                                               self.OnTextValidated,
                                               pending_color=params.wxvt_bg )
        wxvt.setup_validated_integer_callback( self.space_bins_box,
                                               xrc.XRCID("text_space_bins"),
                                               self.OnTextValidated,
                                               pending_color=params.wxvt_bg )
        wxvt.setup_validated_integer_callback( self.pos_binsize_box,
                                               xrc.XRCID("text_pos_binsize"),
                                               self.OnTextValidated,
                                               pending_color=params.wxvt_bg )
        wxvt.Validator( self.vel_axes_box, xrc.XRCID("text_vel_axes"),
                        self.OnTextValidated, self.ParseAxes,
                        pending_color=params.wxvt_bg )
        wxvt.Validator( self.orn_axes_box, xrc.XRCID("text_orn_axes"),
                        self.OnTextValidated, self.ParseAxes,
                        pending_color=params.wxvt_bg )
        wxvt.Validator( self.space_axes_box, xrc.XRCID("text_space_axes"),
                        self.OnTextValidated, self.ParseAxes,
                        pending_color=params.wxvt_bg )
        wxvt.Validator( self.pos_axes_box, xrc.XRCID("text_pos_axes"),
                        self.OnTextValidated, self.ParseAxes,
                        pending_color=params.wxvt_bg )

        self.frame.Show()

    def OnTextValidated( self, evt ):
        """User-entered text has been validated; set global variables
        correspondingly."""
        if evt.GetId() == xrc.XRCID( "text_vel_bins" ):
            const.vel_bins = int(self.vel_bins_box.GetValue())
        elif evt.GetId() == xrc.XRCID( "text_orn_bins" ):
            const.orn_bins = int(self.orn_bins_box.GetValue())
        elif evt.GetId() == xrc.XRCID( "text_space_bins" ):
            const.space_bins = int(self.space_bins_box.GetValue())
        elif evt.GetId() == xrc.XRCID( "text_pos_binsize" ):
            const.pos_binsize = int(self.pos_binsize_box.GetValue())
        elif evt.GetId() == xrc.XRCID( "text_vel_axes" ):
            const.vel_x_min = self.new_axes_vals[0]
            const.vel_x_max = self.new_axes_vals[1]
            const.vel_y_min = self.new_axes_vals[2]
            const.vel_y_max = self.new_axes_vals[3]
            # set axes box values to currently stored values (removes user formatting)
            self.vel_axes_box.SetValue( "%s,%s,%s,%s"%(str(const.vel_x_min),
                                                       str(const.vel_x_max),
                                                       str(const.vel_y_min),
                                                       str(const.vel_y_max)) )
        elif evt.GetId() == xrc.XRCID( "text_orn_axes" ):
            const.orn_x_min = self.new_axes_vals[0]
            const.orn_x_max = self.new_axes_vals[1]
            const.orn_y_min = self.new_axes_vals[2]
            const.orn_y_max = self.new_axes_vals[3]
            # set axes box values to currently stored values (removes user formatting)
            self.orn_axes_box.SetValue( "%s,%s,%s,%s"%(str(const.orn_x_min),
                                                       str(const.orn_x_max),
                                                       str(const.orn_y_min),
                                                       str(const.orn_y_max)) )
        elif evt.GetId() == xrc.XRCID( "text_space_axes" ):
            const.space_x_min = self.new_axes_vals[0]
            const.space_x_max = self.new_axes_vals[1]
            const.space_y_min = self.new_axes_vals[2]
            const.space_y_max = self.new_axes_vals[3]
            # set axes box values to currently stored values (removes user formatting)
            self.space_axes_box.SetValue( "%s,%s,%s,%s"%(str(const.space_x_min),
                                                       str(const.space_x_max),
                                                       str(const.space_y_min),
                                                       str(const.space_y_max)) )
        elif evt.GetId() == xrc.XRCID( "text_pos_axes" ):
            const.pos_x_min = self.new_axes_vals[0]
            const.pos_x_max = self.new_axes_vals[1]
            const.pos_y_min = self.new_axes_vals[2]
            const.pos_y_max = self.new_axes_vals[3]
            # set axes box values to currently stored values (removes user formatting)
            self.pos_axes_box.SetValue( "%s,%s,%s,%s"%(str(const.pos_x_min),
                                                       str(const.pos_x_max),
                                                       str(const.pos_y_min),
                                                       str(const.pos_y_max)) )

    def ParseAxes( self, string ):
        """Parse user input for drawings axes limits. Return True or False
        depending on whether input is valid."""
        vals = string.split( ',' ) # split on commas
        if len(vals) != 4: vals = string.split() # try again with whitespace
        if len(vals) != 4:
            return False

        # strip parentheses, etc. and make numeric
        for vv in range( len(vals) ):
            vals[vv] = vals[vv].strip( '()[], ' )
            # test for empty
            if vals[vv] == '': return False
            # test for a
            if vals[vv] == 'a': continue
            # test for int
            if vals[vv].isdigit() or \
                   (vals[vv][0] == '-' and vals[vv][1:].isdigit()): # negative int
                vals[vv] = int(vals[vv])
                continue
            # test for float
            try:
                vals[vv] = float(vals[vv])
            except ValueError: pass
            else: continue

            return False

        # validation successful; save values so we don't have to re-parse later
        self.new_axes_vals = vals
        return True



#######################################################################
# DebugPlotPanel
#######################################################################
class DebugPlotPanel( PlotPanel ):
    """Show an image in a matplotlib window."""
    ###################################################################
    # imshow()
    ###################################################################
    def imshow(self,im):
        self.grid = im
        print self.grid.shape
        print self.grid.T


    ###################################################################
    # draw()
    ###################################################################
    def draw(self):
        if not hasattr( self, 'subplot' ):
            self.subplot = self.figure.add_subplot( 111 )
        if hasattr(self,'grid'):
            self.subplot.imshow( self.grid, cmap=matplotlib.cm.jet )
