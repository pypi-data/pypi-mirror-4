# The positions (or velocity, or whatever) of a set of particles are
# defined by an array of shape (n_particles, n_dimensions).  If an
# array has rank one, then it is assumed to refer to a single vector.

import sys, operator, time

import numpy as np
import scipy, scipy.interpolate, numpy
import gsn_util as util

import gsn_numpy_util as nu

# PyX is an optional dependency
try:
    import pyx
    have_pyx = True
except ImportError:
    have_pyx = False
    #pyx = extensions.extensions_pyx.pyx

# sersic module is an optional dependency
# Don't complain if sersic module not found.
try: 
    import sersic as sersic_module
except ImportError:    
    pass

# Reasonable defaults for min/max radius for Sersic profile fits.
RMIN, RMAX = 0.1, 500

# Commonly used angle definitions
#
# These refer to _ACTIVE_ Euler transforms. They give you a viewing
# direction, moving the z axis from its current position to the new
# position.  The middle angle is the inclination, but the position
# angle is set by the other two angles together.  That is, the Euler
# angles do not give a "clean" two parameter representation of the
# unit sphere.

angles = dict(min    =(0,       0,       0),
              med    =(0, np.pi/2,       0),
              maj    =(0, np.pi/2,    np.pi/2),
              medmin =(0, np.pi/4,       0),
              majmin =(0, np.pi/4,    np.pi/2),
              majmed =(0, np.pi/2,    np.pi/4),
              off    =(0, 3*np.pi/10, np.pi/4))

# These refer to PASSIVE transforms.
# TODO Phase these out...
angles_passive = dict(min    =(np.pi,     0,         0),
                      med    =(np.pi,     np.pi/2,   0),
                      maj    =(np.pi/2,   np.pi/2,   0),
                      medmin =(np.pi,     np.pi/4,   0),
                      majmin =(np.pi/2,   np.pi/4,   0),
                      majmed =(3*np.pi/4, np.pi/2,   0),
                      # Not exactly right
                      off    =(3*np.pi/4, np.pi/3,   0))

# For my future sanity, when you do this:
# [ [ el for i in range(5)] for j in range(6)]
# think if this:
# [ [ el for col in cols] for row in rows]

def viewing_angle_average(vals):
    """Simple weighted average of projected quantities weighted by solid angle"""
    # solid angle of strips
    pole = 2 * 2*np.pi*(np.cos(0) - np.cos(np.pi/8))  # two poles
    temperate = 2 * 2*np.pi*(np.cos(np.pi/8) - np.cos(3*np.pi/8)) # two temperate zones
    equator = 2*np.pi*(np.cos(3*np.pi/8) - np.cos(5*np.pi/8))  # one equatorial zone

    ave = equator*(vals['maj']+vals['majmed']+vals['med'])/3.0 \
          + temperate*(vals['majmin']+vals['medmin']+vals['off'])/3.0 \
          + pole*vals['min']
    return ave/(4*np.pi)
    
##################################################
## Basic linear algebra
##################################################

def mag(vs):
    """Compute the norms of a set of vectors or a single vector."""
    vs = np.asarray(vs)
    if len(vs.shape) == 1:
        return np.sqrt( (vs**2).sum() )
    return np.sqrt( (vs**2).sum(axis=-1) )

def mag2(vs):
    """Compute the norms of a set of vectors or a single vector."""
    vs = np.asarray(vs)
    if len(vs.shape) == 1:
        return (vs**2).sum()
    return (vs**2).sum(axis=-1)
    
def centerOfMass(rs,ms):
    """Find center of mass of some particles"""    
    rs, ms = [np.asarray(a) for a in rs, ms]    
    return (rs * ms[:, np.newaxis]).sum(axis=0)/ms.sum()

def specific_angular_momentum(rs,vs,ms):
    """Angular momentum per unit mass for a set of particles."""
    rs, vs, ms = [np.asarray(a) for a in rs, vs, ms]
    return (ms*np.cross(rs, vs)).sum(axis=0)/ms.sum()
    
def matmul(m, v):
    """Multiply a matrix times a set of vectors, or a single vector.
    My nPart x nDim convention leads to two transpositions, which is
    why this is hidden away in a function.  Note that if you try to
    use this to muliply two matricies, it will think that you're
    trying to multiply by a set of vectors and all hell will break
    loose."""    
    assert type(v) is not np.matrix
    v = np.asarray(v)
    m, vs = [np.asmatrix(a) for a in (m, v)]
    
    result = np.asarray(np.transpose(m * np.transpose(vs)))    
    if len(v.shape) == 1:
        return result[0]
    return result
    
def adj_matrix(v, l):
    """Compute the adjacency matrix for a set of particles.

    Two particles are defined to be adjacent if the distance between
    them is less than l

    """
    return all_norms(v, v) <= l

def all_norms(v, w):
    """Compute the inner produce of a set of vectors v and w"""
    v,w = np.asarray(v), np.asarray(w)
    return np.sqrt(((v[:,np.newaxis,:] - w[np.newaxis,:,:])**2).sum(axis=-1))

##################################################
## Coordinate Transformations
##################################################
def ball(rs):
    """For a set of radii, choose orientations such that the resulting
    vectors are oriented randomly in 3d"""
    # Want np.cos(th) distribution to be flat
    costh = 2*np.random.rand(len(rs))-1
    sinth = np.sqrt(1-costh**2)
    phi = 2*np.pi*np.random.rand(len(rs))
    return np.transpose([rs*np.cos(phi)*sinth, rs*np.sin(phi)*sinth, rs*costh])
    
def to_spherical(r,v):
    """Convert positions and velocities to spherical coordinates.
    return R, theta, phi, v_r, v_theta, v_phi"""
    r,v = [np.asarray(a) for a in (r,v)]
    R = mag(r)
    theta = np.arctan2(np.sqrt(r[:,0]**2+r[:,1]**2), r[:,2])
    phi = np.arctan2(r[:,1], r[:,0])

    v_r = v[:,0]*np.sin(theta)*np.cos(phi) \
          + v[:,1]*np.sin(theta)*np.sin(phi) \
          + v[:,2]*np.cos(theta)

    v_theta = v[:,0]*np.cos(theta)*np.cos(phi) \
              + v[:,1]*np.cos(theta)*np.sin(phi) \
              - v[:,2]*np.sin(theta)
    
    v_phi = - v[:,0]*np.sin(phi) \
            + v[:,1]*np.cos(phi) 

    return R, theta, phi, v_r, v_theta, v_phi

def to_cylindrical(r,v):
    """Convert positions and velocities to cylindrical coordinates.
    return R, theta, zed, v_R, v_theta, v_zed"""
    r,v = [np.asarray(a) for a in (r,v)]
    R = mag(r[:,:2])
    zed = r[:,2]
    theta = np.arctan2(r[:,1], r[:,0])

    v_R     =  v[:,0]*np.cos(theta) + v[:,1]*np.sin(theta) 
    v_theta = -v[:,0]*np.sin(theta) + v[:,1]*np.cos(theta)    
    v_zed   = v[:,2]

    return R, theta, zed, v_R, v_theta, v_zed

def to_cartesian(r,v):
    """Split position and velocity arrays into cartesian coordinates.
    return r[:,0], r[:,1], r[:,2], v[:,0], v[:,1], v[:,2]"""
    r,v = [np.asarray(arr) for arr in (r,v)]
    return r[:,0], r[:,1], r[:,2], v[:,0], v[:,1], v[:,2]

##################################################
## Rotations 
##################################################
def rotationMatrix(phi):
    """Make a 2D (passive) rotation matrix"""
    cphi=np.cos(phi)
    sphi=np.sin(phi)
    
    m = np.matrix(np.zeros((2,2)))
    m[0,0] = cphi 
    m[0,1] = sphi
    m[1,0] =  -sphi
    m[1,1] =  cphi
    return m

def rotateActive(v,  phi):
    """2D Active rotation."""
    m = rotationMatrix(phi).transpose()
    return matmul(m,v)

def rotatePassive(v,  phi):
    """2D Passive rotation."""
    m = rotationMatrix(phi)
    return matmul(m,v)

##################################################
## Euler transformations
##################################################

# Goldstein constructs euler x-form as passive.  That is, his forward
# transformation is a passive transformation
def eulerMatrix(phi, the, psi):
    """Make an Euler transformation matrix"""
    cpsi=np.cos(psi)
    spsi=np.sin(psi)
    cphi=np.cos(phi)
    sphi=np.sin(phi)
    cthe=np.cos(the)
    sthe=np.sin(the)
    
    m = np.mat(np.zeros((3,3)))
    m[0,0] = cpsi*cphi - cthe*sphi*spsi
    m[0,1] = cpsi*sphi + cthe*cphi*spsi
    m[0,2] = spsi*sthe
    m[1,0] = -spsi*cphi - cthe*sphi*cpsi
    m[1,1] = -spsi*sphi + cthe*cphi*cpsi 
    m[1,2] = cpsi*sthe
    m[2,0] = sthe*sphi
    m[2,1] = -sthe*cphi
    m[2,2] = cthe

    return m

def passiveEulerMatrix(phi, the, psi):
    """Passive Euler matrix"""
    return eulerMatrix(phi, the, psi)

def activeEulerMatrix(phi, the, psi):
    """Active Euler matrix"""
    return eulerMatrix(phi, the, psi).transpose()
    
def eulerPassive(v, phi, the, psi):
    """Passive Euler transform"""
    m = eulerMatrix(phi, the, psi)
    return matmul(m,v)
    
def eulerPassiveInverse(v,  phi,  the,  psi):
    """Inverse of passive Euler transform"""
    m = eulerMatrix(phi, the, psi).transpose()
    return matmul(m,v)

def eulerActive(v,  phi,  the,  psi):
    """Active Euler transform"""
    m = eulerMatrix(phi, the, psi).transpose()
    return matmul(m,v)

def eulerActiveInverse( v,  phi,  the,  psi):
    """Active Euler transform inverse"""
    m = eulerMatrix(phi, the, psi)
    return matmul(m,v)

##################################################
## Affine transformations
##################################################
def affineVectors(vs):
    """Make a set of vectors suitable for affine transformations"""
    vs = np.asarray(vs)
    if len(vs.shape) == 1:
        return np.concatenate((vs, [1]))        
    N = vs.shape[0]
    return np.hstack((vs, np.ones((N,1))))

def deAffineVectors(vs):
    """Make a set of affine vectors into normal vectors"""
    vs = np.asarray(vs)
    if len(vs.shape) == 1:
        return vs[:-1]
    return vs[:,:-1]

def affineXForm(m, vs):
    """Given an affine matrix m (dim n+1 x n+1) and a set of normal
    vectors, apply the affine transformation."""
    return deAffineVectors(matmul(m, affineVectors(vs)))
    
def affine(rotn, trans):
    """Make an affine matrix, given the linear transoformation part
    and the translation part"""
    rotn, trans = [np.asarray(arr) for arr in (rotn, trans)]
    N=len(trans)
    matrix = np.mat(np.zeros((N+1, N+1)))
    matrix[:-1, :-1] = rotn
    matrix[:-1, N] = trans[:,np.newaxis]
    matrix[N,N] = 1
    return matrix

