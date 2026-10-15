"""Sanitize n8n workflow exports before publishing them on GitHub."""

import json
from pathlib import Path

# --------------------------------------------------
# 1. Define input and output directories
# --------------------------------------------------

INPUT_DIR = Path("private_exports")
OUTPUT_DIR = Path("workflows")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Check that original workflow files exist
# --------------------------------------------------

if not INPUT_DIR.exists():
    raise FileNotFoundError(
        "The private_exports folder does not exist."
    )

workflow_files = list(INPUT_DIR.glob("*.json"))

if not workflow_files:
    raise FileNotFoundError(
        "No JSON files found in private_exports."
    )

# --------------------------------------------------
# 3. Sanitize each workflow
# --------------------------------------------------

for file_path in workflow_files:

    # Read original workflow
    with file_path.open(encoding="utf-8") as file:
        workflow = json.load(file)

    # Process every node
    for node in workflow.get("nodes", []):

        # Remove credential references
        node.pop("credentials", None)

        # Remove webhook identifiers
        node.pop("webhookId", None)

        parameters = node.get("parameters", {})

        # ------------------------------------------
        # Google Sheets
        # ------------------------------------------

        if node.get("type") == "n8n-nodes-base.googleSheets":

            document = parameters.get("documentId")

            if isinstance(document, dict):
                document["value"] = "YOUR_GOOGLE_SHEET_ID"
                document.pop("cachedResultUrl", None)

                # Remove cached document name
                document.pop("cachedResultName", None)

        # ------------------------------------------
        # Clean resource locators
        # ------------------------------------------

        for key in ("sheetName", "workflowId"):

            resource = parameters.get(key)

            if isinstance(resource, dict):

                # Remove cached URLs
                resource.pop("cachedResultUrl", None)

                # Replace instance-specific workflow IDs
                if key == "workflowId":
                    resource["value"] = "SELECT_WORKFLOW_AFTER_IMPORT"

        # ------------------------------------------
        # Remove other sensitive node metadata
        # ------------------------------------------

        node.pop("notes", None)

    # ----------------------------------------------
    # Remove deployment-specific workflow metadata
    # ----------------------------------------------

    workflow.pop("meta", None)
    workflow.pop("versionId", None)
    workflow.pop("pinData", None)

    # Remove original workflow ID
    workflow.pop("id", None)

    # ----------------------------------------------
    # Save sanitized workflow
    # ----------------------------------------------

    output_path = OUTPUT_DIR / file_path.name

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            workflow,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Sanitized: {output_path}")

print("\nAll workflows sanitized successfully!")
