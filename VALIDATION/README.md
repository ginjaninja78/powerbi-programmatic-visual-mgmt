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
