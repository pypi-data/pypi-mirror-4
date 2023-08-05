
import demakein

from nesoni import config

@config.help("""
Design and make all instruments.
""")
@config.Bool_flag('design', 'Run design step.')
@config.Bool_flag('make', 'Run make step.')
@config.String_flag('version', 'version code, for file names')
class All(config.Action_with_output_dir):
    design = True
    make = True
    version = demakein.VERSION.lstrip('0.')

    def run(self):
        workspace = self.get_workspace()
        
        # Flutes
        for transpose, size_name in [
                (5, 'alto'),
                (0, 'tenor'),
                (12, 'soprano'),
                ]:
            for model_name, model_code, decorate, designer in [
                    ('tapered_folk_flute',  'tff', False, demakein.Design_tapered_folk_flute),
                    ('straight_folk_flute', 'sff', True,  demakein.Design_straight_folk_flute),
                    ('tapered_pflute',      'tpf', False, demakein.Design_tapered_pflute),
                    ('straight_pflute',     'spf', True,  demakein.Design_straight_pflute),
                    ]:
                outdir = workspace / (size_name+'_'+model_name)
                print
                print outdir
                if self.design:
                    designer(
                        outdir,
                        transpose=transpose
                        ).run()
                
                if self.make:
                    demakein.Make_flute(
                        outdir,
                        prefix = 'print-'+size_name+'-'+model_code+'-'+self.version+'-',
                        decorate=True,
                        ).run()