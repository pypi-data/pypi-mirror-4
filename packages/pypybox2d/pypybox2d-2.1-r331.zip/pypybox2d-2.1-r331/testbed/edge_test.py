#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# C++ version Copyright (c) 2006-2007 Erin Catto http://www.box2d.org
# Python version Copyright (c) 2010 kne / sirkne at gmail dot com
# 
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

__version__ = "$Revision: 337 $"
__date__ = "$Date: 2011-05-19 16:44:08 -0400 (Thu, 19 May 2011) $"
# $Source$

from framework import *

class EdgeTest (Framework):
    name="EdgeTest"
    description = "Utilizes b2.Edge"
    def __init__(self):
        super(EdgeTest, self).__init__()

        v1=(-10.0, 0.0)
        v2=(-7.0, -1.0)
        v3=(-4.0, 0.0)
        v4=(0.0, 0.0)
        v5=(4.0, 0.0)
        v6=(7.0, 1.0)
        v7=(10.0, 0.0)

        ground=self.world.create_static_body(shapes=
                [b2.Edge(       v1=v1, v2=v2, v3=v3),
                 b2.Edge(v0=v1, v1=v2, v2=v3, v3=v4),
                 b2.Edge(v0=v2, v1=v3, v2=v4, v3=v5),
                 b2.Edge(v0=v3, v1=v4, v2=v5, v3=v6),
                 b2.Edge(v0=v4, v1=v5, v2=v6, v3=v7),
                 b2.Edge(v0=v5, v1=v6, v2=v7),
                ])

        box=self.world.create_dynamic_body(
                position=(4.5, 5.6),
                allow_sleep=False,
                shapes=b2.Polygon(box=(0.5,0.5))
                )

if __name__=="__main__":
     main(EdgeTest)
