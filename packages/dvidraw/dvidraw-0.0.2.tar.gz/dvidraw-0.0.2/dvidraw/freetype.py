from ctypes import (c_void_p, c_char_p, c_uint32, CDLL, byref, POINTER,
                    Structure, c_byte, c_double)
import sys
from functools import partial
import struct

# PyCairo doesn't have any freetype support due to there being no python
# extension for freetype that exposes a C api. Since there is fat chance of this
# happening, as it's a lot of work, it's perhaps easiest to just wrap the
# functions we need. There's only a few needed for interop.

class PycairoContext(Structure):
    _fields_ = [("PyObject_HEAD", c_byte *
                 object.__basicsize__),
                ("ctx", c_void_p),
                ("base", c_void_p)]


# Freetype2 encoding enumerations are defined by packing a 32-bit bigendian
# integer with four bytes. Kinda like how the struct module does in python.
ADOBE_CUSTOM, = struct.unpack('>I', 'ADBC')
UNICODE, = struct.unpack('>I', 'unic')

ftlib = CDLL('libfreetype.so')

class FTFace(object):
    def __init__(self, ft_face):
        self._ft_face = ft_face
        self._as_parameter_ = ft_face
        self.select_charmap = partial(FTFace.select_charmap, self)
        self.get_char_index = partial(FTFace.get_char_index, self)
        self.get_name_index = partial(FTFace.get_name_index, self)

    _lib = ftlib
    get_name_index = _lib.FT_Get_Name_Index
    get_name_index.argtypes = (c_void_p, c_char_p)

    select_charmap = _lib.FT_Select_Charmap
    select_charmap.argypes = (c_void_p, c_uint32)

    get_char_index = _lib.FT_Get_Char_Index
    get_char_index.argtypes = (c_void_p, c_uint32)

class Freetype:
    # TODO: Will want to do some OSX detection here

    cache = {}

    def __init__(self):
        self._ft_lib = c_void_p()
        if self.init_freetype(byref(self._ft_lib)):
            raise RuntimeError("Freetype initialisation failed")

    def new_face(self, filename):
        """Implements a very simple cache"""
        ft_face = self.cache.get(filename)
        if not ft_face:
            ft_face = c_void_p()
            if Freetype._new_face(self._ft_lib, filename, 0, byref(ft_face)):
                raise RuntimeError(
                    "Error creating FreeType font face for " + filename)

            ft_face = FTFace(ft_face)
            ft_face.select_charmap(ADOBE_CUSTOM)
            self.cache[filename] = ft_face

        return ft_face


    _lib = ftlib

    init_freetype = _lib.FT_Init_FreeType
    init_freetype.argtypes = c_void_p,

    _new_face = _lib.FT_New_Face
    _new_face.argtypes = c_void_p, c_char_p, c_uint32, c_void_p

class Cairo:
    #TODO: OSX detection here
    _lib = CDLL('libcairo.so')

    create_from_ft_face = _lib.cairo_ft_font_face_create_for_ft_face
    create_from_ft_face.argtypes = c_void_p, c_uint32

    set_font_face = _lib.cairo_set_font_face
    set_font_face.argtypes = c_void_p, c_void_p

    font_face_status = _lib.cairo_font_face_status
    font_face_status.argtypes = c_void_p,

    font_options_create = _lib.cairo_font_options_create
    font_options_set_antialias = _lib.cairo_font_options_set_antialias
    font_options_set_subpixel_order\
            = _lib.cairo_font_options_set_subpixel_order
    font_options_set_hint_style = _lib.cairo_font_options_set_hint_style

    status = _lib.cairo_status
    status.argtypes = c_void_p,

    @classmethod
    def cr_face_from_ft_face(cls, ft_face):
        cr_face = cls.create_from_ft_face(ft_face, 0)
        if cls.font_face_status(cr_face):
            raise RuntimeError()
        return cr_face

    @classmethod
    def set_font_face(cls, cairo_ctx, cr_face):
        cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx

        cls._lib.cairo_set_font_face (cairo_t, cr_face)
        if cls.status (cairo_t):
            raise RuntimeError("Setting font face failed")

        face = cairo_ctx.get_font_face ()

freetype = Freetype()
