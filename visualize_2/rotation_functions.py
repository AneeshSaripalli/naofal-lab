# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 17:54:24 2017

@author: sxj146830
           |-                   -| |-                   -| |-                   -|
           | cos(y)  -sin(y)   0 | | cos(p)  0   -sin(p) | | 1       0       0   |
 matrix =  | sin(y)   cos(y)   0 |x|  1       0      0   |x| 0    cos(r) -sin(r) |
           |    0        0     1 | | sin(p)  0    cos(p) | | 0    sin(r)  cos(r) |
           |-                   -| |-                   -| |-                   -|
"""
#import numpy as np
#import math

import numpy as np
import math  
from pyquaternion import Quaternion

def eul2mat(angles):
  

    rot_y = np.matrix([[math.cos(angles[0]), -math.sin(angles[0]), 0 ],[math.sin(angles[0]), math.cos(angles[0]), 0],[0, 0, 1]]);
    rot_p = np.matrix([[math.cos(angles[1]), 0, -math.sin(angles[1])],[0, 1, 0],[math.sin(angles[1]), 0, math.cos(angles[1])]]);
    rot_r = np.matrix([[1, 0, 0],[0, math.cos(angles[2]), -math.sin(angles[2])],[0, math.sin(angles[2]), math.cos(angles[2])]]);

    matrix = rot_y*rot_p*rot_r;
    return matrix

ang = [0.2,0.4,0.1];
a=eul2mat(ang)

def mat2eul(input):
    angles = np.zeros(3);
    angles[0] = math.atan2(input[1,0],input[0,0]);
    c = math.cos(angles[0]);
    s = math.sin(angles[0]);
    angles[1] = math.atan2(input[2,0],(input[0,0]*c+input[1,0]*s));
    angles[2] = math.atan2((input[0,2]*s-input[1,2]*c),(-input[0,1]*s+input[1,1]*c));
    return angles

#print(mat2eul(a))

def quat_average(input):
    """averaging quaternions
       input : nx4 array
       
       """
    if len(input) == 0:
        return Quaternion(0,0,0,0)
    else:
        avg = Quaternion(input[0])
        for l1 in range(1,input.shape[0]):
            avg = Quaternion.slerp(avg,Quaternion(input[l1]),1/(l1+1))
        return avg
    
def orient_square(loc,quat):
    sqr = np.array([[0.02, 0.02, 0],[-0.02, 0.02, 0],[-0.02, -0.02, 0],[0.02, -0.02, 0]])
    trans_sqr = np.zeros((4,3))
    for i in range(0,sqr.shape[0]):
        trans_sqr[i,:] = quat.rotate(sqr[i,:]) + loc
    return trans_sqr


        
    
        
    