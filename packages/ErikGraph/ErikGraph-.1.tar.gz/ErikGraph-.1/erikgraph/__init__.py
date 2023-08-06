class VertexDoesNotExist(Exception): pass

INFINITY = float('inf')

class Graph(object):
    """
    A miniature graph class.  Implements the following specification:

    A class Graph representing an undirected graph structure with weighted edges
    (i.e. a set of vertices with undirected edges connecting pairs of vertices, where each edge has a nonnegative weight).
    In addition to methods for adding and removing vertices, class Graph should define (at minimum) the following instance
    methods

    :property data: A dictionary who's keys are vertices and values are another dictionary who's keys are neighboring
        nodes and values are the weight connecting them
    """


    def __init__(self,vertices=[],edges=[]):
        """
        :param vertices: A list of vertices to initialize the graph with.
        :param edges: A list of 3-tuple edges and weights to initialize the graph with.

        >>> G = Graph(['a'],[('a','b',2),('b','c',1)])
        >>> 'b' in G.data
        True
        >>> 'c' in G.data
        True
        >>> 'd' in G.data
        False
        """
        self.data = {}
        for v in vertices:
            self.add_vertex(v)
        for e in edges:
            self.add_edge(*e)

    @property
    def vertices(self):
        "A list of vertices in the graph"
        return self.data.keys()

    def add_vertex(self,v):
        """
        :param v: A vertex

        >>> G = Graph()
        >>> G.add_vertex('a')
        >>> G.data['a']
        {}
        >>> G.data['b']
        Traceback (most recent call last):
            ...
        KeyError: 'b'
        """
        self.data.setdefault(v,{})


    def delete_vertex(self,v):
        """
        :param v: the vertex to delete

        >>> G = Graph(['x'],[('a','b',1)])
        >>> 'b' in G.data
        True
        >>> G.delete_vertex('b')
        >>> 'b' in G.data
        False
        >>> 'b' in G.neighbor_vertices('a')
        False
        """
        for neighbor in self.neighbor_vertices(v):
            del self.data[neighbor][v]
        del self.data[v]

    def add_edge(self,v1,v2,weight):
        """
        :param v1: One of the vertices the edge is connecting to.
        :param v2: The other vertex.
        :param weight: The weight associated with the edge.

        .. warning: If the edge already exists, its weight will be replaced with `weight`

        >>> G = Graph()
        >>> G.add_edge('a','b',1)
        >>> G.data['b']['a'] == 1
        True
        """
        self.data.setdefault(v1,{})[v2] = weight
        self.data.setdefault(v2,{})[v1] = weight

    def delete_edge(self,v1,v2):
        """
        :param v1: a vertex
        :param v2: a neighbor of v1
        :raises VertexDoesNotExist: if a or b are not in the graph

        >>> G = Graph(edges=[('a','b',2)])
        >>> G.neighbors('a','b')
        True
        >>> G.delete_edge('b','a')
        >>> G.neighbors('a','b')
        False
        """
        try:
            del self.data[v1][v2]
            del self.data[v2][v1]
        except KeyError:
            raise VertexDoesNotExist

    def get_edge_weight(self, a , b):
        """
        :returns: The weight of the edge connecting a to b
        :raises VertexDoesNotExist: if a or b are not in the graph

        >>> G = Graph(edges=[('a','b',2)])
        >>> G.get_edge_weight('a','b')
        2
        >>> G.get_edge_weight('a','x')
        Traceback (most recent call last):
        ...
        VertexDoesNotExist
        """
        try:
            return self.data[a][b]
        except KeyError:
            raise VertexDoesNotExist


    def neighbor_vertices(self, a):
        """
        :return: a sequence of vertices that are neighbors of vertex a (e.g. are joined by a single edge).
        :raises VertexDoesNotExist: if a is not in the graph.

        >>> G = Graph(vertices=['a'],edges=[('b','c',1),('d','c',2)])
        >>> ns = G.neighbor_vertices('c')
        >>> 'b' in ns and 'd' in ns and 'a' not in ns
        True
        >>> G.neighbor_vertices('x')
        Traceback (most recent call last):
        ...
        VertexDoesNotExist: The vertex <x> does not exist in this graph
        """
        try:
            return [e[0] for e in self.data[a]]
        except KeyError:
            raise VertexDoesNotExist, 'The vertex <{0}> does not exist in this graph'.format(a)

    def neighbors(self, a, b):
        """
        :return: True if vertices a and b are joined by an edge, and False otherwise.
        :raises VertexDoesNotExist: if a or b are not in the graph.

        >>> G = Graph(vertices=['a'],edges=[('b','c',1)])
        >>> G.neighbors('c','b')
        True
        >>> G.neighbors('a','c')
        False
        >>> G.neighbors('a','x')
        Traceback (most recent call last):
        ...
        VertexDoesNotExist: The vertex <x> does not exist in this graph
        """
        if b not in self.data: raise VertexDoesNotExist, 'The vertex <{0}> does not exist in this graph'.format(b)
        try:
            return any(( e[0] == b for e in self.data[a] ))
        except KeyError:
            raise VertexDoesNotExist, 'The vertex <{0}> does not exist in this graph'.format(a)

    def _single_source_shortest_path(self,a, b, use_weights=True):
        """
        Implements Dijstra's algorithm to determine the shortest path between vertices a and b

        :return: a 2-tuple comprising the minimum-weight path connecting vertices a and b, and the associated minimum weight.
            Return None if no such path exists.
        :raises VertexDoesNotExist: if a or b are not in the graph.
        """

        if a not in self.data or b not in self.data: raise VertexDoesNotExist

        # Keys are nodes, values are the distance from a
        distances = dict([ (v,INFINITY) for v in self.vertices ])

        # Keys are nodes, values are the previous node in the shortest path from a to b
        previous = dict([ (v,None) for v in self.vertices ])

        distances[a] = 0
        Q = self.vertices

        while len(Q):
            next_closest_vertex = min(Q, key = lambda v: distances[v])
            if distances[next_closest_vertex] == INFINITY:
                break

            if next_closest_vertex == b:
                distance = distances[b]
                # Found the shortest path!
                path = [b]
                def path_home(v):
                    if v == a:
                        return [a]
                    return  path_home(previous[v]) + [v]
                return distance, path_home(b)
            else:
                next_closest_vertex_neighbors = self.neighbor_vertices(next_closest_vertex)
                Q.remove(next_closest_vertex)

                if distances[next_closest_vertex] == INFINITY:
                    break

                for current_vertex in next_closest_vertex_neighbors:
                    add_weight = self.get_edge_weight(next_closest_vertex, current_vertex) if use_weights else 1
                    alt = distances[next_closest_vertex] + add_weight
                    if alt < distances[current_vertex]:
                        distances[current_vertex] = alt
                        previous[current_vertex] = next_closest_vertex

        return None # no path

    def minimum_weight_path(self, a, b):
        """
        Implementation of Single Source Shortest Path using Dijkstra's

        :return: a 2-tuple comprising the minimum-weight path connecting vertices a and b, and the associated minimum weight.
            Return None if no such path exists.
        :raises VertexDoesNotExist: if a or b are not in the graph.

        >>> G = Graph(vertices=['x','y'],edges=[('x','y',3),('b','c',1),('a','c',2),('c','d',6),('d','e',2),('c','e',100)])
        >>> G.minimum_weight_path('a','d')
        (8, ['a', 'c', 'd'])
        >>> G.minimum_weight_path('a','e')
        (10, ['a', 'c', 'd', 'e'])
        >>> G = Graph(vertices=['x','y'],edges=[('x','y',3),('b','c',1),('a','c',2),('c','d',4),('d','e',2),('c','e',1)])
        >>> G.minimum_weight_path('a','e')
        (3, ['a', 'c', 'e'])
        >>> G.minimum_weight_path('a','x')

        >>> G.minimum_weight_path('a','foo')
        Traceback (most recent call last):
        ...
        VertexDoesNotExist
        >>> G = Graph(edges=[('a','c',10),('b','c',2),('c','f',20),('a','d',1),('d','e',5),('e','f',16),('e','h',1),('h','f',4),('d','h',7),('d','g',2)])
        >>> G.minimum_weight_path('a','f')
        (11, ['a', 'd', 'e', 'h', 'f'])
        """
        return self._single_source_shortest_path(a,b)



    def minimum_edge_path(self, a, b):
        """
        :return: a 2-tuple comprising the minimum-edge path connecting vertices a and b, and the associated minimum number
            of edges (e.g. a path comprising 3 edges is shorter than a path comprising 4 edges, regardless of the edge weights).
            Return None if no such path exists. Raise an exception if a or b are not in the graph.
        :raises VertexDoesNotExist: if a or b are not in the graph.

        >>> G = Graph(vertices=['x','y'],edges=[('x','y',3),('b','c',1),('a','c',2),('c','d',6),('d','e',2),('c','e',100)])
        >>> G.minimum_edge_path('a','d')
        (2, ['a', 'c', 'd'])
        >>> G.minimum_edge_path('a','e')
        (2, ['a', 'c', 'e'])
        >>> G = Graph(vertices=['x','y'],edges=[('x','y',3),('b','c',1),('a','c',2),('c','d',4),('d','e',2),('c','e',1)])
        >>> G.minimum_edge_path('a','e')
        (2, ['a', 'c', 'e'])
        >>> G.minimum_edge_path('a','x')

        >>> G.minimum_edge_path('a','foo')
        Traceback (most recent call last):
        ...
        VertexDoesNotExist
        >>> G = Graph(edges=[('a','c',10),('b','c',2),('c','f',20),('a','d',1),('d','e',5),('e','f',16),('e','h',1),('h','f',4),('d','h',7),('d','g',2)])
        >>> G.minimum_edge_path('a','f')
        (2, ['a', 'c', 'f'])
        """
        return self._single_source_shortest_path(a,b,False)