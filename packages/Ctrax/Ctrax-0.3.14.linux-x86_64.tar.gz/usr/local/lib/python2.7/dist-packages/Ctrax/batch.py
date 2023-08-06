# batch.py
# KMB 11/06/2208

import codedir
import os
import sys
import wx
from wx import xrc
from wx.lib.mixins.listctrl import TextEditMixin

from numpy import inf

import movies
from params import params

RSRC_FILE = os.path.join(codedir.codedir,'xrc','batch.xrc')

AUTODETECT_ARENA = 0
LOAD_SETTINGS_ARENA = 1
USE_EXISTING_ARENA = 2
DONT_USE_ARENA = 3

AUTODETECT_SHAPE = 0
LOAD_SETTINGS_SHAPE = 1
USE_EXISTING_SHAPE = 2

AUTODETECT_BG = 0
LOAD_SETTINGS_BG = 1
USE_EXISTING_BG = 2

class EditableListCtrl (wx.ListCtrl, TextEditMixin):
    """Subclass wx.ListCtrl in order to use their TextEditMixin features."""
    def __init__( self, *args, **kwargs ):
        wx.ListCtrl.__init__( self, *args, **kwargs )
        TextEditMixin.__init__( self )

    def OpenEditor( self, col, row ):
        """Selectively override the TextEditMixin's OpenEditor function."""
        self._SelectIndex( row )
        if col != 0: # col 0 not editable
            TextEditMixin.OpenEditor( self, col, row )

    def OnLeftDown( self, evt ):
        TextEditMixin.OnLeftDown( self, evt )
        # ^-- that calls evt.Skip() to select the right row, but here Skip()
        # goes to the containing panel, so we must select the row manually
        row, flags = self.HitTest( evt.GetPosition() )
        if row != self.curRow:
            self._SelectIndex( row )

    def Set( self, file_list ):
        """Reset displayed contents based on a BatchWindow.file_list dict."""
        self.DeleteAllItems()
        for m, movie_data in enumerate( file_list ):
            self.InsertStringItem( m, movie_data['filename'] )
            self.SetStringItem( m, 1, str( movie_data['startframe'] ) )
            self.SetStringItem( m, 2, str( movie_data['endframe'] ) )


