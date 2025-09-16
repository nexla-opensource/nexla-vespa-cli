import requests
import webbrowser
import getpass
import yaml


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
    def __init__(self, vespa_map_file_path: str) -> None:
        self.vespa_field_map = self._load_yaml_map(vespa_map_file_path)
    
    def _load_yaml_map(self, file_path: str) -> dict:
        """Load Vespa schema mapping yaml file"""
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            for k, v in data.items():
                parsed = "\n".join(v)
                data[k] = parsed
                
        return data
    
    def _get_vespa_schema_section(self, field_name: str, vespa_field_type: str) -> str:
        """Return a schema section related to a field"""
        section = self.vespa_field_map[vespa_field_type].replace(r"{{FIELD_NAME}}", field_name)
        return section
    
    def create_vespa_schema(self, nexset_schema: dict, nexset_id: str) -> str:
        """Generate a complete Vespa schema.sd file based on a Nexset schema"""
        field_sections = []
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
                        vespa_field_type = "array<float>"
                    else:
                        vespa_field_type = "array<float>"
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

            field_section = self._get_vespa_schema_section(field_name=field_name, vespa_field_type=vespa_field_type)
            field_sections.append(field_section)

        schema_name = f"nexset_{nexset_id}"
        schema_template = self._create_schema_template(schema_name, field_sections)
        output_file = f"vespa_app/app/schemas/{schema_name}.sd"

        with open(output_file, "w") as file:
            file.write(schema_template)

        return output_file

    def _create_schema_template(self, schema_name: str, field_sections: list) -> str:
        """Create a complete Vespa schema template with proper structure"""
        fields_content = "\n".join(field_sections)

        template = f"""schema {schema_name} {{
    document {schema_name} {{
{fields_content}
    }}

    fieldset default {{
        fields: {", ".join([section.split("field ")[1].split(" type")[0] for section in field_sections if "field " in section][:5])}
    }}

    rank-profile default inherits default {{
        first-phase {{
            expression: nativeRank
        }}
    }}
}}"""

        return template


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
