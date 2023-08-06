import copy as copy_module
import types

import scipy
import numpy as np
import gsn_util as util

import gsn_numpy_util as nu

try:
    import pyx
    have_pyx = True
except ImportError:
    have_pyx = False

##################################################
# Graph representations
# Decision about representation of adj lists made here
def normalize_adj_list(adj_list):
    "Turn an adjacency list into a cannonical form"
    # This should represent a deep copy.
    return [ set(el) for el in adj_list]

class Graph (object):
    """Simple class representing a graph

    It doesn't do much other than give you the adjacency list or
    matrix, as you desire.

    """
    @classmethod
    def from_equivalence(cls, eq):
        "Make a graph from an equivalence class object."""
        mat = np.zeros((len(eq), len(eq)))

        sets = eq.finalize()        
        for set in sets:
            for e1 in set:
                for e2 in set:
                    mat[e1, e2] = mat[e2, e1] = 1
        return cls(matrix=mat)

    # Interface
    def __init__(self, matrix=None, list=None): pass
    def __len__(self): pass
    def __eq__(self, h): pass
    def from_matrix(self, adj_list): pass
    def from_list(self, adj_list): pass
    def aslist(self): pass
    def asmatrix(self): pass

class GraphMatrix (Graph):
    def __init__(self, matrix=None, list=None):
        """Make a Graph that uses an adjacency matrix for internal
        respresentation.  Usually you don't expose this kind of thing
        but I"m defining this to do performance studies so it matters.
        You can supply either the adjacency matrix or the adjacency
        list to create the graph.

        """
        if not (matrix is None or list is None): raise SyntaxError
        if matrix is not None: self.from_matrix(matrix)
        if list is not None: self.from_list(list)

    def __len__(self): return len(self._adj)
    def __eq__(self, h): return (self._adj == h.asmatrix()).all()
        
    # Can be expensive
    def from_matrix(self, adj_matrix): 
        """Create the graph from an adjacency matrix."""
        self._adj = np.asarray(adj_matrix)
    def from_list(self, adj_list): 
        """Create the graph from an adjacency list."""
        self._adj = to_adj_matrix(adj_list)

    # Should be cheap, but must return a copy of the representation
    def asmatrix(self): 
        """Return the graph as an adjacency matrix."""
        return np.array(self._adj)
    def aslist(self): 
        """Return the graph as an adjacency list."""
        return to_adj_list(self._adj)

class GraphList (Graph):
    def __init__(self, list=None, matrix=None):
        if not (matrix is None or list is None): raise SyntaxError
        if list is not None: self.from_list(list)
        if matrix is not None: self.from_matrix(matrix)
    
    def __len__(self): return len(self._adj)
    def __eq__(self, h): return self._adj == h.aslist()
        
    # can be expensive
    def from_matrix(self, adj_list): 
        """Create the graph from an adjacency matrix."""
        self._adj = to_adj_list(adj_list)
    def from_list(self, adj_list): 
        """Create the graph from an adjacency list."""
        self._adj = normalize_adj_list(adj_list)

    # should be cheap, but must return a copy of the representation
    def aslist(self): 
        """Return the graph as an adjacency list."""
        return normalize_adj_list(self._adj)
    def asmatrix(self): 
        """Return the graph as an adjacency matrix."""
        return to_adj_matrix(self._adj)

def to_adj_list(adj_matrix):    
    """Convert an adjacency matrix to an adjancency list."""
    adj_matrix = np.asarray(adj_matrix)
    return normalize_adj_list([ np.nonzero(row)[0]
                                for row in adj_matrix])

def to_adj_matrix(adj_list):
    """Convert an adjacency list to an adjancency matrix."""
    # Could conceivably store these as sets, lists, or as arrays
    n = len(adj_list)
    mat = np.zeros((n,n))
    for i in xrange(n):
        mat[i,list(adj_list[i])] = 1
    return mat
        
##################################################
## Everthing below here should use graph, asmatrix, aslist
def n_groups(graph, tc_fn=None):
    """Find the number of connected subgraphs by computing the transitive
    closure.

    """
    # identify groups by the minimum id in the adjacency list
    if tc_fn is None: tc_fn = tc

    adj_list, found = tc_fn(graph).aslist(), set()
    for lst in adj_list:
        found.add(min(lst))
    return len(found)

