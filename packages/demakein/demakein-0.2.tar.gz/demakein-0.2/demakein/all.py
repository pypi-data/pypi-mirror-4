
import demakein

import nesoni
from nesoni import config

@config.help("""\
Design and make all instruments, in a variety of sizes.
""","""\
Note that I use the terms "soprano", "alto", "tenor", and "bass" to \
refer to the sizes of instruments. Flutes and shawms I name this way are actually \
an octave above the singing voices of the same name.
""")
@config.Bool_flag('panpipes', 'Do panpipes.')
@config.Bool_flag('flutes', 'Do flutes.')
@config.Bool_flag('shawms', 'Do shawms.')
@config.String_flag('version', 'version code, for file names')
class All(config.Action_with_output_dir):
    panpipes = True
    flutes = True
    shawms = True
    version = demakein.VERSION.lstrip('0.')
    
    def _do_flute(self, model_name, model_code, designer, transpose, size_name):
        workspace = self.get_workspace()
        outdir = workspace / (model_name+'-'+size_name)

        designer(
            outdir,
            transpose=transpose
            ).make()
        
        demakein.Make_flute(
            outdir,
            prefix = 'print-'+model_code+'-'+size_name+'-'+self.version+'-',
            decorate=True,
            ).make()

    def _do_shawm(self, model_name, model_code, designer, transpose, bore, size_name):
        workspace = self.get_workspace()
        outdir = workspace / (model_name+'-'+size_name)
    
        designer(
            outdir,
            transpose=transpose,
            bore=bore,
            ).make()

        demakein.Make_shawm(
            outdir,
            prefix='print-'+model_code+'-'+size_name+'-'+self.version+'-',
            decorate=True,
            ).make()
                
    def run(self):
        workspace = self.get_workspace()
        
        stage = nesoni.Stage()
        
        if self.panpipes:
            if self.make:
                demakein.Make_panpipe(
                    workspace/'panpipe'
                    ).process_make(stage)
        
        if self.flutes:
            for model_name, model_code, designer in [
                    ('straight-folk-flute', 'sff', demakein.Design_straight_folk_flute),
                    ('tapered-folk-flute',  'tff', demakein.Design_tapered_folk_flute),
                    ('straight-pflute',     'spf', demakein.Design_straight_pflute),
                    ('tapered-pflute',      'tpf', demakein.Design_tapered_pflute),
                    ]:
                for transpose, size_name in [
                        (0, 'tenor'),
                        (5, 'alto'),
                        (12, 'soprano'),
                        ]:
                    stage.process(self._do_flute,model_name,model_code,designer,transpose,size_name)

        if self.shawms:
            for model_name, model_code, designer in [
                 ('shawm', 'sh', demakein.Design_shawm),
                 ('folk-shawm', 'fsh', demakein.Design_folk_shawm),
                 ]:
                 for transpose, bore, size_name in [
                         (5,  4.0, 'alto-4mm'),
                         (0,  4.0, 'tenor-4mm'),
                         (0,  6.0, 'tenor-6mm'),
                         (-7, 6.0, 'bass-6mm'),
                         ]:
                     stage.process(self._do_shawm,model_name,model_code,designer,transpose,bore,size_name)

        stage.barrier()


