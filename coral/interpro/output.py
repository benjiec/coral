import json
import csv
from typing import List

def add_header_to_tsv(tsv_path: str, json_path: str):
    with open(json_path) as jf:
        data = json.load(jf)
    if isinstance(data, list):
        first = data[0]
    elif isinstance(data, dict) and 'results' in data:
        first = data['results'][0]
    else:
        first = data
    columns = list(first.keys())
    with open(tsv_path) as tf:
        lines = tf.readlines()
    with open(tsv_path, 'w') as tf:
        tf.write('\t'.join(columns) + '\n')
        tf.writelines(lines)

def add_accession_column(tsv_path: str, accession: str):
    with open(tsv_path) as tf:
        reader = list(csv.reader(tf, delimiter='\t'))
    for i, row in enumerate(reader):
        if i == 0:
            row.append('accession')
        else:
            row.append(accession)
    with open(tsv_path, 'w', newline='') as tf:
        writer = csv.writer(tf, delimiter='\t')
        writer.writerows(reader)

def add_missing_sequences(tsv_path: str, fasta_path: str):
    seq_ids = set()
    with open(fasta_path) as f:
        for line in f:
            if line.startswith('>'):
                seq_ids.add(line[1:].split()[0])
    with open(tsv_path) as tf:
        reader = list(csv.reader(tf, delimiter='\t'))
    header = reader[0]
    seq_col = None
    for i, col in enumerate(header):
        if 'sequence' in col or 'protein' in col:
            seq_col = i
            break
    if seq_col is None:
        seq_col = 0
    present_ids = set(row[seq_col] for row in reader[1:])
    missing = seq_ids - present_ids
    for seq_id in missing:
        row = [''] * len(header)
        row[seq_col] = seq_id
        reader.append(row)
    with open(tsv_path, 'w', newline='') as tf:
        writer = csv.writer(tf, delimiter='\t')
        writer.writerows(reader) 