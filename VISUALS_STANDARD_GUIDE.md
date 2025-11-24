# The Power BI Visuals Standard: A Comprehensive Guide to Programmatic Layout Management

## Executive Summary

This guide provides an exhaustive, step-by-step methodology for establishing a centralized, code-driven **Visuals Standard** for Power BI dashboards. By extracting and managing visual properties as reusable JSON templates, organizations can achieve unprecedented consistency, drastically reduce maintenance time (especially after breaking updates), and enable programmatic deployment across numerous reports.

This resource is designed to be the single source of truth for all audiences, from Power BI Desktop users to technical developers leveraging Node/CSS and GitHub.

---

## Part 1: Setup and Foundation (The Developer's Toolkit)

This section provides the end-to-end setup required for the technical audience to manage the Visuals Standard via code.

### 1.1 Prerequisites and Tool Installation

| Tool | Purpose | Installation Guide |
| :--- | :--- | :--- |
| **Power BI Desktop** | Creating the initial "Golden Template" PBIX file. | [Link to Microsoft Download Page] |
| **Visual Studio Code (VS Code)** | Primary code editor for managing JSON and Python/TS scripts. | [Link to VS Code Download Page] |
| **Python 3.x** | Required for the PBIX-to-JSON Extraction Script. | [Link to Python Download Page] |
| **Git** | Version control and integration with GitHub. | [Link to Git Download Page] |
| **GitHub Account** | Central repository for the Visuals Standard. | [Link to GitHub Sign-up] |

### 1.2 VS Code Workspace Setup (The Visuals Standard Repository)

1.  **Initialize the Repository:**
    ```bash
    mkdir powerbi-visuals-standard
    cd powerbi-visuals-standard
    git init
    # Create a placeholder README.md
    echo "# Power BI Visuals Standard" > README.md
    ```
2.  **Open in VS Code:**
    ```bash
    code .
    ```
3.  **Recommended VS Code Extensions:**
    *   **JSON Tools:** For formatting and validating JSON templates.
    *   **Python:** For running and debugging the extraction script.
    *   **GitHub Actions:** For managing CI/CD workflows.

### 1.3 The PBIX-to-JSON Extraction Script (The Automation Engine)

To move from a manually created Power BI template (`.pbix`) to a reusable code standard, we must programmatically extract the visual layout JSON.

#### 1.3.1 Script Purpose and Logic

The script, `pbix_extractor.py`, is a Command Line Interface (CLI) tool that:
1.  Treats the `.pbix` file as a standard ZIP archive.
2.  Extracts the `Report/Layout` file, which contains the visual configuration for all pages.
3.  Parses the complex, nested JSON structure.
4.  Isolates the `config` block for each visual, which contains the precise position, size, and all formatting properties.
5.  Saves each visual's `config` as a separate, validated JSON template file in a structured output directory.

#### 1.3.2 Script Implementation (`pbix_extractor.py`)

```python
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
            layout_json_str = layout_data.lstrip('\ufeff')
            
            try:
                layout_json = json.loads(layout_json_str)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from layout data: {e}")
                print("The layout JSON structure is highly complex and often contains escaped strings.")
                print("Please ensure your PBIX file is saved in the latest Power BI Desktop version.")
                return

            # 2. Navigate to the visual definitions
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
                        try:
                            # Simple unescape attempt
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
```

#### 1.3.3 How to Use (CLI and Batch File)

1.  **Installation:** Ensure Python 3 is installed.
2.  **Execution (CLI):**
    ```bash
    python3 src/pbix_extractor.py /path/to/your/Golden_Template.pbix
    ```
3.  **Execution (Batch/Shell Script for non-technical users):**
    *   **Windows (`extract.bat`):**
        ```batch
        @echo off
        SET PBIX_FILE=%1
        IF "%PBIX_FILE%"=="" (
            ECHO ERROR: Please drag and drop a PBIX file onto this script.
            PAUSE
            EXIT /B 1
        )
        ECHO Starting extraction for %PBIX_FILE%...
        python3 src/pbix_extractor.py "%PBIX_FILE%"
        ECHO Extraction complete. Check the 'extracted_visual_templates' folder.
        PAUSE
        ```
    *   **Linux/macOS (`extract.sh`):**
        ```bash
        #!/bin/bash
        PBIX_FILE=$1
        if [ -z "$PBIX_FILE" ]; then
            echo "ERROR: Please provide the path to the PBIX file."
            exit 1
        fi
        echo "Starting extraction for $PBIX_FILE..."
        python3 src/pbix_extractor.py "$PBIX_FILE"
        echo "Extraction complete. Check the 'extracted_visual_templates' folder."
        ```

