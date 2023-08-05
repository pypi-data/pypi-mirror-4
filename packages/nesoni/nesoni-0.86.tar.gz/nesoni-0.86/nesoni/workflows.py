
import nesoni

from nesoni import config, clip, samshrimp, samconsensus, working_directory

@config.help('Analyse reads from a single sample.')
@config.Positional('reference', 'Reference directory created by "make-reference:".')
@config.Section('reads', 'Files containing unpaired reads.')
@config.Section('interleaved', 'Files containing interleaved read pairs.')
@config.Grouped_section('pairs', 'Pair of files containing read pairs.')
@config.Configurable_section('clip', 'Options for clip', allow_none=True)
@config.Configurable_section('align', 'Options for shrimp')
@config.Configurable_section('filter', 'Options for filter')
@config.Configurable_section('reconsensus', 'Options for reconsensus', allow_none=True)
class Analyse_sample(config.Action_with_output_dir):
    reference = None
    reads = [ ]
    interleaved = [ ]
    pairs = [ ]

    clip = clip.Clip()
    align = samshrimp.Shrimp()
    filter = samconsensus.Filter()
    reconsensus = samconsensus.Reconsensus()
    
    _workspace_class = working_directory.Working
    
    def run(self):
        reads = self.reads
        interleaved = self.interleaved
        pairs = self.pairs
        
        workspace = self.get_workspace()
        
        if self.clip:
            act = self.clip(
                workspace/'clipped',
                reads = reads,
                interleaved = interleaved,
                pairs = pairs,
            )
            act.make()
            reads = act.reads_output_filenames()
            interleaved = act.interleaved_output_filenames()
            pairs = [ ]
        
        self.align(
            self.output_dir,
            self.reference,
            reads = reads,
            interleaved = interleaved,
            pairs = pairs, 
        ).make()
        
        if self.filter:
            self.filter(
                self.output_dir
            ).make()
        
        if self.reconsensus:
            self.reconsensus(
                self.output_dir
            ).make()




