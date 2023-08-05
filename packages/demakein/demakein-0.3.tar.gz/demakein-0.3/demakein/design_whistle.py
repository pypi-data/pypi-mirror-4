
import math, copy

from nesoni import config

from . import design, profile

@config.help("""\
Design a whistle with pennywhistle fingering.
""")
@config.Float_flag('tweak_gapextra')
class Design_folk_whistle(design.Instrument_designer):
    def get_whistle_maker(self):
        from . import make_whistle
        return make_whistle.Make_whistle_head(bore=self.inner_diameters[-1])
        
    closed_top = False
    
    initial_length = design.wavelength('D4') * 0.5
    
    min_hole_diameters = design.sqrt_scaler([ 3.0 ]*6)
    max_hole_diameters = design.sqrt_scaler([ 13.0 ]*6)

    balance = [ 0.05, 0.05, 0.05, 0.05 ]

    inner_diameters = design.sqrt_scaler([ 24.0, 20.0, 20.0, 21.0, 20.0, 20.0 ])
    outer_diameters = design.sqrt_scaler([ 38.0, 28.0, 28.0 ])
    
    initial_inner_fractions = [ 0.2, 0.6,0.65,0.7 ]
    
    initial_outer_fractions = [ 0.15 ]
    min_outer_fraction_sep = [ 0.15, 0.8 ]
    
    min_inner_fraction_sep = [ 0.01 ] * 6

    #min_outer_fraction_sep = [ 0.01, 0.5 ]

    fingerings = [
        ('D4',   [1,1,1,1,1,1]),
        ('E4',   [0,1,1,1,1,1]),
        ('F#4',  [0,0,1,1,1,1]),
        ('G4',   [0,0,0,1,1,1]),
        ('A4',   [0,0,0,0,1,1]),
        ('B4',   [0,0,0,0,0,1]),
        ('C5',   [0,0,0,1,1,0]),
        ('C#5',  [0,0,0,0,0,0]),
        ('D5',   [1,1,1,1,1,0]),
        ('E5',   [0,1,1,1,1,1]),
        ('F#5',  [0,0,1,1,1,1]),
        ('G5',   [0,0,0,1,1,1]),
        ('A5',   [0,0,0,0,1,1]),
        ('B5',   [0,0,0,0,0,1]),
        #('C#6',  [1,1,1,0,0,0]),
        ('C#6',  [0,0,0,0,0,0]),
        ('D6',   [1,1,1,1,1,1]),
    ]
    
    tweak_gapextra = 0.37
    
    def patch_instrument(self, inst):
        inst = copy.copy(inst)
        inst.true_length = inst.length
        inst.true_inner = inst.inner
        
        maker = self.get_whistle_maker()
        length = maker.effective_gap_height()
        diameter = maker.effective_gap_diameter()
        
        length += diameter * self.tweak_gapextra  # Virtual extra length seems to be needed, as with flute
        
        inst.inner = profile.Profile(
            inst.inner.pos + [ inst.length + length ],
            inst.inner.low + [ diameter ],
            inst.inner.high[:-1] + [ diameter, diameter ],
            )
        inst.length += length
        return inst


