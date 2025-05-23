import json
import csv
from typing import List

INTERPRO_TSV_HEADER = [
    "Protein Accession",
    "Sequence MD5 digest",
    "Sequence Length",
    "Analysis",
    "Signature Accession",
    "Signature Description",
    "Start location",
    "Stop location",
    "Score",
    "Status",
    "Date",
    "InterPro accession",
    "InterPro description",
    "GO annotations",
    "Pathways annotations"
]

def add_header_to_tsv(tsv_path: str):
    with open(tsv_path) as tf:
        lines = tf.readlines()
    with open(tsv_path, 'w') as tf:
        tf.write('\t'.join(INTERPRO_TSV_HEADER) + '\n')
        tf.writelines(lines)

def add_accession_column(tsv_path: str, accession: str):
    with open(tsv_path) as tf:
        reader = list(csv.reader(tf, delimiter='\t'))
    for i, row in enumerate(reader):
        if i == 0:
            row.append('Genome Accession')
        else:
            row.append(accession)
    with open(tsv_path, 'w', newline='') as tf:
        writer = csv.writer(tf, delimiter='\t')
        writer.writerows(reader)

def add_missing_sequences(tsv_path: str, fasta_path: str, accession: str):
    seq_ids = set()
    with open(fasta_path) as f:
        for line in f:
            if line.startswith('>'):
                seq_ids.add(line[1:].split()[0])
    with open(tsv_path) as tf:
        reader = list(csv.reader(tf, delimiter='\t'))
    header = reader[0]
    seq_col = None
    acc_col = None
    for i, col in enumerate(header):
        if 'Protein Accession' in col or 'sequence' in col or 'protein' in col:
            seq_col = i
        if 'Genome Accession' in col:
            acc_col = i
    if seq_col is None:
        seq_col = 0
    if acc_col is None:
        acc_col = len(header) - 1
    present_ids = set(row[seq_col] for row in reader[1:])
    missing = seq_ids - present_ids
    for seq_id in missing:
        row = [''] * len(header)
        row[seq_col] = seq_id
        row[acc_col] = accession
        reader.append(row)
    with open(tsv_path, 'w', newline='') as tf:
        writer = csv.writer(tf, delimiter='\t')
        writer.writerows(reader) 