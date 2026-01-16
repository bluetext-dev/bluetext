import os
import uuid
from datetime import timedelta
from dataclasses import dataclass
import couchbase.subdocument as SD
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions, QueryOptions, MutateInOptions)
from couchbase.exceptions import ScopeAlreadyExistsException, CollectionAlreadyExistsException, DocumentNotFoundException
from couchbase.management.collections import CreateCollectionSettings
from couchbase.result import MutationResult
from typing import Tuple, Optional, TypeVar, Generic, List, ClassVar
from pydantic import BaseModel, Field

# Environment variables
USERNAME = os.environ['COUCHBASE_USERNAME']
PASSWORD = os.environ['COUCHBASE_PASSWORD']
DEFAULT_BUCKET_NAME = os.environ['COUCHBASE_BUCKET']
HOST = os.environ['COUCHBASE_HOST']
PROTOCOL = os.environ['COUCHBASE_PROTOCOL']

@dataclass
class Keyspace:
    bucket_name: str
    scope_name: str
    collection_name: str

    @classmethod
    def from_string(cls, keyspace: str) -> 'Keyspace':
        parts = keyspace.split('.')
        if len(parts) != 3:
            raise ValueError(
                "Invalid keyspace format. Expected 'bucket_name.scope_name.collection_name', "
                f"got '{keyspace}'"
            )
        return cls(*parts)

    def __str__(self) -> str:
        return f"{self.bucket_name}.{self.scope_name}.{self.collection_name}"

    def query(self, query: str, **kwargs) -> list:
        cluster = get_cluster()
        query = query.replace("${keyspace}", str(self))
        options = QueryOptions(**kwargs)
        result = cluster.query(query, options)
        return [row for row in result]

    def get_scope(self):
        cluster = get_cluster()
        bucket = cluster.bucket(self.bucket_name)
        return bucket.scope(self.scope_name)

    def get_collection(self):
        scope = self.get_scope()
        return scope.collection(self.collection_name)

    def insert(self, value: dict, key: Optional[str] = None, **kwargs) -> MutationResult:
        if key is None:
            key = str(uuid.uuid4())
        collection = self.get_collection()
        return collection.insert(key, value, **kwargs)

    def remove(self, key: str, **kwargs) -> int:
        collection = self.get_collection()
        result = collection.remove(key, **kwargs)
        return result.cas

    def list(self, limit: Optional[int] = None) -> list:
        limit_clause = f" LIMIT {limit}" if limit is not None else ""
        query = f"SELECT META().id, * FROM {self}{limit_clause}"
        return self.query(query)

# Authentication setup
auth = PasswordAuthenticator(
    USERNAME,
    PASSWORD
)

# Module-level cluster cache
_cluster = None

def get_keyspace(collection_name: str, scope_name: Optional[str] = "_default", bucket_name: Optional[str] = DEFAULT_BUCKET_NAME) -> Keyspace:
    """
    Create a Keyspace instance with optional scope and bucket parameters.
    
    Args:
        collection_name: Name of the collection
        scope_name: Name of the scope (defaults to "_default")
        bucket_name: Name of the bucket (defaults to DEFAULT_BUCKET_NAME)
        
    Returns:
        Keyspace instance
    """
    return Keyspace(bucket_name, scope_name, collection_name)

def get_cluster():
    """
    Returns a cached Couchbase cluster connection.
    Creates a new connection if one doesn't exist.
    """
    global _cluster
    if _cluster is None:
        url = PROTOCOL + "://" + HOST
        _cluster = Cluster(url, ClusterOptions(auth))
        _cluster.wait_until_ready(timedelta(seconds=500))
    return _cluster

def get_default_bucket():
    """
    Returns the default bucket using the cached cluster connection.
    """
    cluster = get_cluster()
    return cluster.bucket(DEFAULT_BUCKET_NAME)

