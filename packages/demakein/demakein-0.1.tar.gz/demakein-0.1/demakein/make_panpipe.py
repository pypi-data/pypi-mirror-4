
import sys, os, math
sys.path.insert(0, os.path.split(__file__)[0])

import design, shape, profile

from nesoni import config

RES = 20

LENGTH_CORRECTION = 0.0 # * diameter
   # Hole is rounded at end, so make it a little longer
   # - unknown further correction 

SCALE = [
    'C6',
    'D6',
    'E6',
    'F6',
    'G6',
    'A6',
    'B6',
    'C7',
    'D7',
]

SCALE = [
    'F6',
    'G6',
    'A6',
    'C7',
    #'D7',
    #'F7',
]

def make_hole(diameter, length):
    pos = [ 0.0 ]
    diam = [ diameter ]
    
    radius = diameter*0.5
    n = 10
    for i in range(0,n):
        x = math.pi/2 * float(i)/n
        pos.append(length+radius*(math.sin(x)-1))
        diam.append(diameter*math.cos(x))
    
    prof = profile.Profile(pos,diam,diam)
    hole = shape.extrude_profile(prof)
    
    return hole

@config.Float_flag('thickness', 'Wood thickness (half resultant thickness)')
@config.Int_flag('transpose', 'Transpose (semitones)')
class Make_panpipe(shape.Make):
    thickness = 4.0
    transpose = 0
    
    def run(self):
        super(Make_panpipe,self).run()
        
        zsize = self.thickness * 2
        
        pad = 1.0
        diameter = zsize - pad*2
        
        holes = [ ]
        lengths = [ ]
        xs = [ ]
        for i, note in enumerate(SCALE):
            print 'Make hole %d / %d' % (i+1,len(SCALE))
            length = design.wavelength(note,self.transpose)*0.25 + LENGTH_CORRECTION*diameter
            x = i*(diameter+pad)
            lengths.append(length)
            xs.append(x)
            hole = make_hole(diameter, length)
            hole.move(x,0,0)
            holes.append(hole)
        
        string_hole_loop = shape.circle(diameter*1.5)
        string_hole = shape.extrusion([-zsize,zsize],[string_hole_loop,string_hole_loop])
        string_hole.rotate(1,0,0, 90)
        
        string_x = xs[3]
        string_z = lengths[3] + diameter*2
        string_hole.move(string_x,0,string_z)
        
        xlow = xs[0]-zsize
        xmid = xs[-1]*0.5
        xhigh = xs[-1]+zsize
        
        zhigh = lengths[0]+zsize*0.5
        zmid  = max(lengths[-1]+zsize*0.5, zhigh-(xhigh-xmid))
        
        loop = shape.Loop([
            (xlow,0),
            (xhigh,0),
            (xhigh,zmid),
            (xmid,zhigh),
            (xlow,zhigh)
        ])
        
        #mask = loop.mask(RES)
        
        #amount = diameter * 0.5
        #op = shape.circle(amount).mask(RES)
        #mask = mask.open(op)
        
        #loop = mask.trace(RES)[0]
        
        #sloop = mask.erode(op).trace(RES)[0]
        
        #z1 = zsize*0.5-amount
        z2 = zsize*0.5
        
        positive = shape.extrusion([-z2,z2],[loop,loop])
        positive.rotate(1,0,0,90)
        
        negative = string_hole.copy()
        for i, hole in enumerate(holes):
            print 'Merge hole %d / %d' % (i+1,len(holes))
            negative.add(hole)
        
        instrument = positive.copy()
        
        print 'Remove holes from instrument'
        instrument.remove(negative)

        self.save(instrument,'instrument.stl')
        
        #instrument.rotate(1,0,0,90)
        #extent = instrument.extent()
        #top = shape.block(
        #    extent.xmin-1,extent.xmax+1,
        #    extent.ymin-1,extent.ymax+1,
        #    0,extent.zmax+1
        #)
        #bottom = shape.block(
        #    extent.xmin-1,extent.xmax+1,
        #    extent.ymin-1,extent.ymax+1,
        #    extent.zmin-1,0
        #)
        #
        #top.clip(instrument)
        #bottom.clip(instrument)
        #top.rotate(1,0,0,180)
        #top.move(0,4,0)
        #bottom.add(top)
        #        
        #mask = bottom.mask(RES)
        #op = shape.circle(6).mask(RES)
        #loop = mask.dilate(op).trace(RES)
        #
        #z1 = -self.thickness+1.5
        #z2 = 0.0
        #loop_ext = shape.extrusion([z1,z2],[loop,loop])
        #extent = loop_ext.extent()
        #
        #cut = shape.block(
        #    extent.xmin-1,extent.xmax+1,
        #    extent.ymin-1,extent.ymax+1,
        #    z1,z2
        #)
        #cut.remove(loop_ext)
        #cut.add(bottom)
        #self.save(cut,'mill.stl')


if __name__ == '__main__': 
    shape.main_action(Make_panpipe())


