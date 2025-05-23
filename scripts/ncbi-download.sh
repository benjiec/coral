#!/bin/bash

# NCBI Datasets v2alpha Download Script
# Downloads DNA and protein FASTA and GFF files for a list of genome accessions

# Configuration
BASE_URL="https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession"
ANNOTATION_TYPES="GENOME_FASTA,PROT_FASTA,GENOME_GFF"
OUTPUT_DIR="ncbi-downloads"
DELAY=1  # Delay between requests (seconds) to be respectful to NCBI servers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] <accession_file>"
    echo ""
    echo "Downloads protein FASTA and GFF files from NCBI Datasets API v2alpha"
    echo ""
    echo "Arguments:"
    echo "  accession_file    File containing one genome accession per line (e.g., GCF_000001405.40)"
    echo ""
    echo "Options:"
    echo "  -o, --output DIR     Output directory (default: ncbi_downloads)"
    echo "  -t, --types TYPES    Comma-separated annotation types (default: PROT_FASTA,GENOME_GFF)"
    echo "  -d, --delay SECONDS  Delay between requests (default: 1)"
    echo "  -k, --keep-zip       Keep original zip files after extraction"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Valid annotation types:"
    echo "  GENOME_FASTA, PROT_FASTA, RNA_FASTA, CDS_FASTA,"
    echo "  GENOME_GFF, GENOME_GBFF, GENOME_GTF, SEQUENCE_REPORT"
    echo ""
    echo "Example:"
    echo "  $0 -o my_genomes -t PROT_FASTA,GENOME_GFF accessions.txt"
}

# Parse command line arguments
KEEP_ZIP=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -t|--types)
            ANNOTATION_TYPES="$2"
            shift 2
            ;;
        -d|--delay)
            DELAY="$2"
            shift 2
            ;;
        -k|--keep-zip)
            KEEP_ZIP=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            ACCESSION_FILE="$1"
            shift
            ;;
    esac
done

# Check if accession file is provided
if [[ -z "$ACCESSION_FILE" ]]; then
    print_status "$RED" "Error: Accession file is required"
    show_usage
    exit 1
fi

# Check if accession file exists
if [[ ! -f "$ACCESSION_FILE" ]]; then
    print_status "$RED" "Error: Accession file '$ACCESSION_FILE' not found"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"
if [[ $? -ne 0 ]]; then
    print_status "$RED" "Error: Could not create output directory '$OUTPUT_DIR'"
    exit 1
fi

# Check for required tools
for tool in curl unzip; do
    if ! command -v $tool &> /dev/null; then
        print_status "$RED" "Error: $tool is required but not installed"
        exit 1
    fi
done

# Count total accessions
TOTAL_ACCESSIONS=$(wc -l < "$ACCESSION_FILE")
print_status "$BLUE" "Starting download of $TOTAL_ACCESSIONS genome(s)"
print_status "$BLUE" "Output directory: $OUTPUT_DIR"
print_status "$BLUE" "Annotation types: $ANNOTATION_TYPES"
print_status "$BLUE" "Delay between requests: ${DELAY}s"

# Initialize counters
SUCCESS_COUNT=0
FAILED_COUNT=0
CURRENT=0

# Read accessions and process each one
while IFS= read -r accession || [[ -n "$accession" ]]; do
    # Skip empty lines and comments
    [[ -z "$accession" || "$accession" =~ ^[[:space:]]*# ]] && continue
    
    # Remove whitespace
    accession=$(echo "$accession" | xargs)
    
    ((CURRENT++))
    
    print_status "$YELLOW" "[$CURRENT/$TOTAL_ACCESSIONS] Processing: $accession"
    
    # Create URL
    URL="${BASE_URL}/${accession}/download?include_annotation_type=${ANNOTATION_TYPES}"
    
    # Set output filename
    ZIP_FILE="${OUTPUT_DIR}/${accession}.zip"
    EXTRACT_DIR="${OUTPUT_DIR}/${accession}"
    
    # Download with curl
    print_status "$BLUE" "Downloading: $accession"
    
    # Use curl with error handling
    HTTP_CODE=$(curl -w "%{http_code}" -s -L "$URL" -o "$ZIP_FILE" --connect-timeout 30 --max-time 300)
    
    if [[ $? -eq 0 && "$HTTP_CODE" == "200" ]]; then
        # Check if file was actually downloaded and is not empty
        if [[ -s "$ZIP_FILE" ]]; then
            print_status "$GREEN" "Downloaded successfully: $accession"
            
            # Extract the zip file
            print_status "$BLUE" "Extracting: $accession"
            mkdir -p "$EXTRACT_DIR"
            
            if unzip -q "$ZIP_FILE" -d "$EXTRACT_DIR"; then
                print_status "$GREEN" "Extracted successfully: $accession"
                
                # Remove zip file unless --keep-zip is specified
                if [[ "$KEEP_ZIP" == false ]]; then
                    rm "$ZIP_FILE"
                fi
                
                ((SUCCESS_COUNT++))
            else
                print_status "$RED" "Failed to extract: $accession"
                rm -rf "$EXTRACT_DIR"  # Clean up failed extraction
                ((FAILED_COUNT++))
            fi
        else
            print_status "$RED" "Downloaded file is empty or corrupted: $accession"
            rm -f "$ZIP_FILE"  # Remove empty file
            ((FAILED_COUNT++))
        fi
    else
        print_status "$RED" "Failed to download: $accession (HTTP: $HTTP_CODE)"
        rm -f "$ZIP_FILE"  # Remove any partial download
        ((FAILED_COUNT++))
    fi
    
    # Add delay between requests (except for the last one)
    if [[ $CURRENT -lt $TOTAL_ACCESSIONS ]]; then
        sleep "$DELAY"
    fi
    
done < "$ACCESSION_FILE"

# Print summary
echo ""
print_status "$BLUE" "=== DOWNLOAD SUMMARY ==="
print_status "$GREEN" "Successful downloads: $SUCCESS_COUNT"
print_status "$RED" "Failed downloads: $FAILED_COUNT"
print_status "$BLUE" "Total processed: $CURRENT"

# List what was downloaded
if [[ $SUCCESS_COUNT -gt 0 ]]; then
    echo ""
    print_status "$BLUE" "Files extracted to: $OUTPUT_DIR"
    print_status "$BLUE" "Each genome is in its own subdirectory:"
    ls -la "$OUTPUT_DIR" | grep "^d" | awk '{print "  " $NF}' | grep -v "^\.$\|^\.\.$"
fi

# Exit with appropriate code
if [[ $FAILED_COUNT -eq 0 ]]; then
    print_status "$GREEN" "All downloads completed successfully!"
    exit 0
else
    print_status "$YELLOW" "Some downloads failed. Check the log above for details."
    exit 1
fi
