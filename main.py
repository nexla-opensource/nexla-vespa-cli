import requests
import webbrowser
import getpass
import yaml
import os
import re


class NexlaTools:
    def __init__(self, env_url: str, nexla_session_token: str):
        self.nexla_session_token = nexla_session_token
        self.env_url = env_url
        
    def _get_nexset_data(self, nexset_id: str) -> dict:
        """Fetches nexset metadata from Nexla."""
        url = f"{self.env_url}/data_sets/{nexset_id}?expand=1"
        headers = {'Authorization': f'Bearer {self.nexla_session_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()
        
    def get_nexset_schema(self, nexset_id: str) -> list:
        """Extracts the schema portion from the Nexset data."""
        nexset_data = self._get_nexset_data(nexset_id)
        schema = nexset_data.get('output_schema', [])

        return schema["properties"]
    
    
class VespaMapper:
    def __init__(self, vespa_map_file_path: str, services_xml_path: str = "vespa_app/services.xml") -> None:
        self.vespa_field_map = self._load_yaml_map(vespa_map_file_path)
        self.services_xml_path = services_xml_path
    
    def _load_yaml_map(self, file_path: str) -> dict:
        """Load Vespa schema mapping yaml file"""
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        return data
    
    def _get_vespa_schema_section(self, field_name: str, vespa_field_type: str) -> dict:
        """Return schema sections related to a field"""
        sections = self.vespa_field_map[vespa_field_type]
        processed_sections = {
            'document_field': sections[0].replace(r"{{FIELD_NAME}}", field_name) if len(sections) > 0 else None,
            'derived_field': sections[1].replace(r"{{FIELD_NAME}}", field_name) if len(sections) > 1 else None
        }
        return processed_sections
    
    def create_vespa_schema(self, nexset_schema: dict, nexset_id: str) -> str:
        """Generate a complete Vespa schema.sd file based on a Nexset schema"""
        document_fields = []
        derived_fields = []

        for field_name, properties in nexset_schema.items():
            nexla_field_type = properties["type"]
            nexla_format_type = properties.get("format", "")

            if nexla_field_type == "string":
                if nexla_format_type in ["datetime", "date", "time", "email", "ipv4", "ipv6", "uri", "uri-reference", "iri", "iri-reference", "uuid", "regex", "byte", "binary"]:
                    vespa_field_type = "string"
                else:
                    vespa_field_type = "string"
            elif nexla_field_type == "array":
                array_item_type = properties.get("items", {}).get("type", "string")
                array_format_type = properties.get("items", {}).get("format", "")

                if array_item_type == "string":
                    vespa_field_type = "array<string>"
                elif array_item_type == "integer":
                    if array_format_type == "int32":
                        vespa_field_type = "array<long>"
                    elif array_format_type == "int64":
                        vespa_field_type = "array<long>"
                    else:
                        vespa_field_type = "array<long>"
                elif array_item_type == "number":
                    if array_format_type in ["float", "double", "decimal"]:
                        vespa_field_type = "variablearray<float>"
                    else:
                        vespa_field_type = "variablearray<float>"
                elif array_item_type == "boolean":
                    vespa_field_type = "array<bool>"
                else:
                    vespa_field_type = "array<string>"
            elif nexla_field_type == "boolean":
                vespa_field_type = "bool"
            elif nexla_field_type == "integer":
                if nexla_format_type == "int32":
                    vespa_field_type = "long"
                elif nexla_format_type == "int64":
                    vespa_field_type = "long"
                else:
                    vespa_field_type = "long"
            elif nexla_field_type == "number":
                if nexla_format_type in ["float", "double", "decimal"]:
                    vespa_field_type = "float"
                else:
                    vespa_field_type = "float"
            elif nexla_field_type == "object":
                object_properties = properties.get("properties", {})
                if object_properties:
                    first_property_type = next(iter(object_properties.values())).get("type", "string")
                    if first_property_type == "string":
                        vespa_field_type = "object<string>"
                    elif first_property_type in ["integer", "number"]:
                        vespa_field_type = "object<long>"
                    elif first_property_type == "boolean":
                        vespa_field_type = "object<bool>"
                    else:
                        vespa_field_type = "object<string>"
                else:
                    vespa_field_type = "object<string>"
            elif nexla_field_type == "null":
                continue
            else:
                vespa_field_type = "string"

            field_sections = self._get_vespa_schema_section(field_name=field_name, vespa_field_type=vespa_field_type)

            if field_sections['document_field']:
                document_fields.append(field_sections['document_field'])
            if field_sections['derived_field']:
                derived_fields.append(field_sections['derived_field'])

        schema_name = f"nexset_{nexset_id}"
        schema_template = self._create_schema_template(schema_name, document_fields, derived_fields)
        output_file = f"vespa_app/schemas/{schema_name}.sd"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as file:
            file.write(schema_template)

        self._update_services_xml(schema_name)

        return output_file

    def _create_schema_template(self, schema_name: str, document_fields: list, derived_fields: list) -> str:
        """Create a complete Vespa schema template with proper structure"""
        document_fields_content = "\n".join(document_fields)
        derived_fields_content = "\n".join(derived_fields)

        base_field_names = []
        for section in document_fields:
            if "field " in section:
                field_name = section.split("field ")[1].split(" type")[0]
                base_field_names.append(field_name)

        fieldset_fields = ", ".join(base_field_names[:5])

        template = f"""schema {schema_name} {{
    document {schema_name} {{
{document_fields_content}
    }}

    # Derived fields - MUST be OUTSIDE document block
{derived_fields_content}

    fieldset default {{
        fields: {fieldset_fields}
    }}

    rank-profile default inherits default {{
        first-phase {{
            expression: nativeRank
        }}
    }}
}}"""

        return template

    def _update_services_xml(self, schema_name: str) -> None:
        """Update services.xml with the new document type in the content cluster"""
        if not os.path.exists(self.services_xml_path):
            raise FileNotFoundError(f"services.xml not found at {self.services_xml_path}")

        with open(self.services_xml_path, 'r', encoding='utf-8') as file:
            content = file.read()

        pattern = r'(<document\s+type=")[^"]*("\s+mode="[^"]*"\s*/>)'

        if re.search(pattern, content):
            updated_content = re.sub(pattern, rf'\g<1>{schema_name}\g<2>', content)
        else:
            documents_pattern = r'(<documents>)(.*?)(</documents>)'
            match = re.search(documents_pattern, content, re.DOTALL)

            if match:
                documents_content = match.group(2)
                if '<document' not in documents_content:
                    new_document_line = f'\n            <document type="{schema_name}" mode="index" />'
                    updated_content = content.replace(
                        match.group(0),
                        f'{match.group(1)}{new_document_line}\n        {match.group(3)}'
                    )
                else:
                    raise ValueError("Unexpected document structure in services.xml")
            else:
                raise ValueError("Could not find <documents> element within <content> in services.xml")

        with open(self.services_xml_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)


def main():
    """Fetch Nexset schema and regenerate the Vespa schema file."""
    print("Opening Nexla token page in your browser...")
    try:
        webbrowser.open_new_tab("https://dataops.nexla.io/token")
    except Exception:
        print("Could not open browser automatically. Please visit: https://dataops.nexla.io/token")

    NEXLA_SESSION_TOKEN = ""
    while not NEXLA_SESSION_TOKEN:
        NEXLA_SESSION_TOKEN = getpass.getpass("Paste your Nexla session token: ").strip()
        if not NEXLA_SESSION_TOKEN:
            print("Token cannot be empty. Please try again.")

    NEXSET_ID = ""
    while not NEXSET_ID:
        NEXSET_ID = input("Enter Nexset ID: ").strip()
        if not NEXSET_ID:
            print("Nexset ID cannot be empty. Please try again.")

    try:
        nx = NexlaTools(env_url="https://dataops.nexla.io/nexla-api", nexla_session_token=NEXLA_SESSION_TOKEN)
        nexset_schema = nx.get_nexset_schema(nexset_id=NEXSET_ID)
        vespa_mapper = VespaMapper("vespa_schema_map.yml")
        output_file = vespa_mapper.create_vespa_schema(nexset_schema=nexset_schema, nexset_id=NEXSET_ID)
        print(f"Generated Vespa schema from Nexset and wrote to {output_file}")
    except Exception as e:
        print(f"Failed to generate Vespa schema from Nexset: {e}")
        return

    print("Schema generated. Update the Vespa application manually if deployment is required.")

if __name__ == "__main__":
    main()
