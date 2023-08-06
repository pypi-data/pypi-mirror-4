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
from math import sqrt

class ApplyForce(Framework):
    name="ApplyForce"
    description="Use w, a, and d to control the ship."
    def __init__(self):
        super(ApplyForce, self).__init__()
        self.world.gravity = (0.0, 0.0)

        # The boundaries
        ground = self.world.create_static_body(position=(0, 20))
        ground.create_loop_fixture((-20, -20), (-20, 20), (20, 20), (20, -20))
        xf1 = Transform()
        xf1.angle = 0.3524 * PI
        xf1.position = xf1.rotation * (1.0, 0.0)

        xf2 = Transform()
        xf2.angle = -0.3524 * PI
        xf2.position = xf2.rotation * (-1.0, 0.0)

        self.body = self.world.create_dynamic_body(
                    position=(0, 2), 
                    angle=PI,
                    angular_damping=5.0,
                    linear_damping=0.1,
                    shapes=[shapes.Polygon(vertices=[xf1*(-1,0), xf1*(1,0), xf1*(0,.5)]),
                            shapes.Polygon(vertices=[xf2*(-1,0), xf2*(1,0), xf2*(0,.5)]) ],
                    shape_fixture=b2.Fixture(density=2.0),
                )

        gravity = 10.0
        for i in range(10):
            fixture = b2.Fixture(shape=shapes.Polygon(box=(0.5, 0.5)), density=1, friction=0.3)
            body=self.world.create_dynamic_body(position=(0,5+1.54*i), fixtures=[fixture])

            # For a circle: I = 0.5 * m * r * r ==> r = sqrt(2 * I / m)
            r = sqrt(2.0 * body.inertia / body.mass)

            self.world.create_friction_joint(
                    ground, body,
                    local_anchor_a=(0,0), 
                    local_anchor_b=(0,0), 
                    collide_connected=True,
                    max_force = body.mass * gravity,
                    max_torque = body.mass * r * gravity
                    )

    def key_down(self, key):
        if not self.body:
            return

        if key==Keys.K_w:
            f = self.body.get_world_vector((0.0, -200.0))
            p = self.body.get_world_point((0.0, 2.0))
            self.body.apply_force(f, p)
        elif key==Keys.K_a:
            self.body.apply_torque(50.0)
        elif key==Keys.K_d:
            self.body.apply_torque(-50.0)

if __name__=="__main__":
     main(ApplyForce)