def deAffine(matr):
    """Split up an affine matrix, given the linear transoformation part
    and the translation part"""
    N=len(matr)-1
    rotn = np.array(matr[:-1, :-1])        
    trans = np.array(matr[:-1, N])[:,0]
    return rotn, trans

def affineXFormer(m):
    """Given an affine matrix, make a function that transforms a set
    of vectors with the matrix"""
    # matrix purports to make a copy
    rMatrix = np.matrix(m)
    # the v matrix is the same thing without the translation part
    vMatrix = rMatrix[:-1, :-1]
    
    def f(ws,velocity=False):
        if velocity:
            return matmul(vMatrix, ws)
        return affineXForm(rMatrix, ws)
    return f

##################################################
## Binning particles into images
##################################################

def imageIndicies(rs, xb, yb):
    """Construct an image from a set of particles.  

    For a set of 2d vectors rs, and a list of bin edges in x and y,
    return one list for each pixel that contains the index of all the
    particles that fall into that pixel.  In addition, return the bin
    centers in x and y.

    """
    rs = np.asarray(rs)
    N = rs.shape[1]
    assert N == 2
    
    x = rs[:,0]
    y = rs[:,1]
    
    xb = nu.findEdges(xb, x)
    yb = nu.findEdges(yb, y)

    binLists = nu.partition([x,y], [xb, yb])
    xc, yc, = [ nu.ave(arr) for arr in (xb, yb) ]
    return binLists, xc, yc

def makeImageFromIndicies(binLists, ms):
    """Construct an image from a set of particles.  

    Make the image given the output of imageIndicies() and the mass of
    each particle.

    """
    ms = np.asarray(ms)
    counts = np.array([[len(pix) for pix in row]
                    for row in binLists])
    fracErr = 1/np.sqrt(counts.clip(1,np.inf))
    # TODO -- assuming constant mass/light
    inten = np.array([[ms[pix].sum() for pix in row]
                    for row in binLists])
    intenErr = inten*fracErr
    return inten, intenErr

def makeImage(rs, ms, xb, yb):
    """Construct an image from a set of particles.  

    For a set of 2d vectors rs, a list of particle masses ms, and a
    list of bin edges in x and y, the total mass and estimated error
    that falls into each pixel.

    """
    binLists, xc, yc = imageIndicies(rs, xb, yb)
    return makeImageFromIndicies(binLists, ms)

##################################################
## Determining shapes of particle dists
##################################################
# TODO -- specify r instead of mass fraction
# TODO -- may want to define half mass radius as half of mass
# contained within 5*re, rather than half of the mass in the entire
# volume.
def serialEllipticity(rs,ms, weighted=None, fraction=0.5, 
                # default limits -- 1 degree, 10 pc, 1 pct in axis ratio
                angTol = .01, posTol = .01, axTol = 0.01,
                verbose=False):
    """Compute the shape of a particle distribution by diagonalizing a
    the moment-of-inertia tensor.

    Return the length of the principal axes and an affine matrix that
    transforms from the given coordinate system to the one aligned
    with the particle distribution.

    forward function is affineXFormer(matrix)
    reverse function is affineXFormer(linalg.inv(matrix))

    serialEllipticity(rs,ms, weighted=None, fraction=0.5, 
                      # default limits -- 1 degree, 10 pc, 1 pct in axis ratio
                      angTol = .01, posTol = .01, axTol = 0.01,
                      verbose=False)
                      
    """
    rs, ms = [np.asarray(a) for a in rs, ms]
    if np.iterable(fraction): fin, fout = fraction
    else: fin, fout = 0.0, fraction

    # Move origin to center of mass to have a reasonable chance of
    # finding the remnant when it's not near the origin.
    #rcom = centerOfMass(rs, ms)
    #rs = rs - rcom

    N=rs.shape[1]
    xform = np.mat(np.identity(N+1))
    axes = np.ones(N)
    dAx = dAng = dPos = np.inf
    iteration=1
    
    while not ( dAx < axTol and dAng < angTol and dPos < posTol):
        In = insideShell(rs, ms, axes=axes, fin=fin, fout=fout)
        if weighted: moi = positionMoment(rs[In], ms[In], axes=axes)
        else:        moi = positionMoment(rs[In], ms[In])
        eval, evect = np.linalg.eig(moi)
                                                             
        # Figure out affine transformation
        order = eval.real.argsort()
        shortAx, longAx = [ evect[:,order[i]] for i in (0,-1) ]
        if N==2:   rotation = rotationMatrix( findAngle(shortAx) )
        elif N==3: rotation = eulerMatrix( *findHalfEulerAngles(shortAx, longAx))
        translation = - centerOfMass(rs[In],ms[In])
        m = affine(rotation, matmul(rotation, translation))
        
        # Apply affine transformation
        rs = affineXForm(m, rs)
        xform = m*xform
        lastAxes = axes
        
        # Find new axes
        scaleLengths = np.sqrt( eval.real[order] )[::-1]  # sorted long to short
        axes = fractionalAxes(rs,ms, scaleLengths, f=fout)

        iteration += 1 
        if iteration > 50: break
        dAx = (abs(axes - lastAxes)/lastAxes).max()
        dAng = (abs(abs(rotation) - np.identity(N))).max()
        dPos = mag(translation)
        if verbose: print dAx, dAng, dPos

    # before returning, put the center of mass back in to maintain the
    # same coordinate system
    #rot, trans = deAffine(xform)
    #trans = trans + rcom
    #xform = affine(rot, trans)
    
    if verbose: print iteration, "iterations"    
    # Return the outermost set of axis ratios
    return fractionalAxes(rs,ms, scaleLengths, f=fout), xform

# FIXME
if sys.argv[0] == '' or sys.argv[0] == 'update.py':
    # When doing big database updates running straight python, fork
    # calls to avoid running out of memory
    ellipticity = util.forkify(serialEllipticity)
else:
    # Otherwise just call the function
    ellipticity = serialEllipticity    

# def projectedEllipticity(rs, ms, angles=(0.0, 0.0, 0.0), **kw):
#     """ """
#     rs = eulerPassive(rs, *angles)
#     return ellipticity(rs[:,0:2], ms, **kw)

# def fractionalAxes(rs, qs, axes, f=0.5):
#     """Find axis lengths of half-mass ellipsoid"""
#     axes = np.asarray(axes)/max(axes)
#     return axes * fractionalRadius(rs/axes, qs, f=f)

def fractionalAxes(rs, qs, axes, f=0.5):
    # TESTME
    """Find axis lengths of half-mass ellipsoid"""
    axes = np.asarray(axes)/max(axes)
    radii = fractionalRadius(rs/axes, qs, f=f)
    if len(radii.shape) == 0:
        return axes*radii
    return np.array([axes * radius for radius in radii])

def fractionalRadius(rs,qs,f=0.5):
    """Find the smallest n-sphere that contains at least frac of the
    quantity qs.  The reason for defining it that way is that it gives
    nice behavior for f=0.0 and f=1.0.  That is,
    fractionalRadius(r,q,0.0) => 0.0 and fractionalRadius(r,q,1.0) =>
    max radius in r."""
    rs,qs = [np.asarray(a) for a in (rs,qs)]
    N=len(qs)
    if not np.iterable(f): theF = [f]
    else: theF = f

    rMag = mag(rs)
    order = rMag.argsort()
    cumul = qs[order].cumsum()
    cumulFrac = cumul / float(cumul[-1])
    index = cumulFrac.searchsorted(theF, side='right') - 1
    # index==0 for any value of f that's less than cumulFrac[0].
    # These should be mapped to radius zero, not the smallest actual
    # radius
    result = np.where(index==-1, 0.0, rMag[order][index.clip(0, len(rMag)-1)])
    if not np.iterable(f): return result[0]
    return result

def insideShell(rs, ms, axes=None, fin=0.0, fout=0.5):
    """Find particles inside ellipsoid w/ axes defined by axes"""    
    # TESTME
    rs, ms = np.asarray(rs), np.asarray(ms)
    N = rs.shape[1]
    if not axes is None: rs = rs/axes

    rMag = mag(rs)
    rin, rout = fractionalRadius(rs, ms, f=[fin, fout])
    return np.logical_and(rMag > rin, rMag < rout)

def positionMoment(rs, ms=None, axes=None):
    """Find second position moment tensor.

    If axes is specified, weight by the elliptical radius (Allgood 2005)"""
    rs = np.asarray(rs)
    Npart, N = rs.shape
    if ms is None: ms = np.ones(Npart)
    else: ms = np.asarray(ms)    

    if axes is not None:
        axes = np.asarray(axes,dtype=np.float64)
        axes = axes/axes.max()
        norms2 = mag2(rs/axes)
    else:
        norms2 = np.ones(Npart)
    M = ms.sum()
    result = np.zeros((N,N))
    # matrix is symmetric, so only compute half of it then fill in the
    # other half
    for i in range(N):
        for j in range(i+1):
            result[i,j] = ( rs[:,i] * rs[:,j] * ms / norms2).sum() / M

    result = result + result.transpose() - np.identity(N)*result
    return result

def angle(v1,v2):
    "Find angle b/t two vectors"
    v1,v2 = np.asarray(v1), np.asarray(v2)
    assert v1.shape == (3,) and v2.shape == (3,)
    return np.arccos( np.dot(v1,v2) / np.sqrt(np.dot(v1,v1) * np.dot(v2,v2)) )
    
def findAngle(v):
    """Find 2d angle.  v should be the SHORT axis, and it will be
    rotated to line up with the y axis.

    (old) Calculate angles to bring a body into alignment with the
    coordinate system.  If v1 is the SHORTEST axis and v2 is the
    LONGEST axis, then this will return the angle (Euler angles) to
    make the long axis line up with the x axis and the short axis line
    up with the x (z) axis for the 2 (3) dimensional case."""
    # want v1 lined up with y axis, for symmetry w/ 3d case
    return -np.arctan(v[0]/v[1])
    
def findHalfEulerAngles(v,w):
    """Find the passive euler angles that will make v lie along the z
    axis and w lie along the x axis.  v and w are uncertain up to
    inversions (ie, eigenvectors) so this routine removes degeneracies
    associated with that

    (old) Calculate angles to bring a body into alignment with the
    coordinate system.  If v1 is the SHORTEST axis and v2 is the
    LONGEST axis, then this will return the angle (Euler angles) to
    make the long axis line up with the x axis and the short axis line
    up with the x (z) axis for the 2 (3) dimensional case."""
    # Make sure the vectors are normalized and orthogonal
    v = v/mag(v)
    w = w/mag(w)    
    if abs((v*w).sum()) / (mag(v)*mag(w)) > 1e-5: raise ValueError

    # Break eigenvector scaling degeneracy by forcing it to have a positive
    # z component
    if v[2] < 0: v = -v
    phi,theta = findEulerPhiTheta(v)

    # Rotate w according to phi,theta and then break inversion
    # degeneracy by requiring that resulting vector has positive
    # x component
    w_prime = eulerPassive(w,phi,theta,0.)
    if w_prime[0] < 0: w_prime = -w_prime
    # Now last Euler angle should just be this:
    psi = np.arctan2(w_prime[1],w_prime[0])
    
    return phi, theta, psi

