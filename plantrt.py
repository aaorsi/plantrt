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
        



def next_interaction(p,scene,nbb, tol = 1e-6,skip_id = -1):
    # find next surface. Loop around nbb bounding boxes and nbs boundaries
    r = []
    ids = []
    p_int = []
    norep = p.medium if p.medium > 0 else -1

    for ibb in range(nbb):
        pp = geometry.do_raybox(p, scene.bbox.bounds[ibb])
        logging.debug('%s, pp=%g'%(scene.bbox.name[ibb], pp))
        if pp > tol and ibb != skip_id and ibb != norep:
            p_int.append([pp])
            ids.append(ibb)
            
    if p_int == []:
        logging.critical('Found no intersection. Check')
        logging.critical(f'{p.medium}, Position {p.pos}, Direction {p.dir}')
        import pdb
        pdb.set_trace()
    
    pmin = np.argmin(p_int)
    pval = p_int[pmin]
    idcol = ids[pmin]
#    idd = ids[idcol]
    p.pos = p.pos + p_int[pmin]*p.dir
    
    #p.medium = scene.bbox.name[idcol]
    return p, idcol

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
    elements = scene_conf.default_scene_elements(scene_extent)
    scene = scene_conf.Scene()
    scene.bbox.name     = elements['name']
    scene.bbox.bounds   = elements['bounds'] 
    scene.bbox.type     = elements['type']

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
        skip_ids = [-1]
        while ik < arg['nscat']:
            for il in range(ipl):
                for x in range(3):
                    if p.photon[il].pos[x] < 0:
                        p.photon[il].pos[x] = 0
                    if p.photon[il].pos[x] > scene_extent[x]:
                        p.photon[il].pos[x] = scene_extent[x]

                p.photon[il], idd = next_interaction(p.photon[il], scene, nel,skip_id = skip_ids[il])
                # if a scene element was skipped, don't do that again
                if skip_ids[il] != -1:
                    skip_ids[il] = -1

                normal = geometry.get_normal_aabb(p.photon[il],scene.bbox.bounds[idd])
                old_dir = p.photon[il].dir
                p.photon[il].dir = geometry.specular_reflection(old_dir, normal)
                p.photon[il].medium = idd
                
                # if not a boundary then a new photon might be created
                if il == 0 and idd > 0:
                    nprog = len(p.prog)-1
                    if nprog < nplevels:
                        p.add_photon(il,pos=p.photon[il].pos, direction=old_dir)
                        skip_ids.append(idd)
                        if idd == 0:
                            print ('It seems like the photon is being created at a boundary?')
                            import pdb ; pdb.set_trace()
                
                logging.debug(f'[{ik}], {p.photon[il].medium}, normal: {normal}, dir: {p.photon[il].dir} pos:{p.photon[il].pos}')
                ppos = [p.photon[x].pos for x in range(len(p.prog))]
                pos_history.append(ppos)
            
            ik += 1
            ipl = len(p.prog)
    
    nphotons = ipl

    return nphotons, pos_history, p










if __name__ == '__main__':
    run()


