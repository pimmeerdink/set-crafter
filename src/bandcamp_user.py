import random
import time
import json
import requests
import re
import numpy as np
import platform
import time

from bs4 import BeautifulSoup

from schemas import Item
import aiohttp


async def get_bandcamp_fan_id(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.text()

        soup = BeautifulSoup(content, "lxml")
        pagedata = soup.find(id="pagedata")
        if not pagedata:
            raise ValueError("Pagedata not found in the HTML")

        data_blob = json.loads(pagedata["data-blob"])
        fan_id = data_blob["fan_data"]["fan_id"]
        return fan_id

    except aiohttp.ClientError as e:
        print(f"Error fetching the URL: {e}")
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing the data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


class BcUser:
    def __init__(self, profile_url):
        self.profile_url = profile_url
        self.fan_id = get_bandcamp_fan_id(profile_url)
        # print(profile_url)
        # print(self.fan_id)
        self.wishlist_items = None
        self.collection_items = None
        self._initialize_fan_id_and_older_than_token()

    def _initialize_fan_id_and_older_than_token(self):
        """Initialize fan_id and older_than_token as class attributes."""
        html_wishlist = self._fetch_wishlist_html()
        self.older_than_token = self._generate_older_than_token()
        self.fan_id = self._extract_fan_id(html_wishlist)

    def scrape_collection_items(self):
        """Scrape wishlist items if not already scraped."""
        if self.collection_items is None:
            # print("Scraping collection items...")
            self.collection_items = self._fetch_collection_items(
                self.fan_id, self.older_than_token
            )
            self.collection_items = [
                Item(
                    id=str(x["item_id"]),
                    type=x["item_type"],
                    url=x["item_url"],
                    sales=int(x["also_collected_count"]),
                )
                for x in self.collection_items
            ]

        return self.collection_items

    def _get_track_artist_bandcamp_url_stream_url_for_item(self, item):
        item_track_name = item["item_title"]
        item_band_name = item["band_name"]
        item_url = item["item_url"]

        tralbum_id = item["tralbum_id"]
        embed_url = self._construct_embed_url_from_tralbumid(tralbum_id)
        player_data = self._extract_player_data_from_embed_url(embed_url)

        stream_url = None
        if player_data is not None:
            _, _, stream_url = self._extract_title_artist_stream_url_from_data(
                player_data
            )

        return item_track_name, item_band_name, item_url, stream_url

    def _get_bandcamp_page(self, bandcamp_url):
        response = requests.get(bandcamp_url)
        return BeautifulSoup(response.content, features="html.parser")

    def _fetch_wishlist_html(self):
        """Fetch wishlist HTML for the given username."""
        return BeautifulSoup(
            requests.get(f"{self.profile_url}/wishlist").content,
            features="html.parser",
        )

    def _generate_older_than_token(self):
        """Generate an older_than_token."""
        return f"{int(time.time())}::a::"

    def _extract_fan_id(self, html):
        """Extract fan_id from wishlist HTML."""
        return (
            html.select_one("button.follow-unfollow").get("id").split("_")[-1]
        )

    def _fetch_collection_items(self, fan_id, older_than_token):
        """Fetch collection items using fan_id and older_than_token."""
        resp = requests.post(
            "https://bandcamp.com/api/fancollection/1/collection_items",
            headers={"User-Agent": "Mozilla/5.0"},
            json={
                "fan_id": fan_id,
                "older_than_token": older_than_token,
                "count": 2000,
            },
        )
        # print(len(resp.json()["items"]))
        return resp.json()["items"]


class BcUser:
    def __init__(self, profile_url):
        self.profile_url = profile_url
        self.fan_id = None
        self.wishlist_items = None
        self.collection_items = None
        self.older_than_token = None

    async def initialize(self):
        await self._initialize_fan_id_and_older_than_token()

    async def _initialize_fan_id_and_older_than_token(self):
        html_wishlist = await self._fetch_wishlist_html()
        self.older_than_token = self._generate_older_than_token()
        self.fan_id = await get_bandcamp_fan_id(self.profile_url)

    async def scrape_collection_items(self):
        if self.collection_items is None:
            self.collection_items = await self._fetch_collection_items(
                self.fan_id, self.older_than_token
            )
            self.collection_items = [
                Item(
                    id=str(x["item_id"]),
                    type=x["item_type"],
                    url=x["item_url"],
                    sales=int(x["also_collected_count"]),
                )
                for x in self.collection_items
            ]

        return self.collection_items

    async def _get_track_artist_bandcamp_url_stream_url_for_item(self, item):
        item_track_name = item["item_title"]
        item_band_name = item["band_name"]
        item_url = item["item_url"]

        tralbum_id = item["tralbum_id"]
        embed_url = self._construct_embed_url_from_tralbumid(tralbum_id)
        player_data = await self._extract_player_data_from_embed_url(embed_url)

        stream_url = None
        if player_data is not None:
            _, _, stream_url = self._extract_title_artist_stream_url_from_data(
                player_data
            )

        return item_track_name, item_band_name, item_url, stream_url

    # async def fetch_info_from_bancamp_url(self, bandcamp_url):
    #     bc_page = await self._get_bandcamp_page(bandcamp_url)
    #     info = {
    #         "description": None,
    #         "duration": None,
    #         "tags": [],
    #         "country": None,
    #     }

    #     full_description = self._extract_full_description(
    #         bc_page, bandcamp_url
    #     )

    #     if full_description is not None:
    #         description = (
    #             self._extract_most_important_paragraph_from_description(
    #                 full_description
    #             )
    #         )
    #         # info["description"] = remove_links(description)

    #     tag_links = bc_page.find(
    #         "div", attrs={"class": "tralbum-tags"}
    #     ).find_all("a")
    #     tags = [x.text for x in tag_links]
    #     info["tags"] = tags[:-1]
    #     info["country"] = tags[-1]

    #     return info

    # async def get_title_artist_stream_url_from_url(self, bandcamp_url):
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(bandcamp_url) as response:
    #             content = await response.text()
    #             bs = BeautifulSoup(content, features="html.parser")

    #     bs_script = bs.find("script", attrs={"data-tralbum": True})
    #     data_band = json.loads(bs_script.get("data-band"))
    #     data_tralbum = json.loads(bs_script.get("data-tralbum"))
    #     track = data_tralbum.get("trackinfo")[0]
    #     title = track["title"]
    #     artist = data_band["name"]
    #     stream_url = track["file"]["mp3-128"]
    #     return title, artist, stream_url

    async def _get_bandcamp_page(self, bandcamp_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(bandcamp_url) as response:
                content = await response.text()
                return BeautifulSoup(content, features="html.parser")

    async def _fetch_wishlist_html(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.profile_url}/wishlist") as response:
                content = await response.text()
                return BeautifulSoup(content, features="html.parser")

    def _generate_older_than_token(self):
        return f"{int(time.time())}::a::"

    async def _fetch_collection_items(self, fan_id, older_than_token):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://bandcamp.com/api/fancollection/1/collection_items",
                headers={"User-Agent": "Mozilla/5.0"},
                json={
                    "fan_id": fan_id,
                    "older_than_token": older_than_token,
                    "count": 2000,
                },
            ) as response:
                data = await response.json()
                return data["items"]


async def _extract_player_data_from_embed_url(self, embed_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(embed_url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            script_tag = soup.find("script", {"data-tralbum": True})
            if script_tag:
                return json.loads(script_tag["data-tralbum"])
    return None
