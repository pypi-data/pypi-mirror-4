
from __future__ import print_function

import math, traceback, os, random, sys, io, collections

import profile, design, pack, mask

from nesoni import config

#=====================
#from blender import *
#=====================
from cgal import *
#=====================


# We use mm internally

#SCALE = 0.001   # mm -> m
#SCALE = 1.0   # mm -> mm

QUALITY = 128
def draft_mode():
    global QUALITY
    QUALITY = 16

NAME_COUNT = 0
def make_name(value=None):
    global NAME_COUNT
    if value: return value
    NAME_COUNT += 1
    return 'obj%d' % NAME_COUNT

CLEAN_MLX = os.path.join(os.path.split(__file__)[0], 'clean.mlx')


def noise():
    return (random.random()-0.5)*1e-4

Limits = collections.namedtuple('Limits',
   'xmin xmax ymin ymax zmin zmax'
)

class Loop(list):
    @property
    def circumpherence(self):
        total = 0.0
        last = self[-1]
        for point in self:
            dx = last[0]-point[0]
            dy = last[1]-point[1]
            total += math.sqrt(dx*dx+dy*dy)
            last = point
        return total

    @property
    def area(self):
        total = 0.0
        last = self[-1]
        for point in self:
            total += (
                last[0]*point[1]
              - last[1]*point[0]
            )
            last = point
        return 0.5*total
    
    def scale(self, factor):
        return Loop( (x*factor, y*factor) for x,y in self )

    def scale2(self, factor_x, factor_y):
        return Loop( (x*factor_x, y*factor_y) for x,y in self )
    
    def with_area(self, area):
        return self.scale(math.sqrt( area/self.area ))
    
    def with_effective_diameter(self, diameter):
        return self.with_area(math.pi*0.25*diameter*diameter)
    
    def with_circumpherence(self, circumpherence):
        return self.scale(circumpherence / self.circumpherence)

    def offset(self, dx,dy):
        return Loop( (x+dx,y+dy) for x,y in self )

    def mask(self, res):
        lines = [ (self[i][0]*res,self[i][1]*res,
                   self[(i+1)%len(self)][0]*res,self[(i+1)%len(self)][1]*res)
                  for i in range(len(self)) ]
        return mask.make_mask(lines)

    def mean(self):
        return (float(sum( x for x,y in self )) / len(self),
                float(sum( y for x,y in self )) / len(self))


def circle(diameter=1.0, n=None):
    if n is None: n = QUALITY
    radius = diameter * 0.5
    result = [ ]
    for i in range(n):
        a = (i+0.5)*math.pi*2.0/n
        result.append( (math.cos(a)*radius, math.sin(a)*radius) )
    return Loop(result)


def chorded_circle(amount=0.5):
    """ semi-circle and the like """
    result = [ ]
    a1 = math.pi*(0.5+amount)
    a2 = math.pi*(2.5-amount)
    for i in range(QUALITY):
        a = a1+(i+0.5)*(a2-a1)/QUALITY
        result.append( (math.cos(a), math.sin(a)) )
    return Loop(result)


def squared_circle(xpad,ypad, diameter=1.0):
    """ Squared circle with same area as circle of specified diameter """
    result = [ ]
    for i in range(QUALITY):
        a = (i+0.5)*math.pi*2.0/QUALITY
        x = math.cos(a)
        if x < 0: x -= xpad*0.5
        else: x += xpad*0.5
        y = math.sin(a)
        if y < 0: y -= ypad*0.5
        else: y += ypad*0.5
        result.append( (x,y) )
    
    area = math.pi + xpad*ypad + xpad*2 + ypad*2
    want = math.pi * (diameter*0.5)**2
    scale = math.sqrt( want/area )
    result = [ (x*scale,y*scale) for x,y in result ]
    
    return Loop(result)


