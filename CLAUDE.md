## Purpose
This repository provides a cross-platform CLI that generates Vespa application schemas from Nexla Nexsets. The CLI fetches a Nexset schema from the Nexla API, maps field types to Vespa schema snippets, writes a `.sd` schema into `vespa_app/schemas/`, and updates `vespa_app/services.xml` to reference the generated document type.

## Key Files
- `main.py`: CLI entry point, Nexla API calls, schema generation, and services.xml update.
- `vespa_schema_map.yml`: Mapping from Nexla field types to Vespa schema snippets (multi-line templates).
- `vespa_app/services.xml`: Template services configuration updated with the generated document type.
- `vespa_app/schemas/`: Output directory for generated `.sd` schema files.
- `vespa-nexla-cli.sh` / `vespa-nexla-cli.bat`: Launch scripts that set up a virtual environment and run the CLI.
- `requirements.txt`: Python dependencies for the CLI runtime.

## System Behavior
- Opens the Nexla token page in a browser and prompts for a session token.
- Prompts for a Nexset ID.
- Calls Nexla API endpoint: `https://dataops.nexla.io/nexla-api/data_sets/{nexset_id}?expand=1`.
- Extracts `output_schema.properties` from the API response.
- Maps each field to a Vespa schema snippet based on `vespa_schema_map.yml`.
- Writes `vespa_app/schemas/nexset_{NEXSET_ID}.sd`.
- Updates the `<document>` entry inside `vespa_app/services.xml`.

## Data Flow (Reference)
- Inputs: Nexla session token, Nexset ID.
- External call: Nexla API via `requests`.
- Transform: Nexla schema types are mapped to Vespa schema templates.
- Outputs: `.sd` schema file + updated `services.xml`.

## Making Changes
- Keep changes minimal and localized to the component affected.
- Reuse existing classes:
  - `NexlaTools` for API access and schema extraction.
  - `VespaMapper` for mapping and file generation.
- If changing schema generation behavior, update `VespaMapper` in `main.py`.
- If modifying type mappings, update `vespa_schema_map.yml` and ensure the mapping key matches the type used in `VespaMapper`.
- If altering Nexla API interactions, update `NexlaTools` in `main.py`.
- Preserve current formatting and patterns in `main.py`; avoid introducing new abstractions unless required.

## Constraints and Assumptions
- Requires network access to Nexla API.
- Requires a valid Nexla session token and Nexset ID.
- `vespa_app/services.xml` must exist; the CLI updates a `<document>` entry.

## Failure Modes
- Invalid token or Nexset ID returns a Nexla API error.
- Missing `services.xml` raises a file error.
- Unexpected `<documents>` structure in `services.xml` raises a value error.

## Development Workflow
- Run the CLI via `./vespa-nexla-cli.sh` (Linux/macOS) or `vespa-nexla-cli.bat` (Windows).
- The scripts create a virtual environment, install requirements, and execute `main.py`.

## Verification
- Manual check: run the CLI, provide a valid Nexla token and Nexset ID, and confirm:
  - A new schema file exists in `vespa_app/schemas/`.
  - `vespa_app/services.xml` references the new document type.
  - The schema name matches `nexset_{NEXSET_ID}`.
