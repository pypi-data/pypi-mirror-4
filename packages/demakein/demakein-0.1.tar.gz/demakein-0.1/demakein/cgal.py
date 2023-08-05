
import sys, math

import cpp

import shape

CODE = r"""
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>

#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/minkowski_sum_3.h>

#include <CGAL/Polygon_2.h>
#include <CGAL/Polygon_with_holes_2.h>
#include <CGAL/Polygon_set_2.h>

#include <vector>
#include <iostream>
#include <sstream>

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel;
//typedef CGAL::Extended_homogeneous<CGAL::Gmpz>            Kernel;
//typedef CGAL::Cartesian<CGAL::Gmpq>                       Kernel;

typedef Kernel::Point_3                                   Point_3;
typedef Kernel::Vector_3                                  Vector_3;
typedef CGAL::Polyhedron_3<Kernel>                        Polyhedron;
typedef CGAL::Nef_polyhedron_3<Kernel>                    Nef_polyhedron;
typedef Polyhedron::HalfedgeDS                            HalfedgeDS;
typedef CGAL::Aff_transformation_3<Kernel>                Aff_transformation_3;

typedef Kernel::Point_2                                   Point_2;
typedef CGAL::Polygon_2<Kernel>                           Polygon_2;
typedef CGAL::Polygon_with_holes_2<Kernel>                Polygon_with_holes_2;
typedef CGAL::Polygon_set_2<Kernel>                       Polygon_set_2;


class Build_polyhedron : public CGAL::Modifier_base<HalfedgeDS> {
public:
    std::vector<Kernel::Point_3> points;
    std::vector< std::vector<int> > facets;

    Build_polyhedron() {}
    void operator()( HalfedgeDS& hds) {
        CGAL::Polyhedron_incremental_builder_3<HalfedgeDS> B( hds, true);
         
        B.begin_surface( points.size(), facets.size() );
    
        for(std::vector<Kernel::Point_3>::iterator it = points.begin();
            it < points.end();
            it++) {
            B.add_vertex(*it);
        }
        
        for(std::vector< std::vector<int> >::iterator it = facets.begin();
            it < facets.end();
            it++) {
            B.begin_facet();
            for(std::vector<int>::iterator it1 = it->begin();
                it1 < it->end();
                it1++) {
                B.add_vertex_to_facet(*it1);
            }
            B.end_facet();
        }
        
        B.end_surface();
    }
};

"""

CMAKE_CODE = r"""

find_package(CGAL REQUIRED)

include(${CGAL_USE_FILE})

"""

M = cpp.Module('__cppcache__', CODE, CMAKE_CODE)

def int_round(value):
    return int(math.floor(value+0.5))

