import types, operator, tempfile, itertools, distutils

import numpy as np
import scipy.weave, scipy.optimize, scipy.io
import gsn_util as util

# Added June 2012

scipy_has_fwrite = (distutils.version.LooseVersion(scipy.__version__) < 
                    distutils.version.LooseVersion('0.10'))

# this is a module value so that one can change the default, e.g. to low values for testing
big_array_default_cut = 3e8

class myfile(file):
    """This is a file-like object that reads text files, but enforces the
    constraint that the number of fields is the same as the number of
    fields in the first line of the file.  It only implements enough
    of the file protocol so that it can be used by numpy's loadtxt()
    function.  The purpose is to read text files that record
    simulation status when those simulations may be forcibly killed by
    the batch queuing system, and therefore may contain partial lines.
    The simulation restarts from the last complete restart dump, so it
    will restart in a consistent state, but there will be some garbage
    in the text file.  I just want to skip the garbage.

    """
    
    # Prior to April 2013, numpy's loadtxt called readline() then
    # next() repeatedly.  So it worked to set the field count based on
    # the line encountered by readline.

    def next(self):
        # As of April 2013, numpy's loadtxt just calls next
        # repeatedly.  So we have to check if this is the first call
        # (does the attribute exist) and set the desired field count then.
        line = file.next(self)
        if not hasattr(self, '_count'):
            self._count = len(line.split())
        # Keep reading new lines until you get to one with the right
        # field count.  In the past, I stopped reading the file when
        # this happened.  However, sometimes a simulation is
        # interrupted mid-write, and you get a partial line, but when
        # the simulation starts, you have good data again.  So I
        # really just want to skip bad lines.
        while len(line.split()) != self._count:
            line = file.next(self)
        return line

    # This worked for versions of numpy prior to April 2013.  The
    # implementation for pre-April 2013 numpy will work for older
    # versions, too, so I could just get rid of this.  
    def readline(self, size=-1):
        line = file.readline(self, size)
        self._count = len(line.split())
        return line
    
def azip(*args):
    """zip() for arrays"""
    return np.transpose(np.array(args))
    
# def rms(y,axis=None):
#     y = np.asarray(y)
#     assert len(y.shape) == 1
#     return np.sqrt(sum(y**2))/len(y)

def good_data(aa):
    "Filter out nans and infs"
    aa = np.asarray(aa)
    return (aa==aa) & ((aa == 0) | (aa != 2*aa))

def all_good(f, a):
    """Test whether f(el) is True for all el in a"""
    # better name for this would be nice
    return reduce(np.logical_and, map(f, a))

def weighted_mean(xs,ws):
    """Mean of xs weighted by ws."""
    xs, ws = np.asarray(xs), np.asarray(ws)
    return (xs*ws).sum()/xs.sum()

def weighted_std(xs,ws):
    """Standard deviation of xs weighted by ws."""
    return np.sqrt( (ws*(xs-weighted_mean(xs,ws))**2).sum()/ws.sum() )
    
def geometric_mean(a):
    """Geometric mean"""
    return np.exp(np.mean(np.log(a)))

def rescale(ws, imin=None, imax=None, fmin=0, fmax=256):
    """Rescale an array into an image
    
    Rescale a floating point array into an integer array with values
    ranging from 0 to 256, suitable for writing to an image with the
    Python Image Library (pil) for example.

    """
    ws = np.asarray(ws)
    if imin is None: imin = ws.min()
    if imax is None: imax = ws.max()

    return (fmax-fmin)*(ws.clip(imin, imax) - imin)/(imax-imin) + fmin

def grid_nd(*ns): 
    """Make a len(ns) dimensional grid ranging from 0 to 1 with ns[0]
    points in the first dimension, ns[1] points in the second, etc.
    Exclude the endpoint.

    """
    return _grid_nd(ns, inclusive=False)

def grid_nd_inc(*ns): 
    """Make a len(ns) dimensional grid ranging from 0 to 1 with ns[0]
    points in the first dimension, ns[1] points in the second, etc.
    Include the endpoint.

    """
    return _grid_nd(ns, inclusive=True)
    
def _grid_nd(ns, inclusive):
    """Make a len(ns) dimensional grid ranging from 0 to 1 with ns[0]
    points in the first dimension, ns[1] points in the second, etc.

    """
    assert util.every([type(n) is types.IntType for n in ns])
    # 1 number => 3d cube
    # 2 numbers => 2d mesh
    # 3 numbers => 3d non-cube
    if len(ns) == 1: ns = 3*(ns[0],)

    if inclusive: divisor = np.array([n-1 for n in ns], 'f')
    else: divisor = np.array([n for n in ns],'f')
    
    sl = [slice(0,n) for n in ns]
    ax_order = range(1,len(ns)+1) + [0]

    return np.mgrid[sl].transpose(*ax_order) / divisor

def make_grid(*axs):
    """Expand 1d axis values into an N dimensional grid.

    >>> make_grid([1,2], [3,4,5])
    [np.array([[1, 1, 1], [2, 2, 2]]), 
     np.array([[3, 4, 5], [3, 4, 5]])]

    so 

    >>> xs = np.linspace(0,1,7)
    >>> ys = np.linspace(1,2,9)
    >>> X,Y = make_grid(xs, ys)
    >>> X.shape
    (7,9)
    >>> Y.shape
    (7,9)
    >>> Z = np.sin(X)*Y**2

    """

    shape = [len(ax) for ax in axs]
    ntot = reduce(operator.mul, shape)
    ntile = 1
    nrep = ntot
    result = []
    for ax in axs:
        nrep /= len(ax)
        mesh = np.tile(np.repeat(ax,nrep),ntile).reshape(shape)
        ntile *= len(ax)
        result.append(mesh)
    return result

def randp(n, nExp, yl, yh):
    """Random deviates with a power law distribution"""
    # xs = random deviates w/ flat distribution
    # ys = random deviates with power law distribution
    assert nExp != -1
    nMap = 1.0/(nExp+1)
    xlim = [y**(1.0/nMap) for y in yl, yh]
    xl, xh = min(xlim), max(xlim)
    xs = xl + (xh-xl)*np.random.rand(n)
    return xs**nMap

def randlog(n, yl, yh):
    """Random deviates with a logarithmic distribution"""
    xl, xh = [np.log(y) for y in (yl, yh)]
    xs = xl + (xh-xl)*np.random.rand(n)
    return np.exp(xs)

def rebin(a,n=2):
    """Downsample an array.

    For an array a of length N, make a new array of length N/n by
    taking the mean of n adjacent entries of a for each entry of the
    new array.

    >>> rebin([0,0,1,1,2,2], 2)
    np.array([ 0.,  1.,  2.])

    >>> rebin([1,2,1,3,1,11], 2)
    np.array([ 1.5,  2. ,  6. ])

    >>> rebin([0,0,0, 1,2,3, 100,200,300], 3)
    np.array([   0.,    2.,  200.])

    """
    a = np.asarray(a)
    remainder = len(a) % n
    if remainder == 0:
        result = _rebin(a, n)
    else:
        part = _rebin(a[:-remainder], n)
        result = np.zeros(len(part)+1, np.float_)
        result[:-1] = part
        result[-1] = a[-remainder:].sum()/(1.0*remainder)
    return result
        
def _rebin(a,n=2):
    """Internal function for rebin()"""
    assert len(a) % n == 0
    result = np.zeros(len(a)/n, np.float_)    
    for ii in range(n):
        result += a[ii::n]
    return result/(1.0*n)
        
def ave(a, n=1, axis=-1):
    """Do the 2 point average of array a n times

    >>> ave([1,2,10,20], 0)
    np.array([ 1,  2, 10, 20])

    >>> ave([1,2,10,20], 1)
    np.array([  1.5,   6. ,  15. ])

    >>> ave([1,2,10,20], 2)
    np.array([  3.75,  10.5 ])

    >>> ave([1,2,10,20], 3)
    np.array([ 7.125])

    >>> ave([1,2,10,20], 4)
    np.array([], dtype=float64)

    """    
    if n==0: return np.array(a)
    if n < 0: raise ValueError, 'order must be non-negative but got ' + repr(n)
    a = np.asarray(a)
    nd = len(a.shape)
    slice1 = [slice(None)]*nd
    slice2 = [slice(None)]*nd
    slice1[axis] = slice(1, None)
    slice2[axis] = slice(None, -1)
    slice1 = tuple(slice1)
    slice2 = tuple(slice2)
    if n > 1:
        return ave(0.5*(a[slice1]+a[slice2]), n-1, axis=axis)
    else:
        return 0.5*(a[slice1]+a[slice2])

def lave(a, n=1, axis=-1):    
    """Compute ave() in log space (the geometric mean)

    >>> lave([1,2,10,20])
    np.array([  1.41421356,   4.47213595,  14.14213562])

    """
    return np.exp(ave(np.log(a), n=n, axis=axis))
    
def flattenMap(x,y,*maps):
    """Flatten a 2d image.

    x is a 1d array of N points, y is a 1d array of M points, each map
    is a shape (N,M) array of values.

    The output is three (or more, if you specify more than one map to
    flatten) 1d arrays of N*M points giving the x coordinate of each
    pixel, the y coordinate of each pixel, and the value of the pixel
    itself.

    """
    
    x,y = [np.asarray(arg) for arg in (x,y)]
    maps = [np.asarray(arg) for arg in maps]
    
    fx = x.repeat(len(y))
    fy = np.concatenate(len(x)*[y])
    fmaps = [map.ravel() for map in maps]
    return (fx, fy) + tuple(fmaps)

def unflattenMap(fx,fy,*fmaps):
    """The inverse of flattenMap"""
    fx,fy = [np.asarray(arg) for arg in (fx,fy)]
    fmaps = [np.asarray(arg) for arg in fmaps]

    ny = (fx==fx[0]).sum()
    nx = (fy==fy[0]).sum()
    x = fx[::ny] 
    y = fy[:ny]

    result = [] 
    for fmap in fmaps:
        theMap = fmap.copy()
        theMap.shape = (nx,ny)
        result.append(theMap)
        
    return (x, y) + tuple(result)

def findEdges(spec, v):
    """Find appropriate edges for some kind of binning operation.

    spec can be a scalar (for number of bins w/ min,max given by v)
    spec can be a triple for np.linspace(min,max,n+1).  The n+1 is
    because you generally specify the number of bins, not the number
    of edes you want
    or spec can be an array, in which case it's just returned"""
    # TODO -- make this allow for log spacing?
    # NOTE -- make findEdges accept spec=None to get, say, 50 bins?
    # for purposes of defining limits, nix infs and nans
    v = np.asarray(v)
    v = v[good_data(v)]
    if spec is None:
        return np.linspace(v.min(), v.max(), 50)
    if np.isscalar(spec):
        return np.linspace(v.min(), v.max(), spec)
    if type(spec) is types.TupleType:
        if len(spec) == 2:
            return np.linspace(spec[0], spec[1], 50)
        if len(spec) == 3:
            return np.linspace(spec[0], spec[1], spec[2])
    return np.asarray(spec)

def image(v, binInfo, w=None, overflow=1):
    """Construct an image from a set of points.

    The algorithm works when the number of dimensions is 4 or less,
    but the 2d case is described below for concreteness.

    v is an array giving the particle positions

    binInfo is a tuple of (xedges, yedges) giving the division into pixels

    w is an array of weights

    overflow says whether or not to include an overflow bin for pixels
    that fall off the grid.

    """
    if np.iterable(v[0]): v = np.asarray(v)
    else: v = np.array([v])
    if len(v.shape) == 2 and v.shape[0] > v.shape[1]:
        raise RuntimeError, "You likely want the transpose"
    if not np.iterable(binInfo[0]): binInfo = [binInfo]
    nDim = len(binInfo)
    assert nDim <= 4
    xLow, xHigh = [ np.array([float(dim[i]) for dim in binInfo])
                   for i in (0,1)]
    nBin = np.array([int(dim[2]) for dim in binInfo])
    if w is None:
        w=1
        wCode = 'w'
    else:
        w = np.asarray(w)
        wCode = 'w(iPart)'

    dx = (xHigh - xLow)/nBin
    idx = np.zeros(nDim, 'i')
    im = np.zeros(nBin+2, 'f')
    indexNames = ['idx(%d)' % i for i in range(nDim)]
    arrayRef = 'im(%s)' % reduce(lambda x,y: x+','+y, indexNames)    
    code = """
    int iPart, iDim, hasOverflowed;    
    for (iPart=0; iPart < Nv(1); iPart++) {
       hasOverflowed=0;
       for (iDim=0; iDim < nDim; iDim++) {
          idx(iDim) = (v(iDim, iPart) - xLow(iDim)) / dx(iDim) + 1;
          /*  0 = underflow, 1 through n = good, n+1 = overflow */
          if (idx(iDim) < 0) {
             hasOverflowed=1;
             idx(iDim) = 0;
          }
          if (idx(iDim) >= nBin(iDim) + 2) {
             hasOverflowed=1;
             idx(iDim) = nBin(iDim) + 1;
          }
       }
       if (overflow || (!overflow && !hasOverflowed))
          %s += %s;
    }
    """ % (arrayRef, wCode)

    scipy.weave.inline(code, ['v', 'w', 'xLow', 'xHigh', 'nBin',
                              'nDim', 'dx', 'idx', 'im', 'overflow'], 
                       type_converters=scipy.weave.converters.blitz)
    return im

