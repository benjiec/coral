import os
import sys
import shutil
import traceback
from coral.ncbi.download import download_and_extract_prot_fasta
from coral.ncbi.taxonomy import fetch_and_append_taxonomy
from coral.interpro.exec import run_interproscan
from coral.interpro.output import add_header_to_tsv, add_accession_column, add_missing_sequences

OUTPUTS_DIR = 'outputs'
INTERPRO_OUTPUTS = 'interpro_outputs'
TAXONOMY_TXT = os.path.join(OUTPUTS_DIR, 'taxonomy.txt')

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(INTERPRO_OUTPUTS, exist_ok=True)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch InterProScan pipeline")
    parser.add_argument('accessions_file', help='File with list of accessions')
    parser.add_argument('--skip-interpro', action='store_true', help='Skip running InterProScan and use existing outputs')
    args = parser.parse_args()

    errors = []
    processed = 0
    warnings = []
    with open(args.accessions_file) as f:
        accessions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    for accession in accessions:
        try:
            print(f"Processing {accession}...")
            # Step 1: Download FASTA
            try:
                fasta_path = download_and_extract_prot_fasta(accession, OUTPUTS_DIR)
            except FileNotFoundError as fnf:
                warning = f"Warning: No protein FASTA found for {accession}. Skipping."
                print(warning, file=sys.stderr)
                warnings.append((accession, str(fnf)))
                continue
            # Step 2: Run InterProScan or skip
            if args.skip_interpro:
                print(f"Skipping InterProScan for {accession}, using existing outputs.")
                tsv_path = os.path.join(INTERPRO_OUTPUTS, f"{accession}.tsv")
                json_path = os.path.join(INTERPRO_OUTPUTS, f"{accession}.json")
            else:
                tsv_path, json_path = run_interproscan(fasta_path, accession, INTERPRO_OUTPUTS)
            # Step 3: Copy TSV to outputs and update
            out_tsv = os.path.join(OUTPUTS_DIR, f"{accession}.tsv")
            shutil.copy(tsv_path, out_tsv)
            add_header_to_tsv(out_tsv)
            add_accession_column(out_tsv, accession)
            add_missing_sequences(out_tsv, fasta_path, accession)
            # Step 4: Fetch taxonomy
            fetch_and_append_taxonomy(accession, TAXONOMY_TXT)
            processed += 1
        except Exception as e:
            print(f"Error processing {accession}: {e}", file=sys.stderr)
            traceback.print_exc()
            errors.append((accession, str(e)))
    print(f"\nProcessed {processed} accessions. {len(errors)} errors. {len(warnings)} warnings.")
    if errors:
        print("Errors:")
        for acc, err in errors:
            print(f"  {acc}: {err}")
    if warnings:
        print("Warnings:")
        for acc, warn in warnings:
            print(f"  {acc}: {warn}")

if __name__ == '__main__':
    main() 
