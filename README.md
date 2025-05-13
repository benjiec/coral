# coral

Split GFF files into smaller GFF files, each containing just one sequence's features and FASTA, using coral/utils/split_gff_by_sequence.py.

Run LoVis4U pipeline: lovis4u -gff /coral/data/gff -hl --set-category-colour -c A4p2 --run-hmmscan

Run python3 scripts/extract_gff_info.py to generate a data/gff/gff_summary.tsv file.

4 sets of CSVs:
  - data/gff/gff_summary.tsv: sequence ID to genome build
  - <lovis4u output directory>/feature_annotation_table.tsv: feature and annotations
  - <lovis4u output directory>/locus_annotation_table.tsv: sequence (fragment) information
  - <lovis4u output directory>/hmmscan/*.tsv: PyHMMer outputs