def imagePy1(v, edges, w=None):
    """Construct an image from a set of points in 1d 

    v is an array of vectors 
    edges gives the bin edges
    w is an array of weights

    """
    v = np.asarray(v)    
    xl, xh, nb = float(edges[0]), float(edges[1]), int(edges[2])
    dx = (xh-xl)/nb
    if w is None: w = np.ones(len(v),'i')
    else: w = np.asarray(w)
    # 0 = underflow, 1-n = good, n+1 = overflow
    im = np.zeros(nb+2, w.dtype)
    idx = (v/dx - xl/dx + 1).clip(0,nb+1).astype('i')  # some time    
    for i in xrange(len(v)):   # Most time
        im[idx[i]] += w[i]
    return im

def imagePy2(v, binInfo, w=None):
    """Construct an image from a set of points in 2d

    v is an array giving the particle positions
    binInfo is a tuple of (xedges, yedges) giving the division into pixels
    w is an array of weights

    """
    v = np.asarray(v)
    nDim, nPart = v.shape
    xLow, xHigh = [ np.array([float(dim[i]) for dim in binInfo])
                   for i in (0,1)]
    nBin = np.array([int(dim[2]) for dim in binInfo])
    dx = (xHigh - xLow) / nBin
    if w is None: w = np.ones(nPart, 'i')
    # 0 = underflow, 1-n = good, n+1 = overflow
    im = np.zeros(nBin+2)
    for i in xrange(nPart):   # Most time
        idx = (v[:,i]/dx - xLow/dx + 1).astype('i')
        for iDim in range(nDim):
            idx[iDim] = idx[iDim].clip(0,nBin[iDim]+1)
        im[tuple(idx)] += w[i]
    return im

# Lifted from the numpy mailing list -- uniqe1d that returns the inverse
def unique1d(ar1, return_index=False, return_inverse=False):
    """
    Find the unique elements of an array.

    Parameters
    ----------
    ar1 : array-like
        This array will be flattened if it is not already 1-D.
    return_index : bool, optional
        If True, also return the indices against `ar1` that result in the
        unique array.
    return_inverse : bool, optional
        If True, also return the indices against the unique array that
        result in `ar1`.

    Returns
    -------
    unique : ndarray
        The unique values.
    unique_indices : ndarray, optional
        The indices of the unique values. Only provided if `return_index` is
        True.
    unique_inverse : ndarray, optional
        The indices to reconstruct the original array. Only provided if
        `return_inverse` is True.

    See Also
    --------
      numpy.lib.arraysetops : Module with a number of other functions
                              for performing set operations on arrays.

    Examples
    --------
    >>> np.unique1d([1, 1, 2, 2, 3, 3])
    np.array([1, 2, 3])
    >>> a = np.array([[1, 1], [2, 3]])
    >>> np.unique1d(a)
    np.array([1, 2, 3])

    """
    ar = np.asarray(ar1).flatten()
    if ar.size == 0:
        if return_inverse and return_index:
            return ar, np.empty(0, bool), np.empty(0, bool)
        elif return_inverse or return_index:
            return ar, np.empty(0, bool)
        else:
            return ar

    if return_inverse or return_index:
        perm = ar.argsort()
        aux = ar[perm]
        flag = np.concatenate( ([True], aux[1:] != aux[:-1]) )
        if return_inverse:
            iflag = np.cumsum( flag ) - 1
            iperm = perm.argsort()
            if return_index:
                return aux[flag], perm[flag], iflag[iperm]
            else:
                return aux[flag], iflag[iperm]
        else:
            return aux[flag], perm[flag]

    else:
        ar.sort()
        flag = np.concatenate( ([True], ar[1:] != ar[:-1]) )
        return ar[flag]

# reimplementation of numpy.lib.setmember1d to handle duplicate elements
def setmember1d( ar1, ar2, handle_dupes=True):
    """Reimplementation of numpy.lib.setmember1d to handle duplicate elements

    The docstring of numpy.lib.setmember1d is below (the interface is the same)

    Return a boolean array of shape of ar1 containing True where the elements
    of ar1 are in ar2 and False otherwise.

    If handle_dupes is true, allow for the possibility that ar1 or ar2
    each contain duplicate values.  If you are sure that each array
    contains only unique elelemnts, you can set handle_dupes to False
    for faster execution.
    
    Use unique1d() to generate arrays with only unique elements to use as inputs
    to this function.

    :Parameters:
      - `ar1` : array
      - `ar2` : array
      - `handle_dupes` : boolean
      
    :Returns:
      - `mask` : bool array
        The values ar1[mask] are in ar2.

    :See also:
      numpy.lib.arraysetops has a number of other functions for performing set
      operations on arrays.

    """
    # if np.zeros gets an empty list, it defaults to typecode float,
    # which screws up code below.  Catch empty lists here and do
    # something sensible with them
    ar1, ar2 = np.asarray(ar1), np.asarray(ar2)
    if len(ar1)==0 and len(ar2)==0: return np.array([], ar1.dtype)
    elif len(ar1) == 0: ar1 = np.array([], ar2.dtype)
    elif len(ar2) == 0: ar2 = np.array([], ar1.dtype)
    
    ar = np.concatenate( (ar1, ar2 ) )
    # We need this to be a stable sort, so always use 'mergesort' here. The
    # values from the first array should always come before the values from the
    # second array.    
    order = ar.argsort(kind='mergesort')
    sar = ar[order]        
    equal_adj = (sar[1:] == sar[:-1])
    flag = np.concatenate( (equal_adj, [False] ) )
    
    if handle_dupes:
        # if there is duplication, then being equal to your next
        # higher neighbor in the sorted array equal is not sufficient
        # to establish that your value exists in ar2 -- it may have
        # come from ar1.  A complication is that that this is
        # transitive: setmember1d([2,2], [2]) must recognize _both_
        # 2's in ar1 as appearing in ar2, so neither is it sufficient
        # to test if you're equal to your neighbor and your neighbor
        # came from ar2.  Initially mask is 0 for values from ar1 and
        # 1 for values from ar2.  If an entry is equal to the next
        # higher neighbor and mask is 1 for the higher neighbor, then
        # mask is set to 1 for the lower neighbor also.  At the end,
        # mask is 1 if the value of the entry appears in ar2.
        zlike = np.zeros_like
        mask = np.concatenate( (zlike( ar1 ), zlike( ar2 ) + 1) )
        
        smask = mask[order]
        prev_smask = zlike(smask) - 1
        while not (prev_smask == smask).all():
            prev_smask[:] = smask
            smask[np.where(np.logical_and(equal_adj, smask[1:]))[0]] = 1
        flag *= smask
        
    indx = order.argsort(kind='mergesort')[:len( ar1 )]
    return flag[indx]

def binsToEdges(bins):
    """Given bin centers, make an atttept at calculating edges"""
    edges = ave(bins)
    edges = np.concatenate([[2*edges[0] - edges[1]],
                         edges,
                         [2*edges[-1] + -edges[-2]]])
    return edges

def partition1d(v,edges, w=None, overflow=False, aslist=False):
    """Get list of indices into v that fall into each bin defined by
    edges.  Extra args passed to partition"""        
    if w is None: w = v
    v,w = [np.asarray(arr) for arr in (v,w)]
    edges = findEdges(edges, v)
     
    if len(v) != 0:        
        # bin has size of v and points into edges
        bin = np.digitize(v,edges)
        # Sort an index array and the bin numbers so that they're in order
        # by bin number
        order = bin.argsort()
        w = w[order]
        bin = bin[order]
        # Find where the bin edges fall
        binEdges = np.arange(len(edges)+2)
        binIdx = bin.searchsorted(binEdges)

        result = [ w[l:h] for l,h in azip(binIdx[:-1], binIdx[1:])]
    else:
        # If no data are provided, return len(edges) empty arrays
        # Make sure that they're the correct data type
        result = [ np.array([], dtype=w.dtype) for i in np.arange(len(edges)+1)]

    if not overflow:
        result = result[1:-1]
    if aslist:
        return result

    arr = np.ones(len(result),'O')
    for i in range(len(result)):
        arr[i]=result[i]
    return arr

def argpartition1d(v,edges, **kw):
    """Get list of indices into v that fall into each bin defined by
    edges.  Extra args passed to partition"""
    return partition1d(v,edges,np.arange(len(v)), **kw)

def partition(vs, edgesList, ws=None, overflow=False):
    """Get list the weights ws of particles at positions given by vs that
    fall into each bin defined by edges.

    The algorithm works in an arbitrary number of dimensions.
    
    vs gives the positions and has shape (nDim, nParticle)
    edgesList is [xedges, yedges, ...] 
    ws is an array of weights (if not given, ws = np.ones(n_particles))

    """
    vs = np.asarray(vs)
    if len(vs.shape) == 1:
        vs = np.asarray([vs])
        edgesList = [edgesList]

    edgesList = [findEdges(edges, v) for edges,v in zip(edgesList, vs)]
    rank, nData = vs.shape

    assert rank == len(edgesList)    
    if ws is None: ws = np.arange(np.shape(vs)[1])

    # The plus 2 is to catch outliers
    newShape = [len(edges) + 1 for edges in edgesList]
    nBin = reduce(lambda x,y: x*y, newShape)
    
    # Flattened result matrix
    result = np.zeros(nBin, 'O')

    # get indicies that fall into each bin
    idxs = [np.digitize(v, edges) for v, edges in zip(vs, edgesList)]
    
    # Compute the sample indices in the flattened histogram matrix.
    flatIdx = np.zeros(nData,dtype=np.int32)
    stride = 1
    for idx,dim in zip(idxs, newShape)[::-1]:
        flatIdx += stride*idx
        stride *= dim

    # sort w so that they're in order that they fall into result bins
    order = flatIdx.argsort()
    ws = ws[ order ]
    flatIdx = flatIdx[ order ]

    # Need to find indexes where each bin starts and ends
    # Searchsorted puts something in a bin if low <= value < high
    # If you're paranoid, you can do binEdges = binEdges - 0.5
    # The plus one is to make sure we get all of the data in the
    # slicing below.  If it weren't there, the last slice would be
    # missing    
    binEdges = np.arange(nBin+1)
    binIdx = flatIdx.searchsorted(binEdges)

    for i, l, h in azip(np.arange(nBin), binIdx[:-1], binIdx[1:]):
        result[i] = ws[l:h]
        
    # Shape into a proper matrix
    result = result.reshape(newShape)

    # Remove overflow bins
    if not overflow:
        result = result[ rank*[slice(1,-1)] ]
    return result

def histo_ver1(v,edges,weights=None,overflow=True,normed=False):
    """Make a possibly weighted histogram
    y = data
    b = bin edges
    w = weights (None if unweighted)
    overflow = whether or not to keep overflow bins
    normed = normalized to be a probability distribution

    returns (hist,bins) where hist is the counts
    and bins is the corresponding left bin edge
    """
    v = np.asarray(v)
    edges = findEdges(edges, v)
    binCenters = ave(edges)
                      
    if weights is not None:
        weights = np.asarray(weights)
        idx = v.argsort()            # find indicies that will sort the data
        sv = v[idx] 
        sw = weights[idx]
    else: 
        sv = np.sort(v)
        sw = np.ones(len(v))

    idx = sv.searchsorted(edges)    
    if overflow:
        idx = np.concatenate([[0], idx, [len(v)]])
        dxLow = edges[1]-edges[0]
        dxHigh = edges[-1]-edges[-2]
        binCenters = np.concatenate([[edges[0] - dxLow],
                                  binCenters, [edges[-1] + dxHigh]])

    hist = np.array([ sw[l:h].sum()
                   for l, h in azip(idx[:-1], idx[1:]) ])
    
    if normed:
        db = (edges[-1]-edges[0])/len(binCenters)
        hist = hist/(len(v)*db)

    return hist,binCenters

