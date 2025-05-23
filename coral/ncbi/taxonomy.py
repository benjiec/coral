import requests
import os
import xml.etree.ElementTree as ET

def fetch_and_append_taxonomy(accession: str, taxonomy_tsv: str):
    # Write header if file does not exist or is empty
    header = "Order\tClass\tFamily\tGenus\tSpecies\tAccession\tTaxID\n"
    if not os.path.exists(taxonomy_tsv) or os.path.getsize(taxonomy_tsv) == 0:
        with open(taxonomy_tsv, 'w') as f:
            f.write(header)
    # Remove old line with same accession if exists
    with open(taxonomy_tsv, 'r') as f:
        lines = f.readlines()
    def is_header(line):
        return line.strip() == header.strip()
    def is_not_accession(line):
        parts = line.rstrip().split('\t')
        return is_header(line) or (len(parts) < 2 or parts[-2] != accession)
    lines = [line for line in lines if is_not_accession(line)]
    with open(taxonomy_tsv, 'w') as f:
        f.writelines(lines)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=assembly&term={accession}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    uid_list = r.json()['esearchresult']['idlist']
    if not uid_list:
        print(f"Warning: No UID found for accession {accession}. Skipping taxonomy.", flush=True)
        return
    uid = uid_list[0]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=assembly&id={uid}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    doc = r.json()['result'][uid]
    species = doc.get('speciesname', '')
    taxid = doc.get('taxid', '')
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id={taxid}&retmode=xml"
    r = requests.get(url)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    order = class_ = family = genus = ''
    for taxon in root.findall('.//LineageEx/Taxon'):
        rank = taxon.findtext('Rank')
        name = taxon.findtext('ScientificName')
        if rank == 'order':
            order = name
        elif rank == 'class':
            class_ = name
        elif rank == 'family':
            family = name
        elif rank == 'genus':
            genus = name
    with open(taxonomy_tsv, 'a') as f:
        f.write(f"{order}\t{class_}\t{family}\t{genus}\t{species}\t{accession}\t{taxid}\n") 