def findEulerPhiTheta(v):
    """Find (passive) euler angles that will make v point in the z
    direction"""
    # Make sure the vector is normalized
    v = v/mag(v)
    theta = np.arccos(v[2])
    phi = np.arctan2(v[0],-v[1])
    return phi,theta

##################################################
## Calculate things on snapshots... eg density.
##################################################

def massProfile(rs, ms, rEdges):
    """Compute the cumulative mass profile"""
    ms = np.asarray(ms)
    mags = mag(rs)
    order = mags.argsort()
    mags, ms = mags[order], ms[order]
    result = ms.cumsum()[mags.searchsorted(rEdges) - 1]
    result[mags[0] > rEdges] = 0
    return result

def densityProfile(rs, ms, rEdges=None, physicalUnits=False):
    """Make a runction for mass enclosed as a function of elliptic
    radius.  You feed it _physical_ radii and it _remembers_ the axes
    so that it computes the elliptic radius for you."""
    if rEdges is None: rEdges = np.logspace(np.log10(RMIN), np.log10(RMAX), 50)
    
    ms = np.asarray(ms)
    rBins = nu.ave(rEdges)
    drs = np.diff(rEdges)

    idxs = nu.partition(mag(rs), rEdges)
    dms = [ms[idx].sum() for idx in idxs]

    if   len(rs[0]) == 3: rhos = dms/(4*np.pi*rBins**2*drs)
    elif len(rs[0]) == 2: rhos = dms/(2*np.pi*rBins*drs)
    elif len(rs[0]) == 1: rhos = dms/drs
    
    # 1 code unit = 10 solar masses / pc^3
    if physicalUnits: rhos = 10*rhos
    return rhos, rBins

def densityFunc(rs, ms, **kw):
    """Return a function that computes the density as a function of radius"""
    rhos, rBins = densityProfile(rs, ms, **kw)
    return scipy.interpolate.interp1d(rBins,rhos)

def velocity_profile(rs, vs, ms, fit=None, edges=None):
    """3D velocity dispersion profile"""
    ms = np.asarray(ms)
    if edges is None: edges = logspace(np.log10(RMIN), np.log10(RMAX), 30)
    if fit is None: fit = lambda xs, ws: (nu.weighted_mean(xs, ws), nu.weighted_std(xs,ws))
        
    r, th, phi, vr, vth, vphi = to_spherical(rs, vs)
    order = r.argsort()
    r, th, phi, vr, vth, vphi, ms = [a[order] for a in r, th, phi, vr, vth, vphi, ms]
    
    rBins = nu.ave(edges)
    iEdges = r.searchsorted(edges)
    profs = [ np.transpose([ fit(v[il:ih], ms[il:ih])
                          for il, ih in zip(iEdges[:-1], iEdges[1:])])
              for v in (vr, vth, vphi)]
    # rs, mean_vs, mean_vth, mean_vphi, sig_vr, sig_vth, sig_vphi
    return rBins, profs[0][0], profs[1][0], profs[2][0], profs[0][1], profs[1][1], profs[2][1], 

def dispersion(rs, vs, ms, aperture, fit=None):
    """Aperture velocity dispersion"""
    # Should be fed projected rs and vs
    rs, vs, ms = [np.asarray(ar) for ar in rs, vs, ms]
    assert len(np.shape(vs)) == 1 and rs.shape[1] == 2
    if fit is None: fit = lambda xs, ws: (nu.weighted_mean(xs, ws), nu.weighted_std(xs,ws))

    idx = mag(rs) < aperture
    return fit(vs[idx], ms[idx])[1]

def dispersion_profile(rs, vs, ms, apertures, fit=None):
    return np.array([dispersion(rs,vs,ms, ap, fit=fit) for ap in apertures]), apertures
        
##################################################
## Rickety Code
##################################################

def amap(f, arr):
    """Like map() but for arrays"""
    arr = np.asarray(arr)
    return np.array([ f(el) for el in arr.flat]).reshape(arr.shape)
# TODO -- name conflict with matplotlib
arrmap = amap

def amapInPlace(f, arr):
    """Like amap(), but in place"""
    arr = np.asarray(arr)
    fArr = arr.flat
    n = np.prod(np.shape(arr))
    for i in range(n):
        fArr[i] = f(fArr[i])
    print fArr
    # to emphasize in-place-ness, return no value

def gridFromLimits(limits, N):
    """Make a grid of bin edges
    
    Given limits=[[xl, xh], [yl, yh], ...] and a desired number of
    points N=int or N=[nx, ny], compute bin edges in x, y, (... z,
    etc)

    """
    if not np.iterable(N):
        N = [N for i in range(len(limits)) ]
    return [np.linspace(low, high, N)
            for ((low,high), N) in zip(limits, N) ] 
    
def newcenter(rs, ms, rf, ri=None, c=None, factor=2.0):
    """Find highest density point of particle distribution by
    constantly moving to the center-of-mass of an ever-shrinking
    sphere."""
    rs, ms = np.asarray(rs), np.asarray(ms)
    if c is None: c = np.array([0.0, 0, 0])
    if ri is None: ri = mag(rs-c).max()

    # want radii separated by exactly factor rather than meeting the
    # endpoints (as logspace does).
    r_spectrum = 10**np.arange(np.log10(rf), np.log10(ri), np.log10(factor))
    rads = np.concatenate(([ri], r_spectrum[::-1]))
    for rad in rads:
        idx = mag(rs-c) < rad
        c = centerOfMass(rs[idx], ms[idx])
        print rad, c
    return c

def center(rs, precision, limits=None, ids=None):
    """Find highest density point of particle distribution

    First find the rough center quickly by thinning the particle
    distribution, then repeat with a larger and larger fraction of the
    particles until all are included.

    """
    n = len(rs)
    # small number of particles, just do it
    if n < 10000:
        return slowCenter(rs, precision, limits, ids)        

    # one round with 100 times worse precision, 100 times fewer particles:
    kp = (np.random.rand(n) < 1/81.0)
    limits1 = slowCenter(rs[kp], 81*precision, limits, ids)

    # one round with 10 times worse precision, 10 times fewer particles:
    kp = (np.random.rand(n) < 1/9.0)
    limits2 = slowCenter(rs[kp], 9*precision, limits1, ids)

    # finally, the good round
    return slowCenter(rs, precision, limits2)

def slowCenter(rs, precision, limits=None, ids=None):
    """Find highest density point of particle distribution using
    recursiveCenter"""
    rs = np.transpose(rs)
    if limits is None:
        mx = mag(rs).max()
        n = int(np.log(2*mx / precision)/np.log(3) + 1)
        limits = [(-precision*3**n/2, precision*3**n/2) for i in range(len(rs))]
    if ids is not None: ids = np.asarray(ids)
    return recursiveCenter(rs, np.asarray(limits), precision, ids)
    
def recursiveCenter(rs, limits, precision, ids):
    """Find highest density point of particle distribution 

    Find the center by constructing a 3x3x3 box (the algorithm works
    in n dimensions, 3D used for concretness), finding which cube
    contains the most mass, and recursing until the desired precision
    is acheived.

    """
    rs, limits = np.asarray(rs), np.asarray(limits)
    if max(limits[:,1] - limits[:,0]) <= 1.01*precision:
        nDim = len(limits)
        edges = np.array( gridFromLimits(limits, 4) )

        rBins = nu.partition(rs, edges)
        density = amap(len, rBins)
        print precision, density.sum()  
        return limits
    nDim = len(limits)
    edges = np.array( gridFromLimits(limits, 4) )

    rBins = nu.partition(rs, edges)
    density = amap(len, rBins)
    peak = density==max(density.flat)
    newRs = rs[:, rBins[peak][0]]
    if not ids is None: ids = ids[rBins[peak][0]]

    peakIdx = peak.nonzero()
    if len(peakIdx[0]) != 1: 
        raise ValueError, "Mulitple maxima found"
    edgeXs = [[i,i] for i in range(nDim)]
    edgeYs = [[ i[0], i[0]+1] for i in peakIdx]
    newLimits = edges[edgeXs, edgeYs]
    
    return recursiveCenter(newRs, newLimits, precision, ids)

# def center1(rs, n, limits=None):
#     if not limits:
#         mx = max(abs(rs))
#         limits = (-mx, mx)
#     return rCenter1(rs, limits, n)
    
# def rCenter1(rs, limits, n):
#     if n <= 0: return limits
#     edges = np.linspace(limits[0],limits[1],4)
#     result = nu.partition(rs, edges)
#     density = amap(len, result)
#     idx = np.nonzero(density==max(density))
#     newLimits = edges[idx][0], edges[(idx[0]+1,)][0]
#     return rCenter1( rs[result[density==max(density)][0]], newLimits, n-1)

##################################################
## Surface brightness profile

# def slowSersicBnTable(ns):
#     return [sersic(n)._bn for n in ns]

# sersicBnTable = util.memoize(slowSersicBnTable)

def sersic(d,p,**kw):    
    """Fit a sersic brightness profile"""
    d.toBodyCoordinates(p)
    return fitSersic(d.rs, d.ms, **kw)

def sersicR(d,p,rmins, rmaxes, **kw):    
    """Fit a sersic brightness profile as a function of projected radius"""
    d.toBodyCoordinates(p)
    return fitSersicVsR(d.rs, d.ms, rmins, rmaxes, **kw)

def fitSersic(rs, ms, rmin=None, rmax=None, **kw):
    """Fit a sersic brightness profile."""
    # TODO -- do I really want to make sure that I'm peaked-up on the
    # center of the galaxy?
    # TODO -- assuming constant mass/light
    # Want to do the fit in log
    # Try out to 10 re
    # TODO -- figure out what to do w/ inner cutoff...

    rad2d, reff = findProjShape(rs, ms, **kw)    
    if rmin is None or rmax is None: rb = None
    else: rb = (np.log10(rmin), np.log10(rmax), 50) # TODO -- won't need logs
    return fitSimpleSersic(rad2d, ms, reff, rb)

def fitSersicVsR(rs, ms, rmins, rmaxes, **kw):
    """Fit a sersic brightness profile as a function of projected radius"""
    # TODO -- rmins is in kpc, rmaxes is in reff
    if np.iterable(rmins) and np.iterable(rmaxes):
        raise RuntimeError

    rad2d, reff = findProjShape(rs, ms, **kw)
    if np.iterable(rmins):
        rvar = rmins
        # TODO -- won't need log here
        ns = [fitSimpleSersic(rad2d, ms, reff,
                              (np.log10(rmin), np.log10(reff*rmaxes), 50))
              for rmin in rmins]
    if np.iterable(rmaxes):
        rvar = rmaxes
        # TODO -- won't need log here
        ns = [fitSimpleSersic(rad2d, ms, reff,
                              (np.log10(rmins), np.log10(reff*rmax), 50))
              for rmax in rmaxes]
    return ns, rvar