def get_collection(keyspace: Keyspace):
    """
    Get a collection based on a Keyspace instance.
    
    Args:
        keyspace: Keyspace instance containing bucket, scope, and collection names
        
    Returns:
        Couchbase Collection object
        
    Raises:
        couchbase.exceptions.BucketNotFoundException: If bucket doesn't exist
        couchbase.exceptions.ScopeNotFoundException: If scope doesn't exist
        couchbase.exceptions.CollectionNotFoundException: If collection doesn't exist
    """
    cluster = get_cluster()
    bucket = cluster.bucket(keyspace.bucket_name)
    scope = bucket.scope(keyspace.scope_name)
    return scope.collection(keyspace.collection_name)

DataT = TypeVar("DataT", bound=BaseModel)
T = TypeVar("T", bound="BaseModelCouchbase")

class BaseModelCouchbase(BaseModel, Generic[DataT]):
    id: str
    data: DataT

    _collection_name: ClassVar[str] = ""

    @classmethod
    def get_keyspace(cls) -> Keyspace:
        if not cls._collection_name:
            raise ValueError(f"_collection_name not set for {cls.__name__}")
        return get_keyspace(cls._collection_name)

    @classmethod
    def get(cls: type[T], id: str) -> Optional[T]:
        try:
            result = cls.get_keyspace().get_collection().get(id)
            data = result.content_as(dict)
            return cls(id=id, data=data)
        except DocumentNotFoundException:
            return None

    @classmethod
    def create(cls: type[T], data: DataT) -> T:
        key = str(uuid.uuid4())
        cls.get_keyspace().insert(data.model_dump(), key=key)
        return cls(id=key, data=data)

    @classmethod
    def update(cls: type[T], item: T) -> T:
        cls.get_keyspace().get_collection().replace(item.id, item.data.model_dump())
        return item

    @classmethod
    def delete(cls: type[T], id: str) -> bool:
        try:
            cls.get_keyspace().remove(id)
            return True
        except DocumentNotFoundException:
            return False

    @classmethod
    def list(cls: type[T], limit: Optional[int] = None) -> List[T]:
        rows = cls.get_keyspace().list(limit=limit)
        items = []
        for row in rows:
            # Row structure: {'id': '...', 'collection_name': {...}} or similar
            # Extract data using collection name
            data_dict = row.get(cls._collection_name)
            if data_dict is None:
                # Fallback: try to find the data in other keys if needed? 
                # For now assuming standard behavior
                pass
            
            if data_dict:
                items.append(cls(id=row['id'], data=data_dict))
        return items

    @classmethod
    def get_many(cls: type[T], ids: List[str]) -> List[T]:
        # TODO: Batch implementation when available. Loop for now.
        # This is strictly "get", failing if not found? 
        # Or should it return None for missing?
        # N1QL approach: SELECT META().id, * FROM keyspace USE KEYS [...]
        keyspace = cls.get_keyspace()
        # Use N1QL for batch get
        keys_str = ", ".join([f'"{k}"' for k in ids])
        query = f"SELECT META().id, * FROM {keyspace} USE KEYS [{keys_str}]"
        rows = keyspace.query(query)
        
        items = []
        for row in rows:
            data_dict = row.get(cls._collection_name)
            if data_dict:
                items.append(cls(id=row['id'], data=data_dict))
        return items

    @classmethod
    def create_many(cls: type[T], items: List[DataT]) -> List[T]:
        keyspace = cls.get_keyspace()
        results = []
        for data in items:
            key = str(uuid.uuid4())
            keyspace.insert(data.model_dump(), key=key)
            results.append(cls(id=key, data=data))
        return results

    @classmethod
    def update_many(cls: type[T], items: List[T]) -> List[T]:
        from couchbase.options import ReplaceOptions
        keyspace = cls.get_keyspace()
        collection = keyspace.get_collection()
        results = []
        for item in items:
            collection.replace(item.id, item.data.model_dump())
            results.append(item)
        return results

    @classmethod
    def delete_many(cls: type[T], ids: List[str]) -> List[str]:
        keyspace = cls.get_keyspace()
        params = {"keys": ids}
        # N1QL DELETE: DELETE FROM keyspace USE KEYS $keys
        # But we need to use parametrized query.
        # Wait, simple loop remove is safer/easier for now.
        deleted = []
        for key in ids:
            try:
                keyspace.remove(key)
                deleted.append(key)
            except Exception:
                pass
        return deleted
