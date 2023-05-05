from typing import Dict, List, Optional, Union

from replicate.base_model import BaseModel
from replicate.collection import Collection as BaseCollection
from replicate.exceptions import ReplicateException
from replicate.version import VersionCollection


class Model(BaseModel):
    username: str
    name: str

    def predict(self, *args, **kwargs) -> None:
        raise ReplicateException(
            "The `model.predict()` method has been removed, because it's unstable: if a new version of the model you're using is pushed and its API has changed, your code may break. Use `version.predict()` instead. See https://github.com/replicate/replicate-python#readme"
        )

    @property
    def versions(self) -> VersionCollection:
        return VersionCollection(client=self._client, model=self)


class Collection(BaseModel):
    name: str
    slug: str
    description: str
    # models: List[Model] | None

    @property
    def models(self) -> "ModelCollection":
        return ModelCollection(client=self._client, collection=self)


class CollectionCollection(BaseCollection):
    model = Collection

    def list(self) -> List[Collection]:
        resp = self._client._request("GET", "/v1/collections")
        # TODO: paginate
        collections = resp.json()["results"]
        return [self.prepare_model(obj) for obj in collections]

    def get(self, slug: str) -> Collection:
        resp = self._client._request("GET", f"/v1/collections/{slug}")
        obj = resp.json()
        return self.prepare_model(obj)

    def create(self, **kwargs) -> Collection:
        raise NotImplementedError()

    def prepare_model(self, attrs: Union[Collection, Dict]) -> Collection:
        if isinstance(attrs, BaseModel):
            attrs.id = attrs.slug
            if attrs.models is not None:
                attrs.models = [
                    self._client.models.prepare_model(model) for model in attrs.models
                ]
        elif isinstance(attrs, dict):
            attrs["id"] = attrs["slug"]
            if "models" in attrs:
                attrs["_models"] = [
                    self._client.models.prepare_model(model)
                    for model in attrs.get("models", [])[0].get("models")  # ???
                ]
                del attrs["models"]

        return super().prepare_model(attrs)


class ModelCollection(BaseCollection):
    model = Model

    def __init__(self, client, collection: Optional[Collection] = None) -> None:
        self._collection = collection
        super().__init__(client)

    @property
    def collections(self) -> CollectionCollection:
        return CollectionCollection(client=self._client)

    def list(self) -> List[Model]:
        if self._collection is None:
            raise NotImplementedError()

        resp = self._client._request("GET", f"/v1/collections/{self._collection.slug}")
        obj = resp.json()
        return [self.prepare_model(model) for model in obj["models"]]

    def get(self, name: str) -> Model:
        # TODO: fetch model from server
        # TODO: support permanent IDs
        username, name = name.split("/")
        return self.prepare_model({"username": username, "name": name})

    def create(self, **kwargs) -> Model:
        raise NotImplementedError()

    def prepare_model(self, attrs: Union[Model, Dict]) -> Model:
        if isinstance(attrs, BaseModel):
            attrs.username = attrs.owner
            attrs.id = f"{attrs.username}/{attrs.name}"
        elif isinstance(attrs, dict):
            attrs["username"] = attrs["owner"]
            attrs["id"] = f"{attrs['username']}/{attrs['name']}"
        return super().prepare_model(attrs)
