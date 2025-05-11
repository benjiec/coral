import os
from coral.utils.split_gff_by_sequence import split_gff_by_sequence

def main():
    input_files = [
        'data/ncbi/neu_acer_k2_genomic.gff',
        'data/ncbi/ofav_dov_v1_genomic.gff',
    ]
    output_dir = 'data/gff'
    os.makedirs(output_dir, exist_ok=True)
    for gff_file in input_files:
        print(f"Splitting {gff_file}...")
        out_files = split_gff_by_sequence(gff_file, output_dir)
        print(f"  Wrote {len(out_files)} files to {output_dir}")

if __name__ == "__main__":
    main() 