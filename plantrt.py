import numpy as np
import scene_conf
import geometry
import logging

class Photon:
    def __init__(self,pos=np.zeros(3),direction=np.zeros(3), medium = 0):
        # Upon initialization, 3D positions and direction must be defined
        self.pos = pos
        self.dir = direction
        self.medium = medium
    
    # The following properties are meant to update with every change in direction
    @property
    def dir(self):
        return self._dir
    @dir.setter
    def dir(self,val):
        self._dir = val
        self.invdir = 1./self._dir
        self.sign = np.zeros(3,dtype=np.int)
        self.sign[0] = 1 if self.invdir[0] < 0 else 0
        self.sign[1] = 1 if self.invdir[1] < 0 else 0
        self.sign[2] = 1 if self.invdir[2] < 0 else 0
        

class RayBundle:
    def __init__(self):
        self.photon = [Photon()]
        self.prog = [-1] 
    def add_photon(self,prog, pos=np.zeros(3), direction=np.zeros(3)):
        self.photon.append(Photon(pos=pos, direction=direction))
        self.prog.append(prog)
        



def next_interaction_bbox(p,scene,nbb, tol = 1e-6,skip_id = [-1]):
    # find next surface. Loop around nbb bounding boxes and nbs boundaries
    r = []
    ids = []
    p_int = []
    poi = p.pos
    #norep = p.medium if p.medium > 0 else -1

    for ibb in range(nbb):
        pp = geometry.do_raybox(p, scene.bbox.bounds[ibb])
        logging.debug('%s, pp=%g'%(scene.bbox.name[ibb], pp))
        #if pp > tol and ibb != skip_id and ibb != norep:
        if ibb not in skip_id:
            p_int.append([pp])
            ids.append(ibb)
            
    if p_int == []:
        return poi, -1

    pmin = np.argmin(p_int)
    pval = p_int[pmin]
    idcol = ids[pmin]
    poi += p_int[pmin]*p.dir
    return poi, idcol

def next_interaction_canopy(p,scene,ibb, tol = 1e-6,skip_id = [-1,-1]):
    # find next surface. Loop around nbb bounding boxes and nbs boundaries
    r = []
    ids = []
    p_int = []
    
    leaf = scene.bbox.leaf[ibb]
    nleaves = len(leaf['center'])

    for il in range(nleaves):
        
        pp = geometry.do_raydisk(leaf['normal'][il], leaf['center'][il], 
                leaf['radius'][il], p.dir, p.pos)

        if pp > tol and ibb != skip_id[0] and il != skip_id[1] :
            p_int.append([pp])
            ids.append(ibb)
            
    poi = p.pos
    if p_int == []: # no interaction with canopy
        return p, -1
#        logging.critical('Found no intersection. Check')
#        logging.critical(f'{p.medium}, Position {p.pos}, Direction {p.dir}')
#        import pdb
#        pdb.set_trace()
    else:   
        pmin = np.argmin(p_int)
        pval = p_int[pmin]
        idcol = ids[pmin]
    #    idd = ids[idcol]
        poi = p.pos + p_int[pmin]*p.dir
        
        #p.medium = scene.bbox.name[idcol]
        return poi, idcol




