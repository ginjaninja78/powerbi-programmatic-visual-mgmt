# The Power BI Visuals Standard: An Exhaustive Manual for Code-Based Management

## Executive Summary

This manual provides an **exhaustive, step-by-step guide** on establishing and maintaining a centralized **Visuals Standard** for Power BI dashboards entirely through code, primarily using **Visual Studio Code (VS Code)**.

By directly managing visual properties as reusable JSON templates, you gain **absolute control** over your report's appearance, enabling rapid, programmatic fixes (like the recent update issue) and ensuring organizational consistency. This guide is structured for both Power BI Desktop users and developers, covering the foundational manual process and the advanced automation layer.

---

## Part 1: Setup and Foundation (The Developer's Toolkit)

This section details the end-to-end setup required for code-based management.

### 1.1 Prerequisites and Tool Installation

| Tool | Purpose | Installation Guide |
| :--- | :--- | :--- |
| **Power BI Desktop** | Creating the initial "Golden Template" and final validation. | [Link to Microsoft Download Page] |
| **Visual Studio Code (VS Code)** | **Your primary workspace** for editing JSON and running scripts. | [Link to VS Code Download Page] |
| **Python 3.x** | Required for the Automation Layer scripts. | [Link to Python Download Page] |
| **Git** | Version control and integration with GitHub. | [Link to Git Download Page] |
| **GitHub Account** | Central repository for the Visuals Standard. | [Link to GitHub Sign-up] |