---

## Part 2: The Visuals Standard Architecture and Templates

This section defines the structure of the standard and how the extracted templates are organized and reused.

### 2.1 Repository Structure (One-to-Many Mindset)

The goal is to create a single source of truth that feeds many reports.

```
powerbi-visuals-standard/
├── .github/
│   └── workflows/
│       └── validation.yml  # CI/CD for standards validation
├── src/
│   ├── pbix_extractor.py   # Extracts templates from PBIX
│   ├── visual_fixer.py     # Injects templates into PBIP report.json
│   └── extract.bat / extract.sh
├── templates/
│   ├── Golden_Template.pbix # The source file (optional, for reference)
│   └── VISUAL_TEMPLATES/
│       ├── BAR_CHART/
│       │   ├── Standard_Blue_Bar.json
│       │   └── Dept_A_KPI_Bar.json
│       ├── CARD/
│       │   ├── Standard_KPI_Card.json
│       │   └── Small_Metric_Card.json
│       ├── SLICER/
│       │   └── Date_Range_Slicer.json
│       └── ... (All other visual types)
├── VALIDATION/
│   ├── schema/
│   │   └── visual_schema.json # JSON Schema for validation
│   └── README.md # Nested README for Validation Process
├── README.md # Main Repository README
└── VISUALS_STANDARD_GUIDE.md # This comprehensive guide
```

### 2.2 Template Structure and Reusability

Each JSON file in the `VISUAL_TEMPLATES` folder is a complete, reusable visual configuration.

**Key Components of the JSON Template:**

| JSON Key | Description | Reusability Note |
| :--- | :--- | :--- |
| `x`, `y`, `z` | Position on the canvas. | **LOW REUSABILITY:** Must be modified for each report. |
| `width`, `height` | Size of the visual. | **MEDIUM REUSABILITY:** Can be standardized (e.g., "Half-Width", "Full-Height"). |
| `visualType` | The type of visual (e.g., `barChart`, `card`). | **HIGH REUSABILITY:** Defines the visual component. |
| `config` (nested) | Contains all formatting, title, background, and data role settings. | **HIGH REUSABILITY:** This is the core of the *Standard*. |

**The One-to-Many Strategy:**
The JSON templates define the *look and feel* (the Standard), while the programmatic implementation (Part 3) is responsible for applying the template and setting the unique `x`, `y`, `width`, and data bindings for each specific report.

### 2.3 Visual Aid: Sample Extracted JSON Template

To illustrate the content of a template, here is a simplified example of an extracted `config` block for a standard KPI Card.

```json
{
    "visualType": "card",
    "x": 100,
    "y": 50,
    "z": 1,
    "width": 250,
    "height": 150,
    "title": {
        "text": "Standard KPI Card",
        "show": true,
        "color": { "solid": { "color": "#333333" } },
        "fontFamily": "Segoe UI Bold",
        "fontSize": 12
    },
    "background": {
        "show": true,
        "color": { "solid": { "color": "#FFFFFF" } },
        "transparency": 0
    },
    "dataLabels": {
        "show": true,
        "labelColor": { "solid": { "color": "#0078D4" } },
        "labelDisplayUnits": 1000,
        "labelPrecision": 0
    },
    "dataRoles": [
        {
            "role": "Values",
            "displayName": "Value",
            "queryRef": "MeasureName"
        }
    ]
    // ... many more formatting properties
}
```

---

## Part 3: Implementation and Programmatic Application

This section details how to use the templates to programmatically fix and create reports.

### 3.1 The Power BI Project (.pbip) Format: The Key to Programmatic Control

The traditional `.pbix` file is a compressed archive, making programmatic modification difficult and risky. The modern **Power BI Project (.pbip)** format is the officially supported solution for source control and programmatic manipulation [1].

The `.pbip` format saves the report as a folder structure, separating the data model from the report definition. The visual layout and configuration are stored in a plain text file: `report.json`.

#### 3.1.1 Recommended Workflow for Fixing 80 Dashboards

To fix your 80 dashboards, the most robust and future-proof method is to convert them to the `.pbip` format first, then use a Python script to perform the JSON injection.

| Step | Action | Tool/Method | Audience |
| :--- | :--- | :--- | :--- |
| **1. Convert** | Convert the target `.pbix` file to the `.pbip` folder structure. | Power BI Desktop's "Save as Power BI Project" feature. | Power BI User |
| **2. Identify** | Locate the visual's unique identifier (`name` or `config` properties) in the target `report.json`. | VS Code / Text Editor | Developer |
| **3. Inject** | Run a Python script to load the validated template JSON and replace the broken `config` block in the target `report.json`. | Python Script (`visual_fixer.py`) | Developer |
| **4. Validate** | Open the modified `.pbip` folder in Power BI Desktop to confirm the fix. | Power BI Desktop | Power BI User |

