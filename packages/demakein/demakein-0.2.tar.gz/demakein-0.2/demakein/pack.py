
import os

import profile, shape

class Packable(object):
    def __init__(self, shapes, rotation, dilation, use_upper=True):
        self.shapes = [ item.copy() for item in shapes ]
        for item in self.shapes:
            item.rotate(0,0,1, rotation)
        
        extent = self.shapes[0].extent()
        for item in self.shapes:
            item.move(-extent.xmin,-extent.ymin,0)
        self.extent = self.shapes[0].extent()
        
        self.mask = self.shapes[0].polygon_mask()
        self.mask = shape.create_polygon_2(self.mask.loop(holes=False))

        self.dilated_mask = self.mask.offset_curve(dilation, 16)
        self.dilated_mask = shape.create_polygon_2(self.dilated_mask.loop(holes=False))

        self.dilated_extent = self.dilated_mask.extent()
        self.use_upper = use_upper


class Pack(object):
    def __init__(self, xsize, ysize, zsize, masks=[], items=[]):
        self.xsize = xsize
        self.ysize = ysize
        self.zsize = zsize
        self.masks = masks[:]
        self.items = items[:] #(x,y,packable)

    def copy(self):
        return Pack(self.xsize, self.ysize, self.zsize, self.masks, self.items)

    def put(self, x,y,packable):
        self.items.append((x,y,packable))
        shifted = packable.mask.copy()
        shifted.move(x,y)
        self.masks.append(shifted)
    
    def valid(self, x,y,packable):
        if (packable.extent.zmax > self.zsize or 
            x+packable.dilated_extent.xmin < 0.0 or
            y+packable.dilated_extent.ymin < 0.0 or
            x+packable.dilated_extent.xmax > self.xsize or
            y+packable.dilated_extent.ymax > self.ysize):
            return False
        shifted = packable.dilated_mask.copy()
        shifted.move(x,y)
        for mask in self.masks:
            if mask.intersects(shifted):
                return False
        return True

    def render(self, bit_diameter, bit_pad):
        xsize = self.xsize
        ysize = self.ysize #max( y+packable.extent.ymax for x,y,packable in self.items )+bit_diameter*2
        
        a = bit_pad
        b = bit_pad + self.zsize/10.0
        pad_cone = shape.extrude_profile(profile.Profile([0,self.zsize],[a*2,b*2],[a*2,b*2]), cross_section=lambda d: shape.circle(d,16))
        
        pad = 0.5 + self.zsize/10.0
        
#        dilations = [
##            (z, shape.circle(2.0*( 2.0+z/20.0 )).mask(self.res))
##            for z in range(1)
#            (z, mask.ones(0,0,1,1) if not z else 
#                shape.circle(2.0*( z/10.0 )).mask(self.res))
#            for z in range(0,int(self.zsize),5)
#        ]

        #dilator = shape.circle(2* bit_diameter).mask(res)
        #hole_mask = mask.zero()
        #for x,y,packable in self.items:
        #    if packable.use_upper:
        #        hole_mask = hole_mask | packable.dilated_mask.offset(int(x*self.res+0.5),int(y*self.res+0.5))
        #hole_mask = hole_mask.close(dilator)
        
        upper = shape.block(-pad,xsize+pad,-pad,ysize+pad,0,self.zsize)

        for i,(x,y,packable) in enumerate(self.items):
            if packable.use_upper:
                flat = packable.mask.to_3()
                flat.move(x,y,0)
                minsum = flat.minkowski_sum(pad_cone)
                upper.remove( minsum )

        for x,y,packable in self.items:
            if packable.use_upper:
                temp = packable.shapes[0].copy()
                temp.move(x,y,0)
                upper.add(temp)
            
        bol = int(self.xsize / 30.0)
        bol_width = 1.0
            # 0.5 seemed to allow shifting on a sop flute
        bol_height = 1.0 
            # 0.5 was too low, middle piece tore loose in final pass of
            # contour finishing (x-scan of horizontal-like surfaces)
        xmins = [ x for x,y,packable in self.items ]
        xmaxs = [ x+packable.extent.xmax for x,y,packable in self.items ]
        margin = bit_diameter*2
        for i in range(bol):
            pos = (i+0.5)*xsize/bol
            
            if any( pos-margin <= item <= pos+margin for item in xmins+xmaxs ):
                continue
            
            upper.add(shape.block(
                pos-bol_width*0.5, pos+bol_width*0.5,
                0,ysize,
                #-bit_diameter*0.6, bol_height,
                0,bol_height,
            ))     
        
        # Cut the bottom of upper with lower, to depth    bit_diameter
        lower = shape.block(-pad,xsize+pad,-pad,ysize+pad,bit_diameter,self.zsize)
        lower.add(upper)

        for x,y,packable in self.items:
            temp = packable.shapes[1].copy()
            temp.move(x,y,0)
            lower.remove(temp)
        
        lower.rotate(0,1,0, 180)
        
        return lower, upper