def findProjShape(rs, ms, angles=(0,0,0)):
    """Find projected shape by diagonalizing the moment of inertia tensor"""
    r2d = eulerActive(rs, *angles)[:,0:2]
    axes, matrix = ellipticity(r2d, ms)
    # If we're not going to fit for reff, it's important to get it
    # right, so caluclate a shape and reff for each viewing angle
    # (rather than trying to use a "mean" value)
    reff = axes.max()
    r2d = affineXFormer(matrix)(r2d)
    r2d = reff*r2d/axes
    return mag(r2d), reff

def fitSimpleSersic(rmag, ms, reff, rb=None):
    """Fit a sersic brightness profile."""
    # rmag should be elliptical radii
    def sersic_profile(rr,nn,reff,L):
        ff = sersic_module.sersic.bm_func(nn)
        return (L/reff**2)*ff(rr/reff)

    def residuals(p):
        n,L = p
        return np.log(sb) - np.log(sersic_profile(nu.ave(rb), n, reff, L))

    rmag, ms = np.asarray(rmag), np.asarray(ms)
    if rb is None: rb = 50 # TODO -- won't need this later, won't need log10, 10**
    rb = 10**nu.findEdges(rb, [np.log10(0.5), np.log10(5*reff)])
    # TODO -- calculate area of elliptic rings differently?
    area = 2*np.pi*nu.ave(rb)*np.diff(rb)
    mass = np.array([ms[idx].sum() for idx in nu.partition(rmag, rb)])
    sb = mass/area
    # 1/0
    p, status = scipy.optimize.leastsq(residuals, (4, ms.sum()))
    n, L = p
    # TODO if status != 1: raise RuntimeError
    return n
    #return p, rb, sb, sersic_profile(nu.ave(rb), n, reff, L)

##############################
## Rickety code

def linear_fit_guess(xs, ys, x0):
    """Provide an initial guess at a linear fit where the function to
    be fit is y = slope*(x-x0) + offset"""
    xs, ys = np.asarray(xs), np.asarray(ys)
    slope = (xs*ys).sum()/(xs**2).sum()
    offset = ys.mean() - slope*(xs.mean()-x0)
    return slope, offset    
    
def power_law_fit(rs, rhos, rl, rh, r0):
    "Fit a power law to the density distribution"
    # Returns the slope and the value of rho at reff
    # select the region from 0.5 kpc to 5*reff
    rs, rhos = np.asarray(rs), np.asarray(rhos)
    il, ih = rs.searchsorted(rl), rs.searchsorted(rh, 'right')
    # Make sure that there are at least two points in the fit
    if ih-il < 2: ih = il+2
    xs, ys = np.log10(rs[il:ih]), np.log10(rhos[il:ih])
    
    x0 = np.log10(r0)  # set zero point of fit to effective radius
    result = scipy.optimize.leastsq(lambda (slope,offset): slope*(xs-x0) + offset - ys, linear_fit_guess(xs, ys, x0))
    return result[0][0], 10**result[0][1]
    
def simpleMassSurfaceDensity(d, p):
    "Mean mass surface density"
    return 0.5*d.ms.sum()/(np.pi*p['reff-off']**2)

def massSurfaceDensity(d, p, angles=None, reff=None, f=1.0):
    "Mean mass surface density"
    d.toBodyCoordinates(p)
    # TODO -- getting annoying to get names out of dict
    if reff is None: reff = p['reff']
    if angles is None: angles = angles_passive['min']
            
    rs = eulerPassive(d.rs, *angles)[:,0:2]
    drs = eulerPassive(d.rd, *angles)[:,0:2]
    grs = eulerPassive(d.rg, *angles)[:,0:2]

    m = np.concatenate((d.ms[mag(rs) < f*reff], 
                     d.md[mag(drs) < f*reff],
                     d.mg[mag(grs) < f*reff])).sum()
    return m/(np.pi*reff**2)

def sigma(d,p,angles=None, reff=None, f=1.0):
    "Approximate aperture velocity dispersion"
    d.toBodyCoordinates(p)
    # TODO -- getting annoying to get names out of dict
    if reff is None: reff = p['reff']
    if angles is None: angles = angles_passive['min']
            
    rs = eulerPassive(d.rs, *angles)[:,0:2]
    vs = eulerPassive(d.vs, *angles)[:,2]
    return vs[mag(rs) < f*reff].std()

def sigmaVsR(d,p, rBins, angles=None):
    "Velocity dispersion as a function of radius"
    d.toBodyCoordinates(p)
    # TODO -- getting annoying to get names out of dict
    if angles is None: angles = angles_passive['min']

    rs = mag(eulerPassive(d.rs, *angles)[:,0:2])
    vs = eulerPassive(d.vs, *angles)[:,2]
    
    return rBins, [vs[rs < rBin].std() for rBin in rBins]

##################################################
## Shapes with spherical harmonics
# def zeta(eps):
#     def f(r,th):
#         return r*np.sqrt((1-eps*(2-eps)*np.cos(th)**2)/(1-eps)**2)
#     return f

def findShape(rs, ms, fin=0.0, fout=0.5):
    """Find shape of distribution of points.

    Do this by finding position, euler angles, and axis ratios that
    minimize the squared sum of the dipole and quadrupole spherical
    harmonics.

    """

    def xform(center,angles,a,b):
        """Transform spatial coordinates to body coordinates.  Then
        return spherical coordinates and masses of particles in an
        ellipsoidal window.  See p 36 of June 2007 notebook for
        details"""
        rp = eulerPassive(rs - center, *angles)
        in_idx = insideShell(rp, ms, [1,a,b], fin=fin, fout=fout)
        rIn, mIn = rp[in_idx], ms[in_idx]
        # TODO -- Is this right?  map onto ellipsoidal radius
        #rIn = np.transpose(rIn/[1,a,b])
        rIn = np.transpose(rIn)
        # Finally, convert to spherical coords
        r,th,phi = nu.spherical(rIn[0], rIn[1], rIn[2])
        return r,th,phi,mIn
        
    def chi2(p):
        x0,y0,z0,phi,th,psi,a,b = p
        r, th, phi,mIn = xform([x0,y0,z0], (phi,th,psi), a, b)
        terms = [(mIn*scipy.special.ry(l,m,th,phi)).sum()/mIn.sum()
                 for l,m in ((1,-1), (1,0), (1,1),
                             (2,-2), (2,-1), (2,0), (2,1), (2,2))]
        result = (np.array(terms)**2).sum()
        return result

    # Starting point is output of ellipticity
    axes, matrix = ellipticity(rs, ms, fraction=(fin,fout))
    # Interested in spatial positions of points in body space, so
    # actually interested in inverse matrix
    toSpace = affineXFormer(matrix.getI())
    center = toSpace([0,0,0.0])
    phi,th,psi = findHalfEulerAngles(toSpace([0,0,1]) - center,
                                     toSpace([1,0,0]) - center)
    a = axes[1]/axes[0]
    b = axes[2]/axes[0]

    p0 = center[0], center[1], center[2], phi, th, psi, a, b
    pmin = scipy.optimize.fmin_cg(chi2,p0,gtol=1e-3)
    # Brief tests showed that powell took 25 times more function calls but found a better min
    # pmin = scipy.optimize.fmin_powell(chi2,p0)
    x0,y0,z0,phi,th,psi,a,b = pmin
    mat = affine(passiveEulerMatrix(phi, th, psi),
                 # In xform() above, I translated then rotated: R (v - c)
                 # Affine matrices translate then rotate: Rv + w
                 # So w = -Rc
                 -eulerPassive([x0,y0,z0], phi, th, psi))
    axes = fractionalAxes(affineXForm(mat, rs), ms, [1,a,b], f=fout)
    return axes, mat

def zeta2d(ainv,binv):
    """Return a function that returns the elliptical radius for an
    ellipse defined by ainv**2 x**2 + binv**2 y**2 = const."""
    def f(r,th):
        return r*np.sqrt(ainv**2*np.cos(th)**2 + np.sin(th)**2/binv**2)
    return f

def zeta3d(ainv, binv, cinv):
    """Return a function that returns the elliptical radius for an
    ellipsoid defined by ainv**2 x**2 + binv**2 y**2 + cinv**2 z**2 =
    const."""
    def f(r,th,phi):
        return r*np.sqrt(  (ainv*np.cos(phi)*np.sin(th))**2
                      + (binv*np.sin(phi)*np.sin(th))**2
                      + (cinv*np.cos(th))**2)
    return f

def r2d(ainv,binv):
    """Return a function that returns the elliptical radius for an
    ellipse defined by ainv**2 x**2 + binv**2 y**2 = const."""
    def f(zeta,th):
        return zeta/np.sqrt(ainv**2*np.cos(th)**2 + np.sin(th)**2/binv**2)
    return f

def r3d(ainv, binv, cinv):
    """Return a function that returns the elliptical radius for an
    ellipsoid defined by ainv**2 x**2 + binv**2 y**2 + cinv**2 z**2 =
    const."""
    def f(zeta,th,phi):
        return zeta/np.sqrt(  (ainv*np.cos(phi)*np.sin(th))**2
                           + (binv*np.sin(phi)*np.sin(th))**2
                           + (cinv*np.cos(th))**2)
    return f

def deviation3():
    """Think this has to do with how closely a distribution of points can
    be expected to approximate a spherical distribution as a function
    of the number of points.

    """
    def mu(zeta): return zeta-1
    mu = np.vectorize(mu)
    epsFit = 0.2
    delFit = 0.1
    epsReal = 0.2
    delReal = 0.1
    ths, phis = np.meshgrid(np.linspace(0,np.pi,65), np.linspace(0,2*np.pi,64))
    theR = np.vectorize(r3d(1, 1-delFit, 1-epsFit))
    theZeta = np.vectorize(zeta3d(1, 1-delReal, 1-epsReal))
    rs = theR(1, ths, phis)    
    xs,ys,zs = nu.cartesian(rs,ths,phis)
    angle = .1
    mat = np.matrix([[1,0,0],
                  [0,np.cos(angle),-np.sin(angle)],
                  [0,np.sin(angle),np.cos(angle)]])
    mat = np.matrix([[np.cos(angle),-np.sin(angle),0],
                  [np.sin(angle),np.cos(angle),0],
                  [0,0,1]])
    theShape = xs.shape    
    #xs,ys,zs = np.array(mat*np.array([xs.ravel(),ys.ravel(),zs.ravel()])).reshape((3,)+theShape)
    xs,ys,zs = np.array(mat*np.array([xs.ravel(),ys.ravel(),zs.ravel()])).reshape((3,)+theShape)
    rs, ths, phis = nu.spherical(xs,ys,zs)
    mus = mu(theZeta(rs, ths, phis))
    fPhis = np.array([mus[:,8*i] for i in range(8)])
    fThs = np.array([mus[8*i,:] for i in range(8)])
    return fThs, fPhis

