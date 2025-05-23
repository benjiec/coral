## Third Party Tools

### InterPro

Follow instruction here to download a local copy of InterProScan as a Docker image.

https://hub.docker.com/r/interpro/interproscan

Then you can run InterProScan on your favorite protein sequences using
```scripts/interpro```. This script runs InterProScan on Pfam in a Docker
container.


### LoVis4U

LoVis4U is a pipeline for comparing bacterial genomes. It clusters proteins
from genomes into clusters, annotate them, then draw them on a PDF. To make it
work for eukaryotes we need to split a single GFF with multiple fragments into
separate GFFs first.

1. Split GFF files into smaller GFF files, each containing just one sequence's
features and FASTA, using a script that calls
```coral/utils/split_gff_by_sequence.py```.

2. Run LoVis4U pipeline:
```lovis4u -gff /coral/data/gff -hl --set-category-colour -c A4p2 --run-hmmscan```

3. Run ```python3 coral/utils/extract_gff_info.py``` to generate a
```gff_summary.tsv``` file.

4. The following sets of CSVs can be used in Tableau, see tableau/ for workbook

  - ```gff_summary.tsv```: sequence ID to genome build
  - ```<lovis4u output directory>/feature_annotation_table.tsv```: feature and annotations
  - ```<lovis4u output directory>/locus_annotation_table.tsv```: sequence (fragment) information
  - ```<lovis4u output directory>/hmmscan/*.tsv```: PyHMMer outputs