def histo_ver2(v,edges,weights=None,overflow=True,normed=False, density=False, withBins=True):
    # Use cases:
    # 1) just counts, (overflow or not, will usually want equal sized bins)
    # 2) density (no overflow, nothing to divide by)
    # 3) density and normed to 1 (no overflow)
    
    # FIXME -- test this for unequal bin sizes, etc
    """Make a possibly weighted histogram
    y = data
    b = bin edges
    w = weights (None if unweighted)
    overflow = whether or not to keep overflow bins
    normed = normalized to be a probability distribution

    returns (hist,bins) where hist is the counts
    and bins is the corresponding left bin edge
    """    
    edges = findEdges(edges, v)
    if weights is None: weights = np.ones(len(v))

    # some arg error checking    
    #if not density and (abs(np.diff(edges)/(edges[1]-edges[0]) - 1) > 1e-3).any():
    #    raise ValueError, "Unequal bin sizes means you probably want density, not counts"
    if density and overflow:
        raise ValueError, "There's no good way to make overflow bins into a density"
    if normed and not density:
        raise ValueError, "If you want normalization, you likely also want density"
    
    hist = [ws.sum()
            for ws in partition1d(v, edges, weights, overflow=overflow)]
                      
    if overflow:
        dxLow = edges[1]-edges[0]
        dxHigh = edges[-1]-edges[-2]
        edges = np.concatenate([[edges[0] - dxLow],
                                  edges, [edges[-1] + dxHigh]])
    binCenters = ave(edges)

    if density: hist /= np.diff(edges)
    if normed: hist = hist/ws.sum() # / (hist*np.diff(edges)).sum()

    if withBins: return hist,binCenters
    return hist

def histo(vs, edges, ws=None, normed=False, density=False,
          with_bins=True, silent=False, overflow=True):
    # overflow=True,
    """Make a possibly weighted histogram
    vs = data values
    edges = bin edges
    ws = weights (None if unweighted)
    density => compute density of quantity (divide by bin size)
    normed => should 'integrate' to 1.
    overflow => include overflow bins.  

    Note that the sensible definition of integral changes depending on
    the value of density.  If density is True, then an integrals are
    most sensibly (densities*bin_widths).sum().  If density if False,
    then multiplying by bin widths gives a dimensionally nonsensical
    quantity, so one can only mean the sum: values.sum().  Setting
    normed to True ensures that the relevant quantity is unity.

    Note also that some arg combinations are troublesome:
    density and overflow: have no divisor for the overflow bins
    not density and unequal bins: doesn't have a clear interpretation

    returns (hist,bins) where hist is the counts
    and bins is the corresponding left bin edge
    """    
    edges = findEdges(edges, vs)
    if ws is None: ws = np.ones(len(vs))

    # suspicious arg combination checking
    unequal_bins = (abs(np.diff(edges)/(edges[1]-edges[0]) - 1) > 1e-3).any()
    if not silent and density and overflow:
        print "Warning:numpyUtil.py:histo(): Can't make overflow bins into a density"
    if not silent and unequal_bins and not density:
        print "Warning:numpyUtil.py:histo(): Unuqual bin sizes usually means you want density=True"
    if not silent and normed and not density:
        print "Warning:numpyUtil.py:histo(): Normed usually means you also want density=True"

    hist = np.array([wbin.sum() for wbin in partition1d(vs, edges, ws, overflow=overflow)])

    if overflow:
        dxLow = edges[1]-edges[0]
        dxHigh = edges[-1]-edges[-2]
        edges = np.concatenate([[edges[0] - dxLow],
                                  edges, [edges[-1] + dxHigh]])
        
    if density: hist /= np.diff(edges)
    if normed: hist /= ws.sum()  # (hist*np.diff(edges)).sum()
    
    if with_bins: return hist, ave(edges)
    return hist

##################################################
## Code snarfed from scipy.org
def  histogram2d(x,y, bins, normed = False):
    """Compute the 2D histogram for a dataset (x,y) given the edges or the number of bins.
    Returns histogram, xedges, yedges.
    The histogram array is a count of the number of samples in each bin.
    The array is oriented such that H[i,j] is the number of samples
    falling into binx[j] and biny[i].
    Setting normed to True returns a density rather than a bin count.
    Data falling outside of the edges are not counted.    

    Credit: 
    David Huard, June 2006
    Adapted for python from the matlab function hist2d written by
    Laszlo Balkay, 2006.  Numpy compatible license.
    """
    if len(bins)==2:
        if np.isscalar(bins[0]):
            xnbin = bins[0]
            xedges = np.linspace(x.min(), x.max(), xnbin+1)           
        else:
            xedges = bins[0]
            xnbin = len(xedges)-1       
        if np.isscalar(bins[1]):
            ynbin = bins[1]
            yedges = np.linspace(y.min(), y.max(), ynbin+1)
        else:
            yedges = bins[1]
            ynbin = len(yedges)-1
    else:
        raise AttributeError, 'bins must be a sequence of length 2, with either the number of bins or the bin edges.'
          
    # Flattened histogram matrix (1D)
    hist = np.zeros((xnbin)*(ynbin), int)

    # Count the number of sample in each bin (1D)
    xbin = np.digitize(x,xedges)
    ybin = np.digitize(y,yedges)
 
    # Remove the outliers
    outliers = (xbin==0) | (xbin==xnbin+1) | (ybin==0) | (ybin == ynbin+1)

    xbin = xbin[outliers==False]
    ybin = ybin[outliers == False]
   
    # Compute the sample indices in the flattened histogram matrix.
    if xnbin >= ynbin:
        xy = ybin*(xnbin) + xbin
        shift = xnbin
    else:
        xy = xbin*(ynbin) + ybin
        shift = ynbin
       
    # Compute the number of repetitions in xy and assign it to the
    # flattened histogram matrix.
    edges = np.unique(xy)
    edges.sort()
    flatcount = np.histogram(xy, edges)[0]
    indices = edges - shift - 1
    hist[indices] = flatcount

    # Shape into a proper matrix
    histmat = hist.reshape(xnbin, ynbin)
   
    if normed:
        diff2 = outer(np.diff(yedges), diff(xedges))
        histmat = histmat / diff2 / histmat.sum()
    return histmat, xedges, yedges
   
##################################################
## Code not in current use
##################################################

def partition1d_ver1(v, edges, w=None, overflow=False, aslist=False):
    """Return list of arrays of values in w based on where values in v
    fall into bins defined by edges.  By default, w=v.  If you want the
    indicies falling into each bin, use partition(v,edges,range(len(v)))."""

    if w is None: w = v    

    v,w = [np.asarray(arr) for arr in (v,w)]
    edges = findEdges(edges, v)
     
    order = v.argsort()
    edge_index = v[order].searchsorted(edges)

    lst =  [ w[ order[h:l] ]
            for h,l in azip(edge_index[:-1], edge_index[1:])]

    if overflow:
        under = w[ order[:edge_index[0]] ]
        over = w[ order[edge_index[-1]:] ]
        lst = [under] + lst + [over]

    if aslist: return lst
    
    # Convert to pyarray object
    arr = np.ones(len(lst),'O')
    for i in range(len(lst)):
        arr[i]=lst[i]
    return arr
    
def partition2d_ver1(v1, edges1, v2, edges2, w=None, **kw):
    """Return elements of w based on where v1,v2 fall in bin edges
    edge1, edge2.  To just get indicies into v1 and v2, leave w
    unspecified.  Extra args passed to partition"""
    assert len(v1) == len(v2)
     
    if w is None: w = np.arange(len(v1))
    v1, v2, edges1, edges2, w = [np.asarray(arr)
                               for arr in (v1, v2, edges1, edges2, w)]
    edges1 = findEdges(edges1, v1)
    edges2 = findEdges(edges2, v2)

    v1_lists = argpartition1d(v1, edges1, **kw)    
    lsts = [partition( v2[ v1_list ] , edges2 , w[ v1_list], **kw )
            for v1_list in v1_lists]

    if 'aslist' in kw and kw['aslist']: return lsts
    
    # Convert to array
    Nx, Ny = (len(lsts), len(lsts[0]))
    arr = np.reshape(np.zeros(Nx*Ny,'O'), (Nx,Ny))

    for i in range(Nx):
        for j in range(Ny):
            # not sure why, but it's important to have [i][j], not [i,j]
            arr[i][j] = lsts[i][j]
    return arr

def partition_ver1(vs, edgesList, ws=None, **kw):
    """Return elements of w based on where v1,v2 fall in bin edges
    edge1, edge2.  To just get indicies into v1 and v2, leave w
    unspecified.  Extra args passed to partition"""
    vs = np.asarray(vs)
    if len(vs.shape) == 1:
        vs = np.asarray([vs])
        edgesList = [edgesList]
        
    edgesList = [findEdges(edges, v) for edges,v in zip(edgesList, vs)]
    assert vs.shape[0] == len(edgesList)
    if ws is None: ws = np.arange(shape(vs)[1])

    if vs.shape[0] == 1:
        return partition1d(vs[0], edgesList[0], ws, **kw)

    slices = argpartition1d(vs[0], edgesList[0], **kw)
    # Here's a nice implementation of below, but it fails when a bin is empty
    #     result =  [ partitionNd(vs[1:,slice], edgesList[1:], ws[slice], **kw)
    #                 for slice in slices]
    result = []
    for slice in slices:
        if len(slice) != 0:
            entry = partition_ver1(vs[1:,slice], edgesList[1:], ws[slice], **kw)
            result.append(entry)
        else:
            # Doing this for now to get the dimensionality right
            dummyV = np.array([]).reshape(vs.shape[0]-1, 0)
            dummyW = np.array([], dtype=ws.dtype)
            entry = partition_ver1(dummyV, edgesList[1:], dummyW, **kw)
            result.append(entry)

    if 'aslist' in kw and kw['aslist']: return result
    newshape = (len(result),) + result[0].shape
    aresult = np.ones(newshape, 'O')
    for i in range(len(result)):
        aresult[i] = result[i]
    return aresult

##################################################
## Rickety Code
##################################################

##############################
## Bit matricies and boolean matricies
def bitToDtype(nBit):
    """Given number of bits, give numpy type"""
    if nBit==  8: return   np.uint8
    if nBit== 16: return  np.uint16
    if nBit== 32: return  np.uint32
    if nBit== 64: return  np.uint64
    if nBit==128: return np.uint128    

def bitarr(v, nBit=32):
    """make a bit array out of a boolean array"""
    # convert boolean matrix to a bit matrix, looping over bit numbers 
    if not type(v) is np.ndarray:
        v = np.asarray(v, dtype='bool')
    assert v.dtype == bool
    # Pad so that number of bits comes out even
    if len(v) % nBit != 0:
        v = np.concatenate((v, (nBit - (len(v) % nBit)) * [False]))
    result = np.zeros(int(np.ceil(len(v)/float(nBit))), dtype=bitToDtype(nBit))
    for i in range(nBit):
        result += v[i::nBit] * (1 << i)
    return result

def boolarr(v, size=None):
    """make a boolean array out of a bit array"""
    # convert bit matrix to a boolean matrix
    v = np.asarray(v)
    bitsPerByte = 8
    nBit = v.itemsize * bitsPerByte
    result = np.zeros(nBit*len(v), dtype=bool)

    for i in range(nBit):
        result[i::nBit] = v & (1 << i)

    if size is None: size=nBit*len(v)
    return result[:size]
        
def bitmat(mat, nBit=32):
    """Make a bit matrix out of a boolean matrix"""
    return np.array([bitarr(v, nBit=nBit) for v in mat])

def boolmat(mat, size=None):
    """Make a boolean matrix out of a bit matrix"""
    return np.array([boolarr(v, size=size) for v in mat])

##############################
## Coordinate systems
def spherical(x,y,z):
    """Convert positions and velocities to spherical coordinates.
    return R, theta, phi, v_r, v_theta, v_phi"""
    x,y,z = [np.asarray(a) for a in (x,y,z)]
    R = np.sqrt(x**2+y**2+z**2)
    theta = np.arctan2(np.sqrt(x**2+y**2), z)
    phi = np.arctan2(y, x)

    return R, theta, phi

def cartesian(r,theta,phi):
    """Convert positions and velocities to spherical coordinates.
    return R, theta, phi, v_r, v_theta, v_phi"""
    x = r*np.cos(phi)*np.sin(theta)
    y = r*np.sin(phi)*np.sin(theta)
    z = r*np.cos(theta)
    return x,y,z