def make_segment(instrument, top, low, high, radius, pad=0.0, clip_half=True):
    if not clip_half:
       y1,y2 = -radius,radius
    elif top:
       y1,y2 = 0,radius
    else:
       y1,y2 = -radius,0
    clip = shape.block(-radius,radius, y1,y2, low-pad,high+pad)
    segment = instrument.copy()
    segment.clip(clip)
    #Closed flute is meant to be like this
    #assert abs(segment.size()[2] - (high-low+pad*2)) < 1e-3, 'Need more padding for construction'
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


def deconstruct(outer, bore, top_fractions, bottom_fractions, 
                bit_diameter, dilation):
    """ Object must be large enough to include end padding """
    xsize,ysize,zsize = outer.size()
    radius = max(xsize,ysize)*2
    
    length = zsize
    
    outers, lengths = make_segments(outer, length, radius, top_fractions, bottom_fractions, 0)
    bores, _ = make_segments(bore, length, radius, top_fractions, bottom_fractions, bit_diameter, False)

    return [ [ Packable([outer, bore], 0, dilation),
                Packable([outer, bore], 180, dilation) ]
              for outer, bore in zip(outers, bores) ]


def pack(packables, xsize, ysize, zsize, dilation):
    template = Pack(xsize, ysize, zsize)
    
    peg_diameter = 6
    block_radius = 3.5
    hole = shape.prism(min(zsize,peg_diameter*2.0), peg_diameter)   # *3 is too deep
    hole_block = shape.block(-block_radius,block_radius,-block_radius,block_radius,0,zsize)
    hole_packable = Packable([hole_block,hole], 0, 0.0, use_upper=False)
    
    shift = 4
    template.put(shift, block_radius,hole_packable)
    template.put(xsize-block_radius*2-shift, block_radius,hole_packable)

    template.put(0,ysize-block_radius*3,hole_packable)
    template.put(xsize-block_radius*2,ysize-block_radius*3,hole_packable)
    
    packs = [ template.copy() ]
    pack = packs[-1]
    
    step = 2.0
    step_back = 0.1

    points = [ ]
    for y in xrange(int(ysize/step)):
        for x in xrange(int(xsize/step)):
            points.append((x*step,y*step))
    points.sort(key=lambda item: (-item[1],-item[0]))
    
    todo = sorted(packables, key=lambda item: item[0].extent.xmax)
    while todo:
        try:
            queue = [
                (i,x,y)
                for x,y in points
                for i in range(len(todo))
            ]
        
            #for i in range(len(todo)):
            #    for x,y in points:
            
            def sorter(item):
                i,x,y = item
                return (
                    y >= block_radius*2,
                    -todo[i][0].extent.xmax,
                    y,
                    x,
                )
            queue.sort(key=sorter)
            
            for i,x,y in queue:
                for j in range(len(todo[i])):
                    if pack.valid(x,y,todo[i][j]):
                        raise StopIteration()

            assert len(pack.items) > len(template.items), 'This is never going to work'
            pack = template.copy()
            packs.append(pack)
            
        except StopIteration:
            while True:
                if pack.valid(x-step_back,y,todo[i][j]):
                    x -= step_back
                elif pack.valid(x,y-step_back,todo[i][j]):
                    y -= step_back
                else:
                    break
            
            print len(todo),'put',len(packs),x,y
            
            pack.put(x,y,todo[i][j])
            del todo[i]

    return packs


def save_packs(packs, save, bit_diameter, pad):
    shapes = [ ]
    for i, item in enumerate(packs):
        lower, upper = item.render(bit_diameter, pad)
        shapes.extend([lower,upper])
        save(lower, 'lower-%d-of-%d' % (i+1,len(packs)))
        save(upper, 'upper-%d-of-%d' % (i+1,len(packs)))

    return shapes


def cut_and_pack(outer, bore, top_fractions, bottom_fractions, xsize, ysize, zsize, bit_diameter, save):
    pad = bit_diameter*1.25
    dilation = pad
    
    packables = deconstruct(outer, bore, top_fractions, bottom_fractions, bit_diameter, dilation)

    #for i, item in enumerate([ a for b in packables for a in b ]):
    #    mask.write_pbm(open('/tmp/mask%d.pbm'%i,'w'), item.dilated_mask.data)

    for item in packables:
        print('%.1fmm x %.1fmm x %.1fmm' % (item[0].extent.xmax,item[0].extent.ymax,item[0].extent.zmax))

    packs = pack(packables, xsize, ysize, zsize, dilation)
    
    return save_packs(packs, save, bit_diameter, pad)



