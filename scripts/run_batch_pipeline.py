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
TAXONOMY_TSV = os.path.join(OUTPUTS_DIR, 'taxonomy.tsv')

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(INTERPRO_OUTPUTS, exist_ok=True)

def cleanup_intermediate_files(accession: str, output_dir: str):
    """Clean up all intermediate files for a given accession."""
    # Remove NCBI intermediate files
    extract_dir = os.path.join(output_dir, accession)
    zip_path = os.path.join(output_dir, f"{accession}.zip")
    fasta_path = os.path.join(output_dir, f"{accession}.faa")
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists(fasta_path):
        os.remove(fasta_path)

def check_existing_interpro_results(accession: str, interpro_dir: str) -> bool:
    """Check if InterProScan results already exist for the given accession."""
    tsv_path = os.path.join(interpro_dir, f"{accession}.tsv")
    json_path = os.path.join(interpro_dir, f"{accession}.json")
    return os.path.exists(tsv_path) and os.path.exists(json_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch InterProScan pipeline")
    parser.add_argument('accessions_file', help='File with list of accessions')
    parser.add_argument('--skip-interpro', action='store_true', help='Skip running InterProScan and use existing outputs')
    parser.add_argument('--force-interpro', action='store_true', help='Force running InterProScan even if results exist')
    args = parser.parse_args()

    errors = []
    processed = 0
    warnings = []
    skipped = 0
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
            
            # Step 2: Check if we should run InterProScan
            has_existing_results = check_existing_interpro_results(accession, INTERPRO_OUTPUTS)
            should_skip_interpro = args.skip_interpro or (has_existing_results and not args.force_interpro)
            
            if should_skip_interpro:
                if has_existing_results:
                    print(f"Found existing InterProScan results for {accession}, skipping...")
                else:
                    print(f"Skipping InterProScan for {accession} (--skip-interpro flag)")
                tsv_path = os.path.join(INTERPRO_OUTPUTS, f"{accession}.tsv")
                json_path = os.path.join(INTERPRO_OUTPUTS, f"{accession}.json")
                if not os.path.exists(tsv_path) or not os.path.exists(json_path):
                    warning = f"Warning: InterProScan outputs not found for {accession} despite skip flag"
                    print(warning, file=sys.stderr)
                    warnings.append((accession, warning))
                    continue
                skipped += 1
            else:
                tsv_path, json_path = run_interproscan(fasta_path, accession, INTERPRO_OUTPUTS)
            
            # Step 3: Copy TSV to outputs and update
            out_tsv = os.path.join(OUTPUTS_DIR, f"{accession}.tsv")
            shutil.copy(tsv_path, out_tsv)
            add_header_to_tsv(out_tsv)
            add_accession_column(out_tsv, accession)
            add_missing_sequences(out_tsv, fasta_path, accession)
            
            # Step 4: Fetch taxonomy
            fetch_and_append_taxonomy(accession, TAXONOMY_TSV)
            processed += 1
            
            # Clean up all intermediate files
            cleanup_intermediate_files(accession, OUTPUTS_DIR)
            
        except Exception as e:
            print(f"Error processing {accession}: {e}", file=sys.stderr)
            traceback.print_exc()
            errors.append((accession, str(e)))
            # Clean up even if there was an error
            cleanup_intermediate_files(accession, OUTPUTS_DIR)
            
    print(f"\nProcessed {processed} accessions. {skipped} skipped. {len(errors)} errors. {len(warnings)} warnings.")
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
