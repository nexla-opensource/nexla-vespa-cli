## Repository Overview
This CLI generates Vespa application schemas from Nexla Nexsets. It fetches Nexset metadata from Nexla, maps fields to Vespa schema definitions, writes a `.sd` file to `vespa_app/schemas/`, and updates `vespa_app/services.xml`.

## Primary Responsibilities
- Fetch Nexset metadata via Nexla API.
- Convert Nexla schema types to Vespa schema snippets using a YAML map.
- Emit Vespa `.sd` schema files with a fixed naming convention.
- Update the Vespa services configuration to reference the schema.

## How to Work Here
- Prefer minimal, localized edits.
- Reuse existing functions in `main.py` (`NexlaTools`, `VespaMapper`) rather than adding new entry points.
- Update `vespa_schema_map.yml` for mapping changes; keep the mapping format consistent.
- Keep scripts (`vespa-nexla-cli.sh`, `vespa-nexla-cli.bat`) aligned with their current flow.
- Maintain the current CLI flow: open token page → collect token → collect Nexset ID → generate schema → update services.xml.

## File Map (Operational)
- `main.py`: CLI logic and file generation.
- `vespa_schema_map.yml`: Field-type to schema-template mapping.
- `vespa_app/services.xml`: Vespa services configuration updated in-place.
- `vespa_app/schemas/`: Output folder for generated schemas.

## Development Steps
- Run the CLI using the platform script:
  - Linux/macOS: `./vespa-nexla-cli.sh`
  - Windows: `vespa-nexla-cli.bat`
- Provide a Nexla session token and Nexset ID when prompted.
- Generated output is written under `vespa_app/`.

## Change Guidance
- Schema logic changes belong in `VespaMapper` methods:
  - `_load_yaml_map` for loading mapping templates.
  - `create_vespa_schema` for mapping logic and file output.
  - `_update_services_xml` for document type updates.
- API changes belong in `NexlaTools`:
  - `_get_nexset_data` for request and response handling.
  - `get_nexset_schema` for schema extraction.
- Mapping updates belong in `vespa_schema_map.yml`.

## Behavior Notes
- Schema name is `nexset_{NEXSET_ID}`.
- Output schema path is `vespa_app/schemas/nexset_{NEXSET_ID}.sd`.
- `services.xml` is edited in place; missing or unexpected structure throws an error.

## Suggested Verification
- Confirm the generated schema exists in `vespa_app/schemas/`.
- Confirm `vespa_app/services.xml` contains the generated document type.
- Confirm the schema file uses the same name in `services.xml`.