class BatchWindow:
    def __init__( self, parent, directory, default_extension, init_movie=None ):
        self.file_list = []
        if init_movie is not None:
            self.file_list.append( {"filename": init_movie.fullpath,
                                    "nframes": init_movie.get_n_frames(),
                                    "startframe": 0,
                                    "endframe": inf} )
        self.dir = directory
        self.default_extension = default_extension
        self.executing = False

        self.ShowWindow( parent )


    def panelleftdown( self, evt ):
        """In Windows, pass mouse events in the list-box panel to the box."""
        self.list_box.OnLeftDown( evt )
        

    def ShowWindow( self, parent ):
        rsrc = xrc.XmlResource( RSRC_FILE )
        self.frame = rsrc.LoadFrame( parent, "frame_Ctrax_batch" )

        # event bindings
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonAdd, id=xrc.XRCID("button_add") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonRemove, id=xrc.XRCID("button_remove") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonClose, id=xrc.XRCID("button_close") )
        self.frame.Bind( wx.EVT_CLOSE, self.OnButtonClose )

        # button handles
        self.add_button = xrc.XRCCTRL( self.frame, "button_add" )
        self.remove_button = xrc.XRCCTRL( self.frame, "button_remove" )
        self.execute_button = xrc.XRCCTRL( self.frame, "button_execute" )
        
        # list box
        hsizer = wx.BoxSizer( wx.HORIZONTAL )
        vsizer = wx.BoxSizer( wx.VERTICAL )
        self.list_box = EditableListCtrl( parent=self.frame,
                                          style=(wx.LC_NO_SORT_HEADER | wx.LC_HRULES | wx.LC_SINGLE_SEL | wx.LC_REPORT) )
        vsizer.Add( self.list_box, 1, wx.EXPAND )
        hsizer.Add( vsizer, 1, wx.EXPAND )
        panel = xrc.XRCCTRL( self.frame, "text_list_panel" )
        panel.SetSizer( hsizer )
        panel.SetAutoLayout( True )
        panel.Layout()
        if sys.platform.startswith( 'win' ):
            # in Windows, panel eats its children's mouse events
            panel.Bind( wx.EVT_LEFT_DOWN, self.panelleftdown )
        self.list_box.Bind( wx.EVT_LIST_END_LABEL_EDIT, self.label_edited )

        self.list_box.InsertColumn( 0, "File", width=panel.GetSize()[0] - 150 )
        self.list_box.InsertColumn( 1, "First frame", width=75 )
        self.list_box.InsertColumn( 2, "Last frame", width=75 )
        self.list_box.Set( self.file_list )

        # autodetection options
        self.arena_choice = xrc.XRCCTRL(self.frame,"arena_choice")
        self.shape_choice = xrc.XRCCTRL(self.frame,"shape_choice")
        self.bg_model_choice = xrc.XRCCTRL(self.frame,"bg_model_choice")
        self.choice_boxes = [self.arena_choice, self.shape_choice, self.bg_model_choice]
        self.frame.Bind(wx.EVT_CHOICE,self.OnArenaChoice,self.arena_choice)
        self.frame.Bind(wx.EVT_CHOICE,self.OnShapeChoice,self.shape_choice)
        self.frame.Bind(wx.EVT_CHOICE,self.OnBgModelChoice,self.bg_model_choice)
        if params.batch_autodetect_arena == True:
            self.arena_choice.SetSelection( AUTODETECT_ARENA )
        elif params.batch_autodetect_arena == False:
            self.arena_choice.SetSelection( USE_EXISTING_ARENA )
        else:
            self.arena_choice.SetSelection( DONT_USE_ARENA )
        self.last_arena_selection = self.arena_choice.GetSelection()
        if params.batch_autodetect_shape:
            self.shape_choice.SetSelection( AUTODETECT_SHAPE )
        else:
            self.shape_choice.SetSelection( USE_EXISTING_SHAPE )
        self.last_shape_selection = self.shape_choice.GetSelection()
        if params.batch_autodetect_bg_model:
            self.bg_model_choice.SetSelection( AUTODETECT_BG )
        else:
            self.bg_model_choice.SetSelection( USE_EXISTING_BG )
        self.last_bg_model_selection = self.bg_model_choice.GetSelection()

        self.sbfmf_checkbox = xrc.XRCCTRL( self.frame, "save_sbfmf" )
        
        self.settings_checkbox = xrc.XRCCTRL( self.frame, "use_settings" )
        self.frame.Bind( wx.EVT_CHECKBOX, self.OnCheckSettings, self.settings_checkbox )
        
        self.frame.Show()
        self.is_showing = True

        self.EnableControls()


    def EnableControls( self ):
        """Enable or disable controls."""

        if not self.is_showing: return

        self.add_button.Enable( not self.executing )
        self.remove_button.Enable( not self.executing )
        self.execute_button.Enable( not self.executing )
        self.sbfmf_checkbox.Enable( not self.executing )
        self.settings_checkbox.Enable( not self.executing )
        for choice in self.choice_boxes:
            choice.Enable( not self.executing )
            

    def OnArenaChoice(self,evt):
        v = self.arena_choice.GetSelection()

        if self.should_load_settings() and v == USE_EXISTING_ARENA:
            self.arena_choice.SetSelection( self.last_arena_selection )
            return

        self.last_arena_selection = v

        if v == LOAD_SETTINGS_ARENA:
            self.disable_choice_existing()
        elif not self.should_load_settings():
            self.enable_choice_existing()

        if v == AUTODETECT_ARENA:
            params.batch_autodetect_arena = True
        elif v == DONT_USE_ARENA:
            params.batch_autodetect_arena = None
        else:
            params.batch_autodetect_arena = False

    def OnShapeChoice(self,evt):
        v = self.shape_choice.GetSelection()

        if self.should_load_settings() and v == USE_EXISTING_SHAPE:
            self.shape_choice.SetSelection( self.last_shape_selection )
            return

        self.last_shape_selection = v

        if v == LOAD_SETTINGS_SHAPE:
            self.disable_choice_existing()
        elif not self.should_load_settings():
            self.enable_choice_existing()
            
        params.batch_autodetect_shape = (v == AUTODETECT_SHAPE)
        
    def OnBgModelChoice(self,evt):
        v = self.bg_model_choice.GetSelection()

        if self.should_load_settings() and v == USE_EXISTING_BG:
            self.bg_model_choice.SetSelection( self.last_bg_model_selection )
            return

        self.last_bg_model_selection = v

        if v == LOAD_SETTINGS_BG:
            self.disable_choice_existing()
        elif not self.should_load_settings():
            self.enable_choice_existing()
            
        params.batch_autodetect_bg_model = (v == AUTODETECT_BG)


    def disable_choice_existing( self ):
        self.settings_checkbox.SetValue( True )
        
        for choice in self.choice_boxes:
            if choice == self.arena_choice:
                i = USE_EXISTING_ARENA
                fallback = self.last_arena_selection
                if fallback == i:
                    self.last_arena_selection = AUTODETECT_ARENA
                    fallback = AUTODETECT_ARENA
            elif choice == self.shape_choice:
                i = USE_EXISTING_SHAPE
                fallback = self.last_shape_selection
                if fallback == i:
                    self.last_shape_selection = AUTODETECT_SHAPE
                    fallback = AUTODETECT_SHAPE
            elif choice == self.bg_model_choice:
                i = USE_EXISTING_BG
                fallback = self.last_bg_model_selection
                if fallback == i:
                    self.last_bg_model_selection = AUTODETECT_BG
                    fallback = AUTODETECT_BG
                
            s = choice.GetString( i )
            if s[0] != "[" and s[-1] != "]":
                s = "[" + s + "]"
                choice.Delete( i )
                choice.Insert( s, i )
                choice.SetSelection( fallback )

    def enable_choice_existing( self ):
        for choice in self.choice_boxes:
            if choice == self.arena_choice:
                i = USE_EXISTING_ARENA
            elif choice == self.shape_choice:
                i = USE_EXISTING_SHAPE
            elif choice == self.bg_model_choice:
                i = USE_EXISTING_BG
            fallback = choice.GetSelection()
            
            s = choice.GetString( i )
            if s[0] == "[" and s[-1] == "]":
                s = s[1:-1]
                choice.Delete( i )
                choice.Insert( s, i )
                choice.SetSelection( fallback )
                

    def should_load_settings( self ):
        return (self.arena_choice.GetSelection() == LOAD_SETTINGS_ARENA or \
                self.shape_choice.GetSelection() == LOAD_SETTINGS_SHAPE or \
                self.bg_model_choice.GetSelection() == LOAD_SETTINGS_BG or \
                self.settings_checkbox.IsChecked())

    def should_overwrite_arena( self ):
        return (self.arena_choice.GetSelection() != USE_EXISTING_ARENA and \
                self.arena_choice.GetSelection() != DONT_USE_ARENA)

    def should_overwrite_shape( self ):
        return (self.shape_choice.GetSelection() != USE_EXISTING_SHAPE)

    def should_overwrite_bg_model( self ):
        return (self.bg_model_choice.GetSelection() != USE_EXISTING_BG)
        

    def OnButtonAdd( self, evt ):
        """Add button pressed. Select a movie to add to the batch."""
        try:
            movie = movies.Movie( self.dir,
                                  interactive=True,
                                  parentframe=self.frame,
                                  open_now=True,
                                  default_extension=self.default_extension )
        except ImportError:
            return

        self.dir = movie.dirname
        base, self.default_extension = os.path.splitext( movie.filename )

        # check for duplicates
        add_flag = True
        for filename in self.file_list:
            if filename == movie.fullpath:
                wx.MessageBox( "File has already been added,\nnot duplicating",
                               "Duplicate", wx.ICON_WARNING|wx.OK )
                add_flag = False
                break
                
        if add_flag:
            movie_data = {"filename": movie.fullpath,
                          "nframes": movie.get_n_frames(),
                          "startframe": 0,
                          "endframe": inf}
            self.file_list.append( movie_data )
            self.list_box.Set( self.file_list )


    def OnButtonRemove( self, evt ):
        """Remove button pressed. Remove the currently selected movie from the queue."""
        for ii in reversed( range( len(self.file_list) ) ):
            if self.list_box.IsSelected( ii ):
                # don't remove currently executing job
                if not self.executing or ii != 0:
                    self.file_list.pop( ii )
                    self.list_box.DeleteItem( ii )


    def OnButtonClose( self, evt ):
        """Close button pressed. Close the batch window (batch processing may be ongoing)."""
        self.frame.Destroy()
        self.is_showing = False


    def OnCheckSettings( self, evt ):
        """'Use settings file' checkbox selected. Enable/disable controls."""
        if self.settings_checkbox.IsChecked():
            self.disable_choice_existing()
        elif self.should_load_settings():
            self.settings_checkbox.SetValue( True )
        else:
            self.enable_choice_existing()
            

    def label_edited( self, evt ):
        """Test values to keep them in range; revert or set data."""
        row = evt.GetIndex()
        col = evt.GetColumn()
        
        movie_data = self.file_list[row]
        if col == 1:
            # column 1 is start frame, must be an int
            try:
                new_frame = int( evt.GetLabel() )
            except ValueError:
                pass
            else:
                if new_frame >= movie_data['nframes']:
                    new_frame = movie_data['nframes'] - 1
                elif new_frame < 0:
                    new_frame = 0

                movie_data['startframe'] = new_frame
                if new_frame > movie_data['endframe']:
                    movie_data['endframe'] = new_frame

            self.list_box.Set( self.file_list )
            evt.Veto()
                
        elif col == 2:
            # column 2 is end frame, must be an int or 'inf'
            try:
                new_frame = int( evt.GetLabel() )
            except ValueError:
                if evt.GetLabel() == 'inf':
                    good_val = True
                    new_frame = inf
                else:
                    good_val = False
            else:
                good_val = True
                if new_frame >= movie_data['nframes']:
                    new_frame = inf
                elif new_frame < 0:
                    new_frame = 0

            if good_val:
                movie_data['endframe'] = new_frame
                if new_frame < movie_data['startframe']:
                    movie_data['startframe'] = new_frame

            self.list_box.Set( self.file_list )
            evt.Veto()
