import os
from typing import Dict, List, Optional

def split_gff_by_sequence(gff_path: str, output_dir: Optional[str] = None) -> List[str]:
    """
    Splits a multi-sequence GFF3 file (with embedded FASTA) into per-sequence GFF files.
    Each output file contains the features and the corresponding FASTA for one sequence.
    Returns a list of output file paths.
    """
    if output_dir is None:
        output_dir = os.path.dirname(gff_path)
    os.makedirs(output_dir, exist_ok=True)

    # Read all lines
    with open(gff_path, 'r') as infile:
        lines = infile.readlines()

    # Find FASTA section
    try:
        fasta_idx = next(i for i, line in enumerate(lines) if line.startswith('##FASTA'))
    except StopIteration:
        return []

    global_headers = []
    seq_region_headers: Dict[str, List[str]] = {}
    species_headers: Dict[str, List[str]] = {}
    features: Dict[str, List[str]] = {}

    last_seqid = None
    for line in lines[:fasta_idx]:
        if line.startswith('##sequence-region'):
            # Example: ##sequence-region JARQWQ010000001.1 1 8337363
            parts = line.strip().split()
            if len(parts) > 1:
                seqid = parts[1]
                seq_region_headers.setdefault(seqid, []).append(line)
                last_seqid = seqid
        elif line.startswith('##species'):
            # Associate with last seen seqid
            if last_seqid is not None:
                species_headers.setdefault(last_seqid, []).append(line)
        elif line.startswith('#'):
            # Global header (##gff-version, #!...)
            if not (line.startswith('##sequence-region') or line.startswith('##species')):
                global_headers.append(line)
        elif line.strip():
            seqid = line.split('\t', 1)[0]
            features.setdefault(seqid, []).append(line)

    # Parse FASTA section
    fasta: Dict[str, List[str]] = {}
    current_seqid = None
    for line in lines[fasta_idx+1:]:
        if line.startswith('>'):
            current_seqid = line[1:].split()[0]
            fasta[current_seqid] = [line]
        elif current_seqid:
            fasta[current_seqid].append(line)

    # Write out per-sequence GFF files
    output_files = []
    for seqid in features:
        out_path = os.path.join(output_dir, f"{seqid}.gff")
        with open(out_path, 'w') as out:
            for h in global_headers:
                out.write(h)
            for h in seq_region_headers.get(seqid, []):
                out.write(h)
            for h in species_headers.get(seqid, []):
                out.write(h)
            for f in features[seqid]:
                out.write(f)
            out.write('##FASTA\n')
            if seqid in fasta:
                for l in fasta[seqid]:
                    out.write(l)
        output_files.append(out_path)
    return output_files 