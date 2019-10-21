# Scene elements and their properties are defined here
# comment

import numpy as np

class scene_element:
    
    def __init__(self):
        # name: 'soil', 'leaf', etc... 
        self.name   = []
        # normal vector determining the orientation of the element in cell
        self.type = []
        self.normal = [] 
        self.bounds = []

class Scene:
    def __init__(self): # p contains all boundary elements
        self.dimensions = np.zeros(3) # (0,x1), (0,x2), (0,x3)
        self.bbox = scene_element() # boundary boxes need to be specified explicitly



def default_scene_elements(scene_extent):
    
    bboxes ={
            'name': [],
            'type': [],
            'normal':[],
            'bounds': [],
            'canopy': []
            }

    
    bboxes['name'].append('Boundaries')
    bboxes['type'].append('scene')
    bboxes['bounds'].append([[0,0,0],scene_extent])
    # Bounding boxes go here


    ntrees = 1
    nrows  = 1
    
    ax_al  = 0 # canopy aligned along axis ax_al

    cwidth = scene_extent[ax_al]/(3.5*ntrees)
    twidth = scene_extent[ax_al]/(10.0*ntrees)

    gapx = scene_extent[ax_al] - cwidth*ntrees

    cgaps = gapx/ntrees 
    
    ibb = 0
    for i in range(ntrees):
        for j in range(nrows):
            # canopy
            bboxes['name'].append(f'canopy_{i}.{j}')
            bboxes['type'].append('bbox')
            bboxes['bounds'].append([[(cgaps + cwidth)*(0.5+i)-cwidth/2., 
                                        (scene_extent[1]/2.-cwidth/2.) - (2*j-(nrows-1))*cwidth*.75 ,
                                        scene_extent[2]/5.],
                                    [(cgaps+cwidth)*(0.5+i)+cwidth/2., 
                                        scene_extent[1]/2.+cwidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        scene_extent[2]*3/5.]])
            
            bboxes['canopy'].append(kiwi_tbar(bboxes, ibb))
            
            # trunk
            bboxes['name'].append(f'trunk_{i}.{j}')
            bboxes['type'].append('bbox')
            bboxes['bounds'].append([[(cwidth+cgaps)*(0.5+i) - twidth/2., 
                                        scene_extent[1]/2.-twidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        0],
                                      [(cwidth+cgaps)*(0.5+i) + twidth/2., 
                                        scene_extent[1]/2.+twidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        scene_extent[2]*1./5]])
                
            

            bboxes['canopy'].append([]) 
            ibb += 1
            


    return bboxes


def lad_0():
    return np.random.normal(0,np.pi/8.)


def kiwi_tbar(bboxes, ibb, nleaves = 100, lad = lad_0):
    # Constructs a T-bar kiwifruit structure within bounding box ibb


    cane_sep = 40.0 # cane separation
    bar_height = 85.0 # height of structure

    bb_sizex = bboxes['bounds'][ibb][1][0] - bboxes['bounds'][ibb][0][0]
    bb_sizey = bboxes['bounds'][ibb][1][1] - bboxes['bounds'][ibb][0][1]
    
    cane_length0 = bb_sizey
    ncanes       = int(bb_sizex/cane_sep)
    coff         = bb_sizex - cane_sep*ncanes 
    nshoots_avg  = 5
    shoot_size   = cane_sep
    lead_pos = bb_sizey/2.
    leaf = {}
    leaf['center'] = []
    leaf['radius'] = []
    leaf['normal'] = []
    
    kl = 0 # leaf counter
    for ic in range(ncanes):
        pos_cane = coff/2. + bboxes['bounds'][ibb][0][0] + ic*cane_sep # + np.random.normal(0.0,5.0)
        
        for ix in range(2):
        # canes have different shoots in both sides wrt the main lead
            nshoots = int(nshoots_avg)# + np.random.normal(0.0,3))
            
            for ish in range(nshoots):
                sign = 1 if np.random.random() < 0.5 else -1
                spos = np.random.uniform(0,cane_length0/2.)
                ssize = shoot_size # + np.random.normal(0.0, shoot_size/2.)
                leaves_shoot_half = int(5)# + np.random.normal(0.0, 5))
                if leaves_shoot_half < 1:
                    leaves_shoot_half = 1

                lsep = int(ssize/leaves_shoot_half)
                loff = ssize - lsep*leaves_shoot_half

                for il in range(leaves_shoot_half):
                    leaf_rad = 2.0 # + np.random.normal(0.0,2.0)
                    lpos = loff/2. + lsep*il

                    leaf['center'].append([pos_cane + lpos, lead_pos + ssize*sign, bar_height])
                    leaf['radius'].append(leaf_rad)
                    leaf['normal'].append([lad_0(), 2*np.pi*np.random.uniform()])

                    leaf['center'].append([pos_cane - lpos, lead_pos + ssize*sign, bar_height])
                    leaf['radius'].append(leaf_rad)
                    leaf['normal'].append([lad_0(), 2*np.pi*np.random.uniform()])
                    
                    kl += 2
                    

    print (f'Number of leaves {kl}')
    return leaf
                


