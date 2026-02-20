from typing import Optional, List
from models.entities.{{ entity_plural }} import {{ entity_singular | capitalize }}, {{ entity_singular | capitalize }}Data
from models.types.{{ entity_plural }} import Create{{ entity_singular | capitalize }}Request, Update{{ entity_singular | capitalize }}Request


def create_{{ entity_singular }}(request: Create{{ entity_singular | capitalize }}Request) -> {{ entity_singular | capitalize }}:
    data = {{ entity_singular | capitalize }}Data(**request.model_dump())
    return {{ entity_singular | capitalize }}.create(data)


def get_{{ entity_singular }}({{ entity_singular }}_id: str) -> Optional[{{ entity_singular | capitalize }}]:
    return {{ entity_singular | capitalize }}.get({{ entity_singular }}_id)


def list_{{ entity_plural }}(limit: Optional[int] = None) -> List[{{ entity_singular | capitalize }}]:
    return {{ entity_singular | capitalize }}.list(limit=limit)


def update_{{ entity_singular }}({{ entity_singular }}_id: str, request: Update{{ entity_singular | capitalize }}Request) -> Optional[{{ entity_singular | capitalize }}]:
    existing = {{ entity_singular | capitalize }}.get({{ entity_singular }}_id)
    if existing is None:
        return None
{{ update_logic }}
    return {{ entity_singular | capitalize }}.update(existing)


def delete_{{ entity_singular }}({{ entity_singular }}_id: str) -> bool:
    return {{ entity_singular | capitalize }}.delete({{ entity_singular }}_id)
