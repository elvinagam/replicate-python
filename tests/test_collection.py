import responses

from replicate.client import Client


@responses.activate
def test_collections():
    client = Client(api_token="abc123")

    responses.get(
        "https://api.replicate.com/v1/collections",
        json={
            "results": [
                {
                    "name": "Image to text",
                    "slug": "image-to-text",
                    "description": "Models that generate text prompts and captions from images",
                },
                {
                    "name": "Text to image",
                    "slug": "text-to-image",
                    "description": "Models that generate images from text prompts",
                },
            ]
        },
    )

    collections = client.models.collections.list()
    assert len(collections) == 2
    assert collections[0].name == "Image to text"
    assert collections[1].name == "Text to image"


@responses.activate
def test_collection():
    client = Client(api_token="abc123")

    responses.get(
        "https://api.replicate.com/v1/collections/text-to-image",
        json={
            "name": "Text to image",
            "slug": "text-to-image",
            "description": "Models that generate images from text prompts",
            "models": [
                {
                    "name": "Text to image",
                    "slug": "text-to-image",
                    "description": "Models that generate images from text prompts",
                    "models": [
                        {
                            "url": "https://replicate.com/afiaka87/laionide-v4",
                            "owner": "afiaka87",
                            "name": "laionide-v4",
                            "description": "GLIDE-text2im w/ humans and experimental style prompts.",
                        }
                    ],
                }
            ],
        },
    )

    collection = client.models.collections.get("text-to-image")
    assert collection is not None
    models = collection.models.list()
    assert len(models) == 1
    assert models[0].name == "Text to image"
    assert models[0].models[0].name == "laionide-v4"