#### 3.1.2 Programmatic JSON Injection Script (`visual_fixer.py`)

This script automates Step 3, allowing you to batch-fix your 80 reports.

```python
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
    fixed_count = 0
    
    for section in report_json.get('sections', []):
        for container in section.get('visualContainers', []):
            config_str = container.get('config')
            if not config_str:
                continue

            try:
                current_config = json.loads(config_str)
            except json.JSONDecodeError:
                try:
                    current_config = json.loads(config_str.replace('\\"', '"').replace('\\n', '\n'))
                except json.JSONDecodeError:
                    continue

            visual_type = current_config.get('visualType', 'unknown_type')
            visual_title = current_config.get('title', {}).get('text', '')
            
            # Match logic: check if the visual type or title contains the search term
            if visual_name_to_fix.lower() in visual_title.lower() or visual_name_to_fix.lower() == visual_type.lower():
                
                print(f"  -> Found visual '{visual_title}' ({visual_type}). Applying template...")
                
                # --- CORE LOGIC: Apply Template while preserving critical properties ---
                
                # 1. Preserve position, size, filters, and data bindings from the existing visual
                preserved_properties = {
                    "x": current_config.get("x"),
                    "y": current_config.get("y"),
                    "width": current_config.get("width"),
                    "height": current_config.get("height"),
                    "z": current_config.get("z"),
                    "filters": current_config.get("filters"),
                    "dataRoles": current_config.get("dataRoles")
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
```

#### 3.1.3 How to Use the Fixer Script

1.  **Prerequisite:** Ensure the target report is saved as a `.pbip` project.
2.  **Execution:**
    ```bash
    python3 src/visual_fixer.py /path/to/Dept_A_Report_PBIP_Folder templates/VISUAL_TEMPLATES/CARD/Standard_KPI_Card.json "Card"
    ```
    *   The script will search the `report.json` file inside `/path/to/Dept_A_Report_PBIP_Folder` for any visual with the type or title containing `"Card"`.
    *   It will then replace the entire formatting configuration of that visual with the content of `Standard_KPI_Card.json`, while preserving its position and data roles.

---

## Part 4: Maintenance and CI/CD Automation (GitHub)

This section ensures the standard remains current and validated.

### 4.1 Standards Validation (The "Fully Validated" Requirement)

To ensure the integrity of the Visuals Standard, every template must be validated against a master JSON Schema before it is merged into the main branch.

#### 4.1.1 JSON Schema for Visuals

A JSON Schema (`VALIDATION/schema/visual_schema.json`) defines the required structure and data types for a valid visual template. This prevents developers from accidentally introducing malformed JSON that could break the programmatic application.

#### 4.1.2 GitHub Actions for Validation

A GitHub Action will automatically run the validation script on every Pull Request (PR) that modifies a template file.

**File:** `.github/workflows/validation.yml`

```yaml
name: Visuals Standard Validation

on:
  pull_request:
    branches: [ main ]
    paths:
      - 'templates/VISUAL_TEMPLATES/**/*.json'

jobs:
  validate_json_schema:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        # Install the library for JSON Schema validation
        pip install jsonschema

    - name: Run Validation Script
      run: |
        # This script is executed directly in the action environment
        # It iterates over all template JSON files and validates them against the schema
        python - << EOF
import json
import os
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

SCHEMA_PATH = Path('VALIDATION/schema/visual_schema.json')
TEMPLATES_DIR = Path('templates/VISUAL_TEMPLATES')

def validate_all_templates():
    if not SCHEMA_PATH.exists():
        print(f"Error: Schema file not found at {SCHEMA_PATH}")
        sys.exit(1)

    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    print(f"Starting validation against schema: {SCHEMA_PATH}")
    
    validation_failed = False
    
    for template_path in TEMPLATES_DIR.rglob('*.json'):
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            validate(instance=template_data, schema=schema)
            print(f"  [PASS] {template_path}")
            
        except ValidationError as e:
            print(f"  [FAIL] {template_path}")
            print(f"    Validation Error: {e.message} at {e.path}")
            validation_failed = True
        except Exception as e:
            print(f"  [FAIL] {template_path}")
            print(f"    General Error: {e}")
            validation_failed = True

    if validation_failed:
        print("\n*** VALIDATION FAILED: One or more templates do not conform to the standard schema. ***")
        sys.exit(1)
    else:
        print("\n*** ALL TEMPLATES PASSED VALIDATION. Standards are compliant. ***")

if __name__ == '__main__':
    validate_all_templates()
EOF

    - name: Final Success Message
      if: success()
      run: echo "Validation successful. Ready to merge."
```