def rms(a,**kw):    
    """Compute root mean square of a."""
    a=np.asarray(a)
    return np.sqrt(a.std(**kw)**2 + a.mean(**kw)**2)

def clipOdd(*aas):
    """Get rid of infs and nans.

    Keep entries of each argument where the value of _all_ of the
    arguments is a finite number.

    >>> x = np.array([1,2,3,4])
    >>> y = np.array([1,nan,3,4])
    >>> z = np.array([1,2,inf,4])
    >>> x,y,z = clipOdd(x,y,z)
    >>> x,y,z 
    (np.array([1,4]), 
     np.array([1,4]), 
     np.array([1,4]))    

    """
    keep = reduce(np.logical_and, [np.isfinite(a) for a in aas])
    return [np.asarray(a)[keep] for a in aas]

def graham_schmidt(vs, verbose=False):
    """Graham Schmidt orthonomalization of basis vectors."""
    # generate a set of orthonormal basis vectors given a partial set
    def dot(v,w): return (v*w).sum()
    def norm(v): return np.sqrt(dot(v,v))
    def normalize(v): return v/norm(v)
    def any(seq): return reduce(lambda x,y: x or y, seq)
    def all_orthogonal(ws):
        result = True
        for ii in range(len(ws)):
            for jj in range(ii+1,len(ws)):
                if dot(ws[ii],ws[jj]) > 1e-5:
                    result = False
        return result

    def gs_rec(ws):
        if verbose: print ws
        nw = len(ws)
        if nw == nd: return ws
        # Note -- algorithm fails if new vector is spanned by old vectors.
        vnew = normalize(np.random.rand(nd))
        
        for ww in ws:
            vnew = vnew - ww*dot(vnew, ww)
        return gs_rec(ws + [normalize(vnew)])

    nd = len(vs[0])
    id = [0]
    vs = [normalize(np.asarray(v)) for v in vs]
    if not all_orthogonal(vs): raise ValueError 

    return gs_rec(vs)

def graham_schmidt_guess_3d(vs, gs, verbose=False):
    """Graham Schmidt orthonomalization of basis vectors."""
    # generate a set of orthonormal basis vectors given a partial set
    def dot(v,w): return (v*w).sum()
    def norm(v): return np.sqrt(dot(v,v))
    def normalize(v): return v/norm(v)
    def any(seq): return reduce(lambda x,y: x or y, seq)
    def curl(a,b):
        return np.array([a[1]*b[2] - a[2]*b[1], 
                      a[2]*b[0] - a[0]*b[2], 
                      a[0]*b[1] - a[1]*b[0]])
    def spanned(vv,ws):
        if len(ws) == 0: return False
        elif len(ws) == 1:
            if abs(dot(vv, ws[0])) < 1e-2: return True
        elif len(ws) == 2:
            if abs(dot(vv, curl(ws[0], ws[1]))) < 1e-2: return True
        elif len(ws) == 3:
            return True
        else: raise ValueError            
            
    def all_orthogonal(ws):
        result = True
        for ii in range(len(ws)):
            for jj in range(ii+1,len(ws)):
                if dot(ws[ii],ws[jj]) > 1e-5:
                    result = False
        return result

    def gs_rec(ws, gs):
        if len(ws) == nd: return ws
        
        vnew = normalize(gs[0])
        gs = gs[1:]
        
        if verbose: print "Trying",  vnew
        while spanned(vnew, ws):
            vnew = normalize(gs[0])
            gs = gs[1:]
            if verbose: print "Didn't work, trying ", vnew

        for ww in ws:
            vnew = vnew - ww*dot(vnew, ww)
        return gs_rec(ws + [normalize(vnew)], gs)

    nd = len(gs)
    id = [0]
    vs = [normalize(np.asarray(v)) for v in vs]
    gs = [normalize(np.asarray(g)) for g in gs]
    # Use 3d cross product above, ensure that I'm working in 3d.
    assert util.every([len(v)==3 for v in vs])
    assert util.every([len(g)==3 for g in gs])
    if not all_orthogonal(vs): raise ValueError 
    if not all_orthogonal(gs): raise ValueError 

    return gs_rec(vs, gs)

##################################################
## Binary I/O

# class LazyArray(object):
#     # Only makes sense with large, out of memory arrays, right?
#     def __init__(self, *a):
#         self.a = array(*a)
        
#     def __add__(self, y):
#         return itertools.imap(operator.add, self, y)
        
#     def __mul__(self): pass
#         return itertools.imap(operator.mul, self, y)
    
#     def __getitem__(self,i):
#         return a[i]


def big_array(shape, dtype, cut=None):        
    """Make a big (disk-based) array"""    
    # Funny expression is to handle case where cut == 0 (ie, False)
    # otherwise could use cut = cut or big_array_default_cut
    if not cut and cut is None: cut = big_array_default_cut
    
    nitems = reduce(operator.mul, shape)
    size = nitems*np.array([], type).itemsize
    if size > cut:
        return BigArray(None, dtype=dtype, shape=shape)
    else:
        return np.empty(shape, dtype)
    
def generated_array(ar):
    """Make an array with Python generators."""    
    for i in range(len(ar)):
        yield ar[i]
        
# class GeneratedArray(object):
#     def __init__(self, gen):
#         self.g = gen

#     def __mul__(self, yy):
#         for x,y in itertools.izip(self.g, yy):
#             yield x*y

#     def __div__(self, yy):
#         for x,y in itertools.izip(self.g, yy):
#             yield x*y

class BigArray(object):
    """A big (disk-based) array that doesn't fit in memory.  

    Today you would probably compile things 64 bit an memmap your
    array, but I got some mileage out of this on 32 bit
    machines...

    """    
    # Want to do something with generators to handle operations?  But
    # need it to be closed over multiplication...

    # Want to implment in-mem arrays as using generators... to use for
    # testing, or so that code works for either in-mem or out-of-mem
    # arrays.

    # Or, just compile 64 bit and mem map everything....
    
    # Thoughts: This works, but slicing and assigning to slices is not
    # transparent.  Perhaps it can't be.  If it _were_ going to be
    # transparent, it then __getitem__ would need to return not a
    # numpy array, but a wrapper around an array that intercepts calls
    # to __setitem__ and writes back to the original BigArray.

    # This is not a completely transparent replacement for arrays.  In
    # particular v[1,2,3] generates a disk read of an entire block to
    # return the one element.  Looping over things in this way is
    # harmful.  Could fix this by implementing just a "last one read"
    # cache.
    
    __version = 1
    _header_type = np.int32
    _header_type = np.int32
    _pad_type = np.int32

    # the _types array is used to identify the data type of files on
    # disk.  You can change the ordering, but that will make arrays
    # currently on disk unintellible, so you should never change the
    # ordering.  None is the zeroth element so that arrays with this
    # type code are easily recognized as erroneous.  The other Nones
    # are there to leave spaces for data types that theoretically
    # could exist, but do not presently exist.  That's because you
    # should never change the order to insert them, so we leave space.
    _types = [None, np.int8,   np.uint8,   None,        None,
                    np.int16,  np.uint16,  None,        None,
                    np.int32,  np.uint32,  np.float32,  None, 
                    np.int64,  np.uint64,  np.float64,  np.complex64,
                    None,      None,       np.float128, np.complex128, 
                    None,      None,       None,        np.complex256]

    # Use cases:
    # 'r', existing file read-only
    # 'r+w', existing file read/write
    # 'w', new file read/write

    def __init__(self, f, shape=None, dtype=None,
                 read_only=False, endian=None):
        self.read_only = read_only
        
        if dtype is None and shape is None: new_file = False
        elif dtype is None or shape is None: raise AssertionError
        else: new_file = True
        
        # If the file is opened for reading, no choice about endianness
        if not new_file: assert endian is None
        if read_only: assert not new_file
        
        if type(f) in types.StringTypes:
            if read_only:  self.f = open(f, mode='r')
            elif new_file: self.f = open(f, mode='w+')
            else: self.f = open(f, mode='r+')
        elif f is None:
            self.f = tempfile.TemporaryFile()
            assert new_file
        else:
            self.f = f
        
        if new_file: 
            self.open_new(dtype, shape, endian)
        else: 
            self.open_existing()
                    
    def unpack_header(self, header):
        # Byte swapping already handled.
        self.version = header[1]
        if self.version != self.__version: raise RuntimeError
        self.dtype = self._types[header[2]]
        self.shape = tuple(header[3:])

    def pack_header(self):
        header = np.zeros(3 + len(self.shape), self._header_type)        
        header[0] = 1
        header[1] = self.__version
        header[2] = self._types.index(self.dtype)
        header[3:] = self.shape
        return header

    def open_existing(self):
        self.swap = self.swap_p()

        self.f.seek(0)        
        header = read_fortran(self.f, self._header_type, swap=self.swap)
        self.header_pos = self.f.tell()
        self.unpack_header(header)

    def swap_p(self):
        self.f.seek(0)
        if scipy_has_fwrite:
            scipy.io.fread(self.f, 1, self._pad_type)
            byte_order = scipy.io.fread(self.f, 1, self._header_type)[0]
        else:
            np.fromfile(self.f, self._pad_type, 1)  # skip first pad
            byte_order = np.fromfile(self.f, self._header_type, 1)

        if byte_order == 0x00000001: return False
        elif byte_order == 0x01000000: return True
        else: raise RuntimeError
        
    def open_new(self, dtype, shape, endian_):
        assert dtype is not None and shape is not None
        # Want this to be the numpy type object, so create a small
        # array and fetch the type object from it.
        self.dtype = np.array([], dtype).dtype
        self.shape = tuple(shape)
        self.swap = endian(endian_)
        
        header = self.pack_header()
        write_fortran(self.f, header, swap=self.swap)
        self.header_pos = self.f.tell()
        self.write_pads()

    def write_pads(self):
        block = self.block_size()
        pad = np.array([self.data_size()], self._pad_type)
        pad_size = np.array([], self._pad_type).itemsize
        swapped_pad = pad.byteswap()

        for i in range(len(self)):
            for pos in (self.header_pos + i*block,
                        self.header_pos + (i+1)*block - pad_size):                
                self.f.seek(pos)
                if scipy_has_fwrite:                    
                    scipy.io.fwrite(self.f, 1, pad, self._pad_type, self.swap)
                elif self.swap:
                    swapped_pad.tofile(self.f)
                else:
                    pad.tofile(self.f)
                    
    def close(self):
        self.f.close()

    def data_size(self):
        el_size = np.array([], self.dtype).itemsize
        nitems = reduce(lambda x,y: x*y, self.shape[1:])
        return el_size*nitems

    def block_size(self):
        pad_size = np.array([], self._pad_type).itemsize
        return 2*pad_size + self.data_size()
    
    def get_slice(self, sl):
        for idx in range(*sl.indices(len(self))):
            yield self[idx]
        
    def set_slice(self, sl, vals):
        for idx, val in itertools.izip(range(*sl.indices(len(self))),
                                       vals):
            self[idx] = val
                
    def __getitem__(self, i):
        # For multi-D arrays, split off the first index
        if type(i) is types.TupleType: return self[i[0]][i[1:]]
        # For slices, return an iterator over the values
        if type(i) is type(slice(0)): return self.get_slice(i)

        # Default case: read a block and return it
        if i < 0: i = len(self) + i
        if i < 0 or i >= len(self): raise IndexError 

        block = self.block_size()
        self.f.seek(self.header_pos + i*block)
        dat = read_fortran(self.f, self.dtype, swap=self.swap)
        return dat.reshape(self.shape[1:])

    def __setitem__(self, i, val):
        # For multi-D arrays, split off the first index
        if type(i) is types.TupleType:
            #self[i[0]][i[1:]] = val
            #return
            raise NotImplementedError
        # For slices, iterate over them one by one
        if type(i) is type(slice(0)):
            self.set_slice(i, val)
            return
            
        if not np.iterable(val): val = np.zeros(self.shape[1:], self.dtype) + val
        assert val.shape == self.shape[1:]
        if self.read_only: raise RuntimeError
        if i < 0: i = len(self) + i
        if i < 0 or i >= len(self): raise IndexError 
        block = self.block_size()
        self.f.seek(self.header_pos + i*block)
        write_fortran(self.f, val.astype(self.dtype), swap=self.swap)

    def __len__(self):
        return self.shape[0]    
    
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

