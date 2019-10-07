# A bunch of geometrical calculations

import numpy as np
import logging

def get_normal_aabb(p,bounds):
    # Quicker function that assumes that the bbox is axis aligned and so all normals would correspond to
    # either +-^i, +-^j or +- ^k. The sign is obtained by forcing that the dot product between the normal
    # and the photon's direction is negative.
    pp = p.pos
    idmin = np.argmin(np.abs([pp-bounds[0], pp-bounds[1]]).flatten())
    ib = int(idmin/3)
    ic = idmin - (ib*3)
    normal = np.zeros(3,dtype=int)
    normal[ic] = 1
    dd = p.dir.dot(normal)
    logging.debug(f'normal calculation: pos {p.pos}, normal {normal}, dd {dd}')
    if dd >0:
        normal[ic] = -1

    return normal


def get_normal(pp,bounds,tol=1e-3):

#    pp  = np.array(p.pos)
   
    idmin = np.argmin(np.abs([pp-bounds[0], pp-bounds[1]]).flatten())
    ib = int(idmin/3)
    ic = idmin - (ib*3)
    # Photon is hitting face defined by boundary ib, side ic
    s1 = [(bounds[1][j]-bounds[0][j])/2. for j in range(3)]
    s1[ic]  = bounds[ib][ic]
    s2      = [bounds[ib][j] for j in range(3)]
    s2[ic]  = bounds[ib][ic]

    normal = np.cross(s1-pp, s2-pp)
    if np.sum(normal) < tol: # if the three vectors happen to be (almost) parallel
        s2 = [(bounds[1][j] - bounds[0][j])*2./3 for j in range(3)]
        s2[ic] = bounds[ib][ic]
        s2[2] = s1[ic]
        normal = np.cross(s1-pp, s2-pp)
        
    return normal/np.linalg.norm(normal)


def dir_vector(theta, phi):
    return np.array([np.sin(theta)*np.cos(phi), 
            np.sin(theta)*np.sin(phi),
            np.cos(theta)])


def specular_reflection(incident, normal):
    # Function to compute mirror-like reflection
    # returns the direction of the outgoing photon

    out = incident - 2*(np.dot(incident,normal))*normal
    return out/np.linalg.norm(out)



def get_rayplaneintersect(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):

    # This function is adapted from 
    # https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python
    
    ndotu = planeNormal.dot(rayDirection)
    if abs(ndotu) < epsilon: # no collision if the plane normal and photon direction are perpendicular.
            return -1
    elif ndotu > 0:
        return -1 # photon is moving away from this surface, instead of towards it
    else:
        w = rayPoint - planePoint
        si = -planeNormal.dot(w) / ndotu
        Psi = w + si * rayDirection + planePoint
        return Psi


def do_raybox(r, bounds, tol = 1e-4):
    # Computes intersection between ray and bounding box, 
    # returns distance to intersection if exists, and -1 otherwise
    # This is based on the algorithm described here for c++:
    # https://www.scratchapixel.com/code.php?id=10&origin=/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes&src=1
   
    for x in range(3):
        if r.pos[x] < tol:
            r.pos[x] = 0.0

    tmin = (bounds[r.sign[0]][0] - r.pos[0])*r.invdir[0]
    tmax = (bounds[1-r.sign[0]][0] - r.pos[0])*r.invdir[0]
    
    tymin = (bounds[r.sign[1]][1] - r.pos[1])*r.invdir[1]
    tymax = (bounds[1-r.sign[1]][1] - r.pos[1])*r.invdir[1]
    
    if ((tmin > tymax) or (tymin > tmax)):
        return -1
    if (tymin > tmin):
        tmin = tymin
    if (tymax < tmax):
        tmax = tymax
    

    tzmin = (bounds[r.sign[2]][2] - r.pos[2])*r.invdir[2]
    tzmax = (bounds[1-r.sign[2]][2] - r.pos[2])*r.invdir[2]

    
    if ((tmin > tzmax) or (tzmin > tmax)):
        return -1
    if (tzmin > tmin):
        tmin = tzmin
    if (tzmax < tmax):
        tmax = tzmax

    t = tmin
    if t <= 0:
        t = tmax
        if t < 0:
            return -1
    
    return t






