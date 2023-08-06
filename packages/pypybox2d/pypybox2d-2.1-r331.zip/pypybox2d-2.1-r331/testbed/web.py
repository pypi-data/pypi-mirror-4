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

class Web(Framework):
    name="Web"
    description="This demonstrates a soft distance joint. Press: (b) to delete a body, (j) to delete a joint"
    def __init__(self):
        super(Web, self).__init__()

        # The ground
        ground = self.world.create_static_body(shapes=b2.Edge((-40, 0),(40, 0)))

        fixture=b2.Fixture(shape=b2.Polygon(box=(0.5,0.5)), 
                           density=5, friction=0.2)

        self.bodies = [self.world.create_dynamic_body(
                            position=pos, 
                            fixtures=fixture
                            ) for pos in ( (-5,5), (5,5), (5,15), (-5,15) )]

        bodies = self.bodies

        # Create the joints between each of the bodies and also the ground
        #         body_a      body_b   local_anchor_a local_anchor_b
        sets = [ (ground,    bodies[0], (-10,0), (-0.5,-0.5)),
                 (ground,    bodies[1], (10,0),  (0.5,-0.5)),
                 (ground,    bodies[2], (10,20), (0.5,0.5)),
                 (ground,    bodies[3], (-10,20),(-0.5,0.5)),
                 (bodies[0], bodies[1], (0.5,0), (-0.5,0)),
                 (bodies[1], bodies[2], (0,0.5), (0,-0.5)),
                 (bodies[2], bodies[3], (-0.5,0),(0.5,0)),
                 (bodies[3], bodies[0], (0,-0.5),(0,0.5)),
                ]
    
        # We will define the positions in the local body coordinates, the length
        # will automatically be set by the DistanceJoint
        self.joints=[]
        for body_a, body_b, local_anchor_a, local_anchor_b in sets:
            joint = self.world.create_distance_joint(
                    body_a, body_b,
                    frequency=4.0,
                    damping_ratio=0.5,
                    local_anchor_a=local_anchor_a,
                    local_anchor_b=local_anchor_b,
                )
            self.joints.append(joint)

    def key_down(self, key):
        if key==Keys.K_b:
            for body in self.bodies:
                # Gets both FixtureDestroyed and JointDestroyed callbacks.
                print('Destroying a body...')
                self.world.destroy_body(body)
                break

        elif key==Keys.K_j:
            for joint in self.joints:
                # Does not get a JointDestroyed callback!
                print('Destroying a joint...')
                self.world.destroy_joint(joint)
                self.joints.remove(joint)
                break

    def fixture_destroyed(self, fixture):
        body = fixture.body
        if body in self.bodies:
            print(body)
            self.bodies.remove(body)
            print("Fixture destroyed, removing its body from the list. Bodies left: %d" \
                    % len(self.bodies))

    def joint_destroyed(self, joint):
        if joint in self.joints:
            self.joints.remove(joint)
            print("Joint destroyed and removed from the list. Joints left: %d" \
                    % len(self.joints))

if __name__=="__main__":
     main(Web)