def big_transpose(u,buf_size=None,cut=None, verbose=False):
    """Transpose a BigArray"""
    buf_size = buf_size or 1e8

    if type(u) is np.ndarray:
        return u.transpose(*[1,0] + range(2,len(u.shape)))

    itemsize = np.array([],u.dtype).itemsize
    new_shape = (u.shape[1],u.shape[0]) + u.shape[2:]
    slice_size = itemsize*reduce(operator.mul, new_shape[1:])
    assert 2*slice_size < buf_size
    slices_per_pass = int(buf_size/slice_size)
    n_passes = u.shape[1]/slices_per_pass
    if verbose: print n_passes, "passes"
    idxs = range(0,u.shape[1],slices_per_pass) + [u.shape[1]]
    result = big_array(new_shape, u.dtype, cut=cut)
    
    buf = np.zeros((u.shape[0],slices_per_pass) + u.shape[2:], u.dtype)

    sl = (len(u)-1)*(slice(None),)
    for il, ih in zip(idxs[:-1],idxs[1:]):
        # Pull data into the buffer
        for iin in range(len(u)):            
            buf[iin][:ih-il] = u[iin][il:ih]

        buft = buf.transpose([1,0]+range(2,len(u.shape)))

        # write it back out
        for iout,ibuf in zip(range(il,ih),
                             range(slices_per_pass)):
            result[iout] = buft[ibuf]
    return result

def big_fftn(u, **kw): 
    """FFT a BigArray"""
    return big_transform(u, np.fft.fft, **kw)
def big_ifftn(u, **kw): 
    """FFT a BigArray"""
    return big_transform(u, np.fft.ifft, **kw)
def big_fstn(u, **kw): 
    """FFT a BigArray"""
    return big_transform(u, fst, **kw)
def big_ifstn(u, **kw): 
    """FFT a BigArray"""
    return big_transform(u, ifst, **kw)
def big_fctn(u, **kw): 
    """FFT a BigArray"""
    return big_transform(u, fct, **kw)
def big_ifctn(u, **kw): 
    """FFT a BigArray"""
    return big_transform(u, ifct, **kw)

def big_transform(u, fft, buf_size=None, cut=None):
    """FFT a BigArray"""
    #assert util.every([el == 2**int(log2(el)) for el in u.shape])

    # Figure out type returned by fft function
    test = np.zeros(2,u.dtype)
    the_type = fft(test).dtype.char
    
    temp1 = big_array(u.shape, the_type, cut=cut)
    # Loop over x slices doing transform along all axes except first
    # NOTE -- can do this in-place in u?
    for isl in range(len(u)):
        sl = u[isl]
        for idim in range(len(u.shape)-1):
            sl = fft(sl, axis=idim)
        temp1[isl] = sl

    # need to get all of the x data in at once, so transpose first two axes
    temp2 = big_transpose(temp1,buf_size=buf_size, cut=cut)

    # Do fft's in the x direction (now axis 1 of big array, axis 0 of slices)
    # NOTE -- don't actually need temp3, can do this in-place
    temp3 = big_array(temp2.shape,the_type, cut=cut)
    assert u.shape[1] == temp3.shape[0]   # just to make sure I haven't confused myself
    for isl in range(len(temp3)):
        temp3[isl] = fft(temp2[isl], axis=0)
    
    # Finally transpose back.  Can gain a factor of 2 by skipping this
    # step and letting the inverse transform do the second transpose
    result = big_transpose(temp3,buf_size=buf_size, cut=cut)
    return result
    
def endian(end):    
    """Make a decision about byteswapping

    Given desired endiannness and endianness of present machine,
    decide whether or not byte swapping is necessary.

    argument end can be: 
    None: Definitely don't byteswap
    'native': make result the native byteorder of this machine
    'big': make result bigendian
    'little': make result littlendian
    'swap': definitely byteswap
    """
    assert end in [None, 'native', 'big', 'little', 'swap']
    if end == 'big' and np.little_endian: swap = True
    elif end == 'little' and not np.little_endian: swap = True
    elif end == 'swap': swap = True
    else: swap = False

    return swap

def write_fortran(f, arr, swap=False, pad_type=np.int32):
    """Write a fortran unformatted binary block"""
    # not sure where this numpy version should happen
    if scipy_has_fwrite:
        scipy.io.fwrite(f, 1, np.array([arr.nbytes]), pad_type, swap)
        scipy.io.fwrite(f, arr.size, arr, arr.dtype.char, swap)
        scipy.io.fwrite(f, 1, np.array([arr.nbytes]), pad_type, swap)
    else:
        pad_array = np.array([arr.nbytes]).astype(pad_type)
        
        if swap: 
            pad_array = pad_array.byteswap()
            arr = arr.byteswap()

        pad_array.tofile(f)
        arr.tofile(f) 
        pad_array.tofile(f)
        
def read_fortran(f, type_=np.float32, num=None, swap=False, pad_type=np.int32):
    """Read one unformatted fortran record.
    num = number of data to read.  If None, compute it from the pad word
    swap = whether or not to byte swap
    intType = specifies width of pad words on the computer where the
      files were written."""

    if scipy_has_fwrite:
        pad = scipy.io.fread(f, 1, pad_type, pad_type, swap)
    else: 
        pad = np.fromfile(f, pad_type, 1)
        if swap: pad = pad.byteswap()

    if len(pad) != 1: raise EOFError

    c1 = pad[0]
    if num is None: num = c1/np.array([0], type_).itemsize

    if scipy_has_fwrite:
        dat = scipy.io.fread(f, num, type_, type_, swap)
    else:
        dat = np.fromfile(f, type_, num)
        if swap: dat = dat.byteswap()

    if scipy_has_fwrite:
        c2 = scipy.io.fread(f, 1, pad_type, pad_type, swap)[0]
    else:
        pad2 = np.fromfile(f, pad_type, 1)
        if swap: pad2 = pad2.byteswap()
        c2 = pad2[0]

    assert c1 == c2 == dat.nbytes
    return dat

def read_fortran_inplace(f, type_=np.float32, num=None,
                         swap=False, pad_type=np.int32,
                         dest=None, shape=None, order='C'):
    # I wrote this because I thought it would be faster in certain
    # situations to stuff the data into a destination array inside
    # this function.  However, it turns out I can derive all of the
    # benefit by moving the dest[:] = blah line outside of this
    # function.  Hence, opt for the simpler read_fortran.  However,
    # keep this around in case I _do_ find that I need it.  If so,
    # this function is a drop-in replacement for read_fortran.
    """Read one unformatted fortran record.
    num = number of data to read.  If None, compute it from the pad word
    swap = whether or not to byte swap
    intType = specifies width of pad words on the computer where the
      files were written."""

    if scipy_has_fwrite:
        c1 = scipy.io.fread(f, 1, pad_type, pad_type, swap)[0]
    else:
        pad1 = np.fromfile(f, pad_type, 1)
        if swap: pad1 = pad1.byteswap()
        c1 = pad1[0]

    if num is None: num = c1/np.array([0], type_).itemsize

    if scipy_has_fwrite:
        dat = scipy.io.fread(f, num, type_, type_, swap)
    else:
        dat = np.fromfile(f, type_, num)
        if swap: dat = dat.byteswap()

    if dest is not None:
        if shape is None: shape = (-1,)
        dest[:] = dat.reshape(shape, order=order)
        
    if scipy_has_fwrite:
        c2 = scipy.io.fread(f, 1, pad_type, pad_type, swap)[0]
    else:
        pad2 = np.fromfile(f, pad_type, 1)
        if swap: pad2 = pad2.byteswap()
        c2 = pad2[0]

    if not c1 == c2 == dat.nbytes: raise RuntimeError
    if dest is None: return dat

def skip_fortran(f, n=1, swap=False, pad_type=np.int32):
    """Skip one unformatted fortran record.
    intType = specifies width of pad words on the computer where the
      files were written."""
    for i in range(n):
        if scipy_has_fwrite:
            c1 = scipy.io.fread(f, 1, pad_type)[0]
        else:
            pad2 = np.fromfile(f, pad_type, 1)
            if swap: pad2 = pad2.byteswap()
            c1 = pad2[0]
            
        p1 = f.tell()
        f.seek(c1, 1)
        p2 = f.tell()

        if scipy_has_fwrite:            
            c2 = scipy.io.fread(f, 1, pad_type)[0]
        else:
            pad2 = np.fromfile(f, pad_type, 1)
            if swap: pad2 = pad2.byteswap()
            c2 = pad2[0]

        assert c1 == c2 == p2-p1

# Goal: Have something that produces a read function given a spec.

# Considerations:
# 1) Large data (ability to generate pages
# 2) Endianness (would like to feed a function that serves as a test,
#    restarting reading if necessary
# 3) File version (would again like to be able to detect which file
#    version I'm presented with and act accordingly
# 4) Fortan unformatted io?  Sometimes it's many things w/ one name,
#    Sometimes a few things with different names.  This matters for
#    fortran unformatted b/c you need to read them all at once.
# 5) What is the return format? A dict?  A container?  It's own object?
# 6) Siebel's thing expands into its own object.  You provide code at
#    specific points

# Strategy
# 1) Closure?
# 2) Inheritance?

def binaryReader(specs, swapp=None, postf=None, pad_type=np.int32):
    """Make a function that reads binary files according to specs

    Each field spec of specs can be:
    (type, num, name) means read an array num long of type type.
    (type, names...) means read a scalar for each name of type type.
    (type, True, num, name) means read a fortran unformatted record
    (type, True, names...) means read the whole thing as an unformatted
      fortran record and then split into one scalar for each name.

    """
    # The way of specifying fortran records is kind of dumb...
    def read(f):
        closeFile = False
        if type(f) in types.StringTypes:            
            f = open(f)
            closeFile = True

        # Check to see if I should byte swap
        pos = f.tell()
        swap = False
        if swapp and swapp(f): swap = True
        f.seek(pos)

        # Start collecting results
        result = {}
        for s in specs:
            if type(s[1]) is types.BooleanType and type(s[2]) is types.IntType:
                typ, junk, num, name = s
                result[name] = read_fortran(f, typ, num, swap, pad_type=pad_type)
                
            elif type(s[1]) is types.BooleanType:
                typ, junk, names = s[0], s[1], s[2:]
                tmp = read_fortran(f, typ, len(names), swap, pad_type=pad_type)
                for name, val in zip(names, tmp):
                    result[name] = val

            elif type(s[1]) is types.IntType:
                typ, num, name = s
                if scipy_has_fwrite:
                    result[name] = scipy.io.fread(f, num, typ, typ, swap)
                else:
                    tmp_arr = np.fromfile(f, typ, num)
                    if swap: tmp_arr = tmp_arr.byteswap()
                    result[name] = tmp_arr

            else:
                typ, names = s[0], s[1:]
                if scipy_has_fwrite:
                    tmp = scipy.io.fread(f, len(names), typ, typ, swap)
                else:
                    tmp = np.fromfile(f, typ, len(names))
                    if swap: tmp = tmp.byteswap()

                for name, val in zip(names, tmp):
                    result[name] = val                                    

        result = util.Container(**result)

        # A hook for error checking.
        if postf: postf(result)
        return result

    # do some basic error checking on specs
    assert type(specs) is types.TupleType
    assert util.every([type(el) is types.TupleType for el in specs])
    return read

# NOTE spec is officially optional, but code breaks if not given
def readAllFortran(f, spec=None, swap=False, warning=False, pad_type=np.int32):
    """Read all fortran data from a file.  spec is a list of types of each block"""
# What are the use cases?
# 1) read all blocks using one type
# 2) read a succession of blocks of different type, specifying types as a list
#
#     """Read all data, specifying the types and number or elements, or
#     just the types (taking number of elements from the file, or
#     nothing, in which case everything is read as bytes"""
    closeFile = False
    if type(f) in types.StringTypes:
        closeFile = True
        f = open(f)
        
    if len(spec) > 1:
        result = [read_fortran(f, s, None, swap=swap, pad_type=pad_type)
                  for s in spec]
    else:
        result = []
        while not f.read(1) != '':
            f.seek(-1,1)
            dat = read_fortran(f, spec, None, swap=swap, pad_type=pad_type)
            result.append(dat)
        
    if closeFile:
        # Check to make sure that everything was read
        if f.read() != '':
            if warning: print "Warning, there's more to be read."
            else: raise RuntimeError
        f.close()

    return result

def changes(ar):
    "Find indicies in an array where a[i] != a[i+1]"
    ar = np.asarray(ar)
    return np.nonzero(ar[1:]-ar[:-1])

def blocks(ar):
    "Find blocks of sequential nmbers in an array."
    ar = np.array(ar, copy=1)
    ar.sort()    
    iEdges = np.nonzero(ar[1:]-ar[:-1]-1)

    mins = [ar[0]] + list(ar[iEdges[0]+1])
    maxs = list(ar[iEdges]) + [ar[-1]]
    return zip(mins,maxs)

