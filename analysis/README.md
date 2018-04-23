# `hmc` Analysis Tools

The `hmc` program from Chroma generates XML output which contains information
about the generated trajectories. This suite of analysis tools can go through
the output XML with the XPath query system and extract some data and plot it.

## Dependencies

- `python3`
- `python3-lxml`
- `python3-numpy`
- `python3-scipy`
- `python3-matplotlib`
- `python3-doit`

## Usage

Create a directory like `Runs` where you have different subdirectories for each
run, say `sWC_A2p1_Mpi270_L32T96-forward`. In each of these run directories you
need to have a directory named `hmc-out` which contains text and xml logs and
outputs:

- `hmc.1784081.hazelhen-batch.hww.hlrs.de.log.xml.gz`
- `hmc.1784081.hazelhen-batch.hww.hlrs.de.out.txt.gz`
- `hmc.1784081.hazelhen-batch.hww.hlrs.de.out.xml.gz`

They need to be compressed because the scripts now expect this and it saves
around a factor 10 in disk space. Chroma is very verbose.

Then from the source checkout of the analysis scripts call the analysis:

```bash
python3 -m doit -d path/to/Runs
```

You should then see various tasks being done. Eventually there should be a
directory `extract` which contains flat text files, JSON and CSV data for
further analysis with a language of your choice. The directory `plot` contains
default plots for most of the quantities. These are indented for a quick
overview.

<!-- vim: set spell textwidth=79 : -->
