# Copyright, John Rusnak, 2012
    # This code binding is available under the license agreement of the LGPL with
    # an additional constraint described below,
    # and with the understanding that the webkit API is copyright protected
    # by Apple Computer, Inc. (see below).
    # There is an  additional constraint that any derivatives of this work aimed
    # at providing bindings to GObject, GTK, GDK, or WebKit be strictly
    # python-only bindings with no native code.
    # * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY
    # * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    # * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
    # * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
    # * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    # * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    # * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    #
    # ******************************************************
    # For the API:
    # /*
    # * Copyright (C) 2006 Apple Computer, Inc.  All rights reserved.
    # *
    # * Redistribution and use in source and binary forms, with or without
    # * modification, are permitted provided that the following conditions
    # * are met:
    # * 1. Redistributions of source code must retain the above copyright
    # *    notice, this list of conditions and the following disclaimer.
    # * 2. Redistributions in binary form must reproduce the above copyright
    # *    notice, this list of conditions and the following disclaimer in the
    # *    documentation and/or other materials provided with the distribution.
    # *
    # * THIS SOFTWARE IS PROVIDED BY APPLE COMPUTER, INC. ``AS IS'' AND ANY
    # * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    # * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
    # * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
    # * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    # * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    # * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    # */
from ctypes import *
from gtk3_types import *
from gtk3_enums import *
from gtk3_types import *
from gtk3_enums import *

    
"""Derived Pointer Types"""
_GtkRcStyle = POINTER(c_int)
_PangoContext = POINTER(c_int)
_GParamSpec = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_GdkGeometry = POINTER(c_int)
_GList = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_GParamSpec = POINTER(c_int)
_GList = POINTER(c_int)
_GdkRGBA = POINTER(c_int)
_GtkRequisition = POINTER(c_int)
_GtkRcStyle = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_cairo_font_options_t = POINTER(c_int)
_GdkWindowAttr = POINTER(c_int)
_GdkAtom = POINTER(c_int)
_GtkIconSet = POINTER(c_int)
_cairo_region_t = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_GdkColor = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
_GdkRectangle = POINTER(c_int)
_GdkWMDecoration = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_GdkDeviceManager = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_cairo_t = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
_GtkIconSource = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_GtkAccelGroup = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_cairo_pattern_t = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_GtkStyleContext = POINTER(c_int)
_GtkAllocation = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GtkWidgetClass = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_GValue = POINTER(c_int)
_GtkClipboard = POINTER(c_int)
_GdkAppLaunchContext = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_WebKitGeolocationPolicyDecision = POINTER(c_int)
_GtkSettings = POINTER(c_int)
_GdkDevice = POINTER(c_int)
"""Enumerations"""
GtkWidgetHelpType = c_int
GtkTextDirection = c_int
GtkSizeRequestMode = c_int
GtkAlign = c_int
GdkPixbufError = c_int
GdkColorspace = c_int
GdkPixbufAlphaMode = c_int
GtkIconSize = c_int
GdkWindowType = c_int
GdkWindowWindowClass = c_int
GdkWindowHints = c_int
GdkGravity = c_int
GdkWindowEdgeh = c_int
GdkWindowTypeHint = c_int
GdkWindowAttributesType = c_int
GdkFilterReturn = c_int
GdkModifierType = c_int
GdkWMDecoration = c_int
GdkWMFunction = c_int

