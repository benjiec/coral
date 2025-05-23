import os

gff_dir = 'data/gff'
out_tsv = os.path.join(gff_dir, 'gff_summary.tsv')

def extract_gff_info(gff_path):
    genome_build = None
    genome_build_accession = None
    sequence_ids = []
    with open(gff_path, 'r') as f:
        for line in f:
            if line.startswith('#!genome-build '):
                genome_build = line.strip().split(' ', 1)[1]
            elif line.startswith('#!genome-build-accession '):
                genome_build_accession = line.strip().split(' ', 1)[1]
            elif line.startswith('##sequence-region '):
                seq_id = line.strip().split()[1]
                sequence_ids.append(seq_id)
            # Stop reading after the header (when features start)
            if not line.startswith('#'):
                break
    return sequence_ids, genome_build, genome_build_accession

def main():
    rows = []
    for fname in os.listdir(gff_dir):
        if not fname.endswith('.gff'):
            continue
        gff_path = os.path.join(gff_dir, fname)
        sequence_ids, genome_build, genome_build_accession = extract_gff_info(gff_path)
        for seq_id in sequence_ids:
            rows.append([seq_id, genome_build, genome_build_accession])
    with open(out_tsv, 'w') as out:
        out.write('\t'.join(['sequence_id', 'genome_build', 'genome_build_accession']) + '\n')
        for row in rows:
            out.write('\t'.join(row) + '\n')

if __name__ == '__main__':
    main() 