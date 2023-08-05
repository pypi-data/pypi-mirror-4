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
_PangoFontMap = POINTER(c_int)
_GdkGeometry = POINTER(c_int)
_GList = POINTER(c_int)
_GdkTimeCoord = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_PangoCoverage = POINTER(c_int)
_GParamSpec = POINTER(c_int)
_GList = POINTER(c_int)
_GdkRGBA = POINTER(c_int)
_GtkRequisition = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
_GtkRcStyle = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_PangoRectangle = POINTER(c_int)
_PangoLogAttr = POINTER(c_int)
_PangoGlyphString = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_cairo_font_options_t = POINTER(c_int)
_PangoFontFamily = POINTER(c_int)
_GdkDevice = POINTER(c_int)
_GdkWindowAttr = POINTER(c_int)
_GdkAtom = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GtkIconSet = POINTER(c_int)
_PangoLanguage = POINTER(c_int)
_cairo_region_t = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_GdkColor = POINTER(c_int)
_PangoFontset = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
_GdkRectangle = POINTER(c_int)
_PangoFontMap = POINTER(c_int)
_PangoLanguage = POINTER(c_int)
_PangoFont = POINTER(c_int)
_PangoAttrList = POINTER(c_int)
_GdkWMDecoration = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_GdkDeviceManager = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_PangoMatrix = POINTER(c_int)
_cairo_t = POINTER(c_int)
_GSList = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_PangoContext = POINTER(c_int)
_PangoAnalysis = POINTER(c_int)
_GIcon = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
_GtkIconSource = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_GtkAccelGroup = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_GtkRegionFlags = POINTER(c_int)
_cairo_pattern_t = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_GtkStyleContext = POINTER(c_int)
_PangoAttrIterator = POINTER(c_int)
_GtkAllocation = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GtkStyleProvider = POINTER(c_int)
_GtkWidgetClass = POINTER(c_int)
_GtkBorder = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_GValue = POINTER(c_int)
_GtkClipboard = POINTER(c_int)
_PangoCoverage = POINTER(c_int)
_GdkAppLaunchContext = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_PangoMatrix = POINTER(c_int)
_WebKitGeolocationPolicyDecision = POINTER(c_int)
_GtkSettings = POINTER(c_int)
_GdkDevice = POINTER(c_int)
_PangoFontMetrics = POINTER(c_int)
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
GdkInputSource = c_int
GdkInputMode = c_int
GdkAxisUse = c_int
GdkDeviceType = c_int
GdkGrabOwnership = c_int
GdkCursorType = c_int
GdkVisualType = c_int
GdkByteOrder = c_int
PangoStyle = c_int
PangoWeight = c_int
PangoVariant = c_int
PangoStretch = c_int
PangoFontMask = c_int

