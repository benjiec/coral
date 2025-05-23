import requests

def fetch_and_append_taxonomy(accession: str, taxonomy_txt: str):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=assembly&term={accession}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    uid = r.json()['esearchresult']['idlist'][0]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=assembly&id={uid}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    doc = r.json()['result'][uid]
    species = doc.get('speciesname', '')
    taxid = doc.get('taxid', '')
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id={taxid}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    lineage = r.json()[0]['LineageEx']
    order = class_ = family = ''
    for item in lineage:
        if item['Rank'] == 'order':
            order = item['ScientificName']
        elif item['Rank'] == 'class':
            class_ = item['ScientificName']
        elif item['Rank'] == 'family':
            family = item['ScientificName']
    with open(taxonomy_txt, 'a') as f:
        f.write(f"{order}\t{class_}\t{family}\t{species}\t{accession}\n") 