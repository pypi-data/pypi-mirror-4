# Ctrax_settings.py
# KMB 09/12/07

import os
import sys
import codedir

import wx
from wx import xrc
import numpy as num

import motmot.wxvalidatedtext.wxvalidatedtext as wxvt
from motmot.wxglvideo.simple_overlay import DynamicImageCanvas

import draw
from params import params
from phonehome import HomePhoner
import tracking_settings
import chooseorientations
from version import __version__, DEBUG
from tracking_wizard import TrackingWizard

DEBUG_USERFILE = False
if not DEBUG:
    DEBUG_USERFILE = False

RSRC_FILE = os.path.join(codedir.codedir,'xrc','Ctrax.xrc')
ICON_FILE = os.path.join(codedir.codedir,'icons','Ctraxicon.ico')

# these may import 'const'
import algorithm as alg
import bg
from bg_settings import BgSettingsDialog
from ellipses_draw import EllipseFrame

ID_PRINTINTERVALS = 837487
ID_PRINTBUFFEREL = 837488
ID_PRINTFRAME = 837489


class AppWithSettings( wx.App ):
    """Cannot be used alone -- this class only exists
    to keep settings GUI code together in one file."""
    def InitGUI( self ):
        """Load XML resources, create handles, bind callbacks."""
        rsrc = xrc.XmlResource( RSRC_FILE )

        self.frame = rsrc.LoadFrame( None, "frame_Ctrax" )
        self.frame.SetIcon(wx.Icon(ICON_FILE, wx.BITMAP_TYPE_ICO))
        self.SetTopWindow( self.frame )

        # make references to useful objects
        self.menu = self.frame.GetMenuBar()
        if DEBUG: 
            self.debugmenu = wx.Menu()
            self.debugmenu.Append(ID_PRINTINTERVALS,"Print Intervals",
                                  "Print frame intervals tracked, buffered, and written.")
            self.debugmenu.Append(ID_PRINTBUFFEREL,"Print Buffer...",
                                  "Print ellipses stored at specified element of buffer.")
            self.debugmenu.Append(ID_PRINTFRAME,"Print Frame...",
                                  "Pring ellipses for specified frame.")
            self.menu.Append( self.debugmenu, "DEBUG" )
            
        self.status = xrc.XRCCTRL( self.frame, "bar_status" )
        self.framenumber_text = xrc.XRCCTRL( self.frame, "text_framenumber" )
        self.num_flies_text = xrc.XRCCTRL( self.frame, "text_num_flies" )
        self.rate_text = xrc.XRCCTRL( self.frame, "text_refresh_rate")
        self.slider = xrc.XRCCTRL( self.frame, "slider_frame" )
        self.slider.Enable( False )

        # make image window
        self.img_panel = xrc.XRCCTRL( self.frame, "panel_img" )
        self.reset_img_wind()

        self.zoommode = False
        self.zoom_dragging = False
        self.zoom_drag_roi_scale = 1.

        # set up tools
        self.toolbar = xrc.XRCCTRL(self.frame,'toolbar')

        # other tools
        self.zoom_id = xrc.XRCID('zoom')
        self.play_id = xrc.XRCID('play')
        self.stop_id = xrc.XRCID('stop')
        self.speedup_id = xrc.XRCID('speed_up')
        self.slowdown_id = xrc.XRCID('slow_down')
        self.refresh_id = xrc.XRCID('refresh')

        # set up appearances for toolbar
        self.toolbar.SetToggle(self.zoommode,self.zoom_id)
        self.stop_tracking_tooltip = 'Stop Tracking'
        self.stop_playback_tooltip = 'Stop Video Playback'
        self.start_playback_tooltip = 'Start Video Playback'
        self.speedup_tracking_tooltip = 'Increase Refresh Rate'
        self.speedup_playback_tooltip = 'Increase Playback Speed'
        self.slowdown_tracking_tooltip = 'Decrease Refresh Rate'
        self.slowdown_playback_tooltip = 'Decrease Playback Speed'
        self.play_speed = 1.0

        self.UpdateToolBar('stopped')

        # bind callbacks
        # file menu
        self.frame.Bind( wx.EVT_MENU, self.OnOpen, id=xrc.XRCID("menu_file_open") )
        self.frame.Bind( wx.EVT_MENU, self.OnLoadSettings, id=xrc.XRCID("menu_load_settings") )
        self.frame.Bind( wx.EVT_MENU, self.OnBatch, id=xrc.XRCID("menu_file_batch") )
        self.frame.Bind( wx.EVT_MENU, self.OnSave, id=xrc.XRCID("menu_file_export") )
        self.frame.Bind( wx.EVT_MENU, self.OnSaveAvi, id=xrc.XRCID("menu_file_save_avi") )
        self.frame.Bind( wx.EVT_MENU, self.OnSaveCsv, id=xrc.XRCID("menu_file_save_csv") )
        self.frame.Bind( wx.EVT_MENU, self.OnSaveDiagnostics, id=xrc.XRCID("menu_file_save_diagnostics") )
        self.frame.Bind( wx.EVT_MENU, self.OnQuit, id=xrc.XRCID("menu_file_quit") )
        # help menu
        self.frame.Bind( wx.EVT_MENU, self.OnHelp, id=xrc.XRCID("menu_help_help") )
        self.frame.Bind( wx.EVT_MENU, self.OnAbout, id=xrc.XRCID("menu_help_about") )
        # track menu
        self.frame.Bind( wx.EVT_MENU, self.OnStartTrackingMenu, id=xrc.XRCID("menu_track_start") )
        self.frame.Bind( wx.EVT_MENU, self.OnStartTrackingMenu, id=xrc.XRCID("menu_track_resume") )
        self.frame.Bind( wx.EVT_MENU, self.OnStartTrackingMenu, id=xrc.XRCID("menu_track_resume_here") )
        self.frame.Bind( wx.EVT_MENU, self.OnWriteSBFMF, id=xrc.XRCID("menu_track_writesbfmf") )
        self.frame.Bind( wx.EVT_MENU, self.OnComputeBg, id=xrc.XRCID("menu_compute_background") )
        self.frame.Bind( wx.EVT_MENU, self.OnComputeShape, id=xrc.XRCID("menu_compute_shape") )
        self.frame.Bind( wx.EVT_MENU, self.OnTrackingWizard, id=xrc.XRCID("menu_tracking_wizard") )
        # settings menu
        self.frame.Bind( wx.EVT_MENU, self.OnSettingsBGModel, id=xrc.XRCID("menu_settings_bg_model") )
        self.frame.Bind( wx.EVT_MENU, self.OnSettingsBG, id=xrc.XRCID("menu_settings_bg") )
        self.frame.Bind( wx.EVT_MENU, self.OnSettingsTracking, id=xrc.XRCID("menu_settings_tracking") )
        self.frame.Bind( wx.EVT_MENU, self.OnChooseOrientations,id=xrc.XRCID("menu_choose_orientations"))
        #self.frame.Bind( wx.EVT_MENU, self.OnEllipseSize, id=xrc.XRCID("menu_settings_ellipses") )
        #self.frame.Bind( wx.EVT_MENU, self.OnCheckColorblind, id=xrc.XRCID("menu_settings_use_colorblind") )
        self.frame.Bind( wx.EVT_MENU, self.OnCheckShowAnn, id=xrc.XRCID("menu_playback_show_ann") )
        self.frame.Bind( wx.EVT_MENU, self.OnCheckRefresh, id=xrc.XRCID("menu_do_refresh") )
        self.frame.Bind( wx.EVT_MENU, self.OnTailLength, id=xrc.XRCID("menu_playback_tails") )
        self.frame.Bind( wx.EVT_MENU, self.OnCheckDim, id=xrc.XRCID("menu_playback_dim") )
        self.frame.Bind( wx.EVT_MENU, self.OnCheckZoom, id=xrc.XRCID("menu_settings_zoom") )
        # analyze menu
        self.frame.Bind( wx.EVT_MENU, self.OnMakePlot, id=xrc.XRCID("menu_analyze_plottraj") )
        self.frame.Bind( wx.EVT_MENU, self.OnMakePlot, id=xrc.XRCID("menu_analyze_plotvel") )
        self.frame.Bind( wx.EVT_MENU, self.OnMakePlot, id=xrc.XRCID("menu_analyze_histpos") )
        self.frame.Bind( wx.EVT_MENU, self.OnMakePlot, id=xrc.XRCID("menu_analyze_histspeed") )
        self.frame.Bind( wx.EVT_MENU, self.OnMakePlot, id=xrc.XRCID("menu_analyze_histdtheta") )

        # DEBUG
        if DEBUG:
            self.frame.Bind( wx.EVT_MENU, self.OnDebugPrintIntervals,id=ID_PRINTINTERVALS )
            self.frame.Bind( wx.EVT_MENU, self.OnDebugPrintBufferElement,id=ID_PRINTBUFFEREL )
            self.frame.Bind( wx.EVT_MENU, self.OnDebugPrintFrame,id=ID_PRINTFRAME )

        # stats menu
        #self.frame.Bind( wx.EVT_MENU, self.OnStats, id=xrc.XRCID("menu_stats_vel") )
        #self.frame.Bind( wx.EVT_MENU, self.OnStats, id=xrc.XRCID("menu_stats_orn") )
        #self.frame.Bind( wx.EVT_MENU, self.OnStats, id=xrc.XRCID("menu_stats_space") )
        #self.frame.Bind( wx.EVT_MENU, self.OnStats, id=xrc.XRCID("menu_stats_pos") )
        #self.frame.Bind( wx.EVT_MENU, self.OnSettingsStats, id=xrc.XRCID("menu_stats_settings") )
        #self.frame.Bind( wx.EVT_MENU, self.OnCheckBatchStats, id=xrc.XRCID("menu_stats_batch") )
        # miscellaneous events
        self.frame.Bind( wx.EVT_CLOSE, self.OnQuit )
        self.frame.Bind( wx.EVT_SCROLL, self.OnSlider, self.slider )
        self.frame.Bind( wx.EVT_SIZE, self.OnResize )
        self.frame.Bind( wx.EVT_MAXIMIZE, self.OnResize ) # not called in Gnome?
        # toolbar
        self.frame.Bind(wx.EVT_TOOL,self.ZoomToggle,id=self.zoom_id)
        self.frame.Bind(wx.EVT_TOOL,self.OnPlayButton,id=self.play_id)
        self.frame.Bind(wx.EVT_TOOL,self.OnStopButton,id=self.stop_id)
        self.frame.Bind(wx.EVT_TOOL,self.OnSpeedUpButton,id=self.speedup_id)
        self.frame.Bind(wx.EVT_TOOL,self.OnSlowDownButton,id=self.slowdown_id)
        self.frame.Bind(wx.EVT_TOOL,self.OnRefreshButton,id=self.refresh_id)
        wxvt.setup_validated_integer_callback(self.framenumber_text,
                                              xrc.XRCID('text_framenumber'),
                                              self.OnFrameNumberValidated,
                                              pending_color=params.status_blue)

        self.do_refresh = self.menu.IsChecked( xrc.XRCID("menu_do_refresh") )

        params.enable_feedback( True )

        if self.input_file_was_specified:
            self.menu.Enable( xrc.XRCID("menu_file_open"), False )
        

    def InitState(self):
        # default settings, prior to opening GUI
        if 'win' in sys.platform:
            homedir = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        else:
            homedir = os.environ['HOME']
        self.dir = homedir
        self.ellipse_thickness = params.ellipse_thickness

        # initialize state values
        self.start_frame = 0
        self.tracking = False
        self.batch = None
        self.batch_data = None
        self.bg_window_open = False
        self.framesbetweenrefresh = 1
        self.request_refresh = False
        self.do_refresh = False
        self.dowritesbfmf = False
        self.tracking_settings_window_open = False
        self.choose_orientations_window_open = False


    def SetPlayToolTip(self,s):
        self.toolbar.SetToolShortHelp(self.play_id,s)

    def SetStopToolTip(self,s):
        self.toolbar.SetToolShortHelp(self.stop_id,s)

    def SetSpeedUpToolTip(self,s):
        self.toolbar.SetToolShortHelp(self.speedup_id,s)

    def SetSlowDownToolTip(self,s):
        self.toolbar.SetToolShortHelp(self.slowdown_id,s)

    def EnableRefreshBitmap(self,state):
        self.toolbar.EnableTool(self.refresh_id,state)

    def EnablePlayBitmap(self,state):
        self.toolbar.EnableTool(self.play_id,state)

    def EnableStopBitmap(self,state):
        self.toolbar.EnableTool(self.stop_id,state)

    def UpdateToolBar(self,state):
        if state == 'stopped':
            self.EnablePlayBitmap(True)
            self.SetPlayToolTip(self.start_playback_tooltip)
            self.EnableStopBitmap(True)
            self.SetSpeedUpToolTip(self.speedup_playback_tooltip)
            self.SetSlowDownToolTip(self.slowdown_playback_tooltip)
            self.EnableRefreshBitmap(False)
            self.set_rate_text( use_refresh=False )
        else:
            self.EnableStopBitmap(True)
            self.EnablePlayBitmap(False)
            if self.tracking or (hasattr( self, 'batch_executing' ) and self.batch_executing):
                self.SetStopToolTip(self.stop_tracking_tooltip)
                self.SetSpeedUpToolTip(self.speedup_tracking_tooltip)
                self.SetSlowDownToolTip(self.slowdown_tracking_tooltip)
                self.EnableRefreshBitmap(True)
                self.set_rate_text( use_refresh=True )
            else:
                self.SetStopToolTip(self.stop_playback_tooltip)
                self.SetSpeedUpToolTip(self.speedup_playback_tooltip)
                self.SetSlowDownToolTip(self.slowdown_playback_tooltip)
                self.EnableRefreshBitmap(False)
                self.set_rate_text( use_refresh=False )

    def reset_img_wind( self ):
        box = wx.BoxSizer( wx.VERTICAL )
        self.img_panel.SetSizer( box )
        if self.has( 'img_wind' ):
            self.img_wind.Show( False )
        self.img_wind = DynamicImageCanvas( self.img_panel, -1 )
        box.Add( self.img_wind, 1, wx.EXPAND )
        self.img_panel.SetAutoLayout( True )
        self.img_panel.Layout()

    def set_rate_text( self, use_refresh=False ):
        if not use_refresh:
            if self.play_speed >= 1.:
                self.rate_text.SetValue( "Play Speed: %.1fx"%self.play_speed )
            elif self.play_speed >= 0.1:
                self.rate_text.SetValue( "Play Speed: %.2fx"%self.play_speed )
            else:
                self.rate_text.SetValue( "Play Speed: %.3fx"%self.play_speed )
        else:
            if self.do_refresh:
                self.rate_text.SetValue( "Refresh Period: %02d fr"%self.framesbetweenrefresh )
            else:
                self.rate_text.SetValue( "Refresh: Never" )


    ###################################################################
    # constrain_window_to_screen()
    ###################################################################
    def constrain_window_to_screen( self, pos, size ):
        x = max( min( pos[0], wx.DisplaySize()[0] - size[0] ), 0 )
        y = max( min( pos[1], wx.DisplaySize()[1] - size[1] ), 0 )
        return (x,y)


    ###################################################################
    # ReadUserfile()
    ###################################################################
    def ReadUserfile( self ):
        """Read user settings from file. Set window size, location. Called on startup."""
        try:
            if 'win' in sys.platform:
                homedir = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
            else:
                homedir = os.environ['HOME']
            self.userfile_name = os.path.join( homedir, '.Ctraxrc' )
            userfile = open( self.userfile_name, "r" )
            # line 1: last version used
            last_version = userfile.readline().rstrip()
            if last_version != __version__:
                wx.MessageBox( "Welcome to Ctrax version %s"%__version__,
                               "Ctrax updated", wx.ICON_INFORMATION )
            if DEBUG_USERFILE: print "read last version", last_version
            # line 2: data directory
            self.dir = userfile.readline().rstrip()
            if DEBUG_USERFILE: print "read directory", self.dir
            # line 3: window position and size
            last_pos, last_size = str222tuples( userfile.readline().rstrip() )
            last_pos = self.constrain_window_to_screen( last_pos, last_size )
            self.frame.SetPosition( last_pos )
            self.frame.SetSize( last_size )
            if DEBUG_USERFILE: print "read last main window position"
            # line 4: bg window info
            try:
                self.last_bg_pos, self.last_bg_size = \
                                  str222tuples( userfile.readline().rstrip() )
            except (ValueError, IndexError):
                self.last_bg_pos = None
                self.last_bg_size = None
            if DEBUG_USERFILE: print "read last bg window position"
            # line 5: batch window info
            try:
                self.last_batch_pos, self.last_batch_size = \
                                  str222tuples( userfile.readline().rstrip() )
            except (ValueError, IndexError):
                self.last_batch_pos = None
                self.last_batch_size = None
            if DEBUG_USERFILE: print "read last batch window position"
            # line 6: use colorblind pallette?
            use_cb = userfile.readline().rstrip()
            #if use_cb == "True":
            #    self.menu.Check( xrc.XRCID("menu_settings_use_colorblind"), True )
            #    params.use_colorblind_palette = True
            if DEBUG_USERFILE: print "read colorblind palette setting", use_cb
            #    params.colors = params.colorblind_palette
            # line 7: ellipse thickness
            use_et = userfile.readline().rstrip()
            if use_et.isdigit():
                self.ellipse_thickness = int(use_et)
            if DEBUG_USERFILE: print "read ellipse thickness", use_et
            # line 8: tail length
            use_tl = userfile.readline().rstrip()
            if use_tl.isdigit():
                params.tail_length = int(use_tl)
            if DEBUG_USERFILE: print "read tail length", use_tl
            # line 9: dim image?
            use_di = userfile.readline().rstrip()
            if use_di == "True":
                self.menu.Check( xrc.XRCID("menu_playback_dim"), True )
            if DEBUG_USERFILE: print "read dim-image flag", use_di
            # line 10: file-save directory
            self.save_dir = userfile.readline().rstrip()
            if DEBUG_USERFILE: print "read save directory", self.save_dir
            # line 11: zoom window info
            try:
                self.last_zoom_pos, self.last_zoom_size = \
                                  str222tuples( userfile.readline().rstrip() )
            except (ValueError, IndexError):
                self.last_zoom_pos = None
                self.last_zoom_size = None
            if DEBUG_USERFILE: print "read last zoom window position", self.last_zoom_pos, self.last_zoom_size
            # line 12: extension of last opened movie
            self.last_movie_ext = userfile.readline().rstrip()
            if DEBUG_USERFILE: print "read last extension", self.last_movie_ext
            # line 13: newest version of Ctrax available
            self.newest_ctrax_notified = userfile.readline().rstrip()
            if self.newest_ctrax_notified == '':
                self.newest_ctrax_notified = __version__
            if DEBUG_USERFILE: print "read last-notified version", self.newest_ctrax_notified
            # line 14: newest version of Ctrax Matlab toolboxes available
            self.newest_matlab_notified = userfile.readline().rstrip()
            if self.newest_matlab_notified == '' or self.newest_matlab_notified == "None":
                self.newest_matlab_notified = None
            if DEBUG_USERFILE: print "read last matlab version", self.newest_matlab_notified
            # line 15: does user want notification for newer versions?
            use_note = userfile.readline().rstrip()
            self.menu.Check( xrc.XRCID("menu_help_updates"),
                             (use_note == "True" or use_note == '') )
            if DEBUG_USERFILE: print "read wants notifications", use_note
            # line 16: does user want to be prompted for annotation filenames?
            use_annprompt = userfile.readline().rstrip()
            self.menu.Check( xrc.XRCID("menu_settings_annprompt"),
                             (use_annprompt == "True" or use_annprompt == '') )
        except:
            # silent on all errors... not really important if this fails.
            # however, some attributes do need to be initialized, or
            # else we'll raise errors later (on quit, at latest)
            if not hasattr( self, 'last_bg_pos' ):
                self.last_bg_pos = None
                self.last_bg_size = None
            if not hasattr( self, 'last_batch_pos' ):
                self.last_batch_pos = None
                self.last_batch_size = None
            if not hasattr( self, 'save_dir' ):
                if hasattr( self, 'dir' ):
                    self.save_dir = self.dir
                else:
                    if 'win' in sys.platform:
                        self.save_dir = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
                    else:
                        self.save_dir = os.environ['HOME']
            if not hasattr( self, 'last_zoom_pos' ):
                self.last_zoom_pos = None
                self.last_zoom_size = None
            if not hasattr( self, 'last_movie_ext' ):
                self.last_movie_ext = '.fmf'
            if not hasattr( self, 'newest_ctrax_notified' ):
                self.newest_ctrax_notified = __version__
            if not hasattr( self, 'newest_matlab_notified' ):
                self.newest_matlab_notified = None
        finally:
            try:
                userfile.close()
            except: pass

        # phone home for software updates
        HomePhoner( self.alert_new_version )
        

    ###################################################################
    # alert_new_version()
    ###################################################################
    def alert_new_version( self, latest_ctrax_version, latest_matlab_version ):
        """Alert user if new version of Ctrax is available."""
        if latest_ctrax_version is None:
            return

        # construct alert
        alert_str = ''
        if latest_ctrax_version > self.newest_ctrax_notified:
            alert_str += "Version %s of Ctrax is now available.\n\n"%latest_ctrax_version
            self.newer_ctrax_avail = latest_ctrax_version
        if latest_matlab_version > self.newest_matlab_notified:
            alert_str += "Version %s of the Ctrax toolboxes for Matlab is now available.\n\n"%latest_matlab_version
            self.newer_matlab_avail = latest_matlab_version

        # configure this alert to be shown on main thread, later
        if alert_str != '':
            alert_str += "Download from https://sourceforge.net/projects/ctrax/files/"
            self.update_alert_string = alert_str


    ###################################################################
    # WriteUserfile()
    ###################################################################
    def WriteUserfile( self ):
        """Write current user settings to file. Called on quit."""
        try:
            userfile = open( self.userfile_name, "w" )
        except IOError: pass
        else:
            # line 1: last app version used
            print >> userfile, __version__
            # line 2: working directory
            print >> userfile, self.dir
            # line 3: window position and size
            print >> userfile, \
                  self.frame.GetPosition(), \
                  self.frame.GetSize()
            # line 4: bg window position and size
            if self.last_bg_pos is not None:
                print >> userfile, \
                      self.last_bg_pos, self.last_bg_size
            else: print >> userfile, ""
            # line 5: batch window position and size
            if self.last_batch_pos is not None:
                print >> userfile, \
                      self.last_batch_pos, self.last_batch_size
            else: print >> userfile, ""
            # line 6: use colorblind palette?
            print >> userfile, False
            # line 7: ellipse thickness
            print >> userfile, self.ellipse_thickness
            # line 8: tail length
            print >> userfile, params.tail_length
            # line 9: dim playback
            print >> userfile, self.menu.IsChecked( xrc.XRCID("menu_playback_dim") )
            # line 10: save directory
            print >> userfile, self.save_dir
            # line 11: zoom window position and size
            if self.last_zoom_pos is not None:
                print >> userfile, \
                      self.last_zoom_pos, self.last_zoom_size
            else: print >> userfile, ""
            # line 12: extension of last movie opened
            print >> userfile, self.last_movie_ext
            # line 13: latest Ctrax version found for download
            print >> userfile, self.newest_ctrax_notified
            # line 14: latest Matlab version found for download
            print >> userfile, self.newest_matlab_notified
            # line 15: does user want version updates?
            print >> userfile, self.menu.IsChecked( xrc.XRCID("menu_help_updates") )
            # line 16: does user want to be prompted for .ann filenames?
            print >> userfile, self.menu.IsChecked( xrc.XRCID("menu_settings_annprompt") )
            
            userfile.close()


    ###################################################################
    # OnFrameNumberValidated()
    ###################################################################
    def OnFrameNumberValidated( self,evt ):
        if self.has( 'movie' ):
            new_frame = int(self.framenumber_text.GetValue())
            if new_frame < 0:
                new_frame = 0
            elif new_frame >= self.movie.get_n_frames():
                new_frame = self.movie.get_n_frames() - 1
            
            self.start_frame = new_frame
            self.ShowCurrentFrame()
            
        else:
            self.framenumber_text.SetValue( '0' )


    ###################################################################
    # OnTrackingWizard()
    ###################################################################
    def OnTrackingWizard( self, evt ):
        """Open tracking-wizard window."""
        if self.has( 'wizard' ):
            self.wizard.frame.Raise()
            return

        self.wizard = TrackingWizard( self.frame,
                                      self.bg_imgs,
                                      self.movie.get_n_frames(),
                                      self.movie.get_frame,
                                      self.OnComputeBg,
                                      self.OnStartTracking )
        self.wizard.frame.Bind( wx.EVT_CLOSE, self.OnQuitTrackingWizard )
        self.wizard.frame.Show()


    ###################################################################
    # update_wizard_imgs
    ###################################################################
    def update_wizard_imgs( self ):
        if self.has( 'wizard' ):
            self.wizard.redraw()
        

    ###################################################################
    # OnQuitTrackingWizard()
    ###################################################################
    def OnQuitTrackingWizard( self, evt ):
        self.wizard.frame.Destroy()
        delattr( self, 'wizard' )


    ###################################################################
    # OnSettingsBG()
    ###################################################################
    def OnSettingsBG( self, evt ):
        """Open window for bg threshold settings."""
        # don't create a duplicate window
        if self.bg_window_open:
            self.bg_imgs.frame.Raise()
            return

        # grab previously used threshold, if any, so 'reset' button will work
        if self.has( 'ann_file' ):
            old_thresh = params.n_bg_std_thresh
        else: old_thresh = None

        # show warning if background image calculation is necessary
        isbgmodel = self.CheckForBGModel()
        if isbgmodel == False:
            return

        # set up bg window
        self.bg_imgs.ShowBG( self.frame, self.start_frame, old_thresh,
                             self.update_wizard_imgs )
        self.bg_imgs.frame.Bind( wx.EVT_SIZE, self.OnResizeBG )
        self.bg_imgs.frame.Bind( wx.EVT_MOVE, self.OnResizeBG )
        self.bg_imgs.frame.Bind( wx.EVT_MENU, self.OnQuitBG, id=xrc.XRCID("menu_window_close") )
        self.bg_imgs.frame.Bind( wx.EVT_CLOSE, self.OnQuitBG )

        # set size from memory
        if self.last_bg_pos is not None:
            bg_pos = self.constrain_window_to_screen( self.last_bg_pos, self.last_bg_size )
            self.bg_imgs.frame.SetPosition( bg_pos )
            self.bg_imgs.frame.SetSize( self.last_bg_size )

        # update bg window items with new size
        #self.bg_imgs.OnThreshSlider( None )
        #self.bg_imgs.OnFrameSlider( None )

        # finally, show bg window
        self.bg_imgs.frame.Show()
        self.bg_window_open = True

        # resize slider and image
        self.bg_imgs.DoSub()
        self.bg_imgs.frame_slider.SetMinSize( wx.Size(
            self.bg_imgs.img_panel.GetRect().GetWidth(),
            self.bg_imgs.frame_slider.GetRect().GetHeight() ) )


    ###################################################################
    # OnQuitBG()
    ###################################################################
    def OnQuitBG( self, evt ):
        """Take data from bg threshold window and close it."""
        self.bg_imgs.hf.frame.Destroy()
        self.bg_imgs.frame.Destroy()
        delattr( self.bg_imgs, 'frame' )
        self.bg_window_open = False


    ###################################################################
    # OnSettingsBGModel()
    ###################################################################
    def OnSettingsBGModel( self, evt ):
        """Open window for bg model settings."""

        if params.movie.type == 'sbfmf':
            if not DEBUG:
                resp = wx.MessageBox( "Background Model is already set for SBFMF files, and cannot be changed",
                                      "Cannot Change Background Model", wx.OK )
            return

        # set up bg window
        if not hasattr( self.bg_imgs, 'modeldlg' ):
            self.bg_imgs.modeldlg = BgSettingsDialog( self.frame, self.bg_imgs )
            self.bg_imgs.modeldlg.frame.Bind( wx.EVT_CLOSE, self.OnQuitBGModel )
            self.bg_imgs.modeldlg.frame.Bind( wx.EVT_BUTTON, self.OnQuitBGModel, id=xrc.XRCID("done_button") )
        else:
            self.bg_imgs.modeldlg.frame.Raise()


    ###################################################################
    # OnQuitBgModel()
    ###################################################################
    def OnQuitBGModel(self, evt):
        if hasattr( self.bg_imgs, 'modeldlg' ):
            self.bg_imgs.modeldlg.frame.Destroy()
            delattr( self.bg_imgs, 'modeldlg' )


    ###################################################################
    # OnSettingsTracking()
    ###################################################################
    def OnSettingsTracking( self, evt ):
        """Open window for bg model settings."""

        # don't create a duplicate window
        if hasattr(self,'tracking_settings_window_open') and self.tracking_settings_window_open:
            self.tracking_settings.frame.Raise()
            return

        isbgmodel = self.CheckForBGModel()

        if isbgmodel == False:
            return

        # create window
        self.tracking_settings = tracking_settings.TrackingSettings(self.frame,self.bg_imgs,self.start_frame)
        self.tracking_settings.frame.Bind(wx.EVT_CLOSE,self.OnQuitTrackingSettings)
        self.tracking_settings.frame.Bind(wx.EVT_BUTTON,self.OnQuitTrackingSettings, id=xrc.XRCID("done") )

        # finally, show bg window
        self.tracking_settings.frame.Show()
        self.tracking_settings_window_open = True


    ###################################################################
    # OnQuitTrackingSettings()
    ###################################################################
    def OnQuitTrackingSettings(self, evt):
        self.tracking_settings.frame.Destroy()
        delattr( self, 'tracking_settings' )
        self.tracking_settings_window_open = False


    ###################################################################
    # OnChooseOrientations()
    ###################################################################
    def OnChooseOrientations( self, evt=None ):
        """Open window for choosing orientations."""

        # don't create a duplicate window
        if hasattr(self,'choose_orientations_window_open') and self.choose_orientations_window_open:
            self.choose_orientations.frame.Raise()
            return

        # create window
        self.choose_orientations = chooseorientations.ChooseOrientations(self.frame)
        self.choose_orientations.frame.Bind(wx.EVT_CLOSE,self.OnQuitChooseOrientations)
        self.choose_orientations.frame.Bind(wx.EVT_BUTTON,self.OnQuitChooseOrientations, id=xrc.XRCID("ID_CANCEL") )
        self.choose_orientations.frame.Bind(wx.EVT_BUTTON,self.ChooseOrientations, id=xrc.XRCID("ID_OK") )

        # finally, show bg window
        self.choose_orientations.frame.Show()
        self.choose_orientations_window_open = True


    ###################################################################
    # OnQuitChooseOrientations()
    ###################################################################
    def OnQuitChooseOrientations(self, evt):
        self.choose_orientations.frame.Destroy()
        delattr( self, 'choose_orientations' )
        self.choose_orientations_window_open = False


    ###################################################################
    # ChooseOrientations()
    ###################################################################
    def ChooseOrientations(self, evt):
        self.ann_file = self.choose_orientations.ChooseOrientations(self.ann_file)
        self.OnQuitChooseOrientations(evt)


    ###################################################################
    # OnResizeBG()
    ###################################################################
    def OnResizeBG( self, evt ):
        """BG window was moved or resized. Rescale image and slider,
        and remember new location."""
        evt.Skip()

        if hasattr( self, 'img_size' ) and hasattr( self.bg_imgs, 'img_panel' ):
            sizer = self.bg_imgs.frame.GetSizer()
            panel_item = sizer.GetItem( self.bg_imgs.img_panel, recursive=True )
            panel_item.SetFlag( panel_item.GetFlag() | wx.SHAPED )
            panel_item.SetRatio( float( self.img_size[1] )/self.img_size[0] )
        
        self.bg_imgs.frame.Layout()

        self.bg_imgs.redraw()
        self.bg_imgs.frame_slider.SetMinSize( wx.Size(
            self.bg_imgs.img_panel.GetRect().GetWidth(),
            self.bg_imgs.frame_slider.GetRect().GetHeight() ) )
        self.last_bg_size = self.bg_imgs.frame.GetSize()
        self.last_bg_pos = self.bg_imgs.frame.GetPosition()


    ###################################################################
    # OnCheckZoom()
    ###################################################################
    def OnCheckZoom( self, evt ):
        """Open ellipse zoom window."""
        if self.menu.IsChecked( xrc.XRCID("menu_settings_zoom") ):
            # open zoom window
            self.zoom_window = EllipseFrame( self.frame )
            self.zoom_window.frame.Bind( wx.EVT_CLOSE, self.OnCloseZoom )
            self.zoom_window.frame.Bind( wx.EVT_SIZE, self.OnZoomResize )
            self.zoom_window.frame.Bind( wx.EVT_MOVE, self.OnZoomMove )

            # set window position from memory
            if self.last_zoom_pos is not None:
                set_size = self.last_zoom_size
                zoom_pos = self.constrain_window_to_screen( self.last_zoom_pos, self.last_zoom_size )
                self.zoom_window.frame.SetPosition( zoom_pos )
                self.zoom_window.frame.SetSize( set_size )

            if evt is not None: self.ShowCurrentFrame()
        else:
            self.OnCloseZoom( None )
            

    ###################################################################
    # OnCloseZoom()
    ###################################################################
    def OnCloseZoom( self, evt ):
        """Close ellipse zoom window."""
        self.menu.Check( xrc.XRCID("menu_settings_zoom"), False )
        self.zoom_window.frame.Destroy()


    ###################################################################
    # remember_zoom_window_size()
    ###################################################################
    def remember_zoom_window_size( self ):
        """Remember current size of zoom window."""
        try:
            self.last_zoom_size = self.zoom_window.frame.GetSize()
            self.last_zoom_pos = self.zoom_window.frame.GetPosition()
        except AttributeError:
            pass # during initialization


    ###################################################################
    # OnZoomResize()
    ###################################################################
    def OnZoomResize( self, evt ):
        """Zoom window was resized; remember position and redraw."""
        evt.Skip()
        self.zoom_window.Redraw()
        self.remember_zoom_window_size()


    ###################################################################
    # OnZoomMove()
    ###################################################################
    def OnZoomMove( self, evt ):
        """Zoom window moved; remember position."""
        evt.Skip()
        self.remember_zoom_window_size()


    ###################################################################
    # ZoomToggle()
    ###################################################################
    def ZoomToggle(self,evt):
        self.zoommode = not self.zoommode
        

    ###################################################################
    # OnMouseDown()
    ###################################################################
    def OnMouseDown(self,evt):
        """Mouse clicked in movie window. Zoom in on selected fly."""
        self.zoom_dragging = False
        if not self.zoommode: return

        # get the clicked position
        windowheight = self.img_wind_child.GetRect().GetHeight()
        windowwidth = self.img_wind_child.GetRect().GetWidth()
        if self.has( 'zoom_drag_roi' ):
            # correct for zoom state
            x = float( evt.GetX() )/windowwidth
            x = x/self.zoom_drag_roi_scale + self.zoom_drag_roi[0]
            x *= self.img_size[1]
            y = 1. - float( evt.GetY() )/windowheight
            y = y/self.zoom_drag_roi_scale + self.zoom_drag_roi[1]
            y *= self.img_size[0]
        else:
            x = evt.GetX()*self.img_size[1]/windowwidth
            y = self.img_size[0] - evt.GetY()*self.img_size[0]/windowheight
        if x > self.img_size[1] or y > self.img_size[0]:
            return

        fly_clicked = False
        min_dist = num.inf
        if self.ann_file.IsAnnData and \
               self.start_frame <= self.ann_file.lastframetracked and \
               self.start_frame >= self.ann_file.firstframetracked:
            # determine closest target
            ells = self.ann_file.get_frame(self.start_frame)
            for i,ellipse in ells.iteritems():
                this_dist = (ellipse.center.x - x)**2 + (ellipse.center.y - y)**2
                if this_dist < min_dist:
                    min_ind = i
                    min_dist = this_dist

        maxdshowinfo = (num.maximum(params.movie_size[0],params.movie_size[1])/params.MAXDSHOWINFO)**2
        if min_dist <= maxdshowinfo:
            # go ahead and show this fly
            fly_clicked = True
        
            if not self.menu.IsChecked( xrc.XRCID("menu_settings_zoom") ):
                # open zoom window if not open
                self.menu.Check(xrc.XRCID("menu_settings_zoom"),True)
                self.OnCheckZoom( None )
                self.zoom_window.ellipse_windows[0].spinner.SetValue(ells[min_ind].identity)
            else:
                # check to see if the target is already drawn in some window
                nwindows = self.zoom_window.n_ell
                for i in range(nwindows):
                    if ells[min_ind].identity == self.zoom_window.ellipse_windows[i].spinner.GetValue():
                        # if it is, then do nothing
                        return

                # can we open another window?
                maxnwindows = self.zoom_window.n_ell_spinner.GetMax()
                if nwindows < maxnwindows:
                    # then open and draw in a new window
                    self.zoom_window.AddEllipseWindow(ells[min_ind].identity)
                else:
                    # if we can't, need to choose a window to replace
                    if hasattr(self,'firstzoomwindowcreated'):
                        window = self.firstzoomwindowcreated
                        self.firstzoomwindowcreated = (self.firstzoomwindowcreated+1)%maxnwindows
                    else:
                        window = 0
                        self.firstzoomwindowcreated = 1
                    # set the identity for the chosen window
                    self.zoom_window.ellipse_windows[window].spinner.SetValue(ells[min_ind].identity)

        if not fly_clicked:
            # allow drag-to-zoom
            self.zoom_dragging = True
            self.zoom_drag_origin = (float( evt.GetX() )/windowwidth,
                                     1. - float( evt.GetY() )/windowheight)
            if self.has( 'zoom_drag_roi' ):
                self.zoom_drag_origin = (self.zoom_drag_origin[0]/self.zoom_drag_roi_scale + self.zoom_drag_roi[0],
                                         self.zoom_drag_origin[1]/self.zoom_drag_roi_scale + self.zoom_drag_roi[1])
            self.zoom_drag_current = self.zoom_drag_origin

        self.ShowCurrentFrame()
        evt.Skip()


    ###################################################################
    # OnMouseMoved()
    ###################################################################
    def OnMouseMoved( self, evt ):
        """Mouse motion occurred. Do nothing unless drag mode is active."""
        if self.zoom_dragging:
            if not evt.LeftIsDown():
                # in drag mode, but left mouse button is not down anymore...
                self.OnMouseUp( evt )
                return

            # set to draw bounding box
            self.zoom_drag_current = (float( evt.GetX() - self.img_wind.GetPosition()[0] )/self.img_wind.GetSize()[0],
                                      1. - float( evt.GetY() - self.img_wind.GetPosition()[1] )/self.img_wind.GetSize()[1])
            if self.has( 'zoom_drag_roi' ):
                self.zoom_drag_current = (self.zoom_drag_current[0]/self.zoom_drag_roi_scale + self.zoom_drag_roi[0],
                                          self.zoom_drag_current[1]/self.zoom_drag_roi_scale + self.zoom_drag_roi[1])
            self.ShowCurrentFrame()

        evt.Skip()


    ###################################################################
    # OnMouseUp()
    ###################################################################
    def OnMouseUp( self, evt ):
        """Mouse button released. If dragging, zoom in on ROI."""
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
            self.ShowCurrentFrame()


    ###################################################################
    # OnMouseDoubleClick()
    ###################################################################
    def OnMouseDoubleClick( self, evt ):
        """Mouse was double-clicked. Reset ROI, if present."""
        if evt is not None: evt.Skip()

        if hasattr( self, 'zoom_drag_roi' ):
            delattr( self, 'zoom_drag_roi' )
        self.zoom_drag_roi_scale = 1.
        if evt is not None: self.ShowCurrentFrame()
        

    ###################################################################
    # OnMakePlot()
    ###################################################################
    def OnMakePlot( self, evt ):
        """Make a data plot."""
        window = wx.Frame( self.frame )
        window.SetSize( (400,300) )

        hsizer = wx.BoxSizer( wx.HORIZONTAL )
        vsizer = wx.BoxSizer( wx.VERTICAL )
        vsizer.Add( hsizer, 1, wx.EXPAND )
        window.SetSizer( vsizer )

        wx.BeginBusyCursor()
        wx.Yield()

        if evt.GetId() == xrc.XRCID( "menu_analyze_plottraj" ):
            # plot a max of 500 frames of trajectories
            data = self.ann_file.get_frames( self.ann_file.firstframetracked,
                                             min( self.ann_file.lastframetracked,
                                                  self.ann_file.firstframetracked + 499 ) )
        else:
            # plot a max of 5000 frames of everything else
            data = self.ann_file.get_frames( self.ann_file.firstframetracked,
                                             min( self.ann_file.lastframetracked,
                                                  self.ann_file.firstframetracked + 4999 ) )
            
        if evt.GetId() == xrc.XRCID( "menu_analyze_plottraj" ):
            window.SetTitle( "Trajectories" )
            panel = draw.TrajectoryPlotPanel( window, data )
        elif evt.GetId() == xrc.XRCID( "menu_analyze_plotvel" ):
            window.SetTitle( "Velocities" )
            panel = draw.VelocityPlotPanel( window, data )
        elif evt.GetId() == xrc.XRCID( "menu_analyze_histpos" ):
            window.SetTitle( "Positions" )
            panel = draw.PosHistPanel( window, data, self.movie.get_width(), self.movie.get_height() )
        elif evt.GetId() == xrc.XRCID( "menu_analyze_histspeed" ):
            window.SetTitle( "Speeds" )
            panel = draw.VelPlotPanel( window, data )
        elif evt.GetId() == xrc.XRCID( "menu_analyze_histdtheta" ):
            window.SetTitle( "Turn rates" )
            panel = draw.TurnPlotPanel( window, data )
        else:
            panel = None

        if panel is not None:
            hsizer.Add( panel, 1, wx.EXPAND )
        
            window.Show()

        wx.EndBusyCursor()
    

    #def OnCheckColorblind( self, evt ):
    #    """Colorblind-friendly palette was checked or unchecked."""
    #    if self.menu.IsChecked( xrc.XRCID("menu_settings_use_colorblind") ):
    #        params.use_colorblind_palette = True
    #        params.colors = params.colorblind_palette
    #    else:
    #        params.use_colorblind_palette = False
    #        params.colors = params.normal_palette
    #    # rewrite color lists in annotation data already read
    #    if self.ann_data is not None:
    #        for frame in self.ann_data:
    #            if params.use_colorblind_palette:
    #                frame.colors = params.colorblind_palette
    #            else:
    #                frame.colors = params.normal_palette
    #    self.ShowCurrentFrame()


    def OnCheckShowAnn( self, evt ):
        """"Show annotation" box checked. Repaint current frame."""
        self.ShowCurrentFrame()
	self.menu.Enable( xrc.XRCID("menu_playback_tails"),
                          self.menu.IsChecked( xrc.XRCID("menu_playback_show_ann") ) )


    def OnCheckRefresh( self, evt ):
        if self.menu.IsChecked( xrc.XRCID("menu_do_refresh") ):
            self.do_refresh = True
        else:
            self.do_refresh = False

        if self.tracking:
            self.set_rate_text( use_refresh=True )


    def OnCheckDim( self, evt ):
        self.ShowCurrentFrame()
        

    def OnTailLength( self, evt ):
        try:
            dlg = wx.NumberEntryDialog( self.frame,
                                        "Enter new tail length",
                                        "(0-200 frames)",
                                        "Tail Length",
                                        value=params.tail_length,
                                        min=0,
                                        max=200 )
            if dlg.ShowModal() == wx.ID_OK:
                params.tail_length = dlg.GetValue()
            dlg.Destroy()
        except AttributeError: # NumberEntryDialog not present yet in 2.6.3.2
            print "using getnumber fallback"
            import warnings
            warnings.filterwarnings( 'ignore', '', DeprecationWarning )
            # but for some reason, GetNumberFromUser is already deprecated
            new_num = wx.GetNumberFromUser( "Enter new tail length",
                                            "(0-200 frames)",
                                            "Tail Length",
                                            params.tail_length,
                                            min=0,
                                            max=200,
                                            parent=self.frame )
            warnings.resetwarnings()
            if new_num >= 0:
                params.tail_length = new_num
        self.ShowCurrentFrame()


    ###################################################################
    # IsBGModel()
    ###################################################################
    def IsBGModel(self):
        return hasattr(self.bg_imgs,'center')


    ###################################################################
    # CheckForBGModel()
    ###################################################################
    def CheckForBGModel(self):
        # already have the background?
        if hasattr(self.bg_imgs,'center'):
            return True

        elif params.feedback_enabled:
            # ask what to do
            if self.bg_imgs.use_median:
                algtxt = 'Median'
            else:
                algtxt = 'Mean'
            if not DEBUG:
                msgtxt = 'Background model has not been computed for this movie.\nAutomatically estimate using the following parameters?\n(For better results, use Settings->Background tools instead.)\n\nAlgorithm: %s\nNumber of Frames: %d' %(algtxt,self.bg_imgs.n_bg_frames)
                if wx.MessageBox( msgtxt, "Auto-calculate?", wx.YES_NO ) == wx.NO:
                    # Don't do the computation
                    return False

        return self.OnComputeBg()
    

    ###################################################################
    # CheckForShapeModel()
    ###################################################################
    def CheckForShapeModel(self):
        havevalue = (not params.maxshape.area == 9999.)
        
        haveshape = (not num.isinf( params.maxshape.area ))

        # have read in the shape model
        if haveshape and havevalue:
            return True

        # ask what to do
        if params.interactive and not DEBUG:
            if haveshape:
                msgtxt = 'Shape model has not been automatically computed for this movie. Currently:\n\nMin Area = %.2f\nMax Area = %.2f\n\nDo you want to automatically compute now with the following parameters?\n\nNumber of Frames: %d\nNumber of Standard Deviations: %.2f'%(params.minshape.area,params.maxshape.area,params.n_frames_size,params.n_std_thresh)
            else:
                msgtxt = 'Shape is currently unbounded. Do you want to automatically compute now with the following parameters?\n\nNumber of Frames: %d\nNumber of Standard Deviations: %.2f'%(params.n_frames_size,params.n_std_thresh)
            resp = wx.MessageBox( msgtxt, "Auto-calculate?", wx.YES_NO|wx.CANCEL )
            if resp == wx.NO:
                return True
            elif resp == wx.CANCEL:
                return False

        return self.OnComputeShape()


    def OnDebugPrintIntervals(self,evt):
        print "DEBUG INTERVALS: framestracked = [%d,%d], framesbuffered = [%d,%d], frameswritten = [%d,%d]"%(self.ann_file.firstframetracked,self.ann_file.lastframetracked,self.ann_file.firstframebuffered,self.ann_file.lastframebuffered,self.ann_file.firstframewritten,self.ann_file.lastframewritten)
        sys.stdout.flush()

    def OnDebugPrintBufferElement(self,evt):
        q = wx.TextEntryDialog(self.frame,"Buffer has %d elements, corresponding to frames %d through %d"%(len(self.ann_file.buffer),self.ann_file.firstframebuffered,self.ann_file.lastframebuffered),"Choose buffer element","0")
        q.ShowModal()
        v = q.GetValue()
        try:
            i = int(v)
            if i < 0 or i >= len(self.ann_file.buffer):
                raise NotImplementedError

        except:
            print "DEBUG BUFFER: Must enter integer between 0 and %d"%(len(self.ann_file.buffer)-1)
        else:
            print "DEBUG BUFFER: buffer[%d] (frame %d) = "%(i,i+self.ann_file.firstframebuffered) + str(self.ann_file.buffer[i])
        sys.stdout.flush()

    def OnDebugPrintFrame(self,evt):
        q = wx.TextEntryDialog(self.frame,"Frames tracked: %d through %d ([%d,%d] in buffer)"%(self.ann_file.firstframetracked,self.ann_file.lastframetracked,self.ann_file.firstframebuffered,self.ann_file.lastframebuffered),"Choose frame to print","0")
        q.ShowModal()
        v = q.GetValue()
        try:
            i = int(v)
            if i < self.ann_file.firstframetracked or \
                    i > self.ann_file.lastframetracked:
                raise NotImplementedError
        except:
            print "DEBUG FRAME: Must enter integer between %d and %d"%(self.ann_file.firstframetracked,self.ann_file.lastframetracked)
        else:
            print "DEBUG FRAME: Frame %d = "%i + str(self.ann_file.get_frame(i))
        sys.stdout.flush()



def str222tuples( string ):
    """Converts string into two 2-tuples."""
    vals = string.split()
    for vv in range( len(vals) ):
        vals[vv] = int( vals[vv].strip( '(), ' ) )
    return (vals[0],vals[1]), (vals[2],vals[3])

def str22tuple( string ):
    """Converts string into a 2-tuple."""
    vals = string.split()
    for vv in range( len(vals) ):
        vals[vv] = int( vals[vv].strip( '(), ' ) )
    return (vals[0],vals[1])

