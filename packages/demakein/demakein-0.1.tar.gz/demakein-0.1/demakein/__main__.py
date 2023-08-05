
import nesoni

from . import *

nesoni.run_toolbox([
        Design_tapered_pflute, 
        Design_straight_pflute, 
        Design_tapered_folk_flute, 
        Design_straight_folk_flute,
        Make_flute,          
        Make_panpipe,        
        All
    ],
    show_make_flags=False,
    )