##################################################
## Vector calculus
def grad_faces(phi, dx=1.0):
    """Gives each component of field on cell faces"""
    s0, sm, sp = slice(None), slice(None,-1), slice(1,None)
    return ((phi[sp, s0, s0] - phi[sm, s0, s0])/dx,
            (phi[s0, sp, s0] - phi[s0, sm, s0])/dx,
            (phi[s0, s0, sp] - phi[s0, s0, sm])/dx)

def grad_centers(phi, dx=1.0):
    """Gives grad at cell centers"""
    s0, sm, sp = slice(1,-1), slice(None,-2), slice(2,None)
    shape = [el-2 for el in phi.shape] + [3]
    result = np.empty(shape, dtype=phi.dtype)
    result[...,0] = (phi[sp, s0, s0] - phi[sm, s0, s0])/dx
    result[...,1] = (phi[s0, sp, s0] - phi[s0, sm, s0])/dx
    result[...,2] = (phi[s0, s0, sp] - phi[s0, s0, sm])/dx
    return result

def grad_edges(phi, dx=1.0):
    """Gives grad at cell edges"""
    sm, sp = slice(None,-1), slice(1,None)
    shape = [el-1 for el in phi.shape] + [3]
    result = np.empty(shape, dtype=phi.dtype)
    phixm = 0.25*(phi[sm, sm, sm] + phi[sm, sp, sm] + phi[sm, sm, sp] + phi[sm, sp, sp])
    phixp = 0.25*(phi[sp, sm, sm] + phi[sp, sp, sm] + phi[sp, sm, sp] + phi[sp, sp, sp])

    phiym = 0.25*(phi[sm, sm, sm] + phi[sp, sm, sm] + phi[sm, sm, sp] + phi[sp, sm, sp])
    phiyp = 0.25*(phi[sm, sp, sm] + phi[sp, sp, sm] + phi[sm, sp, sp] + phi[sp, sp, sp])

    phizm = 0.25*(phi[sm, sm, sm] + phi[sp, sm, sm] + phi[sm, sp, sm] + phi[sp, sp, sm])
    phizp = 0.25*(phi[sm, sm, sp] + phi[sp, sm, sp] + phi[sm, sp, sp] + phi[sp, sp, sp])

    result[...,0] = (phixp - phixm)/dx
    result[...,1] = (phiyp - phiym)/dx
    result[...,2] = (phizp - phizm)/dx
    return result

def laplacian1(vv, dx=1.0):
    """Laplacian in 1d"""
    sm, s0, sp = slice(None,-2), slice(1,-1), slice(2,None)
    return (vv[sp] + vv[sm] - 2*vv[s0])/dx**2

def laplacian2(vv, dx=1.0):
    """Laplacian in 2d"""
    sm, s0, sp = slice(None,-2), slice(1,-1), slice(2,None)
    return (vv[s0,sp] + vv[s0,sm] +
            vv[sp,s0] + vv[sm,s0] - 4*vv[s0,s0])/dx**2

def laplacian3_slow(vv, dx=1.0):
    """Laplacian in 3d"""
    sm, s0, sp = slice(None,-2), slice(1,-1), slice(2,None)
    return (vv[sp,s0,s0] + vv[sm,s0,s0] +
            vv[s0,sp,s0] + vv[s0,sm,s0] +
            vv[s0,s0,sp] + vv[s0,s0,sm] - 6*vv[s0,s0,s0])/dx**2

def laplacian3(vv, dx=1.0):
    """Laplacian in 3d"""
    sm, s0, sp = slice(None,-2), slice(1,-1), slice(2,None)
    result = np.zeros((vv.shape[0]-2, vv.shape[1]-2, vv.shape[2]-2))
    expr = """result[:] =  (vv[2:,1:-1,1:-1] + vv[:-2,1:-1,1:-1] + vv[1:-1,2:,1:-1] + vv[1:-1,:-2,1:-1] + vv[1:-1,1:-1,2:] + vv[1:-1,1:-1,:-2] - 6*vv[1:-1,1:-1,1:-1])/(dx*dx)"""
    scipy.weave.blitz(expr,check_size=0)
    return result

def laplacian(vv, dx=1.0):
    """Laplacian in 1,2, or 3 dimensions"""
    if len(vv.shape) == 1: return laplacian1(vv,dx)
    if len(vv.shape) == 2: return laplacian2(vv,dx)
    if len(vv.shape) == 3: return laplacian3(vv,dx)

def div2d_rtp(vr, vth, R, TH):
    """2D divergence in spherical coordinates"""
    def rav(vv): return 0.5*(vv[1:, :] + vv[:-1, :])
    def tav(vv): return 0.5*(vv[:, 1:] + vv[:, :-1])
    def rdif(vv): return vv[1:, :] - vv[:-1, :]
    def tdif(vv): return vv[:, 1:] - vv[:, :-1]

    rterm = tav(rav(1/R**2)*rav(R**2*vr)/rdif(R))
    tterm = rav(tav(1/(R*np.sin(TH)))*tav(vth*np.sin(TH))/tdif(TH))
    return rterm + tterm

def div(vv, dx=1.0):
    """Assumes components of vectors are all at cell centers and gives
    divergence at the corners"""
    sm, sp = slice(None,-1), slice(1,None)

    vxm = 0.25*(vv[sm,sm,sm,0] + vv[sm,sp,sm,0] + vv[sm,sm,sp,0] + vv[sm,sp,sp,0])
    vxp = 0.25*(vv[sp,sm,sm,0] + vv[sp,sp,sm,0] + vv[sp,sm,sp,0] + vv[sp,sp,sp,0])

    vym = 0.25*(vv[sm,sm,sm,1] + vv[sm,sm,sp,1] + vv[sp,sm,sm,1] + vv[sp,sm,sp,1])
    vyp = 0.25*(vv[sm,sp,sm,1] + vv[sm,sp,sp,1] + vv[sp,sp,sm,1] + vv[sp,sp,sp,1])

    vzm = 0.25*(vv[sm,sm,sm,2] + vv[sm,sp,sm,2] + vv[sp,sm,sm,2] + vv[sp,sp,sm,2])
    vzm = 0.25*(vv[sm,sm,sp,2] + vv[sm,sp,sp,2] + vv[sp,sm,sp,2] + vv[sp,sp,sp,2])

    return (vxp-vxm)/dx + (vyp-vym)/dx + (vyp-vym)/dx 

def curl(vv, dx=1.0):
    """Assumes all vector components defined at the same place and
    gives curl at corners of implied grid"""

    s0, sm, sp = slice(None), slice(None,-1), slice(1,None)
    dy = dz = dx

    # X component
    vzm = 0.5*(vv[s0, sm, sm,2] + vv[s0, sm, sp,2])
    vzp = 0.5*(vv[s0, sp, sm,2] + vv[s0, sp, sp,2])
    vym = 0.5*(vv[s0, sp, sm,1] + vv[s0, sm, sm,1])
    vyp = 0.5*(vv[s0, sp, sp,1] + vv[s0, sm, sp,1])
    cx = (vzp - vzm)/dy - (vyp - vym)/dz
    
    # Y component
    vxm = 0.5*(vv[sm, s0, sm,0] + vv[sp, s0, sm,0])
    vxp = 0.5*(vv[sm, s0, sp,0] + vv[sp, s0, sp,0])
    vzm = 0.5*(vv[sm, s0, sm,2] + vv[sm, s0, sp,2])
    vzp = 0.5*(vv[sp, s0, sm,2] + vv[sp, s0, sp,2])
    cy = (vxp - vxm)/dy - (vzp - vzm)/dz

    # Z component
    vxm = 0.5*(vv[sm, sm, s0,0] + vv[sp, sm, s0,0])
    vxp = 0.5*(vv[sm, sp, s0,0] + vv[sp, sp, s0,0])
    vym = 0.5*(vv[sm, sm, s0,1] + vv[sm, sp, s0,1])
    vyp = 0.5*(vv[sp, sm, s0,1] + vv[sp, sp, s0,1])
    cz = (vyp - vym)/dy - (vxp - vxm)/dz

    # Average to get all at cell centers
    shape = [el-1 for el in vv.shape[:-1]] + [3]
    result = np.empty(shape, dtype=vv.dtype)
    result[...,0] = 0.5*(cx[sm, s0, s0] + cx[sp, s0, s0])
    result[...,1] = 0.5*(cy[s0, sm, s0] + cy[s0, sp, s0])
    result[...,2] = 0.5*(cz[s0, s0, sm] + cz[s0, s0, sp])
    return result
    
def curl_(vv, dx=1.0):
    """Curl of a cartesian vector field"""
    # NOTE -- this requires an unsatisfying choice to align arrays in
    # the different dimensions.  Could average, could do face centered values...
    # FIXME -- will probably need to attend to this to get real div B = 0 for code
    return ((vv[:, 1:, :, 2] - vv[:, :-1, :, 2])[:, :, :-1]/dx
            - (vv[:, :, 1:, 1] - vv[:, :, :-1, 1])[:, :-1, :]/dx,
            (vv[:, :, 1:, 0] - vv[:, :, :-1, 0])[:-1, :, :]/dx
            - (vv[1:, :, :, 2] - vv[:-1, :, :, 2])[:, :, :-1]/dx,
            (vv[1:, :, :, 1] - vv[:-1, :, :, 1])[:, :-1, :]/dx
            - (vv[:, 1:, :, 0] - vv[:, :-1, :, 0])[:-1, :, :]/dx)

def curl__(vv, dx=1.0):
    # NOTE -- this requires an unsatisfying choice to align arrays in
    # the different dimensions.  Could average, could do face centered values...
    # FIXME -- will probably need to attend to this to get real div B = 0 for code
    ww = np.empty((vv.shape[0]-1, vv.shape[1]-1, vv.shape[2]-1, 3))
    wx, wy, wz = curl_(vv)    
    ww[..., 0] = wx[:-1, :, :]
    ww[..., 1] = wy[:, :-1, :]
    ww[..., 2] = wz[:, :, :-1]
    return ww

##################################################
## Fast spherical harmonics
def lpSimple(n,x):
    """Compute Legendre polynomial n for many x values.
    Uses recurrence relation from wikipedia"""
    assert n >= 0
    x = np.asarray(x)
    if n==0: return np.ones(x.shape, x.dtype)
    if n==1: return x        
    return (2*n-1)*x*lpSimple(n-1,x)/n - (n-1)*lpSimple(n-2,x)/n

def lp(theN,x):
    """Compute Legendre polynomial n for many x values.
    Uses recurrence relation from wikipedia"""
    assert theN >= 0
    x = np.asarray(x)
    def __lp(n):
        assert n >= 0
        if n==0: return np.ones(x.shape, x.dtype)
        if n==1: return x                
        return (2*n-1)*x*_lp(n-1)/n - (n-1)*_lp(n-2)/n
    
    _lp = util.memoize(__lp, with_file=False)
    return _lp(theN)
    
def alpSimple(l,m,x, fixEdges=True):
    "Associated legendre polynomial for use with sperical harmonic"
    assert abs(m) <= l
    fac = np.math.factorial
    scalar = False
    if not np.iterable(x):
        scalar = True
        x = [x] 
    x=np.asarray(x)
    if m == 0: return lp(l, x)
    if m < 0: return (-1)**(-m) * fac(l+m) * alpSimple(l,-m,x) / fac(l-m)
    result = (  (l-m+1) * x * alpSimple(l, m-1, x)
              - (l+m-1) *     alpSimple(l-1, m-1, x)) / np.sqrt(1-x**2)

    # The 1/np.sqrt(1-x**2) factor gives trouble when x is near +- 1, so
    # recompute those values with a linear interpolation.  This is
    # protected by the if statement to avoid infinite recursion.
    eps = 0.001
    if fixEdges and np.logical_or(x > 1-eps, x < -1+eps).any():
        print "Fixing edges", (x >  1-eps).sum()
        vHigh = alpSimple(l,m, 1-eps, fixEdges=False)
        vLow  = alpSimple(l,m,-1+eps, fixEdges=False)
        fHigh = scipy.interpolate.interp1d([ 1-eps, 1], [vHigh, 0])
        fLow  = scipy.interpolate.interp1d([-1,-1+eps], [0, vLow])

        result[x > 1-eps] =  fHigh(x[x > 1-eps])
        result[x < -1+eps] =  fLow(x[x < -1+eps])
    if scalar:
        return result[0]
    return result
        