libgtk3.gdk_display_flush.restype = None
libgtk3.gdk_display_flush.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_screen.restype = _GdkScreen
libgtk3.gdk_display_get_screen.argtypes = [_GdkDisplay,gint]
libgtk3.gdk_display_get_default_cursor_size.restype = guint
libgtk3.gdk_display_get_default_cursor_size.argtypes = [_GdkDisplay]
libgtk3.gdk_display_is_closed.restype = gboolean
libgtk3.gdk_display_is_closed.argtypes = [_GdkDisplay]
libgtk3.gdk_display_store_clipboard.restype = None
libgtk3.gdk_display_store_clipboard.argtypes = [_GdkDisplay,_GdkWindow,guint32,_GdkAtom,gint]
libgtk3.gdk_display_set_double_click_distance.restype = None
libgtk3.gdk_display_set_double_click_distance.argtypes = [_GdkDisplay,guint]
libgtk3.gdk_display_peek_event.restype = POINTER(GdkEvent)
libgtk3.gdk_display_peek_event.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_n_screens.restype = gint
libgtk3.gdk_display_get_n_screens.argtypes = [_GdkDisplay]
libgtk3.gdk_display_close.restype = None
libgtk3.gdk_display_close.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_maximal_cursor_size.restype = None
libgtk3.gdk_display_get_maximal_cursor_size.argtypes = [_GdkDisplay,POINTER(guint),POINTER(guint)]
libgtk3.gdk_display_set_double_click_time.restype = None
libgtk3.gdk_display_set_double_click_time.argtypes = [_GdkDisplay,guint]
libgtk3.gdk_display_supports_input_shapes.restype = gboolean
libgtk3.gdk_display_supports_input_shapes.argtypes = [_GdkDisplay]
libgtk3.gdk_display_put_event.restype = None
libgtk3.gdk_display_put_event.argtypes = [_GdkDisplay,POINTER(GdkEvent)]
libgtk3.gdk_display_supports_cursor_alpha.restype = gboolean
libgtk3.gdk_display_supports_cursor_alpha.argtypes = [_GdkDisplay]
libgtk3.gdk_display_notify_startup_complete.restype = None
libgtk3.gdk_display_notify_startup_complete.argtypes = [_GdkDisplay,c_char_p]
libgtk3.gdk_display_supports_cursor_color.restype = gboolean
libgtk3.gdk_display_supports_cursor_color.argtypes = [_GdkDisplay]
libgtk3.gdk_display_list_devices.restype = _GList
libgtk3.gdk_display_list_devices.argtypes = [_GdkDisplay]
libgtk3.gdk_display_has_pending.restype = gboolean
libgtk3.gdk_display_has_pending.argtypes = [_GdkDisplay]
libgtk3.gdk_display_beep.restype = None
libgtk3.gdk_display_beep.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_default_group.restype = _GdkWindow
libgtk3.gdk_display_get_default_group.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_event.restype = POINTER(GdkEvent)
libgtk3.gdk_display_get_event.argtypes = [_GdkDisplay]
libgtk3.gdk_display_supports_shapes.restype = gboolean
libgtk3.gdk_display_supports_shapes.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_window_at_pointer.restype = _GdkWindow
libgtk3.gdk_display_get_window_at_pointer.argtypes = [_GdkDisplay,POINTER(gint),POINTER(gint)]
libgtk3.gdk_display_supports_composite.restype = gboolean
libgtk3.gdk_display_supports_composite.argtypes = [_GdkDisplay]
libgtk3.gdk_display_pointer_is_grabbed.restype = gboolean
libgtk3.gdk_display_pointer_is_grabbed.argtypes = [_GdkDisplay]
libgtk3.gdk_display_supports_selection_notification.restype = gboolean
libgtk3.gdk_display_supports_selection_notification.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_app_launch_context.restype = _GdkAppLaunchContext
libgtk3.gdk_display_get_app_launch_context.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_name.restype = c_char_p
libgtk3.gdk_display_get_name.argtypes = [_GdkDisplay]
libgtk3.gdk_display_get_device_manager.restype = _GdkDeviceManager
libgtk3.gdk_display_get_device_manager.argtypes = [_GdkDisplay]
libgtk3.gdk_display_keyboard_ungrab.restype = None
libgtk3.gdk_display_keyboard_ungrab.argtypes = [_GdkDisplay,guint32]
libgtk3.gdk_display_get_default_screen.restype = _GdkScreen
libgtk3.gdk_display_get_default_screen.argtypes = [_GdkDisplay]
libgtk3.gdk_display_warp_pointer.restype = None
libgtk3.gdk_display_warp_pointer.argtypes = [_GdkDisplay,_GdkScreen,gint,gint]
libgtk3.gdk_display_pointer_ungrab.restype = None
libgtk3.gdk_display_pointer_ungrab.argtypes = [_GdkDisplay,guint32]
libgtk3.gdk_display_get_pointer.restype = None
libgtk3.gdk_display_get_pointer.argtypes = [_GdkDisplay,_GdkScreen,POINTER(gint),POINTER(gint),POINTER(GdkModifierType)]
libgtk3.gdk_display_device_is_grabbed.restype = gboolean
libgtk3.gdk_display_device_is_grabbed.argtypes = [_GdkDisplay,_GdkDevice]
libgtk3.gdk_display_supports_clipboard_persistence.restype = gboolean
libgtk3.gdk_display_supports_clipboard_persistence.argtypes = [_GdkDisplay]
libgtk3.gdk_display_request_selection_notification.restype = gboolean
libgtk3.gdk_display_request_selection_notification.argtypes = [_GdkDisplay,POINTER(c_int)]
libgtk3.gdk_display_sync.restype = None
libgtk3.gdk_display_sync.argtypes = [_GdkDisplay]
libgtk3.gdk_display_open.restype = _GdkDisplay
libgtk3.gdk_display_open.argtypes = [c_char_p]
libgtk3.gdk_display_get_default.restype = _GdkDisplay
libgtk3.gdk_display_get_default.argtypes = []
import gobject__GObject
class GdkDisplay( gobject__GObject.GObject):
    """Class GdkDisplay Constructors"""
    def __init__(self, obj = None):
        self._object = obj
    """Methods"""
    def flush(  self, ):

        
        libgtk3.gdk_display_flush( self._object )

    def get_screen(  self, screen_num, ):

        from gobject import GdkScreen
        return GdkScreen( obj=libgtk3.gdk_display_get_screen( self._object,screen_num ) or POINTER(c_int)())

    def get_default_cursor_size(  self, ):

        
        return libgtk3.gdk_display_get_default_cursor_size( self._object )

    def is_closed(  self, ):

        
        return libgtk3.gdk_display_is_closed( self._object )

    def store_clipboard(  self, clipboard_window, time_, targets, n_targets, ):
        if clipboard_window: clipboard_window = clipboard_window._object
        else: clipboard_window = POINTER(c_int)()
        if targets: targets = targets._object
        else: targets = POINTER(c_int)()

        
        libgtk3.gdk_display_store_clipboard( self._object,clipboard_window,time_,targets,n_targets )

    def set_double_click_distance(  self, distance, ):

        
        libgtk3.gdk_display_set_double_click_distance( self._object,distance )

    def peek_event(  self, ):

        
        return libgtk3.gdk_display_peek_event( self._object )

    def get_n_screens(  self, ):

        
        return libgtk3.gdk_display_get_n_screens( self._object )

    def close(  self, ):

        
        libgtk3.gdk_display_close( self._object )

    def get_maximal_cursor_size(  self, width, height, ):

        
        libgtk3.gdk_display_get_maximal_cursor_size( self._object,width,height )

    def set_double_click_time(  self, msec, ):

        
        libgtk3.gdk_display_set_double_click_time( self._object,msec )

    def supports_input_shapes(  self, ):

        
        return libgtk3.gdk_display_supports_input_shapes( self._object )

    def put_event(  self, event, ):

        
        libgtk3.gdk_display_put_event( self._object,event )

    def supports_cursor_alpha(  self, ):

        
        return libgtk3.gdk_display_supports_cursor_alpha( self._object )

    def notify_startup_complete(  self, startup_id, ):

        
        libgtk3.gdk_display_notify_startup_complete( self._object,startup_id )

    def supports_cursor_color(  self, ):

        
        return libgtk3.gdk_display_supports_cursor_color( self._object )

    def list_devices(  self, ):

        from gobject import GList
        return GList( obj=libgtk3.gdk_display_list_devices( self._object ) or POINTER(c_int)())

    def has_pending(  self, ):

        
        return libgtk3.gdk_display_has_pending( self._object )

    def beep(  self, ):

        
        libgtk3.gdk_display_beep( self._object )

    def get_default_group(  self, ):

        from gobject import GdkWindow
        return GdkWindow(None, obj=libgtk3.gdk_display_get_default_group( self._object ) or POINTER(c_int)())

    def get_event(  self, ):

        
        return libgtk3.gdk_display_get_event( self._object )

    def supports_shapes(  self, ):

        
        return libgtk3.gdk_display_supports_shapes( self._object )

    def get_window_at_pointer(  self, win_x, win_y, ):

        from gobject import GdkWindow
        return GdkWindow(None, obj=libgtk3.gdk_display_get_window_at_pointer( self._object,win_x,win_y ) or POINTER(c_int)())

    def supports_composite(  self, ):

        
        return libgtk3.gdk_display_supports_composite( self._object )

    def pointer_is_grabbed(  self, ):

        
        return libgtk3.gdk_display_pointer_is_grabbed( self._object )

    def supports_selection_notification(  self, ):

        
        return libgtk3.gdk_display_supports_selection_notification( self._object )

    def get_app_launch_context(  self, ):

        from gobject import GdkAppLaunchContext
        return GdkAppLaunchContext(None, obj=libgtk3.gdk_display_get_app_launch_context( self._object ) or POINTER(c_int)())

    def get_name(  self, ):

        
        return libgtk3.gdk_display_get_name( self._object )

    def get_device_manager(  self, ):

        from gobject import GdkDeviceManager
        return GdkDeviceManager( obj=libgtk3.gdk_display_get_device_manager( self._object ) or POINTER(c_int)())

    def keyboard_ungrab(  self, time_, ):

        
        libgtk3.gdk_display_keyboard_ungrab( self._object,time_ )

    def get_default_screen(  self, ):

        from gobject import GdkScreen
        return GdkScreen( obj=libgtk3.gdk_display_get_default_screen( self._object ) or POINTER(c_int)())

    def warp_pointer(  self, screen, x, y, ):
        if screen: screen = screen._object
        else: screen = POINTER(c_int)()

        
        libgtk3.gdk_display_warp_pointer( self._object,screen,x,y )

    def pointer_ungrab(  self, time_, ):

        
        libgtk3.gdk_display_pointer_ungrab( self._object,time_ )

    def get_pointer(  self, screen, x, y, mask, ):
        if screen: screen = screen._object
        else: screen = POINTER(c_int)()

        
        libgtk3.gdk_display_get_pointer( self._object,screen,x,y,mask )

    def device_is_grabbed(  self, device, ):
        if device: device = device._object
        else: device = POINTER(c_int)()

        
        return libgtk3.gdk_display_device_is_grabbed( self._object,device )

    def supports_clipboard_persistence(  self, ):

        
        return libgtk3.gdk_display_supports_clipboard_persistence( self._object )

    def request_selection_notification(  self, selection, ):
        if selection: selection = selection._object
        else: selection = POINTER(c_int)()

        
        return libgtk3.gdk_display_request_selection_notification( self._object,selection )

    def sync(  self, ):

        
        libgtk3.gdk_display_sync( self._object )

    @staticmethod
    def open( display_name,):
        from gobject import GdkDisplay
        return GdkDisplay( obj=    libgtk3.gdk_display_open(display_name, )
 or POINTER(c_int)())
    @staticmethod
    def get_default():
        from gobject import GdkDisplay
        return GdkDisplay( obj=    libgtk3.gdk_display_get_default()
 or POINTER(c_int)())