def deviation():
    """Think this has to do with how closely a distribution of points can
    be expected to approximate a spherical distribution as a function
    of the number of points.

    """
    def mu(zeta): return zeta-1
    ths = np.linspace(0,2*np.pi,100)
    epsFit = 0.2
    epsReal = 0.2
    theR = r2d(1,1-epsFit)
    theZeta = zeta2d(1, 1-epsReal)
    rs = np.array([theR(1, th) for th in ths])    
    xs,ys = rs*np.cos(ths), rs*np.sin(ths)
    ys = ys + .1
    rs,ths = np.sqrt(xs**2 + ys**2), np.arctan2(ys,xs)    
    mus = [mu(theZeta(r, th)) for r,th in zip(rs,ths)]
    return mus



##################################################
# FOF implementations
##################################################

def fof_eq(vs, b, Equiv=nu.graph.Equivalence1, min_num=None, min_size_factor=1.0):
    """Equivalence-class-based friend-of-friend (FOF) algorithm, 

    Actually seems pretty fast..."""
    def select_box_slow(lims):
        ilims = [xx.searchsorted(lim)
                 for xx, lim in zip(sorted, lims)]
        ids = [ set(xxo[il:ih]) for xxo, (il, ih) in zip(order, ilims) ]
        result = reduce(lambda x,y: x.intersection(y), ids)
        return np.array(list(result), np.int32)

    def handle_box_very_slow(idx, lims):        
        # Intended to be manifestly correct
        blanket = select_box(lims + np.array([-b, b]))
        ws = vs[idx]
        WS = vs[blanket]
        adj = all_norms(ws, WS) <= b
        for i in xrange(len(ws)):
            for j in xrange(len(WS)):
                if adj[i,j]:
                    eq.join(idx[i], blanket[j])

    def handle_box_slow(idx, lims):
        # Slightly more clever algorithm
        blanket = select_box(lims + np.array([-b, b]))
        ws = vs[idx]
        WS = vs[blanket]
        adj = all_norms(ws, WS) <= b
        js, ks = np.nonzero(adj)
        for i in range(len(js)):
            eq.join(idx[js[i]], blanket[ks[i]])

    def select_box(lims):
        # TODO assumed 3d dist here        
        ids = []
        intersect = np.lib.arraysetops.np.intersect1d
        for i in xrange(len(lims)):
            il, ih = sorted[i].searchsorted(lims[i])
            ids.append(order[i][il:ih])
        return intersect(intersect(ids[0], ids[1]), ids[2])

    def handle_box(idx, lims):
        support = """
inline
int set(blitz::Array<long,1> sets, int i) {
  while (sets(i) < i)
    i = sets(i);
  return i;
}

inline
void join(blitz::Array<long,1> sets, int i, int j) {
  int seti, setj, dest;
  seti = set(sets, i);
  setj = set(sets, j);
  dest = seti < setj ? seti : setj;
  sets(seti) = dest;
  sets(setj) = dest;
}
"""
        code = """
int i, j;
for (i=0; i < Nidx(0); i++)
  for (j=0; j < Nblanket(0); j++)
    if (adj(i,j))
      join(sets, idx(i), blanket(j));
"""
        link_all_code = """
int i, j;
for (i=0; i < Nidx(0); i++)
  for (j=0; j < Nblanket(0); j++)
    join(sets, idx(i), blanket(j));
"""
        assert isinstance(eq, nu.graph.Equivalence1)
        # If the local density is high enough, all of the particles
        # will be linked.  If the number of particles within the
        # smallest cell is such that the adjacency matrix will cause a
        # memory error, just link all of the particles        
        blanket = select_box(lims + np.array([-b, b]))
        if len(idx)*len(blanket)*8 > 1e8:
            code = link_all_code
            adj = None
        else:
            adj = np.array(all_norms(vs[idx], vs[blanket]) <= b, np.int8)

        sets = eq._sets
        scipy.weave.inline(code, ['sets', 'idx', 'blanket', 'adj'],
                           support_code=support, 
                           type_converters=scipy.weave.converters.blitz)
        
    def sub_boxes(ls, ms, hs):
        if len(ls) == 1:
            return np.array([[[ls[0], ms[0]]],
                          [[ms[0], hs[0]]]])
        if len(ls) == 2:
            return np.array([[[ls[0], ms[0]], [ls[1], ms[1]]],
                          [[ls[0], ms[0]], [ms[1], hs[1]]],
                          [[ms[0], hs[0]], [ls[1], ms[1]]],
                          [[ms[0], hs[0]], [ms[1], hs[1]]]])
        elif len(ls) == 3:
            return np.array([[[ls[0], ms[0]], [ls[1], ms[1]], [ls[2], ms[2]]],
                          [[ls[0], ms[0]], [ls[1], ms[1]], [ms[2], hs[2]]],
                          [[ls[0], ms[0]], [ms[1], hs[1]], [ls[2], ms[2]]],
                          [[ls[0], ms[0]], [ms[1], hs[1]], [ms[2], hs[2]]],
                          [[ms[0], hs[0]], [ls[1], ms[1]], [ls[2], ms[2]]],
                          [[ms[0], hs[0]], [ls[1], ms[1]], [ms[2], hs[2]]], 
                          [[ms[0], hs[0]], [ms[1], hs[1]], [ls[2], ms[2]]],
                          [[ms[0], hs[0]], [ms[1], hs[1]], [ms[2], hs[2]]]])
            
    def fof_rec(lims):
        hs, ls = lims.T[1], lims.T[0]
        mids = 0.5*(hs + ls)
        size = (hs - ls).max()
        idx = select_box(lims)

        if len(idx) <= min_num:   # Recursion bottoms out b/c few particles
            handle_box(idx, lims)
        elif size < min_size:     # Recursion bottoms out b/c small box
            handle_box(idx, lims)
        else:                     # recurse
            for box in sub_boxes(ls, mids, hs):
                fof_rec(box)
    if min_num is None: min_num = 512

    vs = np.asarray(vs)
    min_size = min_size_factor*b
    eq = Equiv(len(vs))
    order = [np.argsort(xx) for xx in vs.T]
    sorted = [xx[xxorder] for xx, xxorder in zip(vs.T, order)]    
    fof_rec(np.array([[xx[0], xx[-1]] for xx in sorted]))
    return eq

fof = fof_eq
fast_fof = util.memoize(fof)

def time_fof(thin=50):
    """Time a friend-of-friend algorithm implementation."""
    def timeit(link_factor=0.2, **kw):
        t = time.time()
        eq = fof_eq(rs, link_factor*spacing, **kw)
        print ".",
        sys.stdout.flush()
        return time.time()-t
    
    #rs, ms = util.uncan('the-gsn.dat')
    N = 10000
    rs, ms = np.random.rand(3*N).reshape(N,3), np.random.rand(N)
    rs = rs[::thin]
    vol = 4*np.pi*mag(rs).max()**3/3.0
    spacing = (vol/len(rs))**(1/3.0)

    print "Running",
    sys.stdout.flush()
    return [[timeit(min_size_factor=size, min_num=num)
             for num in (1024, )]
            for size in (0.25, 1, 4)]
#             for num in (1, 16, 256)]
#            for size in (1, 4, 16, 32)]
                  
#     def fof_rec(idx, xl, xh, yl, yh):
#         pass
#         if len(idx) <= min_size:
#             pass # do box
#         if xh-xl < 2*b and yh - yl < 2*b and zh - zl < 2*b:
#             pass # small box, do it

#         xm, ym, zm = 0.5*(xh + xl), 0.5*(yh + yl), 0.5*(zh + zl)

#         fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] <= zm)],
#                 xl, xm, yl, ym, zl, zm)
#         fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] >  zm)],
#                 xl, xm, yl, ym, zm, zh)
#         fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] <= zm)],
#                 xl, xm, ym, yh, zl, zm)
#         fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] >  zm)],
#                 xl, xm, ym, yh, zm, zh)
#         fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] <= zm)],
#                 xm, xh, yl, ym, zl, zm)
#         fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] >  zm)],
#                 xm, xh, yl, ym, zm, zh)
#         fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] <= zm)],
#                 xm, xh, ym, yh, zl, zm)
#         fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] >  zm)],
#                 xm, xh, ym, yh, zm, zh)

#         # Now merge solutions
#         xboundry_idx = idx[(xm - b <= vs[idx,xax]) & (vs[idx,xax] <= xm + b)]
#         yboundry_idx = idx[(ym - b <= vs[idx,yax]) & (vs[idx,yax] <= ym + b)]
#         zboundry_idx = idx[(zm - b <= vs[idx,zax]) & (vs[idx,zax] <= zm + b)]
#         if len(xboundry_idx) > 0: fof_2d(vs, b, xboundry_idx, eq, xax)
#         if len(yboundry_idx) > 0: fof_2d(vs, b, yboundry_idx, eq, yax)
#         if len(zboundry_idx) > 0: fof_2d(vs, b, zboundry_idx, eq, zax)
        

#     min_num = 1
#     max_num = np.inf
#     min_size = b

def fof_0d(vs, b, idx=None, eq=None):
    """Friend-of-friend algorithm in 0d (ie, transitive closure)"""
    if idx is None: idx = np.arange(len(vs))
    else: idx = np.asarray(idx)
    if eq is None: eq = nu.graph.Equivalence1(len(vs))
    vs = np.asarray(vs)    
    # select particles under consideration + construct a graph
    ws = vs[idx]
    adj = nu.graph.tc( nu.graph.GraphMatrix( matrix=adj_matrix(ws, b) ) ).asmatrix()
    for row in adj:
        eq.make_set(idx[np.nonzero(row)])
    return eq

def fof_1d(vs, b, idx=None, eq=None, axis=0):
    """Friend-of-friend algorithm in 1d"""
    def fof_rec(idx, lmin, lmax):
        if len(idx) <= 1:
            # Recursion bottoms out with trivial case of one particle.
            return 
        if lmax-lmin < 2*b:
            # recusion bottoms out w/ small cell.
            fof_0d(vs, b, idx, eq)
        # recurse
        lmid = 0.5*(lmin + lmax)
        fof_rec(idx[vs[idx,axis] <= lmid], lmin, lmid)
        fof_rec(idx[vs[idx,axis]  > lmid], lmid, lmax)

        # Now merge solutions
        boundry_idx = idx[(lmid - b <= vs[idx,axis]) & (vs[idx,axis] <= lmid + b)]
        if len(boundry_idx) > 0: fof_0d(vs, b, boundry_idx, eq)

    vs = np.asarray(vs)
    if idx is None: idx = np.arange(len(vs))
    else: idx = np.asarray(idx)
    if eq is None: eq = nu.graph.Equivalence1(len(vs))

    ws = vs[idx,axis]
    fof_rec(idx, ws.min(), ws.max())
    return eq