class Shape(object):
    """ Wrapper around Nef_polyhedron """
    
    def __init__(self, nef):
        self.nef = nef

    def copy(self):
        return Shape(M.new('Nef_polyhedron(a)',a=self.nef))

    def extent(self):
        xs = []
        ys = []
        zs = []
        for tri in self.triangles(): #Possibly slow?
            for point in tri:
                xs.append(point[0])
                ys.append(point[1])
                zs.append(point[2])
        #for vertex in M.iterate('a.vertices_begin()','a.vertices_end()',a=self.nef):
        #    point = M('a.point()',a=vertex)
        #    xs.append(M('CGAL::to_double(a.x())',a=point))
        #    ys.append(M('CGAL::to_double(a.y())',a=point))
        #    zs.append(M('CGAL::to_double(a.z())',a=point))
        return shape.Limits(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
    
    def size(self):
        xmin,xmax,ymin,ymax,zmin,zmax = self.extent()
        return xmax-xmin,ymax-ymin,zmax-zmin

    def triangles(self):
        polyhedron = M.new('Polyhedron()')
        M('a.interior().convert_to_polyhedron(b)',a=self.nef,b=polyhedron)
        
        #assert M('(int)a.is_valid(true, 3)',a=polyhedron)
        
        triangles = [ ]
        for item in M.iterate('a.facets_begin()','a.facets_end()',a=polyhedron):
            verts = [ ]
            for item2 in M.circulate('a.facet_begin()',a=item):
                point = M('a.vertex()->point()',a=item2)
                verts.append((
                     M('CGAL::to_double(a.x())',a=point),
                     M('CGAL::to_double(a.y())',a=point),
                     M('CGAL::to_double(a.z())',a=point),
                ))
                
            assert len(verts) == 3
            triangles.append(verts)
        return triangles

    def save(self, filename):
        sys.stdout.write(filename)
        sys.stdout.flush()
        triangles = self.triangles()
        with open(filename,'wb') as f:
            print >> f, 'solid'
            for tri in triangles:
                print >> f, 'facet normal 0 0 0'
                print >> f, 'outer loop'
                for vert in tri:
                    print >> f, 'vertex %f %f %f' % tuple(vert)
                print >> f, 'endloop'
                print >> f, 'endfacet'
            print >> f, 'endsolid'
        print

    def remove(self, other):
        M.do('a -= b',a=self.nef,b=other.nef)

    def add(self, other):
        M.do('a += b',a=self.nef,b=other.nef)

    def clip(self, other):
        M.do('a *= b',a=self.nef,b=other.nef)

    def inverse(self):
        return Shape(M('!a',a=self.nef))

    def minkowski_sum(self, other):
        return Shape(M('CGAL::minkowski_sum_3(a,b)',a=self.nef,b=other.nef))

    def rotate(self, x,y,z,angle, accuracy=1<<16):
        length = math.sqrt(x*x+y*y+z*z)
        x = x/length
        y = y/length
        z = z/length
        angle = angle * (math.pi/180.0)
        c = math.cos(angle)
        s = math.sin(angle)
        rot = [
            [ c+x*x*(1-c),   x*y*(1-c)-z*s, x*z*(1-c)+y*s ],
            [ y*x*(1-c)+z*s, c+y*y*(1-c),   y*z*(1-c)-x*s ],
            [ z*x*(1-c)-y*s, z*y*(1-c)+x*s, c+z*z*(1-c)   ],
        ]
        
        transform = M.call('Aff_transformation_3',
            *[ int_round(item*accuracy) for row in rot for item in row ] + [ accuracy ]
        )
        M.do('a.transform(b)',a=self.nef, b=transform)
    
    def move(self, x,y,z, accuracy=1<<16):
        transform = M('Aff_transformation_3(CGAL::TRANSLATION,Vector_3(a,b,c,d))',
            a=int_round(x*accuracy), b=int_round(y*accuracy), c=int_round(z*accuracy), d=accuracy
        )
        M.do('a.transform(b)',a=self.nef, b=transform)

    def mask(self, res):
        import mask
        
        lines = [ ]
        
        for points in self.triangles():
            points = [ (x*res,y*res) for x,y,z in points ]
            points = points + [ points[0] ]
            
            area = 0.0
            for i in range(len(points)-1):
                area += (
                    (points[i+1][0]-points[i][0])*
                    (points[i+1][1]+points[i][1])*0.5
                )
            if area > 0.0: 
                points = points[::-1]
            for i in range(len(points)-1):
                lines.append( points[i]+points[i+1] )
            
        return mask.make_mask(lines)
    
    def polygon_mask(self):
        triangles = self.triangles()
        
        things = [ create_polygon_2([ (x,y) for x,y,z in triangle ]) 
                   for triangle in triangles ]

        if not things:        
            return empty_shape_2()

        while len(things) > 1:
            item = things.pop(-1)
            things[len(things)//2].add(item)
        return things[0]
        
        
        #result = empty_shape_2()
        #for triangle in self.triangles():
        #    result.add( create_polygon_2([ (x,y) for x,y,z in triangle ]) )
        #return result
        
    
    #def show(self):
    #    app = M.new('QApplication(argc, argv)',argc=0,argv=0)
    #    widget = M('new CGAL::Qt_widget_Nef_3<Nef_polyhedron_3>(a)',a=self.nef)
    #    M.do('a.setMainWidget(b)',a=app,b=widget)
    #    M.do('a.show()',a=widget)
    #    return M('a.exec()',a=app)

def empty_shape():
    return Shape(M.new('Nef_polyhedron'))

def create(verts, tris, name=None, accuracy=1<<16):
    polyhedron = M.new('Polyhedron()')
    
    builder = M.new('Build_polyhedron()')
    
    for tri in tris:
        assert len(tri) == 3
    
    seen = set()
    for vert in verts:
        [x,y,z] = [ int_round(item*accuracy) for item in vert ]
        assert (x,y,z) not in seen
        seen.add((x,y,z))
        point = M.new('Point_3(a,b,c,d)',a=x,b=y,c=z,d=accuracy)
        M.do('a.points.push_back(b)',a=builder,b=point)
    
    for tri in tris:
        assert tri[0] != tri[1] and tri[0] != tri[2] and tri[1] != tri[2]
        vec = M.new('std::vector<int>()')
        for item in tri: 
            M.do('a.push_back(b)',a=vec,b=item)
        M.do('a.facets.push_back(b)',a=builder,b=vec)
    
    M.do('a.delegate(b)',a=polyhedron,b=builder)
    
    assert M('a.is_closed()',a=polyhedron), 'Polyhedron is not closed'        

    nef = M.new('Nef_polyhedron(a)',a=polyhedron)    
    
    assert M('a.is_valid()',a=nef)
    assert M('a.is_simple()',a=nef)    
    
    return Shape(nef)

def create_polygon_3(verts, accuracy=1<<16):
    vec = M.new('std::vector<Point_3>')

    for vert in verts:
        [x,y,z] = [ int_round(item*accuracy) for item in vert ]
        M.do('a.push_back(Point_3(b,c,d,e))',a=vec,b=x,c=y,d=z,e=accuracy)
    
    return Shape(M.new('Nef_polyhedron(a.begin(),a.end())',a=vec))

#Needs more complicated representation
#def create_halfspace():
#    return Shape(M.new('Nef_polyhedron(Nef_polyhedron::Plane_3(0,0,1,0))'))

def read_stl(filename):
    with open(filename,'rU') as f:
        verts = [ ]
        for line in f:
            parts = line.rstrip().split()
            if parts[0] == 'vertex':
                verts.append((float(parts[1]),float(parts[2]),float(parts[3])))
            elif parts[0] == 'endloop':
                assert len(verts) == 3
                yield verts
                verts = [ ]
        assert not verts

def load_stl(filename):
    verts = [ ]
    vert_index = { }
    tris = [ ]
    for triangle in read_stl(filename):
        tri = [ ]
        for point in triangle:
            if point not in vert_index:
                vert_index[point] = len(verts)
                verts.append(point)
            tri.append(vert_index[point])
        assert len(set(tri)) == 3, tri
        tris.append(tri)
    
    return create(verts, tris)



def show_only(*shapes):
    pass




class Shape_2(object):
    def __init__(self, pset):
        self.pset = pset
    
    def loops(self):
        def point_decode(point):
            return (
                M('CGAL::to_double(a.x())',a=point),
                M('CGAL::to_double(a.y())',a=point)
            )
        def polygon_decode(poly):
            return [ point_decode(item) for item in M.iterate('a.vertices_begin()','a.vertices_end()',a=poly) ]
    
        loops = [ ]
    
        phole_vec = M.new('std::vector<Polygon_with_holes_2>')
        M.do('a.polygons_with_holes(std::back_inserter(b))', a=self.pset,b=phole_vec)        
        for phole in M.iterate('a.begin()','a.end()',a=phole_vec):
            loops.append( polygon_decode( M('a.outer_boundary()',a=phole) ) )
            loops.extend( polygon_decode(item) for item in  M.iterate('a.holes_begin()','a.holes_end()',a=phole) )
        return loops
    
    def to_3(self):
        #TESTME!
   
        def polygon_recode(poly):
            vec = M.new('std::vector<Point_3>')
            for point_3 in M.iterate('a.vertices_begin()','a.vertices_end()',a=poly):
                M.do('a.push_back(Point_3(b.x(),b.y(),0))',a=vec,b=point_3)
            return Shape(M.new('Nef_polyhedron(a.begin(),a.end())',a=vec))
        
        #result = empty_shape()
        result = None
        phole_vec = M.new('std::vector<Polygon_with_holes_2>')
        M.do('a.polygons_with_holes(std::back_inserter(b))', a=self.pset,b=phole_vec)        
        for phole in M.iterate('a.begin()','a.end()',a=phole_vec):
            phole_3 = polygon_recode( M('a.outer_boundary()',a=phole) )
            for hole in M.iterate('a.holes_begin()','a.holes_end()',a=phole):
                phole_3.remove( polygon_recode(hole) )
            if result is None:
                result = phole_3
            else:
                result.add(phole_3)
        
        assert result is not None #CGAL gets explodey with empty shapes
            
        return result
        

    def remove(self, other):
        M.do('a.difference(b)',a=self.pset,b=other.pset)

    def add(self, other):
        M.do('a.join(b)',a=self.pset,b=other.pset)

    def clip(self, other):
        M.do('a.intersection(b)',a=self.pset,b=other.pset)

    def invert(self):
        M.do('a.complement()',a=self.pset)
    
    def orientation(self):
        return M('(int)a.orientation()',a=self.pset)

    def move(self, x,y, accuracy=1<<16):
        transform = M('Aff_transformation_2(CGAL::TRANSLATION,Vector_2(a,b,c))',
            a=int_round(x*accuracy), b=int_round(y*accuracy), c=accuracy
        )
        M.do('a.transform(b)',a=self.pset, b=transform)


def empty_shape_2():
    return Shape_2(M.new('Polygon_set_2'))


def create_polygon_2(verts, accuracy=1<<16):
    vec = M.new('std::vector<Point_2>')

    for vert in verts:
        [x,y] = [ int_round(item*accuracy) for item in vert ]
        M.do('a.push_back(Point_2(b,c,d))',a=vec,b=x,c=y,d=accuracy)
    
    poly = M.new('Polygon_2(a.begin(),a.end())',a=vec)
    
    orientation = M('(int)a.orientation()',a=poly)
    
    if orientation == 0:
        return empty_shape_2()
        
    if orientation < 0:
        M('a.reverse_orientation()',a=poly)
    
    return Shape_2(M.new('Polygon_set_2(a)',a=poly))
    



def main(func, *args, **kwargs):
    #return M.run(func,sys.argv[1:],*args,**kwargs)
    return func(sys.argv[1:],*args,**kwargs)


if __name__ == '__main__':
    def run():
        #print module.as_reference('new int(42)').__dict__
        #print 'hello'
        #return
    
        polyhedron = M.new('Polyhedron()')
    
        #builder = module('Build_polyhedron()')
        #
        #for p in [(1,0,0),(0,1,0),(0,0,1)]:
        #    point = module.call('Kernel::Point_3',*p)
        #    module('a.points.push_back(b)',a=builder,b=point)
        #
        #for f in [(0,1,2)]:
        #    vec = module('std::vector<int>()')
        #    for item in f: 
        #        module('a.push_back(b)',a=vec,b=item)
        #    module('a.facets.push_back(b)',a=builder,b=vec)
        #
        #module('a.delegate(b)',a=polyhedron,b=builder)
    
        M('a.make_tetrahedron(Point_3(0,0,0),Point_3(1,0,0),Point_3(0,1,0),Point_3(0,0,1))',a=polyhedron)
    
        print M('a.size_of_vertices()',a=polyhedron)
        print M('a.size_of_halfedges()',a=polyhedron)
        print M('a.size_of_facets()',a=polyhedron)
        
        print 'Closed:', M('(int)a.is_closed()',a=polyhedron)
        
        nef = M.new('Nef_polyhedron(a)',a=polyhedron)
        
        print 'Simple:', M('(int)a.is_simple()',a=nef)
        
        polyhedron2 = M.new('Polyhedron()')
        M('a.convert_to_polyhedron(b)',a=nef,b=polyhedron2)
    
        print 'Closed:', M('(int)a.is_closed()',a=polyhedron2)
        
        #i = module('a.facets_begin()',a=polyhedron2)
        #end = module('a.facets_end()',a=polyhedron2)
        #while module('a<b',a=i,b=end):
        #    value = module('*a',a=i)
        #    print 'boop'
        #    module('a++',a=i)
            
        for item in M.iterate('a.facets_begin()','a.facets_end()',a=polyhedron2):
            print 'boop'
            for item2 in M.circulate('a.facet_begin()',a=item):
                print M('a.vertex()->point()',a=item2)
    
        print 'lovely'
    
    #M.run(run)
    run()
    

