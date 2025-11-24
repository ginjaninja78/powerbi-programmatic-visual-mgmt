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
