# Scene elements and their properties are defined here

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
            'bounds': []
            }

    
    bboxes['name'].append('Boundaries')
    bboxes['type'].append('scene')
    bboxes['bounds'].append([[0,0,0],scene_extent])
    # Bounding boxes go here


    ntrees = 2
    nrows  = 1
    
    ax_al  = 0 # canopy aligned along axis ax_al

    cwidth = scene_extent[ax_al]/(1.5*ntrees)
    twidth = scene_extent[ax_al]/(10.0*ntrees)

    gapx = scene_extent[ax_al] - cwidth*ntrees

    cgaps = gapx/ntrees 

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
            # trunk
            bboxes['name'].append(f'trunk_{i}.{j}')
            bboxes['type'].append('bbox')
            bboxes['bounds'].append([[(cwidth+cgaps)*(0.5+i) - twidth/2., 
                                        scene_extent[1]/2.-twidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        0],
                                      [(cwidth+cgaps)*(0.5+i) + twidth/2., 
                                        scene_extent[1]/2.+twidth/2. - (2*j-(nrows-1))*cwidth*.75,
                                        scene_extent[2]*1./5]])
                
            

    return bboxes

