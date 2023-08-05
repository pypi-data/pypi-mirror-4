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
_GtkIconSet = POINTER(c_int)
_cairo_region_t = POINTER(c_int)
_GdkColor = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
_GdkRectangle = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_cairo_t = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
_GtkIconSource = POINTER(c_int)
_GtkAccelGroup = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_GtkStyleContext = POINTER(c_int)
_GtkAllocation = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GtkWidgetClass = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_GValue = POINTER(c_int)
_GtkClipboard = POINTER(c_int)
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

libgtk3.gtk_icon_set_unref.restype = None
libgtk3.gtk_icon_set_unref.argtypes = [_GtkIconSet]
libgtk3.gtk_icon_set_add_source.restype = None
libgtk3.gtk_icon_set_add_source.argtypes = [_GtkIconSet,_GtkIconSource]
libgtk3.gtk_icon_set_copy.restype = _GtkIconSet
libgtk3.gtk_icon_set_copy.argtypes = [_GtkIconSet]
libgtk3.gtk_icon_set_ref.restype = _GtkIconSet
libgtk3.gtk_icon_set_ref.argtypes = [_GtkIconSet]
libgtk3.gtk_icon_set_render_icon.restype = _GdkPixbuf
libgtk3.gtk_icon_set_render_icon.argtypes = [_GtkIconSet,_GtkStyle,GtkTextDirection,GtkStateType,GtkIconSize,_GtkWidget,c_char_p]
libgtk3.gtk_icon_set_get_sizes.restype = None
libgtk3.gtk_icon_set_get_sizes.argtypes = [_GtkIconSet,POINTER(GtkIconSize),POINTER(gint)]
libgtk3.gtk_icon_set_new_from_pixbuf.restype = _GtkIconSet
libgtk3.gtk_icon_set_new_from_pixbuf.argtypes = [_GdkPixbuf]
import gobject__GObject
class GtkIconSet( gobject__GObject.GObject):
    """Class GtkIconSet Constructors"""
    def __init__( self,  obj = None):
        if obj: self._object = obj
        else:
            libgtk3.gtk_icon_set_new.restype = POINTER(c_int)
            
            libgtk3.gtk_icon_set_new.argtypes = []
            self._object = libgtk3.gtk_icon_set_new()

    """Methods"""
    def unref(  self, ):

        
        libgtk3.gtk_icon_set_unref( self._object )

    def add_source(  self, source, ):
        if source: source = source._object
        else: source = POINTER(c_int)()

        
        libgtk3.gtk_icon_set_add_source( self._object,source )

    def copy(  self, ):

        from gtk3 import GtkIconSet
        return GtkIconSet( obj=libgtk3.gtk_icon_set_copy( self._object ) or POINTER(c_int)())

    def ref(  self, ):

        from gtk3 import GtkIconSet
        return GtkIconSet( obj=libgtk3.gtk_icon_set_ref( self._object ) or POINTER(c_int)())

    def render_icon(  self, style, direction, state, size, widget, detail, ):
        if style: style = style._object
        else: style = POINTER(c_int)()
        if widget: widget = widget._object
        else: widget = POINTER(c_int)()

        from gobject import GdkPixbuf
        return GdkPixbuf( obj=libgtk3.gtk_icon_set_render_icon( self._object,style,direction,state,size,widget,detail ) or POINTER(c_int)())

    def get_sizes(  self, sizes, n_sizes, ):

        
        libgtk3.gtk_icon_set_get_sizes( self._object,sizes,n_sizes )

    @staticmethod
    def new_from_pixbuf( pixbuf,):
        if pixbuf: pixbuf = pixbuf._object
        else: pixbuf = POINTER(c_int)()
        from gtk3 import GtkIconSet
        return GtkIconSet( obj=    libgtk3.gtk_icon_set_new_from_pixbuf(pixbuf, )
 or POINTER(c_int)())