##################################################
## Transitive Closure

# Manifestly correct TC algorithm
def very_slow_tc(graph):
    """Compute the transitive closure"""
    adj, N = graph.asmatrix(), len(graph)

    done = False
    while (not done):
        done = True
        for i in xrange(N):
            for j in xrange(N):
                for k in xrange(N):                    
                    if not adj[i,j] and adj[i,k] and adj[k, j]:
                        done = False
                        adj[i,j] = True
    return GraphMatrix(matrix=adj)

# Somewhat faster tc algorithm
def slow_tc(graph):
    """Compute the transitive closure"""
    adj, N = graph.asmatrix(), len(graph)

    for k in xrange(N):                    
        for i in xrange(N):
            if adj[i,k]:
                for j in xrange(N):
                    if adj[i,k] and adj[k, j]:
                        adj[i,j] = True
    return GraphMatrix(matrix=adj)

# Reasonably fast pure python TC
def py_tc(graph):
    """Compute the transitive closure"""
    adj, n = np.array(graph.asmatrix(), dtype=bool), len(graph)
    for k in xrange(n):
        for i in xrange(n):
            if adj[i,k]:
                adj[i,:] |= adj[k,:]
    return GraphMatrix(matrix=adj)

# Fastest TC
def tc(graph):
    """Compute the transitive closure"""
    code = """
int i,j,k;
for (k=0; k < n; k++) 
  for (i=0; i < n; i++) 
    if (adj(i,k))
      for (j=0; j < n; j++)
        if (adj(k,j))
          adj(i,j) = 1;
"""
    adj = np.array( graph.asmatrix().astype(np.bool_), dtype=np.int8)
    n = len(graph)
    scipy.weave.inline(code, ['adj', 'n'], type_converters=scipy.weave.converters.blitz)
    return GraphMatrix(matrix=adj.astype(bool))

# TC w/o adjacency matrix
def py_list_tc(graph):
    """Compute the transitive closure"""
    adj_list, N = graph.aslist(), len(graph)

    for k in xrange(N):
        for i in xrange(N):
            if k in adj_list[i]:
                for j in xrange(N):
                    if j in adj_list[k]:
                        adj_list[i].add(j)
    return GraphMatrix(list=adj_list)

# TC w/o adjacency matrix
def list_tc(graph):
    """Compute the transitive closure"""
    code = """
int i,j,k;
PyObject *pj, *pk, *piset, *pkset;
for (k=0; k < n; k++) {    
  pk = Py_BuildValue("i", k);    
  pkset = PyList_GetItem(adj_list, k);  
  for (i=0; i < n; i++) {
    piset = PyList_GetItem(adj_list, i);  
    if (PySet_Contains(piset,pk)) {
      for (j=0; j < n; j++) {
        pj = Py_BuildValue("i", j);
        if (PySet_Contains(pkset, pj)) {
          PySet_Add(piset, pj);
        }
      }
    }
  }
}
"""
    adj_list, n = graph.aslist(), len(graph)
    scipy.weave.inline(code, ['adj_list', 'n'])
    return GraphMatrix(list=adj_list)

# TC by mulitplying bit matricies, possibly competitive for dense graphs
def bit_tc(graph, nBit=32):
    """Compute the transitive closure"""
    bool_adj, N = np.array(graph.asmatrix(), np.bool_), len(graph)
    adj = np.array(nu.bitmat(bool_adj, nBit=nBit))

    for k in xrange(N):
        kidx = int(np.floor(k/float(nBit)))
        for i in xrange(N):
            if adj[i, kidx] & (1 << k - nBit*kidx):
                adj[i] |= adj[k]
    return GraphMatrix(matrix=nu.boolmat(adj, size=N))

# TC w/ adjacency list
def particle_tc3(vs, l, f=1):
    """Define groups of particles via the 'Friends of frinds' algorithm,
    where particles are 'friends' if they're separated by less then
    the distance l.  This is the same thing as the transitive closure
    of the similarly defined graph.

    """
    vs = np.asarray(vs)
    adjList = [set(np.nonzero(l >= np.sqrt(((vs - vs[i])**2).sum(axis=-1)))[0])
               for i in xrange(len(vs)/f)]
    return adjList
    #return particle_tc1(adjList)

