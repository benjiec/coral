import os
import subprocess

def run_interproscan(fasta_path: str, accession: str, output_dir: str, interpro_script: str = 'scripts/interpro') -> str:
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run([
        interpro_script, fasta_path, accession, output_dir
    ], check=True)
    tsv_path = os.path.join(output_dir, f"{accession}.tsv")
    if not os.path.exists(tsv_path):
        raise FileNotFoundError(f"InterProScan TSV output not found for {accession} in {output_dir}")
    return tsv_path 