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


@dataclass
class CouchbaseConf:
    """Couchbase connection configuration"""
    host: str
    username: str
    password: str
    bucket: str
    protocol: str


class CouchbaseClient:
    """
    Couchbase client that holds a connection to a specific cluster.
    Provides lazy, cached cluster access and keyspace creation.
    """

    def __init__(self, conf: CouchbaseConf):
        self._conf = conf
        self._cluster: Optional[Cluster] = None

    def get_cluster(self) -> Cluster:
        """Returns a cached Couchbase cluster connection."""
        if self._cluster is None:
            auth = PasswordAuthenticator(self._conf.username, self._conf.password)
            url = self._conf.protocol + "://" + self._conf.host
            self._cluster = Cluster(url, ClusterOptions(auth))
            self._cluster.wait_until_ready(timedelta(seconds=500))
        return self._cluster

    def get_keyspace(self, collection_name: str, scope_name: str = "_default", bucket_name: Optional[str] = None) -> 'Keyspace':
        """Create a Keyspace instance bound to this client."""
        if bucket_name is None:
            bucket_name = self._conf.bucket
        return Keyspace(bucket_name, scope_name, collection_name, client=self)

    def get_default_bucket(self):
        """Returns the default bucket using the cached cluster connection."""
        cluster = self.get_cluster()
        return cluster.bucket(self._conf.bucket)


# Client registry keyed by service instance name
_clients: dict[str, CouchbaseClient] = {}


def register_client(name: str, conf: CouchbaseConf):
    """Register a CouchbaseClient for the given service instance name."""
    _clients[name] = CouchbaseClient(conf)


def get_client(name: str) -> CouchbaseClient:
    """
    Get a CouchbaseClient by service instance name.
    Auto-registers from environment variables on first access.
    Env var prefix is derived from the name: e.g. "couchbase-server" -> COUCHBASE_SERVER_*.
    """
    if name not in _clients:
        prefix = name.upper().replace("-", "_")
        conf = CouchbaseConf(
            host=os.environ[f'{prefix}_HOST'],
            username=os.environ[f'{prefix}_USERNAME'],
            password=os.environ[f'{prefix}_PASSWORD'],
            bucket=os.environ[f'{prefix}_BUCKET'],
            protocol=os.environ[f'{prefix}_PROTOCOL'],
        )
        register_client(name, conf)
    return _clients[name]


@dataclass
class Keyspace:
    bucket_name: str
    scope_name: str
    collection_name: str
    client: CouchbaseClient

    @classmethod
    def from_string(cls, keyspace: str, client: CouchbaseClient) -> 'Keyspace':
        parts = keyspace.split('.')
        if len(parts) != 3:
            raise ValueError(
                "Invalid keyspace format. Expected 'bucket_name.scope_name.collection_name', "
                f"got '{keyspace}'"
            )
        return cls(*parts, client=client)

    def __str__(self) -> str:
        return f"{self.bucket_name}.{self.scope_name}.{self.collection_name}"

    def query(self, query: str, **kwargs) -> list:
        cluster = self.client.get_cluster()
        query = query.replace("${keyspace}", str(self))
        options = QueryOptions(**kwargs)
        result = cluster.query(query, options)
        return [row for row in result]

    def get_scope(self):
        cluster = self.client.get_cluster()
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


DataT = TypeVar("DataT", bound=BaseModel)
T = TypeVar("T", bound="BaseModelCouchbase")

class BaseModelCouchbase(BaseModel, Generic[DataT]):
    id: str
    data: DataT

    _collection_name: ClassVar[str] = ""
    _service_instance: ClassVar[str] = "couchbase-server"

    @classmethod
    def get_keyspace(cls) -> Keyspace:
        if not cls._collection_name:
            raise ValueError(f"_collection_name not set for {cls.__name__}")
        client = get_client(cls._service_instance)
        return client.get_keyspace(cls._collection_name)

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
