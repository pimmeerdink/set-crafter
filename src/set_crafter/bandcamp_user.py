import json

from bs4 import BeautifulSoup

from .schemas import Item

COLLECTION_PAGE_SIZE = 50


async def get_fan_id_from_profile(session, profile_url):
    """Resolve a bandcamp profile URL (e.g. https://pim.bandcamp.com) to a fan_id."""
    async with session.get(profile_url) as response:
        response.raise_for_status()
        content = await response.text()
    soup = BeautifulSoup(content, "lxml")
    pagedata = soup.find(id="pagedata")
    if not pagedata:
        return None
    try:
        data_blob = json.loads(pagedata["data-blob"])
        return data_blob["fan_data"]["fan_id"]
    except (KeyError, TypeError, json.JSONDecodeError):
        return None


def _item_from_api(x):
    return Item(
        id=str(x["item_id"]),
        type=x["item_type"],
        url=x["item_url"],
        sales=int(x.get("also_collected_count") or 0),
    )


class BcUser:
    def __init__(self, fan_id, session):
        self.fan_id = fan_id
        self.session = session
        # Far-future timestamp so the bandcamp API returns the most recent
        # items regardless of acquisition date. Matches the pattern used by
        # other bandcamp tools (e.g. bc-explorer).
        self.older_than_token = "2145916799::t"
        self.collection_items = None
        self.wishlist_items = None

    async def _fetch_items(self, endpoint, count):
        try:
            async with self.session.post(
                f"https://bandcamp.com/api/fancollection/1/{endpoint}",
                json={
                    "fan_id": self.fan_id,
                    "older_than_token": self.older_than_token,
                    "count": count,
                },
            ) as response:
                data = await response.json(content_type=None)
        except Exception as exc:
            print(f"{endpoint} failed for fan {self.fan_id}: {exc}")
            return []
        items = data.get("items", []) if isinstance(data, dict) else []
        return [_item_from_api(x) for x in items]

    async def scrape_collection_items(self, count=COLLECTION_PAGE_SIZE):
        if self.collection_items is None:
            self.collection_items = await self._fetch_items(
                "collection_items", count
            )
        return self.collection_items

    async def scrape_wishlist_items(self, count=COLLECTION_PAGE_SIZE):
        if self.wishlist_items is None:
            self.wishlist_items = await self._fetch_items(
                "wishlist_items", count
            )
        return self.wishlist_items