# TC w/ adjacency list
def particle_tc4(vs, l, f=1):
    """Define groups of particles via the 'Friends of frinds' algorithm,
    where particles are 'friends' if they're separated by less then
    the distance l.  This is the same thing as the transitive closure
    of the similarly defined graph.

    """
    vs = np.asarray(vs)
    idx = np.arange(len(vs))
    six, siy, siz = [vs[:,i].argsort() for i in (0,1,2)]
    xvs, yvs, zvs = [vs[si,i] for si,i in ((six,0), (siy,1), (siz,2))]
    ix, iy, iz = [idx[si] for si in (six, siy, siz)]

    adjList = []
    for v in vs:
        ixl, ixh = xvs.searchsorted([v[0]-l, v[0]+l])
        iyl, iyh = yvs.searchsorted([v[1]-l, v[1]+l])
        izl, izh = zvs.searchsorted([v[2]-l, v[2]+l])
        iws = np.array(list(set(ix[ixl:ixh]).intersection(iy[iyl:iyh]).intersection(iz[izl:izh])))
        adjList.append(set(iws[l >= np.sqrt(((vs[iws] - v)**2).sum(axis=-1))]))
        
    return adjList

##################################################
## Equivalence Class object with two implementations
class Equivalence(object):
    """Class representing an equivalence classes"""
    @classmethod
    def from_graph(cls, graph):
        """Create an equivalence class from a graph"""
        # ensure that it's actually an equivalence relation
        assert graph == tc(graph)

        self = cls(len(graph))
        for set in graph.aslist():
            self.make_set(set)
        return self
    
class Equivalence1(Equivalence):
    """Equivalence class data structure.  

    The fast operation is to join two groups based on arbitrary
    elements being deemed equal.  Finding all elements of a class is a
    slow operation.

    """    
    # self._sets is an np.array where self._sets[i] given another element
    # in the same class.  The id of a class is is deemed to be the
    # element with the lowest index.  Thus to find the id of a class,
    # keep finding new elements until i == self._sets[i]
    def __init__(self, n):
        self._sets, self._n = np.arange(n), n
        self._maxdepth = 1

    def __len__(self): return self._n

    def __eq__(self, other):
        self._flatten()
        other._flatten()
        return (self._sets == other._sets).all()
    
    def set(self, i):
        while self._sets[i] < i:
            i = self._sets[i]
        return i
             
    def join(self, i, j):
        seti, setj = self.set(i), self.set(j)
        self._sets[seti] = self._sets[setj] = min(seti, setj)        
            
    def make_set(self, ids):
        if type(ids) is type(set()): ids = list(ids)
        sets = [self.set(i) for i in ids]
        dest = min(sets)
        self._sets[sets] = dest

    def _flatten(self):
        for i in xrange(self._n):
            self._sets[i] = self.set(i)

    def finalize(self):
        self._flatten()
        ids = set(self._sets)
        return [ np.nonzero(self._sets == i)[0] for i in ids]

    def asgraph(self):
        adj = np.zeros((self._n,self._n))
        for set in self.finalize():
            for el1 in set:
                for el2 in set:
                    adj[el1, el2] = True
        return GraphList(matrix=adj)

class Equivalence2(Equivalence):
    """Equivalence class data structure.  

    The fast operation is to join two groups based on arbitrary
    elements being deemed equal.  Finding all elements of a class is a
    slow operation.

    """
    def __init__(self, n):
        self._n = n
        self._id2set = np.arange(n)
        self._set2ids = [[i] for i in xrange(n)]

    def __len__(self): return self._n
        
    def set(self, i): return self._id2set[i]

    def join(self, i, j):
        if i==j: return
        iset, jset = self._id2set[i], self._id2set[j]
        if iset==jset: return
        self._id2set[self._set2ids[jset]] = iset
        self._set2ids[iset] += self._set2ids[jset]
        self._set2ids[jset] = None

    def finalize(self):
        # remove the Nones
        return [el for el in self._set2ids if el]

    def make_set(self, ids):
        for i in ids[1:]:
            self.join(ids[0], i)
        


##################################################
### Functions used for testing and timing.
                
def rand_adj_list(n, neighbors=2):
    """Create a random adjacency list"""
    # f = average fraction of population to which each entry is adjacent
    # Don't allocate the entire matrix to allow large populations
    result = []
    f = neighbors/(1.0*n)
    for i in xrange(n):
        s = set(np.nonzero(np.random.rand(n) < f)[0])
        s.add(i)  # Make all entries adjacent to themselves
        result.append(s)
    return GraphMatrix(list=result)

