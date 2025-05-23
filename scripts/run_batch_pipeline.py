import os
import sys
from coral.ncbi.download import download_and_extract_prot_fasta
from coral.ncbi.taxonomy import fetch_and_append_taxonomy
from coral.interpro.exec import run_interproscan
from coral.interpro.output import add_header_to_tsv, add_accession_column, add_missing_sequences

ACCESSIONS_FILE = 'data/accessions.txt'
OUTPUTS_DIR = 'outputs'
INTERPRO_OUTPUTS = 'interpro_outputs'
TAXONOMY_TXT = os.path.join(OUTPUTS_DIR, 'taxonomy.tsv')

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(INTERPRO_OUTPUTS, exist_ok=True)


def main():
    errors = []
    processed = 0
    with open(ACCESSIONS_FILE) as f:
        accessions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    for accession in accessions:
        try:
            print(f"Processing {accession}...")
            # Step 1: Download FASTA
            fasta_path = download_and_extract_prot_fasta(accession, OUTPUTS_DIR)
            # Step 2: Run InterProScan
            tsv_path, json_path = run_interproscan(fasta_path)
            # Step 3: Copy TSV to outputs and update
            out_tsv = os.path.join(OUTPUTS_DIR, f"{accession}.tsv")
            with open(tsv_path) as src, open(out_tsv, 'w') as dst:
                dst.writelines(src.readlines())
            add_header_to_tsv(out_tsv, json_path)
            add_accession_column(out_tsv, accession)
            add_missing_sequences(out_tsv, fasta_path)
            # Step 4: Fetch taxonomy
            fetch_and_append_taxonomy(accession, TAXONOMY_TXT)
            processed += 1
        except Exception as e:
            print(f"Error processing {accession}: {e}", file=sys.stderr)
            errors.append((accession, str(e)))
    print(f"\nProcessed {processed} accessions. {len(errors)} errors.")
    if errors:
        print("Errors:")
        for acc, err in errors:
            print(f"  {acc}: {err}")

if __name__ == '__main__':
    main() 
