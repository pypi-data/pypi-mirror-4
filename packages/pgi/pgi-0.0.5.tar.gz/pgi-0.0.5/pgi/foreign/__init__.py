# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.


_registered = {}


class ForeignStruct(object):

    def from_pointer(pointer):
        raise NotImplementedError

    def from_to(pointer):
        raise NotImplementedError

    def destroy(pointer):
        raise NotImplementedError

    def copy(pointer):
        raise NotImplementedError


def register(namespace, name, foreign):
    _registered[(namespace, name)] = foreign


def get(namespace, name):
    return _registered[(namespace, name)]
