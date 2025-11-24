import json
import os
import sys
from pathlib import Path

# --- Configuration ---
REPORT_JSON_FILE = 'report.json'

def fix_visual_config(pbip_path, template_path, visual_name_to_fix):
    """
    Replaces the 'config' block of a specific visual in a PBIP's report.json
    with a validated template JSON.
    
    The PBIP structure is expected to be:
    <pbip_path>/<report_name>/report.json
    """
    pbip_dir = Path(pbip_path)
    
    # 1. Locate the report.json file
    report_json_path = pbip_dir / REPORT_JSON_FILE
    if not report_json_path.exists():
        print(f"Error: report.json not found in {pbip_dir}. Ensure this is a valid PBIP report folder.")
        return

    # 2. Load the target report.json
    try:
        with open(report_json_path, 'r', encoding='utf-8') as f:
            report_json = json.load(f)
    except Exception as e:
        print(f"Error loading target report.json: {e}")
        return

    # 3. Load the template JSON
    template_file = Path(template_path)
    if not template_file.exists():
        print(f"Error: Template file not found at {template_path}")
        return
        
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_config = json.load(f)
    except Exception as e:
        print(f"Error loading template JSON: {e}")
        return

    # 4. Find the visual in the report.json and replace its config
    # The structure is typically: sections -> (page) -> visualContainers
    
    fixed_count = 0
    
    for section in report_json.get('sections', []):
        for container in section.get('visualContainers', []):
            config_str = container.get('config')
            if not config_str:
                continue

            try:
                # The config is stored as a JSON string within the main JSON structure
                current_config = json.loads(config_str)
            except json.JSONDecodeError:
                # Attempt simple unescape if needed
                try:
                    current_config = json.loads(config_str.replace('\\"', '"').replace('\\n', '\n'))
                except json.JSONDecodeError:
                    continue

            # Check if this is the visual we want to fix
            # We will use the visualType and a partial title match for robustness
            visual_type = current_config.get('visualType', 'unknown_type')
            visual_title = current_config.get('title', {}).get('text', '')
            
            # The visual_name_to_fix should be a unique identifier or a pattern
            if visual_name_to_fix.lower() in visual_title.lower() or visual_name_to_fix.lower() == visual_type.lower():
                
                print(f"  -> Found visual '{visual_title}' ({visual_type}). Applying template...")
                
                # --- CORE LOGIC: Apply Template while preserving critical properties ---
                
                # 1. Preserve position and size (x, y, width, height) from the existing visual
                preserved_properties = {
                    "x": current_config.get("x"),
                    "y": current_config.get("y"),
                    "width": current_config.get("width"),
                    "height": current_config.get("height"),
                    "z": current_config.get("z"),
                    "filters": current_config.get("filters"), # Preserve filters
                    "dataRoles": current_config.get("dataRoles") # Preserve data bindings
                }
                
                # 2. Overwrite the current config with the template
                new_config = template_config
                
                # 3. Re-apply preserved properties to the new config
                for key, value in preserved_properties.items():
                    if value is not None:
                        new_config[key] = value
                
                # 4. Convert the new config back to a JSON string and update the container
                container['config'] = json.dumps(new_config)
                fixed_count += 1

    # 5. Save the modified report.json
    if fixed_count > 0:
        try:
            with open(report_json_path, 'w', encoding='utf-8') as f:
                json.dump(report_json, f, indent=4)
            print(f"\nSuccessfully fixed {fixed_count} visual(s) in {report_json_path.name}.")
        except Exception as e:
            print(f"Error saving modified report.json: {e}")
    else:
        print(f"\nNo visuals matching '{visual_name_to_fix}' were found to fix.")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 visual_fixer.py <path_to_pbip_report_folder> <path_to_template_json> <visual_name_to_fix>")
        print("\nExample: python3 visual_fixer.py ./Dept_A_Report ./templates/CARD/Standard_KPI_Card.json 'KPI Card'")
        sys.exit(1)
    
    pbip_folder = sys.argv[1]
    template_file = sys.argv[2]
    visual_name = sys.argv[3]
    
    fix_visual_config(pbip_folder, template_file, visual_name)