def fof_2d(vs, b, idx=None, eq=None, axis=2):
    """Friend-of-friend algorithm in 2d"""
    def fof_rec(idx, xl, xh, yl, yh):
        if len(idx) <= 1:
            # Recursion bottoms out with trivial case of one particle.
            return 
        if xh-xl < 2*b and yh - yl < 2*b:
            # recusion bottoms out w/ small cell.
            fof_0d(vs, b, idx, eq)
        # recurse
        xm, ym = 0.5*(xh + xl), 0.5*(yh + yl)

        fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] <= ym)], xl, xm, yl, ym)
        fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] >  ym)], xl, xm, ym, yh)
        fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] <= ym)], xm, xh, yl, ym)
        fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] >  ym)], xm, xh, ym, yh)

        # Now merge solutions
        xboundry_idx = idx[(xm - b <= vs[idx,xax]) & (vs[idx,xax] <= xm + b)]
        yboundry_idx = idx[(ym - b <= vs[idx,yax]) & (vs[idx,yax] <= ym + b)]
        if len(xboundry_idx) > 0: fof_1d(vs, b, xboundry_idx, eq, yax)
        if len(yboundry_idx) > 0: fof_1d(vs, b, yboundry_idx, eq, xax)

    if idx is None: idx = np.arange(len(vs))
    else: idx = np.asarray(idx)
    if eq is None: eq = nu.graph.Equivalence1(len(vs))
    if   axis == 0: xax, yax = 1,2
    elif axis == 1: xax, yax = 0,2
    elif axis == 2: xax, yax = 0,1

    vs = np.asarray(vs)
    xs, ys = vs[idx,xax], vs[idx,yax]
    fof_rec(idx, xs.min(), xs.max(), ys.min(), ys.max())
    return eq

def fof_3d(vs, b, idx=None, eq=None):
    """Friend-of-friend algorithm in 3d"""
    def fof_rec(idx, xl, xh, yl, yh, zl, zh):
        if len(idx) <= 1:
            # Recursion bottoms out with trivial case of one particle.
            return 
        if xh-xl < 2*b and yh - yl < 2*b and zh - zl < 2*b:
            # recusion bottoms out w/ small cell.
            fof_0d(vs, b, idx, eq)
        # recurse
        xm, ym, zm = 0.5*(xh + xl), 0.5*(yh + yl), 0.5*(zh + zl)

        fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] <= zm)],
                xl, xm, yl, ym, zl, zm)
        fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] >  zm)],
                xl, xm, yl, ym, zm, zh)
        fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] <= zm)],
                xl, xm, ym, yh, zl, zm)
        fof_rec(idx[(vs[idx, xax] <= xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] >  zm)],
                xl, xm, ym, yh, zm, zh)
        fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] <= zm)],
                xm, xh, yl, ym, zl, zm)
        fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] <= ym) & (vs[idx, zax] >  zm)],
                xm, xh, yl, ym, zm, zh)
        fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] <= zm)],
                xm, xh, ym, yh, zl, zm)
        fof_rec(idx[(vs[idx, xax] >  xm) & (vs[idx, yax] >  ym) & (vs[idx, zax] >  zm)],
                xm, xh, ym, yh, zm, zh)

        # Now merge solutions
        xboundry_idx = idx[(xm - b <= vs[idx,xax]) & (vs[idx,xax] <= xm + b)]
        yboundry_idx = idx[(ym - b <= vs[idx,yax]) & (vs[idx,yax] <= ym + b)]
        zboundry_idx = idx[(zm - b <= vs[idx,zax]) & (vs[idx,zax] <= zm + b)]
        if len(xboundry_idx) > 0: fof_2d(vs, b, xboundry_idx, eq, xax)
        if len(yboundry_idx) > 0: fof_2d(vs, b, yboundry_idx, eq, yax)
        if len(zboundry_idx) > 0: fof_2d(vs, b, zboundry_idx, eq, zax)

    if idx is None: idx = np.arange(len(vs))
    else: idx = np.asarray(idx)
    if eq is None: eq = nu.graph.Equivalence1(len(vs))
    xax, yax, zax = 0,1,2
    vs = np.asarray(vs)
    xs, ys, zs = vs[idx,xax], vs[idx,yax], vs[idx,zax]
    fof_rec(idx, xs.min(), xs.max(), ys.min(), ys.max(), zs.min(), zs.max())
    return eq
    
#return particle_tc1(adjList)

def old_fof_1(v, l, theN=1):
    """Friend-of-friend algorithm"""
    def old_fofrec(idx, mn, mx):
        mn, mx = np.asarray(mn), np.asarray(mx)
        if iwidth[-1] > maxdepth[0]: maxdepth[0] = iwidth[-1]
        
        # Free variables: x, idxHalo, haloList, nextHalo, l
        if len(idx) <= theN:
            bigt = time.time()
            t = time.time()
            adj_matrix = all_norms(v[idx], v[idx]) <= l
            adj = nu.graph.GraphMatrix(matrix=adj_matrix)
            ts[8] += time.time() - t

            t = time.time()
            theTc = nu.graph.tc(adj).asmatrix()
            ts[9] += time.time() - t

            t = time.time()
            for i in range(len(idx)):
                js = np.nonzero(theTc[i, i+1:])[0]
                if len(js) > 0:
                    j = js[-1] + i + 1
                    deadHalo = idxHalo[idx[i]]
                    idxHalo[haloList[deadHalo]] = idxHalo[idx[j]]
                    haloList[idxHalo[idx[j]]] += haloList[deadHalo]
                    haloList[deadHalo] = []                    
            ts[10] += time.time() - t

            ts[7] += time.time() - bigt

        elif np.sqrt(((mx-mn)**2).sum()) <= l:
            # Spatial recursion has bottomed out -- these cannot be in another halo.
            assert util.every([len(haloList[i]) == 1 and haloList[i][0] == i for i in idx])
            haloList[idxHalo[idx[0]]] = idx.tolist()
            for i in idx[1:]:
                haloList[idxHalo[i]] = []
            idxHalo[idx] = idxHalo[idx[0]]
        else:
            vs = v[idx]
            ct = 0.5*(mx + mn)
            t = time.time()
            
            subidxs = [idx[(vs[:,X] <= ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] <= ct[Z])],
                       idx[(vs[:,X] <= ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] >  ct[Z])],
                       idx[(vs[:,X] <= ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] <= ct[Z])],
                       idx[(vs[:,X] <= ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] >  ct[Z])],
                       idx[(vs[:,X] >  ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] <= ct[Z])],
                       idx[(vs[:,X] >  ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] >  ct[Z])],
                       idx[(vs[:,X] >  ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] <= ct[Z])],
                       idx[(vs[:,X] >  ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] >  ct[Z])]]

            submns = [[mn[X], mn[Y], mn[Z]], [mn[X], mn[Y], ct[Z]],
                      [mn[X], ct[Y], mn[Z]], [mn[X], ct[Y], ct[Z]],
                      [ct[X], mn[Y], mn[Z]], [ct[X], mn[Y], ct[Z]],
                      [ct[X], ct[Y], mn[Z]], [ct[X], ct[Y], ct[Z]]]

            submxs = [[ct[X], ct[Y], ct[Z]], [ct[X], ct[Y], mx[Z]],
                      [ct[X], mx[Y], ct[Z]], [ct[X], mx[Y], mx[Z]],
                      [mx[X], ct[Y], ct[Z]], [mx[X], ct[Y], mx[Z]],
                      [mx[X], mx[Y], ct[Z]], [mx[X], mx[Y], mx[Z]]]
            ts[0] += time.time() - t
            
            iwidth.append(iwidth[-1]+1)
            for subidx, submn, submx in zip(subidxs, submns, submxs):
                old_fofrec(subidx, submn, submx)
            iwidth.pop()
            
            t = time.time()
            if len(idx) > 0:
                c.stroke(pyx.path.line(f*ct[X], f*mn[Y], f*ct[X], f*mx[Y]),
                         [lwidth[iwidth[-1]]])
                c.stroke(pyx.path.line(f*mn[X], f*ct[Y], f*mx[X], f*ct[Y]),
                         [lwidth[iwidth[-1]]])
                c.stroke(pyx.path.circle(f*ct[X], f*ct[Y], 0.01))
            ts[1] += time.time() - t
                         
            # Find particles near cut planes
            t = time.time()
            ibndry = idx[((vs[:,X] > ct[X]-l) & (vs[:,X] <= ct[X]+l)) | 
                         ((vs[:,Y] > ct[Y]-l) & (vs[:,Y] <= ct[Y]+l)) |
                         ((vs[:,Z] > ct[Z]-l) & (vs[:,Z] <= ct[Z]+l)) ]
            ts[2] += time.time() - t

            t = time.time()
            haloNums = list(set(idxHalo[ibndry]))
            idxSet = set(idx)
            haloEdges = [list(idxSet.intersection(set(haloList[ih]))) for ih in haloNums]
            ts[3] += time.time() - t

            t = time.time()
            adj_matrix = np.zeros((len(haloNums), len(haloNums)), dtype=bool)
            for i in range(len(haloNums)):
                for j in range(len(haloNums)):                    
                    adj_matrix[i,j] = l >= all_norms(v[haloEdges[i]], v[haloEdges[j]]).min()
            if iwidth[-1] == 0: print time.time() - t, len(haloNums), [len(haloList[h]) for h in haloNums]
            ts[4] += time.time() - t

            t = time.time()
            adj = nu.graph.GraphMatrix(matrix=adj_matrix)            
            theTc = nu.graph.tc(adj).asmatrix()
            ts[5] += time.time() - t

            t = time.time()
            for i in range(len(haloNums)):
                js = np.nonzero(theTc[i, i+1:])[0]
                if len(js) > 0:
                    j = js[0] + i + 1
                    # TODO deadHalo = idxHalo[idx[i]]
                    idxHalo[haloList[haloNums[i]]] = haloNums[j]
                    haloList[haloNums[j]] += haloList[haloNums[i]]
                    haloList[haloNums[i]] = []
            ts[6] += time.time() - t
            
    v = np.asarray(v)
    c = pyx.canvas.canvas()
    f = 10.0/(v.max(axis=0) - v.min(axis=0)).max()
    lw = pyx.style.linewidth
    lwidth = [lw.Thick, lw.thick, lw.normal, lw.thin, lw.Thin, lw.THin, lw.THIn] + 100*[lw.THIN]
    iwidth = [0]
    maxdepth = [0]
    ts = np.zeros(100)
    X,Y,Z = 0,1,2
    idxHalo = np.arange(len(v), dtype=np.int32)
    haloList = np.zeros(len(v), 'O')
    for i in xrange(len(v)):
        haloList[i] = [i]

    mns = np.array(v.shape[1]*[v.min()])
    mxs = np.array(v.shape[1]*[v.max()])
    old_fofrec(np.arange(len(v), dtype='i'), mns, mxs)
    print ts[0:12]
    print "MAXDEPTH", maxdepth[0]
    return idxHalo, haloList, c

def old_fof_2(v, l, theN=1):
    """Friend-of-friend algorithm"""
    def old_fofrec(idx, mn, mx):
        cntr[0] += 1
        # Free variables: x, idxHalo, haloList, nextHalo, l
        #mn, mx = np.asarray(mn), np.asarray(mx)        
        if idx.shape[0] > 1:
            # t = time.time()
            #vs = v[idx].transpose()
            vs = v[:,idx]
            ct = [0.5*(mx[i] + mn[i]) for i in (0,1,2)]
            # ts[0] += time.time() - t
            #ct = 0.5*(mx + mn)
            