def rand_adj_spectrum(nmax, neighbors=2, factor=2):
    """Make a spectrum of random adjacency matricies of different sizes"""
    # Spectrum in size
    assert nmax > factor**2 
    nsets = int(np.log(nmax)/np.log(factor)) - 1
    divisor = factor*np.ones(nsets)
    divisor[0] = 1
    divisor = divisor.cumprod()[::-1]
    ns = (nmax*np.ones(nsets)/divisor).astype(np.int32)
    return [rand_adj_list(n, neighbors=neighbors) for n in ns]

def rand_adj_population(nmax, neighbors=None, factor=2):
    """Make a bunch of adjacency matrix spectra, where each spectrum has a
    different level of connectivity in the graph

    """
    # Generate population of spectra.  Each member of the population
    # has a different number of averate neighbors.    
    if neighbors is None: neighbors = np.array([0, 1, 2, 3, 5, 7, 9])
    
    return [(n, rand_adj_spectrum(nmax, n, factor=factor))
            for n in neighbors]

def n_groups_spectrum(spectrum, tc_fn=None):
    """Find the number of groups for a spectrum of adjacency matricies"""
    return [ n_groups(graph, tc_fn=tc_fn)
             for graph in spectrum]

def n_groups_population(population, tc_fn=None):
    """Find the number of groups for a population of adjacency matricies
    (a function of both size and level of connectivity) returned by
    rand_adj_spectrum.

    """
    return [(nbr, n_groups_spectrum(spectrum, tc_fn=tc_fn))
            for nbr, spectrum in population]

def time_spectrum(f, spectrum, tmin=1, clock_rate=3e9):
    """Compute the transitive closure on a spectrum of adjacency matricies
    and time the computation.  clock_rate is the machine clock rate in
    Ghz, to estimate the number of instructions per particle.

    """ 
    # with the smallest dataset and run each bigger one until it takes
    # at least tmin seconds.  Report a list of tuples of size and time.
    result = []
    for graph in spectrum:
        orig_graph = copy_module.deepcopy(graph)
        size = len(graph)
        groups = n_groups(graph)
        t, n = util.timer(f, graph, timer_tmin=tmin)
        result.append((size, t, clock_rate*t/size**3,
                       clock_rate*t/size**2,
                       clock_rate*t/size,
                       groups))        
        assert graph == orig_graph
        if n == 1: break        
    return result

def time_population(f, population, tmin=1):
    """Compute the transitive closure on a population of adjacency
    matricies (returned by rand_adj_population) and time the
    computation.

    """ 
    return [(nbr, time_spectrum(f, spectrum, tmin=tmin))
            for (nbr, spectrum) in population]
    
def print_time_spectrum(result):
    """Print the results of time_spectrum()"""
    for  el in result:
        print "%7d %7.4f %7d %7d %7d %7d" % el

def print_time_population(result):
    """Print the results of time_population()"""
    for (nbr, spectrum) in result:
        print "Neighbors: ", nbr
        print_time_spectrum(spectrum)    

def tc_evaluation(tmin=1.0):
    """Evaluate different transitive closure algorithms based on timing."""
    tcs = [very_slow_tc, slow_tc, py_tc, tc, py_list_tc, list_tc, bit_tc]
    pop = rand_adj_population(1600)
    
    for tc_fn in tcs:
        print "*** ", tc_fn.__name__, " ******************************"
        print_time_population(time_population(tc_fn, pop, tmin=tmin))


def matToList(adj):
    """Old routine to translate b/t adjacency list and matrix form"""
    adj = np.asarray(adj)
    return [(np.nonzero(adj[i,:])[0]).tolist() for i in xrange(len(adj))]

def listToMat(lst):
    """Old routine to translate b/t adjacency list and matrix form"""
    mat = np.zeros((len(lst), len(lst)), dtype=bool)
    for i in xrange(len(lst)):
        mat[i, lst[i]] = True
    return mat

def listToHalos(lst):
    """Old routine to help with plotting particle based TC"""
    # assumes undirected graph...
    mat = listToMat(lst)
    assert (mat == mat.transpose()).all()
    total = []
    result = []
    for i in xrange(len(lst)):
        if len(lst[i]) > 0 and lst[i][0] not in total:
            result.append(lst[i])
            total += lst[i]
    return result

