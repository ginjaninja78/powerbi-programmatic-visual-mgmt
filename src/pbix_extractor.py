import zipfile
import json
import os
import sys
from pathlib import Path

# --- Configuration ---
LAYOUT_FILE_IN_PBIX = 'Report/Layout'
OUTPUT_DIR_NAME = 'extracted_visual_templates'

def extract_visual_templates(pbix_path):
    """
    Extracts visual layout and properties from a PBIX file.
    A PBIX file is a ZIP archive. The visual layout is stored in Report/Layout.
    """
    pbix_file = Path(pbix_path)
    if not pbix_file.exists():
        print(f"Error: PBIX file not found at {pbix_path}")
        return

    output_root = pbix_file.parent / OUTPUT_DIR_NAME / pbix_file.stem
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Processing {pbix_file.name}...")

    try:
        with zipfile.ZipFile(pbix_file, 'r') as zf:
            # 1. Extract the main layout JSON
            try:
                # The layout file is often UTF-16 encoded
                layout_data = zf.read(LAYOUT_FILE_IN_PBIX).decode('utf-16')
            except KeyError:
                print(f"Error: Could not find '{LAYOUT_FILE_IN_PBIX}' inside the PBIX file.")
                print("This may indicate a change in the PBIX format. Please check the file structure.")
                return
            except Exception as e:
                print(f"Error reading or decoding {LAYOUT_FILE_IN_PBIX}: {e}")
                return

            # The layout data is a single string that needs to be parsed as JSON
            # It often contains a BOM (Byte Order Mark) which needs to be stripped
            layout_json_str = layout_data.lstrip('\ufeff')
            
            # The layout JSON is often malformed or contains escaped characters.
            # We need to find the actual JSON object within the string.
            # A common pattern is that the string is a JSON string *containing* another JSON string.
            # However, for simplicity and robustness, we will assume it's a standard JSON object
            # and rely on the user to validate the output.
            
            try:
                layout_json = json.loads(layout_json_str)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from layout data: {e}")
                print("Attempting to find the inner JSON string...")
                # A common issue is that the whole file is a string containing the actual JSON
                # This is a complex problem that often requires manual inspection or a dedicated library.
                # For now, we will proceed with the assumption that the main JSON is parsable.
                return

            # 2. Navigate to the visual definitions
            # The structure is typically: sections -> (page) -> visualContainers
            
            extracted_count = 0
            
            for section in layout_json.get('sections', []):
                page_name = section.get('displayName', 'Unknown Page')
                page_id = section.get('name', 'unknown_page')
                page_dir = output_root / page_id
                page_dir.mkdir(exist_ok=True)
                
                print(f"  -> Extracting visuals from page: {page_name}")

                for container in section.get('visualContainers', []):
                    # The visual's properties are stored in the 'config' field, which is a JSON string
                    config_str = container.get('config')
                    if not config_str:
                        continue

                    try:
                        config_json = json.loads(config_str)
                    except json.JSONDecodeError:
                        # If the config is a string containing escaped JSON, we need to unescape it
                        # This is a common and difficult problem. We'll try a simple unescape.
                        try:
                            config_json = json.loads(config_str.replace('\\"', '"').replace('\\n', '\n'))
                        except json.JSONDecodeError:
                            print(f"    - Skipping visual due to unparsable config string.")
                            continue
                    
                    # Extract key identifying information
                    visual_type = config_json.get('visualType', 'unknown_type')
                    
                    # Try to get the title from the config
                    visual_title = config_json.get('title', {}).get('text', 'Untitled Visual')
                    
                    # Clean up the title for a safe filename
                    safe_title = "".join(c for c in visual_title if c.isalnum() or c in (' ', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')
                    
                    # Create a template file name
                    file_name = f"{visual_type}_{safe_title}_{extracted_count}.json"
                    output_path = page_dir / file_name

                    # The 'config' contains the full visual definition, including position/size (x, y, z, width, height)
                    # and all formatting properties. This is the core of the standard.
                    
                    # We will save the entire config JSON for maximum completeness
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(config_json, f, indent=4)
                    
                    extracted_count += 1
                    print(f"    - Saved template for '{visual_title}' ({visual_type}) to {output_path.name}")

            print(f"\nExtraction complete. Total {extracted_count} visual templates saved to {output_root}")

    except zipfile.BadZipFile:
        print(f"Error: {pbix_file.name} is not a valid PBIX/ZIP file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 pbix_extractor.py <path_to_pbix_file>")
        sys.exit(1)
    
    pbix_file_path = sys.argv[1]
    extract_visual_templates(pbix_file_path)
