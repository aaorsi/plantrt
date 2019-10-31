# Scene elements and their properties are defined here
# comment

import numpy as np
import geometry

class scene_element:
    
    def __init__(self):
        # name: 'soil', 'leaf', etc... 
        self.name   = []
        # normal vector determining the orientation of the element in cell
        self.type = []
        self.normal = [] 
        self.bounds = []
        self.leaf = []

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
    bboxes['canopy'].append([])
    # Bounding boxes go here


    ntrees = 1
    nrows  = 1
    
    ax_al  = 0 # canopy aligned along axis ax_al

    cwidth = scene_extent[ax_al]/(ntrees*1.1)
#    twidth = scene_extent[ax_al]/(10.0*ntrees)

    gapx = scene_extent[ax_al] - cwidth*ntrees

    cgaps = gapx/ntrees 
    
    ibb = 1

    cane_list = []

    for i in range(ntrees):
        for j in range(nrows):
            # canopy
            bboxes['name'].append(f'canopy_{i}.{j}')
            bboxes['type'].append('bbox')
            bboxes['bounds'].append([[(cgaps + cwidth)*(0.5+i)-cwidth/2., 
                                        (scene_extent[1]/2.-cwidth/2.) - (2*j-(nrows-1))*cwidth*.75 ,
                                        0],
                                    [(cgaps+cwidth)*(0.5+i)+cwidth/2., 
                                        scene_extent[1]/2.+cwidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        scene_extent[2]*3/5.]])
            
            leaf, cane = kiwi_tbar(bboxes,ibb)
            cane_list.append(cane)
            bboxes['canopy'].append(leaf)
            
            """            # trunk
            bboxes['name'].append(f'trunk_{i}.{j}')
            bboxes['type'].append('bbox')
            bboxes['bounds'].append([[(cwidth+cgaps)*(0.5+i) - twidth/2., 
                                        scene_extent[1]/2.-twidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        0],
                                      [(cwidth+cgaps)*(0.5+i) + twidth/2., 
                                        scene_extent[1]/2.+twidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        scene_extent[2]*1./5]])
                
            

            bboxes['canopy'].append([]) 
            """
            
            ibb += 1
            


    return bboxes, cane_list


def lad_0():
    return np.random.normal(0,np.pi/8.)


def kiwi_tbar(bboxes, ibb, nleaves = 100, lad = lad_0):
    # Constructs a T-bar kiwifruit structure within bounding box ibb


    cane_sep = 40.0 # cane separation
    bar_height = 85.0 # height of structure

    bbox_pos = bboxes['bounds'][ibb]

    bb_sizex = bbox_pos[1][0] - bbox_pos[0][0]
    bb_sizey = bbox_pos[1][1] - bbox_pos[0][1]
    
    cane_length0 = bb_sizey
    ncanes       = int(bb_sizex/cane_sep)
    coff         = bb_sizex - cane_sep*ncanes 
    nshoots_avg  = 10
    shoot_size   = cane_sep
    lead_pos     = bb_sizey/2.
    leaf = {}
    leaf['center'] = []
    leaf['radius'] = []
    leaf['normal'] = []
    
    cane = {}
    cane['cane_pos'] = []
    cane['shoot_pos'] = []
    cane['trunk_pos'] = [[(bbox_pos[0][0] + bbox_pos[1][0])/2.,
                         (bbox_pos[0][1] + bbox_pos[1][1])/2.,
                         0],
                         [(bbox_pos[0][0] + bbox_pos[1][0])/2.,
                         (bbox_pos[0][1] + bbox_pos[1][1])/2.,
                         bar_height]]
    cane['lead_pos'] = [[bbox_pos[0][0], (bbox_pos[0][1] + bbox_pos[1][1])/2.,
                        bar_height],
                        [bbox_pos[1][0], (bbox_pos[0][1] + bbox_pos[1][1])/2.,
                        bar_height]]





#    import pdb ; pdb.set_trace()

    kl = 0 # leaf counter
    for ic in range(ncanes):
        pos_cane = coff/2. + bbox_pos[0][0] + ic*cane_sep  + np.random.normal(0.0,2.0)
#        print (f'cane position x {pos_cane}')
        # canes have different shoots in both sides wrt the main lead
        nshoots = int(nshoots_avg + np.random.uniform(0.0,5))
        if nshoots < 1:
            nshoots = 1
        cane['cane_pos'].append([[pos_cane, bbox_pos[0][1], bar_height],
                                 [pos_cane, bbox_pos[1][1], bar_height]])

        
        for ish in range(nshoots):
#            sign = 1 if np.random.random() < 0.5 else -1
#            print (f'sign {sign}')
            #spos = np.random.uniform(0,cane_length0)
            sign = 1
            spos = int(cane_length0/nshoots)*ish + np.random.uniform(0,10)
#            print (f'shoot position y {spos}')
            ssize = shoot_size/2. + np.random.uniform(0.0, shoot_size/4.)
#            print (f'shoot size x {ssize}')
            leaves_shoot_half = int(3)# + np.random.normal(0.0, 2))
            if leaves_shoot_half < 1:
                leaves_shoot_half = 1

            lsep = int(ssize/leaves_shoot_half)
            loff = ssize - lsep*leaves_shoot_half

            cane['shoot_pos'].append([[pos_cane - ssize, spos + bbox_pos[0][1], bar_height],
                                      [pos_cane + ssize, spos + bbox_pos[0][1], bar_height]])

            for iss in [-1,1]:
                for il in range(leaves_shoot_half):
                    leaf_rad = 5.0  + np.random.uniform(-.5,.5)
                    lpos = loff/2. + lsep*il + np.random.normal(0.0,2)

                    clx = pos_cane + lpos*iss
                    cly = bbox_pos[0][1]+spos

                    if (clx < bbox_pos[1][0] and clx > bbox_pos[0][0]) and (
                            cly < bbox_pos[1][1] and cly > bbox_pos[0][1]):
                        
                        leaf['center'].append([pos_cane + lpos*iss, 
                            bbox_pos[0][1] + spos - leaf_rad, bar_height])
                        leaf['radius'].append(leaf_rad)
                        leaf['normal'].append(geometry.dir_vector(lad_0(), 2*np.pi*np.random.uniform()))
                        leaf['center'].append([pos_cane + lpos*iss, 
                            bbox_pos[0][1] + spos + leaf_rad, bar_height])
                        leaf['radius'].append(leaf_rad)
                        leaf['normal'].append(geometry.dir_vector(lad_0(), 2*np.pi*np.random.uniform()))

#                    print (f'leaf data {leaf}')

            kl += 2
                
#                import pdb ; pdb.set_trace()

#    print (f'Number of leaves {kl}')
    return leaf, cane
                