# def haloToAdj(halos):
#     if len(halos) == 2:
#         idx, haloList  = halos
#     else:
#         idx, haloList, junk  = halos
#     return idx[newaxis,:] == idx[:,newaxis]

##################################################
## Plotting graphs and transitive closures.
def plotGrid(n):
    """Plot results of transitive closure"""
    c = pyx.canvas.canvas()
    for i in range(n):
        for x in np.linspace(0,1,2**i + 1):
            c.stroke(pyx.path.line(10*x, 0, 10*x, 1-i/float(n)))
    return c

if have_pyx:
    colors = [pyx.color.gradient.Rainbow.getcolor(r) for r in np.linspace(0,1,1000)]
    colors = np.array(colors)[np.random.permutation(len(colors))]

def plotTc1d(xs, adj):
    """Plot results of transitive closure"""
    xs = np.asarray(xs)
    black = pyx.color.rgb(0,0,0)
    ys = 0.02*np.random.rand(len(xs))
    c = pyx.canvas.canvas()
    halos = listToHalos(matToList(adj))
    for halo, color in zip(halos, colors):
        for x,y in zip(xs[halo], ys[halo]):
            c.stroke(pyx.path.circle(10*x, 10*y, 0.03), [color, pyx.deco.filled([color])])
    c.stroke(pyx.path.line(0, 0, 10*0.03, 0))
    return c

def oldplotTc(vs, adj, tc):
    """Plot results of transitive closure"""
    vs,adj,ts = [np.asarray(arr) for arr in vs, adj, tc]
    f = 10.0/(vs.max(axis=0) - vs.min(axis=0)).max()
    c = pyx.canvas.canvas()
    halos = listToHalos(matToList(tc))
    for i in range(len(adj)):
        for j in range(len(adj)):
            if adj[i,j]:
                c.stroke(pyx.path.line(f*vs[i,0], f*vs[i,1],
                                       f*vs[j,0], f*vs[j,1]),
                         [pyx.style.linewidth.THIN])
    for halo, color in zip(halos, colors):
        for x,y in zip(vs[halo,0], vs[halo,1]):
            c.stroke(pyx.path.circle(f*x, f*y, 0.03), [color, pyx.deco.filled([color])])
    return c

def plot_tc(vs, adj_graph, closure):
    """Plot results of transitive closure"""
    # adj_graph is a graph representing single-level adjacency
    # closure is an equivalence relation or a graph
    vs,adj_graph,closure = [np.asarray(arr) for arr in vs,adj_graph,closure]

    if isinstance(closure, Graph):
        closure = Equivalence1.from_graph(closure).finalize()
    elif isinstance(closure, Equivalence):
        closure = closure.finalize()

    f = 10.0/(vs.max(axis=0) - vs.min(axis=0)).max()
    c = pyx.canvas.canvas()

    lst = adj_graph.tolist()
    for i in range(len(lst)):
        for j in lst[i]:
            c.stroke(pyx.path.line(f*vs[i,0], f*vs[i,1],
                                   f*vs[j,0], f*vs[j,1]),
                     [pyx.style.linewidth.THIN])

    for set, color in zip(closure, colors):
        for x,y in zip(vs[set,0], vs[set,1]):
            c.stroke(pyx.path.circle(f*x, f*y, 0.07), [color, pyx.deco.filled([color])])
    return c

##################################################
##

def bfs(g, predicate=None, pre=None, post=None, start=None, with_extra=False):
    """Simple breadth-first-seach on a graph represented by a dict.

    g is a dict representing a graph.  A sample graph is 
    dict(a=('b', 'c'), b=('a',), c=('c',)) 
    for edges a->b, a->c, b->a, and c->c

    predicate takes a vertex name and tests to see if the search
    should terminate.  pre is a function that takes a vertex name and
    is called upon arrival at the vertex.  post is a function that
    takes a vertex name and is called upon leaving a vertex.  start is
    a vertex name at which to start the search.  If with_visited is
    true, then the list of already visited verticies is also passed.
    This facilitates detection of cycles, for example.

    If predicate is supplied and ever returns true, the name of the
    successful node is returned.  Otherwise a list of visited nodes
    is returned (to facilitate searching graphs with mulitple
    components)
    """
    if start is None: start = g.keys()[0]
    visited = []
    queue = [start]
    
    while queue:
        vertex = queue.pop()
        if pre:
            if with_extra: pre(vertex, visited, queue)
            else: pre(vertex)            
        if predicate and (with_extra and predicate(vertex, visited, queue) or 
                          not with_extra and predicate(vertex)):
            return vertex
        visited.append(vertex)
        queue = [edge for edge in reversed(g[vertex]) if edge not in visited] + queue
        if post:
            if with_extra: post(vertex, visited, queue)
            else: post(vertex)
        
    return visited

