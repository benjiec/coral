import os
import subprocess
import zipfile
import glob
import shutil

BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession"

def download_and_extract_prot_fasta(accession: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    zip_path = os.path.join(output_dir, f"{accession}.zip")
    extract_dir = os.path.join(output_dir, accession)
    url = f"{BASE_URL}/{accession}/download?include_annotation_type=PROT_FASTA"
    try:
        subprocess.run([
            "wget", "-O", zip_path, url
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to download {accession}: {e}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        raise RuntimeError(f"Failed to extract {zip_path}: {e}")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
    fasta_files = glob.glob(os.path.join(extract_dir, '**', '*.faa'), recursive=True)
    if not fasta_files:
        fasta_files = glob.glob(os.path.join(extract_dir, '**', '*.fasta'), recursive=True)
    if not fasta_files:
        raise FileNotFoundError(f"No PROT_FASTA file found for {accession}")
    return fasta_files[0] 