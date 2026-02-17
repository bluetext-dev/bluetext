from pydantic import BaseModel
from clients.couchbase import BaseModelCouchbase

class {{ entity_singular | capitalize }}Data(BaseModel):
    # Add your fields here
    pass

class {{ entity_singular | capitalize }}(BaseModelCouchbase[{{ entity_singular | capitalize }}Data]):
    _collection_name = "{{ entity_plural }}"
    _service_instance = "{{ service_instance }}"
