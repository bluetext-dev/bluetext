from typing import Optional, List
from fastapi import APIRouter, HTTPException
from models.operations.{{ entity_plural }} import (
    create_{{ entity_singular }},
    get_{{ entity_singular }},
    list_{{ entity_plural }},
    update_{{ entity_singular }},
    delete_{{ entity_singular }},
)
from models.types.{{ entity_plural }} import Create{{ entity_singular | capitalize }}Request, Update{{ entity_singular | capitalize }}Request
from models.entities.{{ entity_plural }} import {{ entity_singular | capitalize }}

{{ entity_plural }}_router = APIRouter(prefix="/{{ entity_plural }}", tags=["{{ entity_plural }}"])


@{{ entity_plural }}_router.post("/", response_model={{ entity_singular | capitalize }})
async def create_{{ entity_singular }}_route(request: Create{{ entity_singular | capitalize }}Request):
    return create_{{ entity_singular }}(request)


@{{ entity_plural }}_router.get("/{{{ entity_singular }}_id}", response_model={{ entity_singular | capitalize }})
async def get_{{ entity_singular }}_route({{ entity_singular }}_id: str):
    result = get_{{ entity_singular }}({{ entity_singular }}_id)
    if result is None:
        raise HTTPException(status_code=404, detail="{{ entity_singular | capitalize }} not found")
    return result


@{{ entity_plural }}_router.get("/", response_model=List[{{ entity_singular | capitalize }}])
async def list_{{ entity_plural }}_route(limit: Optional[int] = None):
    return list_{{ entity_plural }}(limit=limit)


@{{ entity_plural }}_router.put("/{{{ entity_singular }}_id}", response_model={{ entity_singular | capitalize }})
async def update_{{ entity_singular }}_route({{ entity_singular }}_id: str, request: Update{{ entity_singular | capitalize }}Request):
    result = update_{{ entity_singular }}({{ entity_singular }}_id, request)
    if result is None:
        raise HTTPException(status_code=404, detail="{{ entity_singular | capitalize }} not found")
    return result


@{{ entity_plural }}_router.delete("/{{{ entity_singular }}_id}")
async def delete_{{ entity_singular }}_route({{ entity_singular }}_id: str):
    success = delete_{{ entity_singular }}({{ entity_singular }}_id)
    if not success:
        raise HTTPException(status_code=404, detail="{{ entity_singular | capitalize }} not found")
    return {"deleted": True}
