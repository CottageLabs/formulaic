from formulaic.schema.es7x import ES7xSchemaConfig, ES7xMappingGenerator
from formulaic.test.example.structs import JournalStructure

class GeneralES7xSchemaConfig(ES7xSchemaConfig):
    dynamic_mappings = [
        {
            "strings": {
                "match_mapping_type": "string",
                "mapping": {
                    "type": "text",
                    "fields": {
                        "exact": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
    ]

    additional_mappings = {
        "all_meta": {
            "type": "text",
            "fields": {
                "exact": {
                    "type": "keyword",
                    "store": True
                }
            }
        }
    }

    index_settings = {
        'number_of_shards': 4,
        'number_of_replicas': 1
    }

generator = ES7xMappingGenerator(GeneralES7xSchemaConfig())
struct = JournalStructure()
schema = generator.serialise(struct)
print(schema.to_string())