libgtk3.gtk_widget_path_iter_has_qname.restype = gboolean
libgtk3.gtk_widget_path_iter_has_qname.argtypes = [_GtkWidgetPath,gint,GQuark]
libgtk3.gtk_widget_path_iter_add_region.restype = None
libgtk3.gtk_widget_path_iter_add_region.argtypes = [_GtkWidgetPath,gint,c_char_p,GtkRegionFlags]
libgtk3.gtk_widget_path_iter_clear_regions.restype = None
libgtk3.gtk_widget_path_iter_clear_regions.argtypes = [_GtkWidgetPath,gint]
libgtk3.gtk_widget_path_iter_has_name.restype = gboolean
libgtk3.gtk_widget_path_iter_has_name.argtypes = [_GtkWidgetPath,gint,c_char_p]
libgtk3.gtk_widget_path_iter_has_qregion.restype = gboolean
libgtk3.gtk_widget_path_iter_has_qregion.argtypes = [_GtkWidgetPath,gint,GQuark,_GtkRegionFlags]
libgtk3.gtk_widget_path_iter_remove_region.restype = None
libgtk3.gtk_widget_path_iter_remove_region.argtypes = [_GtkWidgetPath,gint,c_char_p]
libgtk3.gtk_widget_path_is_type.restype = gboolean
libgtk3.gtk_widget_path_is_type.argtypes = [_GtkWidgetPath,GType]
libgtk3.gtk_widget_path_has_parent.restype = gboolean
libgtk3.gtk_widget_path_has_parent.argtypes = [_GtkWidgetPath,GType]
libgtk3.gtk_widget_path_iter_get_name.restype = c_char_p
libgtk3.gtk_widget_path_iter_get_name.argtypes = [_GtkWidgetPath,gint]
libgtk3.gtk_widget_path_iter_has_qclass.restype = gboolean
libgtk3.gtk_widget_path_iter_has_qclass.argtypes = [_GtkWidgetPath,gint,GQuark]
libgtk3.gtk_widget_path_iter_clear_classes.restype = None
libgtk3.gtk_widget_path_iter_clear_classes.argtypes = [_GtkWidgetPath,gint]
libgtk3.gtk_widget_path_free.restype = None
libgtk3.gtk_widget_path_free.argtypes = [_GtkWidgetPath]
libgtk3.gtk_widget_path_prepend_type.restype = None
libgtk3.gtk_widget_path_prepend_type.argtypes = [_GtkWidgetPath,GType]
libgtk3.gtk_widget_path_iter_get_object_type.restype = GType
libgtk3.gtk_widget_path_iter_get_object_type.argtypes = [_GtkWidgetPath,gint]
libgtk3.gtk_widget_path_append_type.restype = gint
libgtk3.gtk_widget_path_append_type.argtypes = [_GtkWidgetPath,GType]
libgtk3.gtk_widget_path_iter_set_object_type.restype = None
libgtk3.gtk_widget_path_iter_set_object_type.argtypes = [_GtkWidgetPath,gint,GType]
libgtk3.gtk_widget_path_iter_remove_class.restype = None
libgtk3.gtk_widget_path_iter_remove_class.argtypes = [_GtkWidgetPath,gint,c_char_p]
libgtk3.gtk_widget_path_iter_list_regions.restype = _GSList
libgtk3.gtk_widget_path_iter_list_regions.argtypes = [_GtkWidgetPath,gint]
libgtk3.gtk_widget_path_iter_has_region.restype = gboolean
libgtk3.gtk_widget_path_iter_has_region.argtypes = [_GtkWidgetPath,gint,c_char_p,_GtkRegionFlags]
libgtk3.gtk_widget_path_iter_set_name.restype = None
libgtk3.gtk_widget_path_iter_set_name.argtypes = [_GtkWidgetPath,gint,c_char_p]
libgtk3.gtk_widget_path_get_object_type.restype = GType
libgtk3.gtk_widget_path_get_object_type.argtypes = [_GtkWidgetPath]
libgtk3.gtk_widget_path_iter_list_classes.restype = _GSList
libgtk3.gtk_widget_path_iter_list_classes.argtypes = [_GtkWidgetPath,gint]
libgtk3.gtk_widget_path_iter_add_class.restype = None
libgtk3.gtk_widget_path_iter_add_class.argtypes = [_GtkWidgetPath,gint,c_char_p]
libgtk3.gtk_widget_path_iter_has_class.restype = gboolean
libgtk3.gtk_widget_path_iter_has_class.argtypes = [_GtkWidgetPath,gint,c_char_p]
libgtk3.gtk_widget_path_copy.restype = _GtkWidgetPath
libgtk3.gtk_widget_path_copy.argtypes = [_GtkWidgetPath]
libgtk3.gtk_widget_path_length.restype = gint
libgtk3.gtk_widget_path_length.argtypes = [_GtkWidgetPath]
class GtkWidgetPath( object):
    """Class GtkWidgetPath Constructors"""
    def __init__( self,  obj = None):
        if obj: self._object = obj
        else:
            libgtk3.gtk_widget_path_new.restype = POINTER(c_int)
            
            libgtk3.gtk_widget_path_new.argtypes = []
            self._object = libgtk3.gtk_widget_path_new()

    """Methods"""
    def iter_has_qname(  self, pos, qname, ):

        
        return libgtk3.gtk_widget_path_iter_has_qname( self._object,pos,qname )

    def iter_add_region(  self, pos, name, flags, ):
        if flags: flags = flags._object
        else: flags = POINTER(c_int)()

        
        libgtk3.gtk_widget_path_iter_add_region( self._object,pos,name,flags )

    def iter_clear_regions(  self, pos, ):

        
        libgtk3.gtk_widget_path_iter_clear_regions( self._object,pos )

    def iter_has_name(  self, pos, name, ):

        
        return libgtk3.gtk_widget_path_iter_has_name( self._object,pos,name )

    def iter_has_qregion(  self, pos, qname, flags, ):
        if flags: flags = flags._object
        else: flags = POINTER(c_int)()

        
        return libgtk3.gtk_widget_path_iter_has_qregion( self._object,pos,qname,flags )

    def iter_remove_region(  self, pos, name, ):

        
        libgtk3.gtk_widget_path_iter_remove_region( self._object,pos,name )

    def is_type(  self, type, ):

        
        return libgtk3.gtk_widget_path_is_type( self._object,type )

    def has_parent(  self, type, ):

        
        return libgtk3.gtk_widget_path_has_parent( self._object,type )

    def iter_get_name(  self, pos, ):

        
        return libgtk3.gtk_widget_path_iter_get_name( self._object,pos )

    def iter_has_qclass(  self, pos, qname, ):

        
        return libgtk3.gtk_widget_path_iter_has_qclass( self._object,pos,qname )

    def iter_clear_classes(  self, pos, ):

        
        libgtk3.gtk_widget_path_iter_clear_classes( self._object,pos )

    def free(  self, ):

        
        libgtk3.gtk_widget_path_free( self._object )

    def prepend_type(  self, type, ):

        
        libgtk3.gtk_widget_path_prepend_type( self._object,type )

    def iter_get_object_type(  self, pos, ):

        
        return libgtk3.gtk_widget_path_iter_get_object_type( self._object,pos )

    def append_type(  self, type, ):

        
        return libgtk3.gtk_widget_path_append_type( self._object,type )

    def iter_set_object_type(  self, pos, type, ):

        
        libgtk3.gtk_widget_path_iter_set_object_type( self._object,pos,type )

    def iter_remove_class(  self, pos, name, ):

        
        libgtk3.gtk_widget_path_iter_remove_class( self._object,pos,name )

    def iter_list_regions(  self, pos, ):

        from gobject import GSList
        return GSList( obj=libgtk3.gtk_widget_path_iter_list_regions( self._object,pos ) or POINTER(c_int)())

    def iter_has_region(  self, pos, name, flags, ):
        if flags: flags = flags._object
        else: flags = POINTER(c_int)()

        
        return libgtk3.gtk_widget_path_iter_has_region( self._object,pos,name,flags )

    def iter_set_name(  self, pos, name, ):

        
        libgtk3.gtk_widget_path_iter_set_name( self._object,pos,name )

    def get_object_type(  self, ):

        
        return libgtk3.gtk_widget_path_get_object_type( self._object )

    def iter_list_classes(  self, pos, ):

        from gobject import GSList
        return GSList( obj=libgtk3.gtk_widget_path_iter_list_classes( self._object,pos ) or POINTER(c_int)())

    def iter_add_class(  self, pos, name, ):

        
        libgtk3.gtk_widget_path_iter_add_class( self._object,pos,name )

    def iter_has_class(  self, pos, name, ):

        
        return libgtk3.gtk_widget_path_iter_has_class( self._object,pos,name )

    def copy(  self, ):

        from gtk3 import GtkWidgetPath
        return GtkWidgetPath( obj=libgtk3.gtk_widget_path_copy( self._object ) or POINTER(c_int)())

    def length(  self, ):

        
        return libgtk3.gtk_widget_path_length( self._object )

