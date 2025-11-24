#!/bin/bash
PBIX_FILE=$1
if [ -z "$PBIX_FILE" ]; then
    echo "ERROR: Please provide the path to the PBIX file."
    exit 1
fi
echo "Starting extraction for $PBIX_FILE..."
python3 pbix_extractor.py "$PBIX_FILE"
echo "Extraction complete. Check the 'extracted_visual_templates' folder in the same directory as the PBIX file."