### 4.2 Automated Updates with GitHub Actions (CI/CD for Standards)

When a new visual standard is approved and merged into the `main` branch (after passing validation), you can use a GitHub Action to automatically notify downstream teams or even trigger automated report updates.

**Example: Automated Notification**

This action runs after a successful merge to `main` and posts a notification to a communication channel (e.g., Slack, Teams, or a dedicated internal API).

**File:** `.github/workflows/notify_update.yml`

```yaml
name: Standards Update Notification

on:
  push:
    branches: [ main ]
    paths:
      - 'templates/VISUAL_TEMPLATES/**/*.json'

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
    - name: Send Notification of New Standard
      # Replace this with your actual notification method (e.g., Slack webhook, Teams connector)
      run: |
        echo "New Visual Standard deployed to main branch by ${{ github.actor }}."
        echo "New templates are available for use."
        # Example: curl -X POST -H 'Content-type: application/json' --data '{"text":"New Power BI Visual Standard Deployed."}' YOUR_WEBHOOK_URL
```

---

## Part 5: Guide for the Power BI Only Audience

This section translates the technical concepts into simple, actionable steps for Power BI Desktop users who are not familiar with code, GitHub, or JSON.

### 5.1 The "Golden Template" Approach

The Visuals Standard is embodied in a single, perfectly formatted Power BI file called the **Golden Template** (`Golden_Template.pbix`).

1.  **Creation:** The Golden Template is created by a senior Power BI developer who manually formats every visual component (Bar Chart, Card, Slicer, etc.) to the exact company standard.
2.  **Maintenance:** When the standard changes (e.g., a new color palette is required), the senior developer updates the Golden Template and saves it.
3.  **Extraction:** The technical team runs the `extract.bat` file (from Part 1) on the updated Golden Template. This automatically pulls out the new standard JSON templates and commits them to GitHub.

### 5.2 How to Use the Extractor (`extract.bat`)

This is the simplest way for a Power BI user to contribute to the standard.

1.  **Locate the Tool:** Find the `src` folder in the shared repository.
2.  **Update the Template:** Open the `Golden_Template.pbix` in Power BI Desktop, make your required visual changes, and save it.
3.  **Run the Extractor:** Drag and drop the `Golden_Template.pbix` file directly onto the `extract.bat` file.
4.  **Result:** A new folder named `extracted_visual_templates` will appear next to your PBIX file, containing the new standard templates. The technical team will then review and integrate these into the main standard via GitHub.

---

## Part 6: Complete Resource List

| Resource | Description | Audience | Link |
| :--- | :--- | :--- | :--- |
| **Power BI Desktop** | Primary tool for report creation and template design. | All | [Link to Microsoft Download Page] |
| **Visual Studio Code** | Primary IDE for managing JSON, Python, and GitHub. | Developer | [Link to VS Code Download Page] |
| **Python 3.x** | Runtime for the extraction and fixing scripts. | Developer | [Link to Python Download Page] |
| **Git** | Version control system. | Developer | [Link to Git Download Page] |
| **Power BI Project (.pbip) Documentation** | Microsoft's official guide on the modern source control format. | Developer | [Link to Microsoft PBIP Documentation] |
| **Power BI Visuals Project Structure** | Microsoft's resource on the underlying visual structure. | Developer | [Link to Microsoft Visuals Project Structure] |
| **JSON Schema Documentation** | Guide to defining and validating JSON structures. | Developer | [Link to JSON Schema Documentation] |

---

## Part 7: Repository READMEs

To ensure the repository is **RICHLY outfitted** and **thoroughly informative**, we will use nested READMEs.

### 7.1 Main Repository README (`README.md`)

