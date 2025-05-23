import os
import subprocess
import zipfile
import glob
import shutil

BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession"

def download_and_extract_prot_fasta(accession: str, output_dir: str) -> str:
    """
    Downloads and extracts protein FASTA file for a given accession.
    Cleans up all intermediate files after extraction.
    Returns path to the extracted FASTA file.
    """
    os.makedirs(output_dir, exist_ok=True)
    zip_path = os.path.join(output_dir, f"{accession}.zip")
    extract_dir = os.path.join(output_dir, accession)
    url = f"{BASE_URL}/{accession}/download?include_annotation_type=PROT_FASTA"
    
    try:
        # Download file
        subprocess.run([
            "wget", "-O", zip_path, url
        ], check=True)
        
        # Extract file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # Find FASTA files
        fasta_files = glob.glob(os.path.join(extract_dir, '**', '*.faa'), recursive=True)
        if not fasta_files:
            fasta_files = glob.glob(os.path.join(extract_dir, '**', '*.fasta'), recursive=True)
        
        if not fasta_files:
            raise FileNotFoundError(f"No PROT_FASTA file found for {accession}")
            
        # Get the first FASTA file path
        fasta_path = fasta_files[0]
        
        # Move FASTA file to output directory with standardized name
        final_fasta_path = os.path.join(output_dir, f"{accession}.faa")
        shutil.copy2(fasta_path, final_fasta_path)
        
        return final_fasta_path
        
    except Exception as e:
        raise e
    finally:
        # Clean up all intermediate files, regardless of success or failure
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir) 