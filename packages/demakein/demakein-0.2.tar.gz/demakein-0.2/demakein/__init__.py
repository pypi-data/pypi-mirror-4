
VERSION = '0.2'

from .design_flute import Design_tapered_pflute, Design_straight_pflute, Design_tapered_folk_flute, Design_straight_folk_flute
from .make_flute import Make_flute
from .make_cork import Make_cork

from .design_shawm import Design_shawm, Design_folk_shawm
from .make_shawm import Make_shawm
from .make_mouthpiece import Make_mouthpiece

from .make_panpipe import Make_panpipe

from .all import All

def main():
    """ Command line interface. """
    import nesoni    
    nesoni.run_toolbox([
            'Flutes',
            Design_tapered_pflute, 
            Design_straight_pflute, 
            Design_tapered_folk_flute, 
            Design_straight_folk_flute,
            Make_flute,
            Make_cork,
            
            'Shawms',
            Design_shawm,
            Design_folk_shawm,
            Make_shawm,
            Make_mouthpiece,
            
            'Panpipes',        
            Make_panpipe,
            
            'Everything',        
            All,
            '"demakein all:" uses the nesoni make system, see flags below.',
        ],
        show_make_flags=True,
        )