#             subidxs = [idx[(vs[:,X] <= ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] <= ct[Z])],
#                        idx[(vs[:,X] <= ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] >  ct[Z])],
#                        idx[(vs[:,X] <= ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] <= ct[Z])],
#                        idx[(vs[:,X] <= ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] >  ct[Z])],
#                        idx[(vs[:,X] >  ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] <= ct[Z])],
#                        idx[(vs[:,X] >  ct[X]) & (vs[:,Y] <= ct[Y]) & (vs[:,Z] >  ct[Z])],
#                        idx[(vs[:,X] >  ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] <= ct[Z])],
#                        idx[(vs[:,X] >  ct[X]) & (vs[:,Y] >  ct[Y]) & (vs[:,Z] >  ct[Z])]]
# t = time.time()
            xl, xh = vs[X] <= ct[X], vs[X] >  ct[X]
            yl, yh = vs[Y] <= ct[Y], vs[Y] >  ct[Y]
            zl, zh = vs[X] <= ct[X], vs[X] >  ct[X]                        
            # ts[1] += time.time() - t
                                               
            # t = time.time()
            subidx = np.array(idx, copy=1)
            nums = np.zeros(len(idx), dtype=bool)
            lens = []
            nums[:] = xl & yl & zl
            lens.append(nums.sum())
            subidx[:lens[-1]] = idx[nums]
            nums[:] = xl & yl & zh
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]
            nums[:] = xl & yh & zl
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]
            nums[:] = xl & yh & zh
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]
            nums[:] = xh & yl & zl
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]
            nums[:] = xh & yl & zh
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]
            nums[:] = xh & yh & zl
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]
            nums[:] = xh & yh & zh
            lens.append(lens[-1] + nums.sum())
            subidx[lens[-2]:lens[-1]] = idx[nums]

            # ts[2] += time.time() - t

            # t = time.time()
            submns = [[mn[X], mn[Y], mn[Z]], [mn[X], mn[Y], ct[Z]],
                      [mn[X], ct[Y], mn[Z]], [mn[X], ct[Y], ct[Z]],
                      [ct[X], mn[Y], mn[Z]], [ct[X], mn[Y], ct[Z]],
                      [ct[X], ct[Y], mn[Z]], [ct[X], ct[Y], ct[Z]]]
            # ts[3] += time.time() - t
            # t = time.time()
            submxs = [[ct[X], ct[Y], ct[Z]], [ct[X], ct[Y], mx[Z]],
                      [ct[X], mx[Y], ct[Z]], [ct[X], mx[Y], mx[Z]],
                      [mx[X], ct[Y], ct[Z]], [mx[X], ct[Y], mx[Z]],
                      [mx[X], mx[Y], ct[Z]], [mx[X], mx[Y], mx[Z]]]
            # ts[4] += time.time() - t

            # t = time.time()
            nls, nhs = lens[:-1], lens[1:]
            # ts[5] += time.time() - t

            for nl, nh, submn, submx in zip(nls, nhs, submns, submxs):
                if nl != nh:
                    old_fofrec(subidx[nl:nh], submn, submx)

    v = np.asarray(v)
    mns = np.array(v.shape[1]*[v.min()])
    mxs = np.array(v.shape[1]*[v.max()])
    ts = np.zeros(100)
    X,Y,Z = 0,1,2
    cntr = [0]
    v = v.transpose()
    old_fofrec(np.arange(v.shape[1], dtype='i'), mns, mxs)
    print ts
    print cntr

##################################################
## Roving sphere algorithm via Klypin
    
def allspheres(vs):
    """Playing around with Klypin bound-density-maximum halo finding algorithm"""
    vs = np.asarray(vs)
    N = vs.shape[0]
    ns = np.logspace(7,4,7).astype('i')
    stuff = None
    result = []
    for n in ns:
        ms = np.ones(N)
        # m=n => assume particles have unity mass
        final, stuff = spheres(vs, ms, m=n, stuff=stuff)
        result.append((n, final))
        #util.can(result, 'gsn.dat')
    return result

def dmspheres(vs, n=None, l=None, stuff=None, delta = 500, factor=10,
            precision=0.05, nTot=None, centers=None, nMean=8.0, verbose=True):
    """Playing around with Klypin bound-density-maximum halo finding algorithm"""
    # n is desired number of particles in a halo
    vs = np.asarray(vs)
    N, nDim = vs.shape
    mn, mx = vs.min(axis=0), vs.max(axis=0)
    vol = reduce(operator.mul, mx - mn)
    # print "Beware, must use cosmologically average region"
    if l and n or not l and not n: raise ValueError
    elif not l: l = (4*np.pi*nMean*delta/(3.0*n))**(-0.333)
    elif not n: n = 4*np.pi*nMean*delta*l**3/3.0
    nExp = np.ceil(N/(n*np.log(N)))

    if stuff is None:
        idx = np.arange(len(vs))
        six, siy, siz = [vs[:,i].argsort() for i in (0,1,2)]
        xvs, yvs, zvs = [vs[si,i] for si,i in ((six,0), (siy,1), (siz,2))]
        ix, iy, iz = [idx[si] for si in (six, siy, siz)]
        stuff = idx, six, siy, siz, xvs, yvs, zvs, ix, iy, iz 
    else:
        idx, six, siy, siz, xvs, yvs, zvs, ix, iy, iz = stuff

    if nTot:
        nExp = nTot
        factor=1
    print "N, l, nExp, nExp = ", N, l, N/(n*np.log(N)), nExp

    ms = np.ones(len(vs))
    if centers is None:
        centers = vs[(N*np.random.rand(nExp*factor)).astype(np.int32)]
    else:
        centers = np.asarray(centers)
    ixls = xvs.searchsorted(centers[:,0] - 4*l)
    ixhs = xvs.searchsorted(centers[:,0] + 4*l)
    iyls = yvs.searchsorted(centers[:,1] - 4*l)
    iyhs = yvs.searchsorted(centers[:,1] + 4*l)
    izls = zvs.searchsorted(centers[:,2] - 4*l)
    izhs = zvs.searchsorted(centers[:,2] + 4*l)
    result = []
    for c, ixl, ixh, iyl, iyh, izl, izh in zip(centers, ixls, ixhs, iyls, iyhs, izls, izhs):
        lastC = c + l
        origC = c
        theVs = vs[np.intersect1d(np.intersect1d(ix[ixl:ixh], iy[iyl:iyh]),
                               iz[izl:izh])]
        while mag(c - lastC) > precision*l:
            if mag(c - origC) > 3*l:
                ixl, ixh = xvs.searchsorted([c[0]-2*l, c[0]+2*l])
                iyl, iyh = yvs.searchsorted([c[1]-2*l, c[1]+2*l])
                izl, izh = zvs.searchsorted([c[2]-2*l, c[2]+2*l])
                ivs = np.intersect1d(np.intersect1d(ix[ixl:ixh], iy[iyl:iyh]),
                                  iz[izl:izh])
                theVs = vs[ivs]
                origC = c

            lastC = c
            ws =  theVs[mag(theVs - c) < l]
            c = centerOfMass(ws, ms[0:len(ws)])                    
        if verbose: print "n, delta = %3d, %0.2f" % (len(ws), (len(ws)/(4*np.pi*l**3/3.0))/(nMean))
        if (len(ws)/(4*np.pi*l**3/3.0))/(nMean) > 100.0:
            result.append((c, (len(ws), l, (len(ws)/(4*np.pi*l**3/3.0))/(nMean))))

    # ensure uniqueness
    centers = np.array([r[0] for r in result])
    if len(centers)==0:
        return [], stuff
    ds = all_norms(centers, centers)
    # include in result if
    final = []
    for i in xrange(len(ds)):
        sames = np.nonzero(ds[i] < 0.5*l)[0]
        if len(sames) > 0:
            if sames[0] >= i:
                final.append(result[i])
    return final, stuff

def makeUnique(hs):
    """Ensure that halo spheres are unique.  

    Takes results from spheres"""
    # Sort based on delta
    hs = sorted(hs, key=lambda x: x[1][0], reverse=True)
    # ensure uniqueness
    centers = np.array([h[0] for h in hs])
    if len(centers)==0:
        return []
    ds = all_norms(centers, centers)
    # include in result if
    final = []    
    for i in xrange(len(ds)):
        sames = at(ds[i] < hs[i][1][1])[0]
        if len(sames) > 0:
            if sames[0] >= i:
                final.append(hs[i])
    return final

def spheres(vs, ms, m=None, l=None, stuff=None, delta = 200, factor=10,
            precision=0.05, nTot=None, centers=None, rhoMean=8.0, delta_min=100.0,
            verbose=True):    
    """Playing around with Klypin bound-density-maximum halo finding algorithm"""
    # n is desired number of particles in a halo
    vs,ms = np.asarray(vs), np.asarray(ms)
    N, nDim = vs.shape
    mn, mx = vs.min(axis=0), vs.max(axis=0)
    vol = reduce(operator.mul, mx - mn)
    if verbose: print "Beware, must use cosmologically average region"
    if l and m or not l and not m: raise ValueError
    elif not l: l = (4*np.pi*rhoMean*delta/(3.0*m))**(-0.333)
    elif not m: m = 4*np.pi*rhoMean*delta*l**3/3.0

    voll = 4*np.pi*l**3/3.0    
    nExp = np.ceil(ms.sum()/(m*np.log(len(ms))))

    if stuff is None:
        #idx = np.arange(len(vs))
        six, siy, siz = [vs[:,i].argsort() for i in (0,1,2)]
        xvs, yvs, zvs = [vs[si,i] for si,i in ((six,0), (siy,1), (siz,2))]
        #ix, iy, iz = [idx[si] for si in (six, siy, siz)]
        stuff = six, siy, siz, xvs, yvs, zvs, # ix, iy, iz
    else:
        #idx, six, siy, siz, xvs, yvs, zvs, ix, iy, iz = stuff
        six, siy, siz, xvs, yvs, zvs = stuff

    if nTot:
        nExp = nTot
        factor=1

    if verbose: print "l, nExp = ", l, nExp

    if centers is None:
        centers = vs[(N*np.random.rand(nExp*factor)).astype(np.int32)]
    else:
        centers = np.asarray(centers)
    ixls = xvs.searchsorted(centers[:,0] - 4*l)
    ixhs = xvs.searchsorted(centers[:,0] + 4*l)
    iyls = yvs.searchsorted(centers[:,1] - 4*l)
    iyhs = yvs.searchsorted(centers[:,1] + 4*l)
    izls = zvs.searchsorted(centers[:,2] - 4*l)
    izhs = zvs.searchsorted(centers[:,2] + 4*l)
    result = []
    for c, ixl, ixh, iyl, iyh, izl, izh in zip(centers, ixls, ixhs, iyls, iyhs, izls, izhs):
        lastC = c + l
        origC = c
        ivs = np.intersect1d(np.intersect1d(six[ixl:ixh], siy[iyl:iyh]),
                          siz[izl:izh])
        theVs = vs[ivs]
        theMs = ms[ivs]
        while mag(c - lastC) > precision*l:
            if mag(c - origC) > 3*l:
                ixl, ixh = xvs.searchsorted([c[0]-2*l, c[0]+2*l])
                iyl, iyh = yvs.searchsorted([c[1]-2*l, c[1]+2*l])
                izl, izh = zvs.searchsorted([c[2]-2*l, c[2]+2*l])
                ivs = np.intersect1d(np.intersect1d(six[ixl:ixh], siy[iyl:iyh]),
                                  siz[izl:izh])
                theVs = vs[ivs]
                theMs = ms[ivs]
                origC = c

            lastC = c
            
            inside = mag(theVs - c) < l
            ws =  theVs[inside]
            mws = theMs[inside]
            c = centerOfMass(ws, mws)                    
        thisDelta = mws.sum()/(rhoMean*voll)
        if verbose: print "m, delta = %0.2g e10, %0.2g" % (mws.sum(), thisDelta)
              
        if thisDelta > delta_min:
            result.append((c, (mws.sum(), l, thisDelta)))

    # Sort based on delta
    result = sorted(result, key=lambda x: x[1][2], reverse=True)
    # ensure uniqueness
    centers = np.array([r[0] for r in result])
    if len(centers)==0:
        return [], stuff
    ds = all_norms(centers, centers)
    # include in result if
    final = []    
    for i in xrange(len(ds)):
        sames = np.nonzero(ds[i] < 0.5*l)[0]
        if len(sames) > 0:
            if sames[0] >= i:
                final.append(result[i])
    return final, stuff
    