### 1.2 VS Code Workspace Setup (The Visuals Standard Repository)

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ginjaninja78/powerbi-programmatic-visual-mgmt.git powerbi-visuals-standard
    cd powerbi-visuals-standard
    ```
2.  **Open in VS Code:**
    ```bash
    code .
    ```
3.  **Recommended VS Code Extensions:**
    *   **JSON Tools:** For formatting and validating JSON templates.
    *   **Python:** For running and debugging the automation scripts.
    *   **GitHub Actions:** For managing CI/CD workflows.

---

## Part 2: The Manual Process: Creating and Editing the Standard

This is the core of the manual, code-based approach. You will learn how to extract the raw visual configuration and manually refine it into a reusable template.

### 2.1 Step 1: Extracting the Raw Visual Configuration

The Power BI visual configuration is a deeply nested JSON object. We use a two-step process to get the raw JSON:

#### A. The "Golden Template" Approach (Recommended)

1.  **Create the Golden Template:** In Power BI Desktop, create a new report (`Golden_Template.pbix`).
2.  **Design the Visual:** Add a single visual (e.g., a Bar Chart) and apply **ALL** desired formatting settings (colors, fonts, borders, titles, data labels, etc.) to meet the standard.
3.  **Run the Extractor Script (Automation Layer):** Use the `pbix_extractor.py` script to automatically pull the raw JSON from the PBIX file.
    *   **Developer:** `python3 src/pbix_extractor.py /path/to/Golden_Template.pbix`
    *   **Power BI User:** Drag and drop the PBIX onto `src/extract.bat` or `src/extract.sh`.
4.  **Result:** The script deposits the raw, unrefined JSON for each visual into the `extracted_visual_templates` folder.

#### B. The PBIP Manual Extraction (Alternative)

1.  Save your report as a **Power BI Project (.pbip)** file. This creates a folder structure.
2.  Navigate to the `report.json` file inside the project folder.
3.  **Manually Locate:** Search the `report.json` for the visual you want to template. The visual's configuration is stored as a JSON string inside the `config` property of a `visualContainer`.
4.  **Copy:** Copy the entire JSON string from the `config` property.

### 2.2 Step 2: Refining the Raw JSON into a Reusable Template (The Manual Edit)

The raw JSON contains *everything*, including the visual's position, size, and data bindings. A reusable template **must only contain the standard formatting**.

1.  **Open in VS Code:** Open the raw JSON file (or paste the copied string) into VS Code.
2.  **Remove Non-Standard Properties:** Manually delete the following properties, as they are unique to each report and must be set programmatically during implementation:
    *   `x`, `y`, `z` (Position)
    *   `width`, `height` (Size)
    *   `dataRoles` (Data Bindings/Fields)
    *   `filters` (Visual-level filters)
3.  **Verify Standard Properties:** Ensure all remaining properties (e.g., `title`, `background`, `dataLabels`, `visualType`) are correctly formatted according to the organizational standard.
4.  **Save the Template:** Save the refined JSON file into the appropriate folder in the repository (e.g., `templates/VISUAL_TEMPLATES/CARD/Standard_KPI_Card.json`).

### 2.3 Step 3: Validating the New Template

Before committing, you must ensure your manually edited template conforms to the required structure defined in the `VALIDATION/schema/visual_schema.json`.

1.  **Install Validator:** `pip install jsonschema`
2.  **Run Local Validation:** Use the Python validation script (or the local test command provided in `VALIDATION/README.md`) to confirm compliance.

---

## Part 3: Implementation: Applying the Standard Programmatically

This section details how to use the validated templates to fix or create reports.

### 3.1 The Power BI Project (.pbip) Format: The Key to Programmatic Control

The **Power BI Project (.pbip)** format is the officially supported solution for source control and programmatic manipulation [1]. It saves the report as a folder structure, with the visual layout in a plain text file: `report.json`.

### 3.2 The Manual Fix (For Understanding)

To fix a single visual in a `.pbip` report manually:

1.  Open the target report's `report.json` in VS Code.
2.  Locate the visual's `visualContainer` that needs fixing.
3.  **Manually Replace:** Copy the entire content of your validated template JSON (e.g., `templates/VISUAL_TEMPLATES/CARD/Standard_KPI_Card.json`).
4.  **Manually Inject:** Paste the template content back into the visual's `config` property, ensuring you **preserve** the original visual's `x`, `y`, `width`, `height`, and `dataRoles` properties.
5.  Save the `report.json` and open the `.pbip` in Power BI Desktop to see the fixed visual.

### 3.3 The Automation Layer: Batch Fixing with `visual_fixer.py`

For fixing 80 dashboards, the manual process is not scalable. The `visual_fixer.py` script automates the injection process, following the exact manual steps above.

**Usage:**
```bash
python3 src/visual_fixer.py <path_to_pbip_report_folder> <path_to_template_json> <visual_name_to_fix>
```
The script handles the complex JSON parsing, the replacement of the formatting block, and the preservation of the unique report-specific properties (`x`, `y`, `dataRoles`).

---

## Part 4: Maintenance and CI/CD Automation (GitHub)

This section ensures the standard remains current and validated.

### 4.1 Standards Validation (The "Fully Validated" Requirement)

All template changes must be submitted via a Pull Request (PR) to GitHub. The GitHub Action in `.github/workflows/validation.yml` automatically runs the validation script to ensure compliance before merging. This is your automated quality gate.

### 4.2 Automated Updates with GitHub Actions

The CI/CD pipeline ensures that once a standard is approved and merged, downstream systems are notified or automatically updated. (See `VALIDATION/README.md` for details).

---

## Part 5: Guide for the Power BI Only Audience

This section focuses on the simple actions required by Power BI Desktop users.

1.  **Standard Creation:** Use the **Golden Template** (`Golden_Template.pbix`) to define the standard visually.
2.  **Standard Extraction:** Use the simple drag-and-drop `extract.bat` or `extract.sh` to generate the raw templates for the technical team.
3.  **Report Fixing:** Save the report as a **Power BI Project (.pbip)** and hand the folder to the technical team for the automated fix using `visual_fixer.py`.

---

## Part 6: Complete Resource List

| Resource | Description | Audience | Link |
| :--- | :--- | :--- | :--- |
| **Power BI Desktop** | Primary tool for report creation and template design. | All | [Link to Microsoft Download Page] |
| **Visual Studio Code** | Primary IDE for managing JSON, Python, and GitHub. | Developer | [Link to VS Code Download Page] |
| **Python 3.x** | Runtime for the automation scripts. | Developer | [Link to Python Download Page] |
| **Git** | Version control system. | Developer | [Link to Git Download Page] |
| **Power BI Project (.pbip) Documentation** | Microsoft's official guide on the modern source control format. | Developer | [Link to Microsoft PBIP Documentation] |
| **Power BI Visuals Project Structure** | Microsoft's resource on the underlying visual structure. | Developer | [Link to Microsoft Visuals Project Structure] |
| **JSON Schema Documentation** | Guide to defining and validating JSON structures. | Developer | [Link to JSON Schema Documentation] |

[1] Microsoft Power BI Documentation: Power BI Desktop projects (PBIP)
