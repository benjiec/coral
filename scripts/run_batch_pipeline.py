import os
import sys
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
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <accession_list_file>", file=sys.stderr)
        sys.exit(1)
    accessions_file = sys.argv[1]
    errors = []
    processed = 0
    warnings = []
    with open(accessions_file) as f:
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
            # Step 2: Run InterProScan
            tsv_path, json_path = run_interproscan(fasta_path, accession, INTERPRO_OUTPUTS)
            # Step 3: Update TSV in place
            add_header_to_tsv(tsv_path)
            add_accession_column(tsv_path, accession)
            add_missing_sequences(tsv_path, fasta_path, accession)
            # Step 4: Fetch taxonomy
            fetch_and_append_taxonomy(accession, TAXONOMY_TXT)
            processed += 1
        except Exception as e:
            print(f"Error processing {accession}: {e}", file=sys.stderr)
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
