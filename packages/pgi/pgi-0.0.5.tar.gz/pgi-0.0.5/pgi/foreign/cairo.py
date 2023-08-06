# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from gpi.foreign import ForeignStruct

import ctypes

has_cairo = False
is_cairocffi = False

try:
    import cairo
except ImportError:
    try:
        import cairocffi as cairo
    except ImportError:
        has_cairo = False
    else:
        cairo.install_as_pycairo()
        is_cairocffi = True

if not has_cairo:
    def cairo_context_from_pointer(pointer):
        return

    def cairo_context_to_pointer(context):
        return
elif is_cairocffi:
    pass
else:
    class PycairoContext(ctypes.Structure):
        _fields_ = [
            ("head", ctypes.py_object),
            ("ctx", ctypes.c_void_p),
            ("base", ctypes.POINTER(ctypes.py_object)),
        ]

    lib = ctypes.CDLL("libcairo.so")
    cairo_destroy = getattr(lib, "cairo_destroy")
    cairo_destroy.argtypes = [ctypes.c_void_p]
    cairo_destroy.restype = None

    cairo_get_reference_count = getattr(lib, "cairo_get_reference_count")
    cairo_get_reference_count.argtypes = [ctypes.c_void_p]
    cairo_get_reference_count.restype = ctypes.c_uint

    def cairo_context_from_pointer(pointer):
        # ugly hack..
        context = cairo.Context(cairo.ImageSurface(0, 0, 0))
        context_struct = PycairoContext.from_address(id(context))
        cairo_destroy(context_struct.ctx)
        context_struct.ctx = pointer
        return context

    def cairo_context_to_pointer(context):
        context_struct = PycairoContext.from_address(id(context))
        return context_struct.ctx

def init():
    pass
