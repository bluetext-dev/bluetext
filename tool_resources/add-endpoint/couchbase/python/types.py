from pydantic import BaseModel
from typing import Optional


class Create{{ entity_singular | capitalize }}Request(BaseModel):
{{ create_fields }}


class Update{{ entity_singular | capitalize }}Request(BaseModel):
{{ update_fields }}