def dfs(g, predicate=None, pre=None, post=None, start=None, with_visited=False):
    """Simple depth-first-search on a graph represented by a dict.

    g is a dict representing a graph.  A sample graph is 
    dict(a=('b', 'c'), b=('a',), c=('c',)) 
    for edges a->b, a->c, b->a, and c->c

    predicate takes a vertex name and tests to see if the search
    should terminate.  pre is a function that takes a vertex name and
    is called upon arrival at the vertex.  post is a function that
    takes a vertex name and is called upon leaving a vertex.  start is
    a vertex name at which to start the search.  If with_visited is
    true, then the list of already visited verticies is also passed.
    This facilitates detection of cycles, for example.

    If predicate is supplied and ever returns true, the name of the
    successful node is returned.  Otherwise a list of visited nodes
    is returned (to facilitate searching graphs with mulitple
    components)

    """
    
    def dfs_rec(vertex):
        if pre:
            if with_visited: pre(vertex, visited)
            else: pre(vertex)
        if predicate:
            if with_visited and predicate(vertex, visited) \
               or (not with_visited) and predicate(vertex):
                return vertex
        visited.append(vertex)
        for edge in g[vertex]:
            if edge not in visited:
                found = dfs_rec(edge)
                if found: return found
        if post:
            if with_visited: post(vertex, visited)
            else: post(vertex)

    visited = []
    if start is None: start = g.keys()[0]
    return dfs_rec(start) or visited

def full_search(f, g, start=None, **kw):
    """Simple search on a graph represented by a dict.  This does multiple
    searches until all of the nodes of the graph have been visited at
    least once.

    f is the search strategy, either bfs or dfs

    g is a dict representing a graph.  A sample graph is 
    dict(a=('b', 'c'), b=('a',), c=('c',)) 
    for edges a->b, a->c, b->a, and c->c

    Extra keyword args are passed to bfs or dfs

    """

    # This ensures that all nodes are visited, but does not guarantee
    # that all nodes are visited _only_ once.  That is, a random
    # starting vertex is chosen, and then a full dfs or bfs is done,
    # ensuring that each node is visited once.  Then a random
    # unvisited node is chosen, and the full search is done again.  If
    # that leads into the subgraph already searched, so be it.  This
    # could be fixed by giving dfs and bfs args of
    # already-searched-verticies.

    todo = set(g.keys())
    if start is None: start = todo.pop()
    done = False
    while not done:
        result = f(g, start=start, **kw)
        if type(result) is not types.ListType: return result
        todo.difference_update(result)
        if todo: start=todo.pop()
        else: done = True
    
def full_bfs(*a, **kw): 
    """Full breadth first search of a graph represented by dict g.  

    This does multiple searches until all of the nodes of the graph
    have been visited at least once.

    Arguments passed to full_search()
    """
    full_search(bfs, *a, **kw)

def full_dfs(*a, **kw): 
    """Full depth first search of a graph represented by dict g.  

    This does multiple searches until all of the nodes of the graph
    have been visited at least once.

    Arguments passed to full_search()
    """
    full_search(dfs, *a, **kw)

def cyclep(g):
    """Check for cycles in graph represented by dict g"""
    def pred(v, visited):
        for edge in g[v]:
            if edge in visited:
                return True
    return full_dfs(g, predicate=pred, with_visited=True)
    
def topological_sort(g):    
    """This gives a topological order in which things must be
    processed if the sense of the graph edge is 'depends on.'  This
    may be the reverse of the conventional meaning of topo sort."""
    def post(v):
        if v not in postorder: 
            postorder.append(v)    
    postorder = []
    full_dfs(g, post=post)
    return postorder

