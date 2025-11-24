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
