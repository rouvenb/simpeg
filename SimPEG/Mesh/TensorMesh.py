from SimPEG import Utils, np, sp
from BaseMesh import BaseMesh
from TensorView import TensorView
from DiffOperators import DiffOperators
from InnerProducts import InnerProducts

class TensorMesh(BaseMesh, TensorView, DiffOperators, InnerProducts):
    """
    TensorMesh is a mesh class that deals with tensor product meshes.

    Any Mesh that has a constant width along the entire axis
    such that it can defined by a single width vector, called 'h'.

    ::

        hx = np.array([1,1,1])
        hy = np.array([1,2])
        hz = np.array([1,1,1,1])

        mesh = Mesh.TensorMesh([hx, hy, hz])

    Example of a padded tensor mesh:

    .. plot::

        from SimPEG import Mesh, Utils
        M = Mesh.TensorMesh(Utils.meshTensors(((10,10),(40,10),(10,10)), ((10,10),(20,10),(0,0))))
        M.plotGrid()

    For a quick tensor mesh on a (10x12x15) unit cube::

        mesh = Mesh.TensorMesh([10, 12, 15])

    """

    __metaclass__ = Utils.SimPEGMetaClass

    _meshType = 'TENSOR'

    def __init__(self, h_in, x0=None):
        assert type(h_in) is list, 'h_in must be a list'
        h = range(len(h_in))
        for i, h_i in enumerate(h_in):
            if type(h_i) in [int, long, float]:
                # This gives you something over the unit cube.
                h_i = np.ones(int(h_i))/int(h_i)
            assert type(h_i) == np.ndarray, ("h[%i] is not a numpy array." % i)
            assert len(h_i.shape) == 1, ("h[%i] must be a 1D numpy array." % i)
            h[i] = h_i[:] # make a copy.

        BaseMesh.__init__(self, np.array([x.size for x in h]), x0)
        assert len(h) == len(self.x0), "Dimension mismatch. x0 != len(h)"

        # Ensure h contains 1D vectors
        self._h = [Utils.mkvc(x.astype(float)) for x in h]

    def __str__(self):
        outStr = '  ---- {0:d}-D TensorMesh ----  '.format(self.dim)
        def printH(hx, outStr=''):
            i = -1
            while True:
                i = i + 1
                if i > hx.size:
                    break
                elif i == hx.size:
                    break
                h = hx[i]
                n = 1
                for j in range(i+1, hx.size):
                    if hx[j] == h:
                        n = n + 1
                        i = i + 1
                    else:
                        break

                if n == 1:
                    outStr = outStr + ' {0:.2f},'.format(h)
                else:
                    outStr = outStr + ' {0:d}*{1:.2f},'.format(n,h)

            return outStr[:-1]

        if self.dim == 1:
            outStr = outStr + '\n   x0: {0:.2f}'.format(self.x0[0])
            outStr = outStr + '\n  nCx: {0:d}'.format(self.nCx)
            outStr = outStr + printH(self.hx, outStr='\n   hx:')
            pass
        elif self.dim == 2:
            outStr = outStr + '\n   x0: {0:.2f}'.format(self.x0[0])
            outStr = outStr + '\n   y0: {0:.2f}'.format(self.x0[1])
            outStr = outStr + '\n  nCx: {0:d}'.format(self.nCx)
            outStr = outStr + '\n  nCy: {0:d}'.format(self.nCy)
            outStr = outStr + printH(self.hx, outStr='\n   hx:')
            outStr = outStr + printH(self.hy, outStr='\n   hy:')
        elif self.dim == 3:
            outStr = outStr + '\n   x0: {0:.2f}'.format(self.x0[0])
            outStr = outStr + '\n   y0: {0:.2f}'.format(self.x0[1])
            outStr = outStr + '\n   z0: {0:.2f}'.format(self.x0[2])
            outStr = outStr + '\n  nCx: {0:d}'.format(self.nCx)
            outStr = outStr + '\n  nCy: {0:d}'.format(self.nCy)
            outStr = outStr + '\n  nCz: {0:d}'.format(self.nCz)
            outStr = outStr + printH(self.hx, outStr='\n   hx:')
            outStr = outStr + printH(self.hy, outStr='\n   hy:')
            outStr = outStr + printH(self.hz, outStr='\n   hz:')

        return outStr

    def h():
        doc = "h is a list containing the cell widths of the tensor mesh in each dimension."
        fget = lambda self: self._h
        return locals()
    h = property(**h())

    def hx():
        doc = "Width of cells in the x direction"
        fget = lambda self: self._h[0]
        return locals()
    hx = property(**hx())

    def hy():
        doc = "Width of cells in the y direction"
        fget = lambda self: None if self.dim < 2 else self._h[1]
        return locals()
    hy = property(**hy())

    def hz():
        doc = "Width of cells in the z direction"
        fget = lambda self: None if self.dim < 3 else self._h[2]
        return locals()
    hz = property(**hz())

    def vectorNx():
        doc = "Nodal grid vector (1D) in the x direction."
        fget = lambda self: np.r_[0., self.hx.cumsum()] + self.x0[0]
        return locals()
    vectorNx = property(**vectorNx())

    def vectorNy():
        doc = "Nodal grid vector (1D) in the y direction."
        fget = lambda self: None if self.dim < 2 else np.r_[0., self.hy.cumsum()] + self.x0[1]
        return locals()
    vectorNy = property(**vectorNy())

    def vectorNz():
        doc = "Nodal grid vector (1D) in the z direction."
        fget = lambda self: None if self.dim < 3 else np.r_[0., self.hz.cumsum()] + self.x0[2]
        return locals()
    vectorNz = property(**vectorNz())

    def vectorCCx():
        doc = "Cell-centered grid vector (1D) in the x direction."
        fget = lambda self: np.r_[0, self.hx[:-1].cumsum()] + self.hx*0.5 + self.x0[0]
        return locals()
    vectorCCx = property(**vectorCCx())

    def vectorCCy():
        doc = "Cell-centered grid vector (1D) in the y direction."
        fget = lambda self: None if self.dim < 2 else np.r_[0, self.hy[:-1].cumsum()] + self.hy*0.5 + self.x0[1]
        return locals()
    vectorCCy = property(**vectorCCy())

    def vectorCCz():
        doc = "Cell-centered grid vector (1D) in the z direction."
        fget = lambda self: None if self.dim < 3 else np.r_[0, self.hz[:-1].cumsum()] + self.hz*0.5 + self.x0[2]
        return locals()
    vectorCCz = property(**vectorCCz())

    def gridCC():
        doc = "Cell-centered grid."

        def fget(self):
            if self._gridCC is None:
                self._gridCC = Utils.ndgrid(self.getTensor('CC'))
            return self._gridCC
        return locals()
    _gridCC = None  # Store grid by default
    gridCC = property(**gridCC())

    def gridN():
        doc = "Nodal grid."

        def fget(self):
            if self._gridN is None:
                self._gridN = Utils.ndgrid(self.getTensor('N'))
            return self._gridN
        return locals()
    _gridN = None  # Store grid by default
    gridN = property(**gridN())

    def gridFx():
        doc = "Face staggered grid in the x direction."

        def fget(self):
            if self._gridFx is None:
                self._gridFx = Utils.ndgrid(self.getTensor('Fx'))
            return self._gridFx
        return locals()
    _gridFx = None  # Store grid by default
    gridFx = property(**gridFx())

    def gridFy():
        doc = "Face staggered grid in the y direction."

        def fget(self):
            if self._gridFy is None and self.dim > 1:
                self._gridFy = Utils.ndgrid(self.getTensor('Fy'))
            return self._gridFy
        return locals()
    _gridFy = None  # Store grid by default
    gridFy = property(**gridFy())

    def gridFz():
        doc = "Face staggered grid in the z direction."

        def fget(self):
            if self._gridFz is None and self.dim > 2:
                self._gridFz = Utils.ndgrid(self.getTensor('Fz'))
            return self._gridFz
        return locals()
    _gridFz = None  # Store grid by default
    gridFz = property(**gridFz())

    def gridEx():
        doc = "Edge staggered grid in the x direction."

        def fget(self):
            if self._gridEx is None:
                self._gridEx = Utils.ndgrid(self.getTensor('Ex'))
            return self._gridEx
        return locals()
    _gridEx = None  # Store grid by default
    gridEx = property(**gridEx())

    def gridEy():
        doc = "Edge staggered grid in the y direction."

        def fget(self):
            if self._gridEy is None and self.dim > 1:
                self._gridEy = Utils.ndgrid(self.getTensor('Ey'))
            return self._gridEy
        return locals()
    _gridEy = None  # Store grid by default
    gridEy = property(**gridEy())

    def gridEz():
        doc = "Edge staggered grid in the z direction."

        def fget(self):
            if self._gridEz is None and self.dim > 2:
                self._gridEz = Utils.ndgrid(self.getTensor('Ez'))
            return self._gridEz
        return locals()
    _gridEz = None  # Store grid by default
    gridEz = property(**gridEz())

    # --------------- Geometries ---------------------
    def vol():
        doc = "Construct cell volumes of the 3D model as 1d array."

        def fget(self):
            if(self._vol is None):
                vh = self.h
                # Compute cell volumes
                if(self.dim == 1):
                    self._vol = Utils.mkvc(vh[0])
                elif(self.dim == 2):
                    # Cell sizes in each direction
                    self._vol = Utils.mkvc(np.outer(vh[0], vh[1]))
                elif(self.dim == 3):
                    # Cell sizes in each direction
                    self._vol = Utils.mkvc(np.outer(Utils.mkvc(np.outer(vh[0], vh[1])), vh[2]))
            return self._vol
        return locals()
    _vol = None
    vol = property(**vol())

    def area():
        doc = "Construct face areas of the 3D model as 1d array."

        def fget(self):
            if(self._area is None):
                # Ensure that we are working with column vectors
                vh = self.h
                # The number of cell centers in each direction
                n = self.nCv
                # Compute areas of cell faces
                if(self.dim == 1):
                    self._area = np.ones(n[0]+1)
                elif(self.dim == 2):
                    area1 = np.outer(np.ones(n[0]+1), vh[1])
                    area2 = np.outer(vh[0], np.ones(n[1]+1))
                    self._area = np.r_[Utils.mkvc(area1), Utils.mkvc(area2)]
                elif(self.dim == 3):
                    area1 = np.outer(np.ones(n[0]+1), Utils.mkvc(np.outer(vh[1], vh[2])))
                    area2 = np.outer(vh[0], Utils.mkvc(np.outer(np.ones(n[1]+1), vh[2])))
                    area3 = np.outer(vh[0], Utils.mkvc(np.outer(vh[1], np.ones(n[2]+1))))
                    self._area = np.r_[Utils.mkvc(area1), Utils.mkvc(area2), Utils.mkvc(area3)]
            return self._area
        return locals()
    _area = None
    area = property(**area())

    def edge():
        doc = "Construct edge legnths of the 3D model as 1d array."

        def fget(self):
            if(self._edge is None):
                # Ensure that we are working with column vectors
                vh = self.h
                # The number of cell centers in each direction
                n = self.nCv
                # Compute edge lengths
                if(self.dim == 1):
                    self._edge = Utils.mkvc(vh[0])
                elif(self.dim == 2):
                    l1 = np.outer(vh[0], np.ones(n[1]+1))
                    l2 = np.outer(np.ones(n[0]+1), vh[1])
                    self._edge = np.r_[Utils.mkvc(l1), Utils.mkvc(l2)]
                elif(self.dim == 3):
                    l1 = np.outer(vh[0], Utils.mkvc(np.outer(np.ones(n[1]+1), np.ones(n[2]+1))))
                    l2 = np.outer(np.ones(n[0]+1), Utils.mkvc(np.outer(vh[1], np.ones(n[2]+1))))
                    l3 = np.outer(np.ones(n[0]+1), Utils.mkvc(np.outer(np.ones(n[1]+1), vh[2])))
                    self._edge = np.r_[Utils.mkvc(l1), Utils.mkvc(l2), Utils.mkvc(l3)]
            return self._edge
        return locals()
    _edge = None
    edge = property(**edge())

    # --------------- Methods ---------------------

    def getTensor(self, locType):
        """ Returns a tensor list.

        :param str locType: What tensor (see below)
        :rtype: list
        :return: list of the tensors that make up the mesh.

        locType can be::

            'Ex'    -> x-component of field defined on edges
            'Ey'    -> y-component of field defined on edges
            'Ez'    -> z-component of field defined on edges
            'Fx'    -> x-component of field defined on faces
            'Fy'    -> y-component of field defined on faces
            'Fz'    -> z-component of field defined on faces
            'N'     -> scalar field defined on nodes
            'CC'    -> scalar field defined on cell centers
        """

        if   locType is 'Fx':
            ten = [self.vectorNx , self.vectorCCy, self.vectorCCz]
        elif locType is 'Fy':
            ten = [self.vectorCCx, self.vectorNy , self.vectorCCz]
        elif locType is 'Fz':
            ten = [self.vectorCCx, self.vectorCCy, self.vectorNz ]
        elif locType is 'Ex':
            ten = [self.vectorCCx, self.vectorNy , self.vectorNz ]
        elif locType is 'Ey':
            ten = [self.vectorNx , self.vectorCCy, self.vectorNz ]
        elif locType is 'Ez':
            ten = [self.vectorNx , self.vectorNy , self.vectorCCz]
        elif locType is 'CC':
            ten = [self.vectorCCx, self.vectorCCy, self.vectorCCz]
        elif locType is 'N':
            ten = [self.vectorNx , self.vectorNy , self.vectorNz ]

        return [t for t in ten if t is not None]


    def isInside(self, pts):
        """
        Determines if a set of points are inside a mesh.

        :param numpy.ndarray pts: Location of points to test
        :rtype numpy.ndarray
        :return inside, numpy array of booleans
        """

        pts = np.atleast_2d(pts)
        inside = (pts[:,0] >= self.vectorNx.min()) & (pts[:,0] <= self.vectorNx.max())
        if self.dim > 1:
            inside = inside & ((pts[:,1] >= self.vectorNy.min()) & (pts[:,1] <= self.vectorNy.max()))
        if self.dim > 2:
            inside = inside & ((pts[:,2] >= self.vectorNz.min()) & (pts[:,2] <= self.vectorNz.max()))
        return inside

    def getInterpolationMat(self, loc, locType):
        """ Produces interpolation matrix

        :param numpy.ndarray loc: Location of points to interpolate to
        :param str locType: What to interpolate (see below)
        :rtype: scipy.sparse.csr.csr_matrix
        :return: M, the interpolation matrix

        locType can be::

            'Ex'    -> x-component of field defined on edges
            'Ey'    -> y-component of field defined on edges
            'Ez'    -> z-component of field defined on edges
            'Fx'    -> x-component of field defined on faces
            'Fy'    -> y-component of field defined on faces
            'Fz'    -> z-component of field defined on faces
            'N'     -> scalar field defined on nodes
            'CC'    -> scalar field defined on cell centers
        """

        loc = np.atleast_2d(loc)
        assert np.all(self.isInside(loc)), "Points outside of mesh"

        ind = 0 if 'x' in locType else 1 if 'y' in locType else 2 if 'z' in locType else -1
        if locType in ['Fx','Fy','Fz','Ex','Ey','Ez'] and self.dim >= ind:
            nF_nE = self.nFv if 'F' in locType else self.nEv
            components = [Utils.spzeros(loc.shape[0], n) for n in nF_nE]
            components[ind] = Utils.interpmat(loc, *self.getTensor(locType))
            Q = sp.hstack(components)
        elif locType in ['CC', 'N']:
            Q = Utils.interpmat(loc, *self.getTensor(locType))
        else:
            raise NotImplementedError('getInterpolationMat: locType=='+locType+' and mesh.dim=='+str(self.dim))
        return Q

if __name__ == '__main__':
    print('Welcome to tensor mesh!')

    testDim = 1
    h1 = 0.3*np.ones(7)
    h1[0] = 0.5
    h1[-1] = 0.6
    h2 = .5 * np.ones(4)
    h3 = .4 * np.ones(6)

    h = [h1, h2, h3]
    h = h[:testDim]

    M = TensorMesh(h)
    print M

    xn = M.plotGrid()