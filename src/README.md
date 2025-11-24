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