def alp(theL,theM,x,fixEdges=True):
    "Associated legendre polynomial for use with sperical harmonic"
    assert abs(theM) <= theL
    fac = np.math.factorial
    scalar = False
    if not np.iterable(x): 
        scalar = True
        x = [x]    
    x = np.asarray(x)
    
    def __lp(n):
        if n==0: return np.ones(x.shape, x.dtype)
        if n==1: return x
        return (2*n-1)*x*_lp(n-1)/n - (n-1)*_lp(n-2)/n

    def __alp(l,m):
        """Slow version of associated legendre polynomials."""
        if m == 0: return _lp(l)
        if m < 0:  return (-1)**(-m) * fac(l+m) * _alp(l,-m) / fac(l-m)
        return ((l-m+1) * x * _alp(l, m-1) - (l+m-1) * _alp(l-1, m-1)) \
               / np.sqrt(1-x**2)
     
    _lp = util.memoize(__lp, with_file=False)
    _alp = util.memoize(__alp, with_file=False)

    result = _alp(theL, theM)

    if fixEdges and theM != 0:
        # The 1/np.sqrt(1-x**2) factor gives trouble when x is near +- 1,
        # so recompute those values with a linear interpolation
        eps = 0.001
        low, high  =  x < -1+eps,  x > 1-eps
        if low.any() or high.any():
            # print "Fixing edges", low.sum() + high.sum()
            result[low] = alp(theL,theM,-1+eps) * (1+x[low]) / eps
            result[high] = alp(theL,theM, 1-eps) * (1-x[high]) / eps

    if scalar:
        return result[0]
    return result
    
def y(l,m,theta,phi):
    """Complex valued spherical harmonic ylm.

    There are many different conventions concerning the labeling of
    l,m and theta, phi.  This implementation uses the "physics"
    convention.  

    In terms of quantum mechanics, l refers to the angular momentum
    and m to the z component of the angular momentum, so m <= l.
    Theta is the angle from the z axis and phi is the azimuthal angle.

    In order to catch inadvertent errors, the phi is allowed to take
    any value (wrapping periodically into the interval from 0 to 2
    pi), but theta outside the range 0 to pi will raise an
    exception.

    """

    theta, phi = [np.asarray(arr) for arr in (theta, phi)]
    assert not (theta > np.pi).any()
    fac = np.math.factorial
    norm = np.sqrt((2*l+1)*fac(l-m)/(fac(l+m)*4*np.pi))
    return norm * alp(l,m, np.cos(theta)) * np.exp(1j*m*phi)

def ry(l,m,theta,phi):
    """Real valued spherical harmonic ylm.

    There are many different conventions concerning the labeling of
    l,m and theta, phi.  This implementation uses the "physics"
    convention.  

    In terms of quantum mechanics, l refers to the angular momentum
    and m to the z component of the angular momentum, so m <= l.
    Theta is the angle from the z axis and phi is the azimuthal angle.

    In order to catch inadvertent errors, the phi is allowed to take
    any value (wrapping periodically into the interval from 0 to 2
    pi), but theta outside the range 0 to pi will raise an
    exception.

    """
    theta, phi = [np.asarray(arr) for arr in (theta, phi)]
    assert not (theta > np.pi).any()
    
    # This is guaranteed to be real, but 0*1j results in numpy making
    # the type complex.  So explicitly make it real
    if m==0: return y(l,m,theta,phi).real

    fac = np.math.factorial
    posm = abs(m)
    norm = np.sqrt((2*l+1)*fac(l-posm)/(fac(l+posm)*4*np.pi))    
    if m > 0: trig = np.cos(m*phi)
    else: trig = np.sin(posm*phi)

    return np.sqrt(2) * norm * alp(l,posm,np.cos(theta)) * trig

##################################################
# Transforms, poisson solver
def sine_transform(u,fft,sign,axis):
    """Fourier sin transform"""
    def get(l,h,dn=1):
        result = len(u.shape)*[slice(None)]
        result[axis] = slice(l,h,dn)
        return result
    
    N=u.shape[axis]
    new_shape = list(u.shape)
    new_shape[axis] = 2*N-2
    v = np.zeros(new_shape, u.dtype)

    v[get(None,N)] = u
    v[get(N,None)] = - u[get(1,-1)][get(None,None,-1)]
    return sign*fft(v,axis=axis).imag[get(None,N)]

def cosine_transform(u,fft,axis):
    """Fourier cos transform"""
    def get(l,h,dn=1):        
        result = len(u.shape)*[slice(None)]
        result[axis] = slice(l,h,dn)
        return result
    
    N=u.shape[axis]
    new_shape = list(u.shape)
    new_shape[axis] = 2*N-2
    v = np.zeros(new_shape, u.dtype)

    v[get(None,N)] = u
    v[get(N,None)] = u[get(1,-1)][get(None,None,-1)]

    return fft(v,axis=axis).real[get(None,N)]
    
def fst(u,axis=-1):  
    "Fourier sin transform"
    return sine_transform(u,np.fft.fft, -1,axis)

def ifst(u,axis=-1): 
    "Fourier sin transform"
    return sine_transform(u,np.fft.ifft, 1,axis)

def fct(u,axis=-1):  
    "Fourier cos transform"
    return cosine_transform(u,np.fft.fft,axis)

def ifct(u,axis=-1): 
    "Fourier cos transform"
    return cosine_transform(u,np.fft.ifft,axis)

def transform_n(u,fft):
    "N dimensional transform"
    for i in range(len(u.shape)):
        u = fft(u, axis=i)
    return u

def fstn(u):  
    "Fourier sin transform in n dimensions"
    return transform_n(u, fst)

def ifstn(u): 
    "Fourier sin transform in n dimensions"
    return transform_n(u, ifst)

def fctn(u):      
    "Fourier cos transform in n dimensions"
    return transform_n(u, fct)

def ifctn(u): 
    "Fourier cos transform in n dimensions"
    return transform_n(u, ifct)

def trig_freq(n, l):
    "Frequencies for sin/cos transforms"
    return np.arange(n)/(2.0*l)

def poisson(rho, fft, ifft, freq, ls=None):
    "Solve Poisson equation using fourier transforms"
    #assert util.every([el % 2 == 0 for el in rho.shape])    
    if ls is None: ls=np.ones(len(rho.shape),np.float_)

    # make a grid of frequencies
    k_vects = [2*np.pi*freq(rho.shape[i],ls[i]) for i in range(len(rho.shape))]
    k_grids = make_grid(*k_vects)
    k2s = np.zeros_like(rho)
    for kg in k_grids:
        k2s += kg**2
    
    rhobar = fft(rho)
    phibar = -rhobar/k2s
    phibar[len(rho.shape)*(0,)] = 0
    phi = ifft(phibar)
    assert abs(phi.imag).max() < 1e-5
    return phi

def big_poisson(rho, fft, ifft, freq, ls=None):
    "Solve Poisson equation using BigArray and fourier transforms"
    if ls is None: ls=np.ones(len(rho.shape),np.float_)

    # make a grid of frequencies
    kxs = 2*np.pi*freq(rho.shape[0], ls[0])
    kyz_vects = [2*np.pi*freq(rho.shape[i],ls[i]) for i in range(1,len(rho.shape))]
    kyz_grids = make_grid(*kyz_vects)
    kyz2 = np.zeros(rho.shape[1:], rho.dtype)
    for kg in kyz_grids:
        kyz2 += kg**2
    
    rhobar = fft(rho)
    phibar = big_array(rhobar.shape, rhobar.dtype)
    for i in range(len(rhobar)):
        phibar[i] = -rhobar[i]/(kyz2 + kxs[i]**2)

    sl = phibar[0]
    sl.flat[0] = 0
    phibar[0] = sl

    phi = ifft(phibar)
    for i in range(len(phi)):
        assert abs(phi[i].imag).max() < 1e-5        
    return phi

def poisson_fft(rho, ls=None):
    "Solve Poisson equation using fourier transforms"
    result = poisson(rho, np.fft.fftn, np.fft.ifftn, np.fft.fftfreq, ls=ls)
    return result.real

def poisson_fst(rho, ls=None):
    "Solve Poisson equation using fourier sin transforms"
    return poisson(rho, fstn, ifstn, trig_freq, ls=ls)

def poisson_fct(rho, ls=None):
    "Solve Poisson equation using fourier cos transforms"
    return poisson(rho, fctn, ifctn, trig_freq, ls=ls)

def big_poisson_fft(rho, ls=None):
    "Solve Poisson equation using BigArray and fourier transforms"
    result = big_poisson(rho, big_fftn, big_ifftn, np.fft.fftfreq, ls=ls)
    return result.real

def big_poisson_fst(rho, ls=None):
    "Solve Poisson equation using BigArray and fourier sin transforms"
    return big_poisson(rho, big_fstn, big_ifstn, trig_freq, ls=ls)

def big_poisson_fct(rho, ls=None):
    "Solve Poisson equation using BigArray and fourier cos transforms"
    return big_poisson(rho, big_fctn, big_ifctn, trig_freq, ls=ls)

##################################################
## Fits, etc
def degenerate_gaussian_fit(vs):
    """Approximate mean and std dev for small numbers of points."""
    if len(vs)==0: return (0,0)
    elif len(vs)==1: return (vs[0],0)
    elif len(vs)==2: return (0.5*(vs[0]+vs[1]),abs(vs[0]-vs[1]))
    else: raise ValueError
        
def gaussian_ml_fit(vs, ws=None):
    """Fit a gaussian using max likelihood

    Note, weightes are NOT USED... they're there so this has the
    same calling convention as other fits."""
    # using max liklihood
    vs = np.asarray(vs)
    def f((mean, sig)):
        return 0.5*((vs-mean)**2).sum()/sig**2 + N*np.log(sig)

    if len(vs) <= 2: return degenerate_gaussian_fit(vs)
    N = len(vs)
    p0 = (vs.mean(), vs.std())
    # for small numbers of particles sigma can go negative since it
    # only appears squared
    mean, sig = scipy.optimize.fmin_cg(f, p0)
    return mean, abs(sig)

def gaussian_bin_fit(vs, ws=None):
    """Fit a gaussian by binning and fitting to the histogram"""
    # Ws are weights
    def f((norm, mean, sig)):
        return ys - norm*np.exp(-0.5*(xs-mean)**2/sig**2)/np.sqrt(2*np.pi*sig**2)

    vs = np.asarray(vs)
    if len(vs) <= 2: return degenerate_gaussian_fit(vs)    
    if ws is None: ws = np.ones(len(vs))
    else: ws = np.asarray(ws)
    mean,sig = weighted_mean(vs,ws), weighted_std(vs,ws)
    
    if len(vs) > 100: bins = np.linspace(mean-5*sig, mean+5*sig, 100)
    else: bins = np.linspace(mean-2*sig, mean+2*sig, 2*len(vs))
    
    ys, xs = histo(vs, bins, ws, overflow=False, normed=True, density=True)
    p0 = (1/np.sqrt(2*np.pi*sig**2), mean, sig)
    result = scipy.optimize.leastsq(f, p0)
    mean, sig = result[0][1], result[0][2]
    # for small numbers of particles sigma can go negative since it
    # only appears squared
    return mean, abs(sig)

def bootstrap(f, xs, N=10, *args, **kw):
    """Do a bootstrap estimate of the error in the value computed by
    the function f.  f takes a list of data values and returns a
    number.  xs is the entire data set.  Returns a tuple containing
    first the value of f applied to the whole data set (ie, the
    central value) and then the standard deviation about the mean of f
    applied to random subsamples of xs, drawn with replacement.  N
    gives the number of times f is called to produce the standard
    deviatiuon.  Any extra arguments are passed on to f."""    
    xs = np.asarray(xs)
    if len(xs.ravel()) == 0: return 0, 0 # No information to be had
    value = f(xs, *args, **kw)
    n = len(xs)
    err = np.std(np.array([ f(np.take(xs, (n*np.random.rand(n)).astype('i')), *args, **kw)
                         for i in range(N) ]))
    return value, err


