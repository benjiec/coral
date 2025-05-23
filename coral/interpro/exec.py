import os
import subprocess
import glob

def run_interproscan(fasta_path: str, output_dir: str, interpro_script: str = 'scripts/interpro') -> tuple:
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run([
        interpro_script, fasta_path, output_dir
    ], check=True)
    base = os.path.splitext(os.path.basename(fasta_path))[0]
    tsv_files = glob.glob(os.path.join(output_dir, f"{base}*.tsv"))
    json_files = glob.glob(os.path.join(output_dir, f"{base}*.json"))
    if not tsv_files or not json_files:
        raise FileNotFoundError(f"InterProScan output not found for {fasta_path} in {output_dir}")
    return tsv_files[0], json_files[0] 