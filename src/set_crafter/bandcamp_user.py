import time

from .schemas import Item

COLLECTION_PAGE_SIZE = 50


class BcUser:
    def __init__(self, fan_id, session):
        self.fan_id = fan_id
        self.session = session
        self.older_than_token = f"{int(time.time())}::a::"
        self.collection_items = None

    async def scrape_collection_items(self):
        if self.collection_items is not None:
            return self.collection_items

        try:
            async with self.session.post(
                "https://bandcamp.com/api/fancollection/1/collection_items",
                json={
                    "fan_id": self.fan_id,
                    "older_than_token": self.older_than_token,
                    "count": COLLECTION_PAGE_SIZE,
                },
            ) as response:
                data = await response.json(content_type=None)
        except Exception as exc:
            print(f"collection_items failed for fan {self.fan_id}: {exc}")
            self.collection_items = []
            return self.collection_items

        items = data.get("items", []) if isinstance(data, dict) else []
        self.collection_items = [
            Item(
                id=str(x["item_id"]),
                type=x["item_type"],
                url=x["item_url"],
                sales=int(x["also_collected_count"]),
            )
            for x in items
        ]
        return self.collection_items