def run(arg, verbose = False):
  
    # Setting up logging
    root = logging.getLogger()
    map(root.removeHandler, root.handlers[:])
    map(root.removeFilter, root.filters[:])
    lev = logging.DEBUG if verbose else logging.INFO
    if 'logfile' in arg:
        logfile = arg['logfile']
        logging.basicConfig(level=lev, format=' %(levelname)s - %(funcName)s(): %(message)s',
            filename=logfile, filemode='w')
    else:
        logging.basicConfig(level=lev, format=' %(levelname)s - %(funcName)s(): %(message)s')

    # 
    logging.debug(f'Verbose mode activated')
    theta_sun = arg['theta_sun']
    phi_sun   = arg['phi_sun']
    
    # (0,0,0) is placed at one of the edges by default
    scene_extent = arg['scene_extent'] 
    elements, junk = scene_conf.default_scene_elements(scene_extent)
    scene = scene_conf.Scene()
    scene.bbox.name     = elements['name']
    scene.bbox.bounds   = elements['bounds'] 
    scene.bbox.type     = elements['type']
    scene.bbox.leaf     = elements['canopy']

    # direct sunlight 
    direct_sun =  geometry.dir_vector(theta_sun, phi_sun)
    observer = {'name'  : 'observer',
                'center': [99, 50, 90],
                'extent': [5,5, 0],
                'normal': [0,0,-1]} # looking downwards

    Nphotons = 1
    th = theta_sun + np.pi/2.
    ph = phi_sun 
    
    # number of scene elements
    nel = len(scene.bbox.name) 
    pos_history = []
    nplevels = arg['nplevels'] # number of levels in photon generation

    ipl = 1
    for ip in range(Nphotons):
        p = RayBundle()
        p.photon[0].pos =  np.array(observer['center'])
        p.photon[0].dir = geometry.dir_vector(th, ph)
        p.photon[0].medium = 0 # within the boundaries
        logging.info(f'photon initial direction {p.photon[0].dir} and position {p.photon[0].pos}')

        pos_history.append(p.photon[0].pos)
        # bouncing photons
        ik = 0
        nnp = 0 
        idd = 0 # first medium is scene
        idl = -1 # no leaf interaction at beginning
        skip_leaf = [[-1,-1]]
        while ik < arg['nscat']:
            for il in range(ipl):
                # fix fp-errors to make sure photon is within scene
                for x in range(3):
                    if p.photon[il].pos[x] < 0:
                        p.photon[il].pos[x] = 0
                    if p.photon[il].pos[x] > scene_extent[x]:
                        p.photon[il].pos[x] = scene_extent[x]
               
                import pdb ; pdb.set_trace()

                # TODO:
                # The logic should be:
                # 1. Compute point of interaction (POI) with scene
                # 2. Compute closest bbox ibb
                # 3. Within ibb, compute closest leaf idl
                # 4. If idl == -1, repeat 2, 3,4  skipping ibb
                # 5. If idl is still -1, then accept step 1. Else, update POI using idl

                target = -1
                skip_list = [0] # by default skips the scene
                no_int = 0
                old_dir = p.photon[il].dir
                
                while target == -1: # Iteratively searching for an interaction
                #Find closest bbox
                    poi, idd = next_interaction_bbox(p.photon[il], scene, nel,
                            skip_id = skip_list)
                    if idd != -1:
                    # 3 Closest leaf within idd
                        poi, idl = next_interaction_canopy(p.photon[il],
                                        scene, idd, skip_id = skip_leaf[il])
                        if idl != -1:
                        # Leaf interaction found
                            normal = scene.bbox.leaf[idd]['normal'][idl]
                            p.photon[il].pos = poi
                            p.photon[il].dir = geometry.specular_reflection(old_dir, normal)
                            if il == 0:
                                nprog = len(p.prog)-1
                                if nprog < nplevels:
                                    # New photon created with same position and old direction
                                    p.add_photon(il,pos=p.photon[il].pos, direction=old_dir)
                                    skip_leaf.append([idd,idl]) # skip this leaf in the next iteration

                            target = 1

                        else:
                        # 4 If no leaf found, repeat skipping bbox idd             
                            skip_list.append(idd)
                            if len(skip_list) == nel:
                            # 5 If no leaf found on any bbox, then bounce against the scene                 
                                pp = geometry.do_raybox(p[il], scene.bbox.bounds[0])
                                p.photon[il].pos += pp*p.photon[il].dir
                                normal = geometry.get_normal_aabb(p.photon[il],scene.bbox.bounds[0])
                                p.photon[il].dir = geometry.specular_reflection(old_dir, normal)
                                target = 1

                
                logging.debug(f'[{ik}], {p.photon[il].medium}, normal: {normal}, dir: {p.photon[il].dir} pos:{p.photon[il].pos}')
                ppos = [p.photon[x].pos for x in range(len(p.prog))]
                pos_history.append(ppos)
            
            ik += 1
            ipl = len(p.prog)
    
    nphotons = ipl

    return nphotons, pos_history, p


if __name__ == '__main__':
    run()


