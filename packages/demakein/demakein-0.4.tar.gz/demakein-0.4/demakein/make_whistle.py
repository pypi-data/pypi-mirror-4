


import sys, os, math

sys.path.insert(0, os.path.normpath(os.path.join(__file__,'..','..')))

import demakein
from demakein import shape, geom, make, profile, pack

import nesoni
from nesoni import config

@config.help("""\
Make the head of a whistle instrument.
""")
@config.Float_flag('bore')
class Make_whistle_head(make.Make):
    bore = 15.0

    def effective_gap_diameter(self):
        # gap_length * airway_ysize
        area = (self.bore*0.25) * (self.bore*0.5)
        return math.sqrt(area/math.pi) * 2.0
    
    def effective_gap_height(self):
        # TODO: further adjustment
        return self.bore*(1.4-1.0) * 0.5

    def construct(self):
        bore = self.bore
        outside = bore * 1.4
        
        bore_length = bore*2.0        
        gap_length = bore * 0.25
        windcutter_length = bore * 0.75
        
        airway_length = bore*1.5

        z_min = -bore_length        
        z_gap_0 = z_min + bore_length - gap_length
        z_gap_1 = z_min + bore_length
        z_windcutter_0 = z_gap_0 - windcutter_length
        z_windcutter_1 = z_gap_0
        z_airway_0 = z_gap_1
        z_airway_1 = z_airway_0 + airway_length
        z_max = z_airway_1
        
        airway_xsize = bore * 0.15
        airway_ysize = bore * 0.5
        
        print 'Note mill bit diameter must be less than: %.1fmm' % (airway_xsize*2.0)
        
        windcutter_rounding = bore * 0.1
        windcutter_ysize = airway_ysize + windcutter_rounding
        windcutter_lip = bore * 0.02

        airway_x_low  = bore*0.5-airway_xsize*0.5+windcutter_lip*0.5
        airway_x_high = bore*0.5+airway_xsize*0.5+windcutter_lip*0.5
        
        airway_line_0 = profile.make_profile(
            [(z_airway_0, airway_x_low),
             (z_airway_1, airway_x_low)])

        airway_line_1 = profile.make_profile(
            [(z_airway_0, airway_x_high),
             (z_airway_1, airway_x_high)])
        
        windcutter_line = profile.make_profile(
            [(z_windcutter_0, outside*0.5),
             (z_windcutter_1, bore*0.5+windcutter_lip)])
        
        undercutter_line = profile.make_profile(
            [(z_windcutter_0, bore*0.45),
             (z_windcutter_1, bore*0.5)])
        
        body = shape.extrude_profile(
            profile.make_profile([(z_min,outside),(z_max,outside)]),
            )
        
        bore_space = shape.extrude_profile(
            profile.make_profile([(z_min,bore),(z_gap_1,bore)]),
            )
        #body.remove(bore_space)
        space = bore_space.copy()
         
        windcutter_space = shape.extrude_profile(
            windcutter_line.clipped(z_windcutter_0-1.0,z_gap_1),
            cross_section = lambda x:
                shape.rounded_rectangle(
                    x, x+bore,
                    windcutter_ysize*-0.5,windcutter_ysize*0.5,
                    windcutter_rounding)
            )
        body.remove(windcutter_space)
        #space.add(windcutter_space)
        
        undercutter_space = shape.extrude_profile(
            undercutter_line.clipped(z_windcutter_0,z_gap_1),
            cross_section = lambda x:
                shape.halfrounded_rectangle(
                    x-airway_xsize, x,
                    windcutter_ysize*-0.5,windcutter_ysize*0.5)
            )
        #body.remove(undercutter_space)
        space.add(undercutter_space)
               
        airway_space = shape.extrude_profile(
            airway_line_0.clipped(z_gap_0,z_airway_1+ airway_xsize*2), #Make longer, for milling inside
            airway_line_1.clipped(z_gap_0,z_airway_1+ airway_xsize*2),
            cross_section = lambda x0, x1:
                shape.halfrounded_rectangle(
                    x0, x1,
                    airway_ysize*-0.5,airway_ysize*0.5)
            )
        body.remove(airway_space)
        space.add(airway_space)
        
        gap_space = shape.block(
            0.0, bore,
            airway_ysize*-0.5,airway_ysize*0.5,
            z_gap_0,z_gap_1
            )
        body.remove(gap_space)
        #space.add(gap_space)
        
        cutaway_diameter = outside*1.5
        cutaway_space = shape.extrude_profile(
            profile.make_profile([(-outside*0.51, cutaway_diameter),(outside*0.51,cutaway_diameter)]))
        cutaway_space.rotate(1,0,0, 90)
        cutaway_space.move(-cutaway_diameter*0.5+bore*0.5-(outside*0.5-bore*0.5),0,z_max)
        cutaway_space.clip(shape.block(-outside*0.51,outside*0.51,-outside*0.51,outside*0.51,z_min,z_max))
        
        body.remove(cutaway_space)
        space.add(cutaway_space)
                
        #self.save(body, 'whistle')
        
        #assert airway_xsize_0 == airway_xsize_1
        #jaw_clipper = shape.extrude_profile(
        #    profile.make_profile([(-outside,0),(outside,0)]),
        #    cross_section=lambda foo: shape.rounded_rectangle(
        #        z_gap_0, z_max+gap_length,
        #        -outside, airway_line_0(z_airway_0),
        #        gap_length*2.0)
        #    )
        #jaw_clipper.rotate(1,0,0,90)
        #jaw_clipper.rotate(0,1,0,-90)
        #jaw_clipper.rotate(0,0,1,180)
        
        #jaw_clipper = shape.extrude_profile(
        #    airway_line_0.clipped(z_airway_0,z_airway_1+1.0),
        #    airway_line_1.clipped(z_airway_0,z_airway_1+1.0),
        #    cross_section = lambda x0, x1:
        #        shape.rounded_rectangle(
        #            -x0*0.8, #(Can't be larger than bore) 
        #            x1 * 0.995, #So as to not leave a little fuzz
        #            airway_ysize*-0.5,airway_ysize*0.5,
        #            (x1-x0)*2.0)
        #    )
        
        d = airway_x_low*2        
        jaw_clipper = shape.extrude_profile(
            profile.make_profile([(-outside*0.5-10, d),(outside*0.5+10, d)]),
            cross_section = lambda d:
                shape.halfrounded_rectangle(
                    -0.01, airway_x_low*1.01,
                    z_airway_0-d*0.5,z_max+d*0.5)
            )
        jaw_clipper.rotate(1,0,0, 90)
        
        #jaw = jaw_clipper.copy()
        #jaw.remove(space)
        #jaw.clip(body)   
        #self.save(jaw, 'jaw')
        
        #head = body.copy()
        #head.remove(jaw)
        #self.save(head, 'head')
        
        return body, space, jaw_clipper
    
    def run(self):
        body, space, jaw_clipper = self.construct()
        
        body.remove(space)
        self.save(body, 'whistle')
        
        jaw = body.copy()
        jaw.clip(jaw_clipper)
        body.remove(jaw_clipper)
        self.save(body, 'head')
        self.save(jaw, 'jaw')


