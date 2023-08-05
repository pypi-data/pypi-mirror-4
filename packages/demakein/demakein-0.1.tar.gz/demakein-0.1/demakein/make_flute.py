
import sys, os, math
sys.path.insert(0, os.path.split(__file__)[0])

import design, design_flute, profile, shape, pack

from nesoni import config

@config.Bool_flag('open', 'Open both ends, thus requiring a cork.')
@config.Float_flag('gap', 
    'Printing: Amount of gap all around in the joins between segments. '
    'The best value for this will depend on the accuracy of your printer. '
    'If a joint is too loose and leaks, it can be sealed using wax or similar.')
@config.Bool_flag('mill', 'Create shapes for milling (rather than 3D printing).')
@config.Float_flag('thickness', 'Milling: Wood thickness for milling.')
@config.Float_flag('width', 'Milling: Wood width for milling.')
@config.Int_flag('scheme', 'Milling: Division scheme for milling.\nValid values: 2 3 4')
@config.Bool_flag('decorate', 'Add some decorations')
@config.String_flag('prefix', 'Output file prefix (useful if you want to make your design several different ways).')
class Make_flute(shape.Make_instrument):
    prefix = ''
    
    gap = 0.3

    mill = False
    open = False
    
    thickness = 12.0
    width = 135.0
    scheme = 2
    
    decorate = False
    
    SCHEMES = {
        2 : [
            [ 0.0, 0.6, 1.0 ],
            [ 0.0, 0.4, 1.0 ],
        ],
        
        3 : [
            [ 0.0, 0.3, 0.6, 1.0 ],
            [ 0.0, 0.4, 0.7, 1.0 ],
        ],
        
        4 : [
            [ 0.0, 0.2, 0.45, 0.7, 1.0 ],
            [ 0.0, 0.3, 0.55, 0.8, 1.0 ],
        ],
    }
    
    def run(self):
        designer = self.designer
        spec = self.instrument
        workspace = self.get_workspace()
    
        length = spec.length * 1.05   # Extend a bit to allow cork.
        
        cork_length = length - spec.length
        cork_diameter = spec.inner(spec.length)
        with open(workspace/(self.prefix+'cork.txt'),'wt') as f:
            f.write('Cork length %.1fmm\n' % cork_length)
            f.write('Cork diameter %.1fmm\n' % cork_diameter)
        
        width = max(spec.outer.low)
        
        outer_profile = spec.outer.clipped(0,length)
        if self.decorate:
           emfrac = 1.0-spec.hole_positions[-1]/length
           for frac, align in [ (0.0,1.0), (1.0-emfrac*2,1.0), (1.0,-1.0) ]:
               dpos = length * frac
               damount = outer_profile(dpos)*0.1
               dpos += damount * frac
               deco_profile = profile.Profile(
                   [ dpos+damount*i for i in [-1,0,1]],
                   [ damount*i      for i in [0,1,0] ],
               )
               outer_profile = outer_profile + deco_profile
        
        instrument = shape.extrude_profile(outer_profile)
        outside = shape.extrude_profile(outer_profile)
        
        if self.open:        
            bore = shape.extrude_profile(spec.inner.clipped(-50,length+50))
        else:
            bore = shape.extrude_profile(spec.inner.clipped(-50,spec.length))
    
        #xpad = [ .25,.25,0,0,0,0 ] + [ 0.0 ]
        #ypad = [ .25,.25,0,0,0,0 ] + [ 0.75 ]
        xpad = [ 0,0,0,0,0,0 ] + [ 0.0 ]
        ypad = [ 0,0,0,0,0,0 ] + [ 0.75 ]
    
        for i, pos in enumerate(spec.hole_positions):
            angle = spec.hole_angles[i]
            radians = angle*math.pi/180.0
        
            height = spec.outer(pos)*0.5 
            shift = math.sin(radians) * height
            
            hole_length = (
                math.sqrt(height*height+shift*shift) + 
                spec.hole_diameters[i]*0.5*abs(math.sin(radians)) + 
                4.0
            )
            hole = shape.prism(
                hole_length, spec.hole_diameters[i],
                shape.squared_circle(xpad[i], ypad[i]).with_effective_diameter
            )
            hole.rotate(1,0,0, -90-angle)
            hole.move(0,0,pos + shift)
            bore.add(hole)
            if angle:
                outside.remove(hole)
    
        instrument.remove(bore)    
        instrument.rotate(0,0,1, 180)
        self.save(instrument,self.prefix+'instrument')
        
        if self.mill:        
            shapes = pack.cut_and_pack(
                outside, bore,
                self.SCHEMES[self.scheme][0], self.SCHEMES[self.scheme][1],
                xsize=190.0, ysize=self.width, zsize=self.thickness,
                bit_diameter=3.0,
                res=10,
                output_dir=workspace.working_dir
            )
        
        else:
            shapes = [ ]
            
            cut1 = spec.inner_hole_positions[2]*0.5+spec.inner_hole_positions[3] * 0.5
            #cut2 = cut1 + (length-cut1)*0.3 + spec.outer.maximum()*0.7
            cut2 = length * 0.65
            cuts = [ 
                cut1,
                cut2,
            ]
            remainder = instrument.copy()
            for cut in cuts:
                d1 = spec.inner(cut)
                d3 = spec.outer(cut)
                d2 = (d1+d3) / 2.0
                
                
                d4 = spec.outer.maximum() * 2.0
                p1 = cut-d2*0.4
                p3 = cut+d2*0.4
                p2 = p1 + (d3-d1)*0.25

                #0.4mm clearance all around
                # radius -> diameter    * 2
                # adjust both diamerers / 2
                # net effect            * 1
                # 0.4mm was loose
                
                d1a = d1 - self.gap
                p1b = p1 - self.gap
                
                d2a = d2 - self.gap
                d2b = d2 + self.gap
                
                prof_inside = profile.Profile(
                    [ p1,  p2,  p3,  length+50 ],
                    [ d1a, d2a, d2a, d4 ],
                    [ d1a, d2a, d4,  d4 ],
                )
                prof_outside = profile.Profile(
                    [ p1b, p2,  p3,  length+50 ],
                    [ d1,  d2b, d2b, d4 ],
                    [ d1,  d2b, d4,  d4 ],
                )
                mask_inside = shape.extrude_profile(prof_inside)
                mask_outside = shape.extrude_profile(prof_outside)
                
                item = remainder.copy()
                item.remove(mask_outside)                
                remainder.clip(mask_inside)
                shapes.append(item)
            shapes.append(remainder)
            shapes = shapes[::-1]
            
            for i, item in enumerate(shapes):
                item.rotate(0,1,0, 180)
            
                self.save(item, self.prefix + 'segment-%d-of-%d' % (i+1,len(shapes)))
        
        shape.show_only(bore, outside, instrument, *shapes)        
        
        #if self.forms == 1:
        #    lower, upper = shape.make_formwork(
        #        outside, bore, length,
        #        [ 0.0, 0.6, 1.0 ],
        #        [ 0.0, 0.4, 1.0 ],
        #        3.0, 6.0, self.thickness, 200.0
        #    )
        #    
        #    self.save(lower,'lower.stl')
        #    self.save(upper,'upper.stl')
        #    
        #    shape.show_only(instrument, lower, upper)
        #
        #elif self.forms == 2:
        #    lower1, upper1 = shape.make_formwork(
        #        outside, bore, length,
        #        [ 0.0, 0.36, 0.66, 1.0 ],
        #        [ ],
        #        3.0, 6.0, self.thickness, 200.0
        #    )
        #    lower2, upper2 = shape.make_formwork(
        #        outside, bore, length,
        #        [ ],
        #        [ 0.0, 0.25, 0.5, 0.75, 1.0 ],
        #        3.0, 6.0, self.thickness, 200.0
        #    )
        #    
        #    self.save(lower1,'lower1.stl')
        #    self.save(upper1,'upper1.stl')
        #    self.save(lower2,'lower2.stl')
        #    self.save(upper2,'upper2.stl')
        #    
        #    shape.show_only(instrument, lower1,upper1,lower2,upper2)
        #
        #else:
        #     assert False, 'Unsupported number of forms'
    

if __name__ == '__main__': 
    shape.main_action(Make_flute())

