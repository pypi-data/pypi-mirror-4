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
        print "panelleftdown"
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
        if 'win' in sys.platform:
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
            self.arena_choice.SetSelection(0)
        elif params.batch_autodetect_arena == False:
            self.arena_choice.SetSelection(1)
        else:
            self.arena_choice.SetSelection( 2 )
        if params.batch_autodetect_shape:
            self.shape_choice.SetSelection(0)
        else:
            self.bg_model_choice.SetSelection(1)
        if params.batch_autodetect_bg_model:
            self.bg_model_choice.SetSelection(0)
        else:
            self.bg_model_choice.SetSelection(1)

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
        if v == 0:
            params.batch_autodetect_arena = True
        elif v == 1:
            params.batch_autodetect_arena = False
        else:
            params.batch_autodetect_arena = None

    def OnShapeChoice(self,evt):
        v = self.shape_choice.GetSelection()
        params.batch_autodetect_shape = (v == 0)
        
    def OnBgModelChoice(self,evt):
        v = self.bg_model_choice.GetSelection()
        params.batch_autodetect_bg_model = (v == 0)
        

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
                               "Duplicate", wx.ICON_WARNING )
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
        for choice in self.choice_boxes:
            choice.Enable( not self.settings_checkbox.IsChecked() )

        if self.settings_checkbox.IsChecked():
            for choice in self.choice_boxes:
                choice.SetSelection( 1 ) # "use from first movie"
            self.OnArenaChoice( None )
            self.OnShapeChoice( None )
            self.OnBgModelChoice( None )


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