@config.help("""\
Produce 3D models using the output of "demakein design-*-whistle:".
""")
class Make_whistle(make.Make_millable_instrument):
    def run(self):
        working = self.working
        designer = working.designer
        spec = working.spec
        workspace = self.get_workspace()
        
        whistle_maker = designer.get_whistle_maker()
        whistle_outer, whistle_inner, whistle_jaw_clipper = whistle_maker.construct()
        
        whistle_outer.move(0,0,spec.length)
        whistle_inner.move(0,0,spec.length)
        whistle_jaw_clipper.move(0,0,spec.length)
        whistle_outer.rotate(0,0,1,90)
        whistle_inner.rotate(0,0,1,90)
        whistle_jaw_clipper.rotate(0,0,1,90)
        
        n_holes = len(spec.hole_diameters)
        
        self.make_instrument(
             inner_profile = spec.inner.clipped(-50,spec.length),
             outer_profile = spec.outer.clipped(0, spec.length-whistle_maker.bore*1.5), #Don't paint over windcutter
             hole_positions = spec.hole_positions,
             hole_diameters = spec.hole_diameters,
             hole_vert_angles = spec.hole_angles,
             hole_horiz_angles = [0.0]*n_holes,
             xpad = [0.0]*n_holes,
             ypad = [0.0]*n_holes,
             with_fingerpad = [True]*n_holes,
             outside_extras = [ whistle_outer ],
             bore_extras = [ whistle_inner ],
             )

        cut1 = spec.hole_positions[2] + spec.hole_diameters[2]*0.75
        cut1 += spec.inner(cut1)*0.5
        cut2 = spec.hole_positions[5] + spec.hole_diameters[5]*0.75
        cut2 += spec.inner(cut2)*0.5
        
        true_length = self.working.instrument.extent().zmax
        
        if not self.mill:
            self.segment([ cut2 ], spec.length, up=True)
            self.segment([ cut1, cut2 ], spec.length, up=True)
        else:
            mid1 = spec.hole_positions[2]*0.5+spec.hole_diameters[2]*0.5-spec.hole_diameters[3]*0.5+spec.hole_positions[3]*0.5
            mid2 = spec.hole_positions[5]+spec.hole_diameters[5]
        
            upper_segments, lower_segments = pack.plan_segments([mid1/true_length,mid2/true_length], self.mill_length / true_length)
            
            whistle_jaw = whistle_jaw_clipper.copy()
            whistle_jaw.clip(self.working.outside)
            whistle_jaw.remove(self.working.bore)
            whistle_jaw.rotate(1,0,0, -90)
            whistle_jaw.move(0,0,-whistle_jaw.extent().zmin)
            self.save(whistle_jaw, 'jaw')
            jaw_packable = [ pack.Packable([ whistle_jaw, shape.empty_shape() ], -90, self.mill_diameter) ]

            self.working.bore.add(whistle_jaw_clipper)
            self.working.outside.remove(whistle_jaw_clipper)
                        
            pack.cut_and_pack(
                self.working.outside, self.working.bore,
                upper_segments, lower_segments,
                xsize=self.mill_length, 
                ysize=self.mill_width, 
                zsize=self.mill_thickness,
                bit_diameter=self.mill_diameter,
                save=self.save,
                
                extra_packables=[ jaw_packable ],
            )



if __name__ == '__main__':
    nesoni.run_tool(Make_whistle)