def lens(amount, circumpherence=math.pi):
    result = [ ]
    turn = math.asin(amount)
    turn2 = math.pi-turn*2
    shift = math.sin(turn)
    for i in range(QUALITY // 2):
        a = (i+0.5)/QUALITY*2 * turn2 + turn
        result.append((
            math.cos(a),
            math.sin(a) - shift
        ))
    result = Loop(
        result +
        [ (-x,-y) for x,y in result ]
    )
    return result.with_circumpherence(circumpherence)

def lens2(amount, circumpherence=math.pi):
    result = [ ]
    turn = math.pi*0.5*amount
    turn2 = math.pi-turn*2
    shift = math.sin(turn)
    for i in range(QUALITY // 2):
        a = (i+0.5)/QUALITY*2 * turn2 + turn
        result.append((
            math.cos(a),
            math.sin(a) - shift
        ))
    result = Loop(
        result +
        [ (-x,-y) for x,y in result ]
    )
    return result.with_circumpherence(circumpherence)


def extrusion(zs, shapes, name=None):
    nz = len(zs)
    nshape = len(shapes[0])
    
    verts = [ ]
    for i,z in enumerate(zs):
        for x,y in shapes[i]:
            verts.append( (x,y,z) )
    
    end0 = len(verts)
    verts.append( shapes[0].mean() + (zs[0],) )
    end1 = len(verts)
    verts.append( shapes[-1].mean() + (zs[-1],) )
    
    
    faces = [ ]
    for i in range(nz-1):
        for j in range(nshape):
            #faces.append( ( 
            #    (i+1)*nshape+j, i*nshape+j,
            #    i*nshape+(j+1)%nshape, (i+1)*nshape+(j+1)%nshape 
            #) )
            faces.append( ( 
                (i+1)*nshape+j, i*nshape+j,
                i*nshape+(j+1)%nshape, 
            ) )
            faces.append( ( 
                (i+1)*nshape+j,
                i*nshape+(j+1)%nshape, (i+1)*nshape+(j+1)%nshape 
            ) )

    for i in range(nshape):
        i1 = (i+1)%nshape
        faces.append( (i1,i,end0) )
        faces.append( (i+nshape*(nz-1),i1+nshape*(nz-1),end1) )

    return create(verts, faces, name)

def block(x1,x2,y1,y2,z1,z2, name=None, ramp=0.0):
    verts = [ ]
    for x in [x1,x2]:
        for y in [y1,y2]:
            verts.append((x,y,z1))
    for x in [x1-ramp,x2+ramp]:
        for y in [y1-ramp,y2+ramp]:
            verts.append((x,y,z2))
        
    faces = [ ]

    def quad(a,b,c,d):
        faces.append((a,b,c))
        faces.append((a,c,d))

    for a,b,c in [ (1,2,4),(4,1,2),(2,4,1) ]:
        quad(0,a,a+b,b)
        quad(c+b,c+a+b,c+a,c+0)

    return create(verts, faces, name)


def extrude_profile(*profiles, **kwargs):
    for arg in kwargs: assert arg in ('cross_section','name')
    cross_section = kwargs.get('cross_section',circle)
    name = kwargs.get('name',None)
    
    zs = [ ]
    shapes = [ ]
    
    pos = set()
    for item in profiles:
        pos.update(item.pos)
    pos = sorted(pos)
    
    for i,z in enumerate(pos):
        lows = [ item(z) for item in profiles ]
        highs = [ item(z,True) for item in profiles ]
    
        if i:
            zs.append(z)
            shapes.append(cross_section(*lows))
        if not i or (i < len(pos)-1 and lows != highs):
            zs.append(z)
            shapes.append(cross_section(*highs))
    
    return extrusion(zs, shapes, name=name)


def prism(height, diameter, cross_section=circle, name=None):
    span = profile.Profile([0.0, height], [diameter, diameter])
    return extrude_profile(span, cross_section=cross_section, name=name)


def make_segment(instrument, top, low, high, radius, pad=0.0, clip_half=True):
    if not clip_half:
       y1,y2 = -radius,radius
    elif top:
       y1,y2 = 0,radius
    else:
       y1,y2 = -radius,0
    clip = block(-radius,radius, y1,y2, low-pad,high+pad)
    segment = instrument.copy()
    segment.clip(clip)
    assert abs(segment.size()[2] - (high-low+pad*2)) < 1e-3, 'Need more padding for construction'
    segment.move(0,0,-low)
    if top:
       segment.rotate(0,0,1, 180)

    segment.rotate(1,0,0,-90)
    segment.rotate(0,0,1,90)
    segment.move(high-low,0,0)
    return segment


def make_segments(instrument, length, radius, top_fractions, bottom_fractions, pad=0.0, clip_half=True):
    parts = [ ]
    lengths = [ ]
    z = [ item*length for item in top_fractions ]
    for i in range(len(top_fractions)-1):
        lengths.append(z[i+1]-z[i])    
        parts.append(make_segment(instrument, True, 
                     z[i],z[i+1], 
                     radius, pad, clip_half))

    z = [ item*length for item in bottom_fractions ]
    for i in range(len(bottom_fractions)-1):    
        lengths.append(z[i+1]-z[i])    
        parts.append(make_segment(instrument, False, 
                     z[i],z[i+1], 
                     radius, pad, clip_half))

    return parts, lengths

def make_formwork(outer, bore, length, top_fractions, bottom_fractions, 
                  bit_diameter, peg_diameter, depth, width):
    """ Object must be large enough to include end padding """
    xsize,ysize,zsize = outer.size()
    radius = max(xsize,ysize)
    
    pad = bit_diameter * 1.25
    ramp = depth / 10.0
    
    peg_margin = max(peg_diameter, ramp)
    
    eps = 1e-4
    
    outers, lengths = make_segments(outer, length, radius, top_fractions, bottom_fractions, 0)
    bores, _ = make_segments(bore, length, radius, top_fractions, bottom_fractions, bit_diameter, False)

    n = len(outers)
    order = sorted(range(n),key=lambda i: -lengths[i])
    lengths = [ lengths[i] for i in order ]
    outers = [ outers[i] for i in order ]
    bores = [ bores[i] for i in order ]

    places = pack.pack([ item.size() for item in outers], pad, width)
    places = [ (x,y+peg_margin) for x,y in places ]

    xsize = 0
    ysize = 0
    for i in range(n):
        xmin,xmax,ymin,ymax,zmin,zmax = outers[i].extent()
        outers[i].move(places[i][0], places[i][1]-ymin, 0)
        bores[i] .move(places[i][0], places[i][1]-ymin, -eps)
        
        xsize = max(xsize,xmax-xmin+places[i][0]+pad)
        ysize = max(ysize,ymax-ymin+places[i][1]+pad)
        
    
    #y = peg_margin + pad
    #xsize = 0
    #for i in range(n):
    #    xmin,xmax,ymin,ymax,zmin,zmax = outers[i].extent()
    #    assert zmax <= depth, 'Too big: %.1f' % zmax
    #    assert abs(zmin) < 1e-3, 'Wut?'
    #    
    #    outers[i].move(pad,-ymin+y,0)
    #    bores[i].move(pad,-ymin+y,0)
    #    y += ymax-ymin+pad
    #    xsize = max(xsize,lengths[i]+pad*2)
    #
    #ysize = y
    
    # Clip tops of bollards... (0.5 max height, pretty small)
    #for i in range(n):
    #    xmin,xmax,ymin,ymax,zmin,zmax = outers[i].extent()
    #    left_height = outers[i].max_z_near_x(xmin)
    #    right_height = outers[i].max_z_near_x(xmax)
    #    
    #    outers[i].remove(block(
    #        xmin-eps,pad,
    #        ymin-eps,ymax+eps,
    #        min(0.5,left_height*0.5), depth
    #    ))
    #    
    #    outers[i].remove(block(
    #        pad+lengths[i],xmax+eps,
    #        ymin-eps,ymax+eps,
    #        min(0.5,right_height*0.5), depth
    #    ))
        
    
    lower = block(-ramp,xsize+ramp,0,ysize+ramp,0,depth+1)
    upper = block(-ramp,xsize+ramp,0,ysize+ramp,eps,depth)
    
    print('Necessary origin: x +', ramp, ' y + ', peg_margin-peg_diameter)
    
    for item in bores:
        lower.remove(item)
    
    hole1 = prism(peg_diameter*1.5, peg_diameter)
    hole2 = hole1.copy()
    
    hole1.move(peg_diameter,peg_margin-peg_diameter*0.5,-eps)
    lower.remove(hole1)
    
    hole2.move(xsize-peg_diameter,peg_margin-peg_diameter*0.5,-eps)
    lower.remove(hole2)
    

    #upper.remove(block(
    #    -eps,xsize+eps, peg_diameter+eps,ysize+eps, 0,depth
    #))
    
    xmins = [ ]
    xmaxs = [ ]
    for i in range(n):
        xmin,xmax,ymin,ymax,zmin,zmax = outers[i].extent()
        xmins.append(xmin)
        xmaxs.append(xmax)
        
        upper.remove(block(
            xmin-pad-eps*(i+1),xmax+pad+eps*(i+1),
            ymin-pad+eps*(i+1),ymax+pad-eps*(i+1), # + (1 if i == n-1 else 0),
            #eps*(i+1),depth+eps,
            0,depth+eps,
            ramp = ramp
        ))

        #Purely to appease boolean ops library:
        outers[i].clip(block(
            xmin+eps*(i+2),xmax-eps*(i+2),
            ymin-pad*0.5,ymax+pad*0.5,
            -1,depth,
        ))
        
    for i in range(n):
        upper.add(outers[i])

    bol = int(xsize / 30.0)
    bol_width = 1.0
    bol_height = 1.5 
        # 0.5 was too low, middle piece tore loose in final pass of
        # contour finishing (x-scan of horizontal-like surfaces)
    for i in range(bol):
        pos = (i+0.5)*xsize/bol
        
        if any( pos-pad <= item <= pos+pad for item in xmins+xmaxs ):
            continue
        
        upper.add(block(
            pos-bol_width*0.5, pos+bol_width*0.5,
            eps,ysize+ramp-eps,
            -bit_diameter*0.6, bol_height,
        ))     
    
    #Flip bore formwork after construction
    lower.rotate(0,1,0, 180)
    
    return lower, upper


@config.Bool_flag('draft', 'Draft output')
class Make_base(config.Action):
    draft = False

    def save(self, shape, prefix):
        prefix = self.get_workspace()/prefix
        
        shape.save(prefix + '.stl')
        
        import sketch
        sketch.sketch(shape, prefix + '-sketch.svg')

    def _before_run(self):
        if self.draft:
            draft_mode()
        self.get_workspace()

class Make(config.Action_with_output_dir, Make_base):
    pass

class Make_instrument(config.Action_with_working_dir, Make_base):
    def _before_run(self):
        self.designer = design.load(self.working_dir)
        self.instrument = self.designer.instrument


def main_action(action):
    def func(args):
        try:
            config.shell_run(action,args,action.__class__.__name__)
        except SystemExit:
            os.abort()
    main(func)

if __name__ == '__main__':
    print(sys.argv)
    main(lambda args: print('Hello world', args))


