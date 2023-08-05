#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
from freetype import *

face = Face('/Library/Fonts/Arial.ttf')
face.set_char_size( 48*64 )
print face.get_kerning('A','V').x

