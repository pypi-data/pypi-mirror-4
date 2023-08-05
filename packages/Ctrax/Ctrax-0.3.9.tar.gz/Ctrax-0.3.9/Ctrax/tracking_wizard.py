# tracking_wizard.py
# JAB 10/25/11

from codedir import codedir
import os.path
import random
import sys
import time

import numpy as num
import wx
from wx import xrc

import bg_settings
from ellipsesk import est_shape
from fixbg import FixBG
from params import params
from roi import ROI
from setarena import SetArena
from tracking_settings import TrackingSettings
from zoomable_image_canvas import ZoomableImageCanvas

RSRC_FILE = os.path.join( codedir, 'xrc', 'tracking_wizard.xrc')

#######################################################################
# TrackingWizard
#######################################################################
class TrackingWizard:
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, parent_frame, bg, n_frames,
                  get_frame_callback,
                  recalculate_bg_callback,
                  starttracking_callback ):
        """Initialize frame and bind callbacks. Caller must Show() frame."""
        self.bg = bg # bg.BackgroundCalculator object
        self.n_frames = n_frames # number of frames in movie

        # make frame
        rsrc = xrc.XmlResource( RSRC_FILE )
        self.frame = rsrc.LoadFrame( parent_frame, "frame_wizard" )

        # connect variables
        self.reset_button = xrc.XRCCTRL( self.frame, "button_reset_frames" )
        self.prev_button = xrc.XRCCTRL( self.frame, "button_previous" )
        self.default_prev_label = self.prev_button.GetLabel()
        self.next_button = xrc.XRCCTRL( self.frame, "button_next" )
        self.default_next_label = self.next_button.GetLabel()
        self.title_text = xrc.XRCCTRL( self.frame, "text_title" )
        self.instruction_text = xrc.XRCCTRL( self.frame, "text_instructions" )

        self.control_panel = xrc.XRCCTRL( self.frame, "panel_control" )
        self.parent_panel = xrc.XRCCTRL( self.frame, "panel_parent" )
        self.single_panel = xrc.XRCCTRL( self.frame, "panel_single" )
        self.multi_panel = xrc.XRCCTRL( self.frame, "panel_multiple" )

        # bind callbacks
        self.frame.Bind( wx.EVT_SIZE, self.OnResize )
        self.frame.Bind( wx.EVT_BUTTON, self.OnResetFrames, id=xrc.XRCID("button_reset_frames") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnPrevButton, id=xrc.XRCID("button_previous") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnNextButton, id=xrc.XRCID("button_next") )

        # remember parent's callbacks
        self.get_frame_callback = get_frame_callback
        self.recalculate_bg_callback = recalculate_bg_callback
        self.starttracking_callback = starttracking_callback

        # list panels
        self.img_winds = []
        for i in range( 9 ):
            panel = xrc.XRCCTRL( self.frame, "panel%d"%i )
            stext = xrc.XRCCTRL( self.frame, "text_fn%d"%i )

            box = wx.BoxSizer( wx.VERTICAL )
            panel.SetSizer( box )
            canvas = ZoomableImageCanvas( panel )
            box.Add( canvas, 1, wx.EXPAND )
            panel.SetAutoLayout( True )
            panel.Layout()

            self.img_winds.append( {'panel': panel,
                                    'stext': stext,
                                    'canvas': canvas,
                                    'framenumber': i,
                                    'n_obs': 0} )
        panel = xrc.XRCCTRL( self.frame, "panel_img" )
        box = wx.BoxSizer( wx.VERTICAL )
        panel.SetSizer( box )
        canvas = ZoomableImageCanvas( panel )
        box.Add( canvas, 1, wx.EXPAND )
        panel.SetAutoLayout( True )
        panel.Layout()
        self.single_wind = {'panel': panel,
                            'stext': None,
                            'canvas': canvas,
                            'framenumber': 0,
                            'n_obs': 0}

        self.prev_button.Enable( False )
        self.prev_calls = []
        self.cur_call = None
        self.next_calls = []

        params.n_bg_std_thresh = 10
        params.n_bg_std_thresh_low = 1
        self.print_n_obs = False
        self.reset_frame_numbers()
        
        self.init_no_bg()


    ###################################################################
    # show_single()
    ###################################################################
    def show_single( self, evt=None ):
        """Show the large, single-frame image panel."""
        self.multi_panel.Hide()
        self.single_panel.Show()
        self.reset_button.Hide()
        self.redraw()
        self.OnResize( evt )


    ###################################################################
    # show_multi()
    ###################################################################
    def show_multi( self, evt=None ):
        """Show the multi-frame image panel."""
        self.single_panel.Hide()
        self.multi_panel.Show()
        self.reset_button.Show()
        self.redraw()
        self.OnResize( evt )


    ###################################################################
    # showing_winds()
    ###################################################################
    def showing_winds( self ):
        """Return the list of which image windows are currently displayed."""
        if self.multi_panel.IsShown():
            return (self.img_winds, self.multi_panel.GetSizer())
        elif self.single_panel.IsShown():
            return ([self.single_wind], self.single_panel.GetSizer())
        return (None, None)
        

    ###################################################################
    # OnResize()
    ###################################################################
    def OnResize( self, evt ):
        """Window was resized. Rescale images."""
        if evt is not None:
            evt.Skip()

        self.single_panel.SetSize( self.parent_panel.GetSize() )
        self.multi_panel.SetSize( self.parent_panel.GetSize() )

        (winds_to_show, sizer) = self.showing_winds()

        if hasattr( self, 'img_size' ) and winds_to_show is not None:
            for wind_data in winds_to_show:
                panel_item = sizer.GetItem( wind_data['panel'], recursive=True )
                panel_item.SetRatio( float( self.img_size[1] )/self.img_size[0] )
                
            self.frame.Layout()

            for wind_data in winds_to_show:
                wind_data['canvas'].redraw()


    ###################################################################
    # redraw()
    ###################################################################
    def redraw( self ):
        """Redraw the images in all the showing image windows."""
        
        (winds_to_show, sizer) = self.showing_winds()
        if winds_to_show is None: return

        prev_enabled = self.prev_button.Enabled
        next_enabled = self.next_button.Enabled
        self.prev_button.Enable( False )
        self.next_button.Enable( False )

        fmt = 'MONO8'
        line_segs = []
        line_clrs = []
        img_src = 'img'

        # erase
        if hasattr( self.bg, 'center' ) and hasattr( self, 'img_size' ) and \
               self.showing_image_type != params.SHOW_RAW_FRAME and \
               self.showing_image_type != params.SHOW_BACKGROUND:
            for wind_data in winds_to_show:
                img = num.zeros( self.img_size[:2], dtype=num.uint8 ) + 127
                wind_data['canvas'].update_image_and_drawings( wind_data['canvas'].current_source,
                                                               img,
                                                               format=fmt )
                wind_data['n_obs'] = 0

        # redraw
        for wind_data in winds_to_show:

            if self.showing_image_type == params.SHOW_RAW_FRAME:
                img, stamp = self.get_frame_callback( wind_data['framenumber'] )
                self.img_size = img.shape

            elif hasattr( self.bg, 'center' ):
                img, fmt, line_segs, line_clrs, a,b,c, n_obs, d = self.bg.get_sub_image( self.showing_image_type, wind_data['framenumber'] )
                self.img_size = img.shape
                
                wind_data['n_obs'] = n_obs

            else:
                self.img_size = (101,101)
                img = num.zeros( self.img_size, dtype=num.uint8 )
                img_src = 'blank'

            wind_data['canvas'].update_image_and_drawings( img_src, img,
                                                           format=fmt,
                                                           linesegs=line_segs,
                                                           lineseg_colors=line_clrs )
            
        if self.print_n_obs:
            self.reset_framenumber_text()
            
        self.prev_button.Enable( prev_enabled )
        self.next_button.Enable( next_enabled )
        self.redraw_time = time.clock()


    ###################################################################
    # resize_control_panel()
    ###################################################################
    def resize_control_panel( self ):
        """Set size of control panel to fill width of instruction box."""
        w = self.frame.GetSize()[0] - 30 - self.parent_panel.GetSize()[0]
        if 'win' in sys.platform:
            w -= 15
        self.control_panel.SetMinSize( (w,self.control_panel.GetSize()[1]) )


    ###################################################################
    # new_control_radio_box()
    ###################################################################
    def new_control_radio_box( self, choices ):
        """Make a new radio box with specified choices, in control panel."""
        self.resize_control_panel()
        box = wx.BoxSizer( wx.VERTICAL )
        self.control_panel.SetSizer( box )

        self.radio_control = wx.RadioBox( self.control_panel, majorDimension=3, style=wx.RA_SPECIFY_ROWS, choices=choices )        
        box.Add( self.radio_control, 1, wx.EXPAND )
        
        self.control_panel.SetAutoLayout( True )
        self.control_panel.Layout()


    ###################################################################
    # get_radio_control_selection()
    ###################################################################
    def get_radio_control_selection( self ):
        """Return the index of the selected choice in the radio control."""
        if hasattr( self, 'radio_control' ):
            sel = self.radio_control.GetSelection()
            self.radio_control.Destroy()
            delattr( self, 'radio_control' )
            return sel
        return None


    ###################################################################
    # new_slider()
    ###################################################################
    def new_slider( self, value, text ):
        """Make a new slider with an initial value and text legend."""
        self.resize_control_panel()
        box = wx.BoxSizer( wx.VERTICAL )
        self.control_panel.SetSizer( box )

        box.Add( (-1,10), 0 )

        self.slider = wx.ScrollBar( self.control_panel )
        self.slider.SetScrollbar( value, 1, 255, 10 )
        self.slider.SetMinSize( (self.control_panel.GetMinSize()[0],-1) )
        box.Add( self.slider )

        self.slider_text = wx.StaticText( self.control_panel, label=text )
        box.Add( self.slider_text, 0, wx.ALIGN_CENTER_HORIZONTAL )

        self.control_panel.SetAutoLayout( True )
        self.control_panel.Layout()


    ###################################################################
    # remove_slider()
    ###################################################################
    def remove_slider( self ):
        """Remove the slider control."""
        if hasattr( self, 'slider' ):
            self.slider.Destroy()
            delattr( self, 'slider' )
            self.slider_text.Destroy()
            delattr( self, 'slider_text' )


    ###################################################################
    # cleanup_controls()
    ###################################################################
    def cleanup_controls( self ):
        """Remove all controls."""
        self.remove_slider()
        self.get_radio_control_selection()

        self.print_n_obs = False
        self.reset_framenumber_text()


    ###################################################################
    # reset_frame_numbers()
    ###################################################################
    def reset_frame_numbers( self ):
        """Choose new random frame numbers for each image window."""
        framenumbers = num.zeros( (len( self.img_winds ),), dtype=num.int32 ) - 1
        for i in range( len( self.img_winds ) ):
            f = random.randrange( 0, self.n_frames )
            while f in framenumbers:
                f = random.randrange( 0, self.n_frames )
            framenumbers[i] = f
        framenumbers.sort()

        for i in range( len( self.img_winds ) ):
            self.img_winds[i]['framenumber'] = framenumbers[i]

        self.reset_framenumber_text()

        
    ###################################################################
    # reset_framenumber_text()
    ###################################################################
    def reset_framenumber_text( self ):
        """Set text labels for image windows."""
        for wnd in self.img_winds:
            if self.print_n_obs:
                text = "frame %d: %d flies"%(wnd['framenumber'], wnd['n_obs'])
            else:
                text = "frame %d"%wnd['framenumber']
            wnd['stext'].SetLabel( text )

        if self.print_n_obs:
            self.OnResize( None )
            # should also resize if n_obs used to be true and is now false


    ###################################################################
    # OnResetFrames()
    ###################################################################
    def OnResetFrames( self, evt ):
        """GUI callback to set frame numbers."""
        self.reset_frame_numbers()
        self.redraw()


    ###################################################################
    # OnPrevButton()
    ###################################################################
    def OnPrevButton( self, evt ):
        """'Previous' button pressed. Go back to last step."""
        if len( self.prev_calls ) == 0: return # should be disabled, actually
        
        prev_call = self.prev_calls.pop()
        if len( self.prev_calls ) == 0:
            self.prev_button.Enable( False )
        self.next_button.SetLabel( self.default_next_label )
        prev_call()
        

    ###################################################################
    # OnNextButton()
    ###################################################################
    def OnNextButton( self, evt ):
        """'Next' button pressed. Execute some calls."""
        if len( self.next_calls ) == 0:
            self.frame.Close()
        else:
            if self.cur_call is not None:
                self.prev_calls.append( self.cur_call )
            self.prev_button.Enable( True )
            for call in self.next_calls:
                call()


    ###################################################################
    # init_no_bg()
    ###################################################################
    def init_no_bg( self ):
        """Set instructions for initializing background."""
        self.showing_image_type = params.SHOW_RAW_FRAME
        self.show_multi()
        self.cleanup_controls()

        self.title_text.SetLabel( "Initialize background" )
        self.instruction_text.SetLabel( "Ctrax depends on an unchanging background, which is subtracted away from each frame of video to leave only the moving objects (i.e., the flies). First, are your flies dark on a light background or light on a dark background?" )
        self.frame.Layout()

        self.new_control_radio_box( ["dark on light background", "light on dark background", "not so clean"] )
        
        self.cur_call = self.init_no_bg
        self.next_calls = [self.set_bg_type]


    ###################################################################
    # set_bg_type()
    ###################################################################
    def set_bg_type( self ):
        """Use current value of radio control to determine background type."""
        selection = self.get_radio_control_selection()
        if selection == 0:
            self.bg.bg_type = 'dark_on_light'
        elif selection == 1:
            self.bg.bg_type = 'light_on_dark'
        else:
            self.bg.bg_type = 'other'

        # calculate background
        success = self.recalculate_bg_callback()

        if success:
            self.redraw()
            self.choose_roi_type()
        else:
            self.OnPrevButton( None )


    ###################################################################
    # choose_roi_type()
    ###################################################################
    def choose_roi_type( self ):
        """Allow user to select region-of-interest type."""
        self.showing_image_type = params.SHOW_RAW_FRAME
        self.show_multi()
        self.cleanup_controls()

        self.title_text.SetLabel( "Define region of interest" )
        self.instruction_text.SetLabel( "We can define a region of interest to prevent tracking in areas where no flies will ever be. What shape is your arena or tracking area?" )

        self.new_control_radio_box( ["circular", "polygonal", "don't use region of interest"] )

        self.frame.Layout()
        
        self.cur_call = self.choose_roi_type
        self.next_calls = [self.set_roi_type]


    ###################################################################
    # set_roi_type()
    ###################################################################
    def set_roi_type( self ):
        """Use current value of radio control to set region-of-interest type."""
        params.do_set_circular_arena = False
        self.prev_button.Enable( False )
        self.next_button.Enable( False )
        
        selection = self.get_radio_control_selection()
        if selection == 0:
            # circular
            params.do_set_circular_arena = True
            self.roi = SetArena( self.frame, self.bg.center )
            self.roi.frame.Bind( wx.EVT_CLOSE, self.OnQuitCircularArena )
            
        elif selection == 1:
            # polygonal
            self.roi = ROI( self.frame, self.bg )
            self.roi.frame.Bind( wx.EVT_BUTTON, self.OnQuitPolygonalArena, id=xrc.XRCID("quit_button") )
            self.roi.frame.Bind( wx.EVT_CLOSE, self.OnQuitPolygonalArena )
            
        else:
            # none
            self.bg.SetROI( num.ones( self.img_size, num.bool ) )
            params.roipolygons = []
            self.bg.UpdateIsArena()

            self.prev_button.Enable( True )
            self.next_button.Enable( True )

            self.check_bg()

        if hasattr( self, 'roi' ):
            self.roi.frame.Show()


    ###################################################################
    # OnQuitCircularArena()
    ###################################################################
    def OnQuitCircularArena( self, evt ):
        """Circular arena ROI was set. Grab parameters and continue."""
        [params.arena_center_x, params.arena_center_y,
         params.arena_radius] = self.roi.GetArenaParameters()
        self.bg.UpdateIsArena()

        self.roi.frame.Destroy()
        delattr( self, 'roi' )

        self.prev_button.Enable( True )
        self.next_button.Enable( True )

        self.check_bg()


    ###################################################################
    # OnQuitPolygonalArena()
    ###################################################################
    def OnQuitPolygonalArena( self, evt ):
        """Polygonal arena ROI was set. Grab parameters and continue."""
        if not self.roi.CheckSave():
            # user pressed "cancel"
            return

        self.roi.frame.Destroy()
        delattr( self, 'roi' )

        self.prev_button.Enable( True )
        self.next_button.Enable( True )

        self.check_bg()


    ###################################################################
    # check_bg()
    ###################################################################
    def check_bg( self ):
        """Prompt user to check over and correct background image."""
        if params.movie.type == 'sbfmf':
            # skip this step
            self.choose_high_threshold()
            return
        
        self.showing_image_type = params.SHOW_BACKGROUND
        self.show_single()
        self.cleanup_controls()

        self.title_text.SetLabel( "Check background" )
        self.instruction_text.SetLabel( "Look carefully at the background image. It should look exactly like an empty arena. If there are any \"ghosts\" of flies in the background image, then flies entering those areas will likely not be tracked correctly. Does the image have \"ghost flies\"?" )

        self.new_control_radio_box( ["yes, fix ghosts", "no, it's fine"] )

        self.frame.Layout()

        if self.prev_calls[-1] == self.check_bg:
            self.cur_call = None
        else:
            self.cur_call = self.check_bg
        self.next_calls = [self.decide_fix_bg]


    ###################################################################
    # decide_fix_bg()
    ###################################################################
    def decide_fix_bg( self ):
        """Use current value of radio control to determine if background needs to be fixed."""
        self.prev_button.Enable( False )
        self.next_button.Enable( False )
        selection = self.get_radio_control_selection()
        if selection == 0:
            self.roi = FixBG( self.frame, self.bg )
            self.roi.frame.Bind( wx.EVT_BUTTON, self.OnQuitFixBg, id=xrc.XRCID("quit_button") )
            self.roi.frame.Bind( wx.EVT_CLOSE, self.OnQuitFixBg )
            self.roi.frame.Show()

        else:
            self.prev_button.Enable( True )
            self.next_button.Enable( True )
            self.choose_high_threshold()


    ###################################################################
    # OnQuitFixBg()
    ###################################################################
    def OnQuitFixBg( self, evt ):
        """Fix-background dialog was closed. Continue."""
        self.OnQuitPolygonalArena( evt )
        self.choose_high_threshold()


    ###################################################################
    # choose_high_threshold()
    ###################################################################
    def choose_high_threshold( self ):
        """Allow user to set high background threshold."""
        self.showing_image_type = params.SHOW_THRESH
        self.show_multi()
        self.cleanup_controls()

        self.print_n_obs = True
        self.reset_framenumber_text()
        
        self.title_text.SetLabel( "Choose high threshold" )
        self.instruction_text.SetLabel( "After subtracting the background, Ctrax uses thresholds to determine which \"foreground\" pixels truly belong to flies. The high threshold is the minumum deviation from background required in at least one pixel of each fly. Set it as high as you can while each fly is visible." )

        self.new_slider( params.n_bg_std_thresh, "high threshold: %3d"%params.n_bg_std_thresh )
        self.slider.Bind( wx.EVT_SCROLL, self.OnHighThreshChanged )
        self.frame.Layout()

        self.cur_call = self.choose_high_threshold
        self.next_calls = [self.choose_low_threshold]


    ###################################################################
    # OnHighThreshChanged()
    ###################################################################
    def OnHighThreshChanged( self, evt ):
        """Value changed in high threshold slider. Update values in bg."""
        evt.Skip()
        new_thresh = self.slider.GetThumbPosition()
        if new_thresh != params.n_bg_std_thresh:
            params.n_bg_std_thresh = new_thresh
            self.slider_text.SetLabel( "high threshold: %3d"%params.n_bg_std_thresh )
            self.redraw()


    ###################################################################
    # choose_low_threshold()
    ###################################################################
    def choose_low_threshold( self ):
        """Allow user to set low background threshold."""
        if params.n_bg_std_thresh_low > params.n_bg_std_thresh:
            params.n_bg_std_thresh_low = params.n_bg_std_thresh
        
        self.showing_image_type = params.SHOW_CC
        self.show_multi()
        self.cleanup_controls()

        self.print_n_obs = True
        self.reset_framenumber_text()

        self.title_text.SetLabel( "Choose low threshold" )
        self.instruction_text.SetLabel( "The high threshold is the minimum signal strength required in at least one pixel of each connected component (fly). The low threshold defines the edges of the flies - pixels are foreground if they are above the low threshold and also near a pixel above the high threshold. Set it to make each fly distinct." )

        self.new_slider( params.n_bg_std_thresh_low, "low threshold: %3d"%params.n_bg_std_thresh_low )
        self.slider.Bind( wx.EVT_SCROLL, self.OnLowThreshChanged )
        self.frame.Layout()

        self.cur_call = self.choose_low_threshold
        self.next_calls = [self.choose_shape_method]


    ###################################################################
    # OnLowThreshChanged()
    ###################################################################
    def OnLowThreshChanged( self, evt ):
        """Value changed in low threshold slider. Update values in bg."""
        evt.Skip()
        new_thresh = self.slider.GetThumbPosition()
        if new_thresh <= params.n_bg_std_thresh and \
               new_thresh != params.n_bg_std_thresh_low:
            params.n_bg_std_thresh_low = new_thresh
            self.slider_text.SetLabel( "low threshold: %3d"%params.n_bg_std_thresh_low )
            self.redraw()
        elif new_thresh > params.n_bg_std_thresh:
            self.slider.SetThumbPosition( params.n_bg_std_thresh_low )


    ###################################################################
    # choose_shape_method()
    ###################################################################
    def choose_shape_method( self ):
        """Choose whether to automatically compute fly shape."""
        self.cleanup_controls()
        
        self.title_text.SetLabel( "Auto-compute shape?" )
        self.instruction_text.SetLabel( "Setting bounds on the shapes of real flies in the movie helps allow Ctrax to discard spurious detections. These bounds can be estimated automatically. However, if your current threshold settings have many spurious detections, the automatic computation might prefer false flies to the real ones." )

        self.new_control_radio_box( ["auto-compute shapes", "manually set bounds"] )
        self.frame.Layout()

        self.cur_call = self.choose_shape_method
        self.next_calls = [self.set_shape_method]

    
    ###################################################################
    # set_shape_method()
    ###################################################################
    def set_shape_method( self ):
        """A shape-computation method was selected. Take action."""
        selection = self.get_radio_control_selection()
        if selection == 0:
            # auto-compute shape
            wx.BeginBusyCursor()
            wx.Yield()
            success = est_shape( self.bg, self.frame )
            wx.EndBusyCursor()

            if success:
                self.show_shape_results()
            else:
                self.OnPrevButton( None )
            
        elif selection == 1:
            # launch settings for manual shape setting
            self.prev_button.Enable( False )
            self.next_button.Enable( False )
            
            self.tracking_settings = TrackingSettings( self.frame, self.bg, 0 )
            self.tracking_settings.frame.Bind( wx.EVT_CLOSE, self.OnQuitTrackingSettings )
            self.tracking_settings.frame.Bind( wx.EVT_BUTTON, self.OnQuitTrackingSettings, id=xrc.XRCID("done") )
            self.tracking_settings.frame.Show()

            # hack to switch dialog to manual settings
            self.tracking_settings.automatic_shape_input.SetValue( False )
            self.tracking_settings.manual_shape_input.SetValue( True )
            self.tracking_settings.OnAutomatic( None )

 
    ###################################################################
    # OnQuitTrackingSettings()
    ###################################################################
    def OnQuitTrackingSettings( self, evt ):
        """Tracking settings dialog was closed. Continue toward tracking."""
        self.tracking_settings.frame.Destroy()
        delattr( self, 'tracking_settings' )

        self.prev_button.Enable( True )
        self.next_button.Enable( True )

        self.show_shape_results()


    ###################################################################
    # show_shape_results()
    ###################################################################
    def show_shape_results( self ):
        """Shapes were computed. Show results."""
        self.showing_image_type = params.SHOW_ELLIPSES
        self.show_multi()
        self.cleanup_controls()

        self.print_n_obs = True
        self.reset_framenumber_text()

        self.title_text.SetLabel( "Start tracking?" )
        self.instruction_text.SetLabel( "Check whether each fly is surrounded by exactly one ellipse in each frame. (You can drag in the frame to zoom in; double-click to zoom out. Also press \"Randomize Frames\" a few times.) Close this window to finish without tracking, or press \"Track\"!" )
        self.frame.Layout()

        self.next_calls = [self.start_tracking]
        self.next_button.SetLabel( "Track" )

    
    ###################################################################
    # start_tracking()
    ###################################################################
    def start_tracking( self ):
        """Done with wizard. Start tracking."""
        self.frame.Close()
        self.starttracking_callback()

        
    ###################################################################
    # test_call()
    ###################################################################
    def test_call( self ):
        self.title_text.SetLabel( "Test complete" )
        self.instruction_text.SetLabel( "You've reached the test callback. This is only a test." )
        self.frame.Layout()

        self.next_calls = []
        self.next_button.SetLabel( "Finish" )
        