```markdown
# Power BI Visuals Standard Repository

## 🌟 Centralized Visuals Standard for Power BI Dashboards

This repository serves as the single source of truth for our organization's Power BI Visuals Standard. It contains all approved visual configurations as reusable JSON templates, enabling programmatic consistency across all department dashboards.

The primary goal is to drastically reduce maintenance overhead (especially after breaking Power BI updates) and enforce a unified look and feel.

### 🚀 Getting Started

1.  **Read the Guide:** Start by reading the comprehensive guide for a full understanding of the architecture and process:
    *   [VISUALS_STANDARD_GUIDE.md](./VISUALS_STANDARD_GUIDE.md)

2.  **Setup Your Environment:** Follow the steps in Part 1 of the guide to set up VS Code, Python, and Git.

### 🛠️ Core Components

| Component | Purpose | Audience |
| :--- | :--- | :--- |
| **`templates/VISUAL_TEMPLATES/`** | The actual JSON files defining the standard (e.g., colors, fonts, borders). | All |
| **`src/pbix_extractor.py`** | **Creation:** Extracts new templates from the Golden Template PBIX. | Developer / Power BI User |
| **`src/visual_fixer.py`** | **Implementation:** Injects validated templates into `.pbip` reports for batch fixing. | Developer |
| **`VALIDATION/`** | Contains the JSON Schema and process for ensuring template compliance. | Developer |

### 🔗 Nested Documentation

*   [**Validation Process**](./VALIDATION/README.md): Learn how the standards are enforced via GitHub Actions.
*   [**Template Structure**](./templates/README.md): Deep dive into the JSON structure and reusability strategy.
*   [**Source Code Usage**](./src/README.md): Detailed instructions for running the Python scripts.

---
*Managed by the Data Governance Team via CI/CD.*
```

### 7.2 Validation README (`VALIDATION/README.md`)

```markdown
# Validation Process: Ensuring Standards Compliance

The **VALIDATION** folder is the core of our quality control process. It ensures that every visual template added or modified adheres to the required structure before it can be used in production reports.

### 1. The JSON Schema

The file `schema/visual_schema.json` is the **Master Definition** of a valid visual template. It defines required fields (like `visualType`, `title`, `background`) and their expected data types.

### 2. Automated Validation via GitHub Actions

Every time a Pull Request (PR) is opened to modify a template file, the GitHub Action defined in `.github/workflows/validation.yml` automatically runs.

*   **Tool:** The action uses the Python `jsonschema` library.
*   **Process:** It iterates through all templates and checks them against the master schema.
*   **Result:** If any template fails validation, the PR is blocked, preventing non-compliant standards from entering the main branch.

### 3. How to Test Locally

Developers should test their templates locally before submitting a PR:

1.  Install the dependency: `pip install jsonschema`
2.  Run the validation script (similar to the one in the GitHub Action):
    ```bash
    python -c "import json, sys; from pathlib import Path; from jsonschema import validate; \
    schema = json.load(open('schema/visual_schema.json')); \
    template = json.load(open('templates/VISUAL_TEMPLATES/CARD/New_Card.json')); \
    validate(instance=template, schema=schema); \
    print('Local Validation Passed!')"
    ```
```

### 7.3 Source Code README (`src/README.md`)

```markdown
# Source Code: Automation Scripts

This folder contains the Python scripts and batch files necessary to automate the creation and implementation of the Visuals Standard.

### 1. `pbix_extractor.py` (Creation Tool)

**Purpose:** Extracts visual configuration JSON from a Power BI `.pbix` file.

**Usage:**
```bash
python3 pbix_extractor.py <path_to_pbix_file>
```

**For Power BI Users:** Use the provided `extract.bat` or `extract.sh` by dragging and dropping the PBIX file onto the script.

### 2. `visual_fixer.py` (Implementation Tool)

**Purpose:** Programmatically injects a validated visual template into a Power BI Project (`.pbip`) `report.json` file. This is the tool used to fix the 80 broken dashboards.

**Usage:**
```bash
python3 visual_fixer.py <path_to_pbip_report_folder> <path_to_template_json> <visual_name_to_fix>
```

**Example:**
```bash
python3 visual_fixer.py ../reports/Dept_A_Report templates/VISUAL_TEMPLATES/CARD/Standard_KPI_Card.json "Card"
```
This command finds all visuals containing "Card" in the Dept_A_Report and applies the new standard template, preserving position and data bindings.
```

### 7.4 Templates README (`templates/README.md`)

```markdown
# Visual Templates: The Core Standard

This folder contains the **Golden Templates**—the reusable JSON files that define the look and feel of every standard visual component.

### 1. Structure

Templates are organized by `VISUAL_TYPE` for easy navigation and management:

```
VISUAL_TEMPLATES/
├── BAR_CHART/
├── CARD/
├── SLICER/
└── ...
```

### 2. Reusability Strategy

Each template is a complete `config` block. When applying a template, the programmatic tool (`visual_fixer.py`) ensures a **One-to-Many** mindset:

*   **One Standard (Template):** The template defines the formatting (colors, fonts, borders, titles). This is applied to all reports.
*   **Many Reports (Implementation):** The implementation script preserves the unique elements of each report:
    *   **Position and Size** (`x`, `y`, `width`, `height`)
    *   **Data Bindings** (`dataRoles`, `filters`)

**NEVER** modify the position/size properties in these template files. They should only contain the **formatting standard**.
```