def interp2d(xx, yy, vv, extrapolate=False):
    """Can't understand scipy's interp2d function, write my own.  The
    situation may have improved in the many years since I've written
    this.

    """
    def interp_func(xp, yp): 
        xp, yp = np.asarray(xp), np.asarray(yp)
        if extrapolate=='clip':
            # Allow xp, yp outside range but clip to range
            xp = xp.clip(xx[0], xx[-1])
            yp = yp.clip(yy[0], yy[-1])
        elif extrapolate:
            pass
        else:
            # ar.searchsorted(val) gives 0 for val <= ar[0].
            # val==ar[0] is valid, but val<ar[0] is not, so detect the
            # error based on xp rather than the results of
            # searchsorted.
            if ((xp<xx[0]) | (xp>xx[-1]) | (yp<yy[0]) | (yp>yy[-1])).any():
                raise ValueError
        ih = xx.searchsorted(xp)
        jh = yy.searchsorted(yp)
        if extrapolate=='clip':
            pass
        elif extrapolate:
            # Ensure that the reference points fall on the grid
            # Ugh, there must be a better way to write this that works
            # for scalars and arrays.
            if np.iterable(jh): 
                jh[jh==0] = 1
                jh[jh==len(yy)] = len(yy)-1
            else: 
                if jh == 0:
                    jh = 1
                if jh == len(yy):
                    jh = len(yy)-1
            if np.iterable(ih): 
                ih[ih==0] = 1
                ih[ih==len(xx)] = len(xx)-1
            else: 
                if ih == 0:
                    ih = 1
                if ih == len(xx):
                    ih = len(xx)-1
        else:
            pass
        il, jl = ih-1, jh-1
        # Ensure float division
        X = (xp-xx[il])/(1.0*(xx[ih]-xx[il]))
        Y = (yp-yy[jl])/(1.0*(yy[jh]-yy[jl]))
        result = (  vv[ih, jh]*X*    Y + vv[il, jh]*(1-X)*    Y
                  + vv[ih, jl]*X*(1-Y) + vv[il, jl]*(1-X)*(1-Y))
        return result
    xx,yy,vv = [np.asarray(arr) for arr in xx,yy,vv]

    return interp_func

def power_spectrum(freq, ft):
    """Convert the fourier transform coefficients into a power spectrum"""
    nn = len(ft)
    def cmag(zz):
        return np.sqrt(zz*zz.conj()).real
    if nn % 2 == 0:
        const = ft[0]                    
        pos = ft[1:nn/2]
        neg = ft[nn/2+1:][::-1]
        sing = ft[nn/2]
        result = np.zeros(len(pos) + 2)
        result[0] = cmag(const)
        result[1:-1] = cmag(pos) + cmag(neg)
        result[-1] = cmag(sing)
        xs = abs(freq[:nn/2+1])
    else:
        const = ft[0]                    
        pos = ft[1:(nn-1)/2+1]
        neg = ft[(nn-1)/2+1:][::-1]
        result = np.zeros(len(pos) + 1)
        result[0] = cmag(const)
        result[1:] = cmag(pos) + cmag(neg)
        xs = freq[0:(nn-1)/2+1]
    return xs, result

def seq_transitions(vv, thr):
    """Given time series data, and a threshold, find transitions."""
    vv = np.asarray(vv)
    return (((vv[:-1] <= thr) & (vv[1:] > thr)) | 
            ((vv[:-1] >= thr) & (vv[1:] < thr)))

def seq_transitions_idx(vv, thr):
    """Given time series data, and a threshold, find index of transitions."""
    idx = np.arange(len(vv)+1)
    tr = seq_transitions(vv, thr)
    tr = np.concatenate(([1], tr, [1])).astype('bool')
    return idx[tr]

def seq_length(vv, thr):
    """Given time series data, and a threshold, find time between transitions"""
    return np.diff(seq_transitions_idx(vv,thr))

def seq_length_above(vv, thr):
    """Find distribution of times above threshold"""
    vv = np.asarray(vv)
    idx = seq_transitions_idx(vv, thr)
    start_idx = idx[:-1]
    seq_above_p = (vv[start_idx] > thr)
    return np.diff(idx)[seq_above_p]
    
def seq_length_below(vv, thr):
    """Find distribution of times below threshold"""
    vv = np.asarray(vv)
    return seq_length_above(-vv,-thr)


######################################################################
#
# From: http://www-personal.umich.edu/~mejn/computational-physics/dcst.py
# 
# Functions to perform fast discrete cosine and sine transforms and
# their inverses in one and two dimensions.  These functions work
# by wrapping the DFT function from numpy, rather than explicitly
# performing the cosine and sine transforms themselves.
#
#   dct(y): Type-II discrete cosine transform (DCT) of real data y
#   idct(a): Type-II inverse DCT of a
#   dct2(y): 2D DCT of 2D real array y
#   idct2(a): 2D inverse DCT real array a
#   dst(y): Type-I discrete sine transform (DST) of real data y
#   idst(a): Type-I inverse DST of a
#   dst2(y): 2D DST of 2D real array y
#   idst2(a): 2D inverse DST real array a
#
# Written by Mark Newman <mejn@umich.edu>, June 24, 2011
# You may use, share, or modify this file freely
#
######################################################################

# def make_dct(transf=np.fft.fft, itransf=np.fft.ifft, real_spectrum=False):

#     def dct(y):
#         "1D DCT Type-II"
#         N = len(y)
#         y2 = np.empty(2*N, y.dtype)
#         y2[:N] = y[:]
#         y2[N:] = y[::-1]

#         c = transf(y2)
#         phi = np.exp(-1j*np.pi*np.arange(N)/(2*N))

#         result = phi*c[:N]

#         if real_spectrum:
#             return real(result)
#         return result

#     def idct(a):
#         "1D inverse DCT Type-II"
#         N = len(a)
#         c = np.empty(N+1,complex)

#         phi = np.exp(1j*np.pi*np.arange(N)/(2*N))
#         c[:N] = phi*a
#         c[N] = 0.0
#         return itransf(c)[:N]

#     return dct, idct

# def make_dst(transf=np.fft.fft, itransf=np.fft.ifft, real_spectrum=False):
#     def dst(y):
#         "1D DST Type-I"
#         N = len(y)
#         y2 = np.empty(2*(N+1),y.dtype)
#         y2[0] = y2[N+1] = 0.0
#         y2[1:N+1] = y[:]
#         y2[N+2:] = -y[::-1]

#         result = transf(y2)[1:N+1]
#         if real_spectrum: 
#             return -np.imag(result)
#         return result

#     def idst(a):
#         "1D inverse DST Type-I"
#         N = len(a)
#         c = np.empty(N+2,complex)
#         c[0] = c[N+1] = 0.0

#         if real_spectrum: 
#             c[1:N+1] = -1j*a

#         return itransf(c)[1:N+1]

#     return dst, idst

# def dstfreq(aa):
#     N=len(aa)
#     return np.fft.fftfreq(2*N)[:N]

# def dctfreq(aa):
#     N=len(aa)
#     return np.fft.fftfreq(2*(N+1))[:N]

# def make_2dtf(transf):
#     def dt2d(y):
#         M = y.shape[0]
#         N = y.shape[1]
#         a = np.empty([M,N],float)
#         b = np.empty([M,N],float)

#         for i in range(M):
#             a[i,:] = transf(y[i,:])
#         for j in range(N):
#             b[:,j] = transf(a[:,j])

#         return b

# # for real valued functions
# rdst, irdst = make_dst(transf=np.fft.rfft, itransf=fft.irfft, real_spectrum=True)
# rdct, irdct = make_dct(transf=np.fft.rfft, itransf=fft.irfft, real_spectrum=True)

# # for complex valued functions
# #dst doesn't work
# dst, idst = make_dst(transf=np.fft.fft, itransf=fft.ifft, real_spectrum=False)
# # doubles freq
# dct, idct = make_dct(transf=np.fft.fft, itransf=fft.ifft, real_spectrum=False)

# # 2D transforms

# rdst2d = make_2dtf(transf=rdst)
# irdst2d = make_2dtf(transf=irdst)
# rdct2d = make_2dtf(transf=rdct)
# irdct2d = make_2dtf(transf=irdct)

# dst2d = make_2dtf(transf=dst)
# idst2d = make_2dtf(transf=idst)
# dct2d = make_2dtf(transf=dct)
# idct2d = make_2dtf(transf=idct)

######################################################################
# End part written by 
# Written by Mark Newman <mejn@umich.edu>, June 24, 2011
######################################################################

######################################################################
# Code based on above code written by Mark Newman
######################################################################

def extend_even_given(y):
    """Extend function to produce even periodic function"""
    y = np.asarray(y)
    N = len(y)
    y2 = np.empty(2*N, y.dtype)
    y2[:N] = y[:]
    y2[N:] = y[::-1]
    return y2

def extend_even(y):
    """Extend function to produce even periodic function"""
    y = np.asarray(y)
    N = len(y)
    y2 = np.empty(2*N-1, y.dtype)
    y2[:N] = y[:]
    y2[N:] = y[1:][::-1]
    return y2

def extend_odd(y):
    """Extend function to produce odd periodic function"""
    y = np.asarray(y)
    N = len(y)
    y = np.asarray(y)
    y2 = np.empty(2*(N+1),y.dtype)
    y2[0] = y2[N+1] = 0.0
    y2[1:N+1] = y[:]
    y2[N+2:] = -y[::-1]
    return y2

def rdct(y):
    """Real discrete cosine transform"""
    N = len(y)
    c = np.fft.rfft(extend_even_given(y))
    phi = np.exp(-1j*np.pi*np.arange(N)/(2*N))
    return np.real(phi*c[:N])

def irdct(a):
    """Inverse real discrete cosine transform"""
    N = len(a)
    c = np.empty(N+1,complex)
    phi = np.exp(1j*np.pi*np.arange(N)/(2*N))
    c[:N] = phi*a
    c[N] = 0.0
    return np.fft.irfft(c)[:N]

def rdst(y):
    """Real discrete sine transform"""
    # Shouldn't include the endpoints which are by defn zero
    N = len(y)
    result = np.fft.rfft(extend_odd(y))[1:N+1]
    return -np.imag(result)

def irdst(a):
    """Inverse real discrete sine transform"""
    a = np.asarray(a)
    N = len(a)
    c = np.empty(N+2,complex)
    c[0] = c[N+1] = 0.0
    c[1:N+1] = -1j*a
    return np.fft.irfft(c)[1:N+1]

########
def dct(y):
    "Discrete Cosine Transform"    
    N = len(y)
    c = np.fft.fft(extend_even_given(y))
    return c[:N]

def idct(a):
    "Inverse Discrete Cosine Transform"    
    N = len(a)
    c = np.empty(2*N-1,complex)
    c[:N] = a
    c[N:] = a[1:][::-1]
    return np.fft.ifft(c)[:N]

def dst(y):
    "Discrete Sine Transform"    
    # Shouldn't include the endpoints which are by defn zero
    N = len(y)
    result = np.fft.fft(extend_odd(y))[1:N+1]
    return result

def idst(a):
    "Inverse Discrete Sine Transform"    
    a = np.asarray(a)
    N = len(a)
    c = np.empty(2*(N+1),complex)
    c[0] = c[N+1] = 0.0
    c[1:N+1] = a
    c[N+2:] = -a[::-1]
    return np.fft.ifft(c)[1:N+1]

########
def rdstfreq(aa):
    """Real discrete sin transform frequencies"""
    N=len(aa)
    return np.fft.fftfreq(2*N)[:N]

def rdctfreq(aa):
    """Real discrete cosine transform frequencies"""
    N=len(aa)
    return np.fft.fftfreq(2*(N+1))[:N]

def make_2dtf(transf):
    """2D discrete sin/cos transform"""
    def dt2d(y):
        y = np.asarray(y)
        M = y.shape[0]
        N = y.shape[1]
        a = np.empty([M,N],float)
        b = np.empty([M,N],float)

        for i in range(M):
            a[i,:] = transf(y[i,:])
        for j in range(N):
            b[:,j] = transf(a[:,j])

        return b
    return dt2d

# # for real valued functions
# rdst, irdst = make_dst(transf=np.fft.rfft, itransf=fft.irfft, real_spectrum=True)
# rdct, irdct = make_dct(transf=np.fft.rfft, itransf=fft.irfft, real_spectrum=True)

# # for complex valued functions
# #dst doesn't work
# dst, idst = make_dst(transf=np.fft.fft, itransf=fft.ifft, real_spectrum=False)
# # doubles freq
# dct, idct = make_dct(transf=np.fft.fft, itransf=fft.ifft, real_spectrum=False)

# 2D transforms

rdst2d = make_2dtf(transf=rdst)
irdst2d = make_2dtf(transf=irdst)
rdct2d = make_2dtf(transf=rdct)
irdct2d = make_2dtf(transf=irdct)

dst2d = make_2dtf(transf=dst)
idst2d = make_2dtf(transf=idst)
dct2d = make_2dtf(transf=dct)
idct2d = make_2dtf(transf=idct)

######################################################################
# End code based on above code written by Mark Newman
######################################################################