##################################################
def moi(rs, ms=None):
    """Moment of inertia"""
    if ms is None: ms = np.ones(len(rs))
    else: ms = np.asarray(ms)
    rs = np.asarray(rs)
    N = rs.shape[1]
    # Matrix is symmetric, so inner/outer loop doesn't matter
    return [[(ms*rs[:,i]*rs[:,j]).sum()/ms.sum()
             for i in range(N)] for j in range(N)]

# import properties
# def theEval(rs, ms, axes=np.ones(3)):
#     axes = np.asarray(axes)
#     # print np.array(moi(rs, ms)/outer(axes,axes))
#     return [(moi(rs, ms)/outer(axes,axes) - np.identity(3)).std()] + \
#            properties.fastYlmLs(None,dict(y=properties.ylmCoefs(rs, ms, axes=axes,L=2)))[1:]
    
def theFunc(N, axes=np.ones(3), **kw):    
    """Don't remember what this is supposed to do..."""
    ms = np.ones(N)
    rs = np.random.randn(N,3)*axes
    result = []
    result.append([0] + theEval(rs, ms, axes))

    # rs = eulerActive(rs, *angles) + v
    for tol in (1e-1, 1e-2, 1e-3, 1e-4):
        ax, m = ellipticity(rs, ms, tolerance=tol, **kw)
        print ax/ax.max()
        rps = affineXForm(m, rs)

        result.append([tol] + theEval(rps, ms, axes))
    return result

def mc(N=10, Np=1000, ax=[20,5,1]):
    """Compute spherical harmonic coefficients for random particle
    distribution to characterize performance and errors."""
    ms = np.ones(Np)
    s1, s2, s3 = [], [], []
    for i in range(N):
        rs = np.random.randn(Np, 3)*ax
        rs = eulerActive(rs, *(2*np.pi*np.random.rand(3))) + 10*np.random.rand(3)
        r1, r2, r3 = [], [], []
        for w in (True, False):
            for s in (True, False):
                for y in (True, False):
                    for r in (True, False):
                        v1, v2, v3 = coefs(rs, ms, w, s, y, r)
                        r1.append(v1)
                        r2.append(v2)
                        r3.append(v3)
        s1.append(r1)
        s2.append(r2)
        s3.append(r3)
    return s1, s2, s3
        
                        
def coefs(rs, ms, weighted, shell, ylmscaled, removeCom):
    """Compute spherical harmonic coefficients"""
    if shell: fin = 0.4
    else: fin = 0.0
    fout = 0.5
    kw = dict(fraction=(fin, fout))

    ax, m = ellipticity(rs, ms, weighted=weighted, **kw)
    rps = affineXForm(m, rs)
    In = insideShell(rps, ms, axes=ax[1], fin=fin, fout=fout)
    if ylmscaled: rps = rps/ax[1]
    if removeCom: rps = rps - centerOfMass(rps[In], ms[In])
    junk, ths, phis = nu.spherical(rps[In][:,0], rps[In][:,1], rps[In][:,2])
    l1 = nu.rms([scipy.special.ry(1,im,ths, phis).sum()/len(ms[In])
                 for im in (-1, 0, 1)])    
    l2Or = nu.rms([scipy.special.ry(2,im,ths, phis).sum()/len(ms[In])
                   for im in (-2,-1,1)])
    l2ax = nu.rms([scipy.special.ry(2,im,ths, phis).sum()/len(ms[In])
                   for im in (0,2)])
    return l1, l2ax, l2Or
    
    
def shapeVsRadius(rs, ms, mBins=10, **kw):
    """Compute shape from ellipticity() as a function of radius"""
    mBins = nu.findEdges(mBins, [0,0.9])
    axs, mats = [], []
    
    for fin, fout in zip(mBins[:-1], mBins[1:]):
        ax, m = ellipticity(rs, ms, fraction=[fin, fout], **kw)
        axs.append(ax); mats.append(m)

    # label by outer mass fraction
    return mBins[1:], axs, mats

def kNN(vs, k):
    """k nearest neighbor"""
    vs = np.asarray(vs)
    result = []
    for v in vs:
        dists = mag(vs-v)
        dists.sort()
        result.append(dists[k])
    return np.array(result)

fast_kNN = util.memoize(kNN)

##################################################
## Spherical Harmonics
##################################################
def ylmCoefsVsRadius(rs, ms, mBins, axesList, matList, L=4):
    """Half mass spherical harmonic coefficients"""
    lmResults = []
    lResults = []
    fins = np.concatenate(([0], mBins[:-1]))
    for fin, fout, axes, mat in zip(fins, mBins, axesList, matList):
        rps = affineXForm(mat, rs)
        lmCoefs = ylmCoefs(rps, ms, L=L, fin=fin, fout=fout, axes=axes)
        lmResults.append(lmCoefs)
        lResults.append([np.sqrt((np.array(mCoefs)**2).sum()) for mCoefs in lmCoefs])

    return [np.array([lmResult[i] for lmResult in lmResults]) for i in range(L+1)], lResults

def ylmCoefs(rs, ms ,L=4, fin=0.0, fout=0.5, axes=[1,1,1]):
    """Half mass spherical harmonic coefficients"""
    # Order the m values this way to allow intuitive access of negative m values
    def mrange (l): return range(0,l+1) + range(-l, 0)
    ms, rs = np.asarray(ms), np.asarray(rs)
    In = insideShell(rs, ms, axes=axes, fin=fin, fout=fout)
    mIn = ms[In]
    rIn = rs[In] - centerOfMass(rs[In], mIn)
    r, th, phi = nu.spherical(*np.transpose(rIn/axes))
    return [[(mIn*scipy.special.ry(l,m,th,phi)).sum()/mIn.sum()
             for m in mrange(l)] for l in range(L+1)]

def ylm_to_yl(ylm):
    """Take y[l][m] values and make a y[l] array"""
    return [np.sqrt((np.array(yl)**2).sum()) for yl in ylm]

##################################################
## Rickety
def disk_mass(rs, vs, ms, r_tot, m_tot, reff, G=1.0):
    """Identify a disk within a particle distribution.

    A disk is defined to be particles that are within half a
    kiloparsec of the midplane, rotating at at least half the circular
    velocity, and have v_phi at least 80% of the total |v|.

    """
    def find_disk(vphi):
        return (vphi/vc > 0.5) & (vphi/mag(vs) > 0.8) & (abs(rs[:,2]) < 0.5) 

    rs, vs, ms = [np.asarray(ar) for ar in rs, vs, ms]
    mags = mag(rs)
    vc = np.sqrt(G*massProfile(r_tot, m_tot, rEdges=mags) / mags)
    
    R,th,phi,v_R,v_th,v_phi = to_spherical(rs, vs)

    # Flip sign of v_phi if it's (predominantly) negative
    if v_phi.mean() < 0: v_phi = -v_phi
    
    return ms[find_disk(v_phi)].sum() - ms[find_disk(-v_phi)].sum()
                  
def stellar_disk_mass(d,p):
    """Find disk of stars"""
    d.toBodyCoordinates(p)
    return disk_mass(d.rs, d.vs, d.ms,
                     np.concatenate((d.rd, d.rs, d.rg)),
                     np.concatenate((d.md, d.ms, d.mg)), p['reff'])

def stellar_disk_fraction(d,p):
    """Mass fraction of stars in disk"""
    return stellar_disk_mass(d,p)/d.ms.sum()


# binned data, just fit for h1, h2=0
def good_moments(vlos, gh_moments=True):    
    """Fit gaussian plus higher order moments to a velocity distribution

    The higher order moments are H3 and H4, moments of Hermit polynomials."""
    if len(vlos) is 0:
        print "good_moments got empty list!"
        # TODO 1/0
        return [1., 0., 1., 0., 0.]
    if len(vlos) is 1: return [1., vlos[0], 1., 0., 0.]
    if len(vlos) is 2: return [1., 0.5*(vlos[0]+vlos[1]), abs(vlos[0]-vlos[1]), 0., 0.]    

    mn=min(vlos)
    mx=max(vlos)
    # FIXME would be nice not to have to bin...
    # If range is zero, just return simple values.
    # This is mostly necessary for bootstrapping w/ few particles.
    if mn==mx:
        return [1., vlos[0], 0., 0., 0.]
    the_bins=np.linspace(2*mn-mx, 2*mx-mn, 150)
    ys,xs=nu.histo(vlos,the_bins)
    # Shift x's to bin centers, not edges
    xs += xs[1]-xs[0]
    # FIXME FIXME FIXME
    dys = np.where(ys>0, np.sqrt(ys), 1)
    dys = 0*ys + 1.0
    
    dx = xs[1]-xs[0]
    norm = sum(ys)*dx
    ys=ys/norm
    dys = dys/norm

    # parameters: norm, mean, sig, h0, h1, h2, h3, h4
    if gh_moments: param_mask = np.array([1,1,1,0,0,0,1,1])
    else:          param_mask = np.array([1,1,1,0,0,0,0,0])
    p0 = [1.,np.mean(vlos),np.std(vlos),1, 0., 0., 0.,0.]

    result = levenberg_marquardt(los_vel_dist, xs,ys,dys,p0, verbose=0,
                                 parameter_mask=param_mask)
    # FIXME - maintain old interface:
    return np.take(result[0], [0,1,2,6,7])

