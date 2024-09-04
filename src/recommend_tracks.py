import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from constants import BpmRange, Item
from bandcamp_user import BcUser
from analyze_bpm import process_bpm_urls
import asyncio

flatten = lambda x: [item for sublist in x for item in sublist]


import aiohttp
from bs4 import BeautifulSoup
import asyncio


async def get_supporters(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()

    soup = BeautifulSoup(content, "html.parser")
    supporters = soup.find_all("a", class_="fan pic")
    return [supporter["href"] for supporter in supporters]


async def get_user_purchases(user_url):
    user = BcUser(user_url)
    collection = await user.scrape_collection_items()
    return collection


async def get_user_purchases(user_url):
    user = BcUser(user_url)
    await user.initialize()
    collection = await user.scrape_collection_items()
    return collection


async def get_recommendations(
    items,
    bpm_range,
    max_supporters=5,
    nof_recs=20,
    filter_bpm=True,
    sort_by="relevance",
):
    # Gather all supporters asynchronously
    all_supporters = await asyncio.gather(
        *[get_supporters(item.url) for item in items]
    )
    all_supporters = pd.Series(flatten(all_supporters))

    weights = all_supporters.value_counts()
    weights = weights**2
    weights = weights / weights.sum()

    # Sample according to weights
    supporters = random.choices(
        weights.index,
        weights=weights.values,
        k=min(max_supporters, len(weights)),
    )

    # Gather all purchases asynchronously
    all_purchases = await asyncio.gather(
        *[get_user_purchases(supporter) for supporter in supporters]
    )
    all_purchases = flatten(all_purchases)

    org_items = [(item.id, item.type, item.url, item.sales) for item in items]
    all_purchases = [
        (item.id, item.type, item.url, item.sales) for item in all_purchases
    ]
    purchase_counts = pd.Series(all_purchases).value_counts()
    org_urls = [x[2] for x in org_items]
    rel_purchase_counts = purchase_counts[
        ~(purchase_counts.index.map(lambda x: x[2]).isin(org_urls))
    ]

    if sort_by == "random":
        rel_purchase_counts = rel_purchase_counts.sample(frac=1)
    elif sort_by == "relevance":
        rel_purchase_counts = rel_purchase_counts.sort_values(
            ascending=False
        ).to_frame()
    else:
        item2sales = pd.Series({x: x[3] for x in rel_purchase_counts.index})
        # sort
        rel_purchase_counts = item2sales.sort_values(
            ascending=False
        ).to_frame()

    if not filter_bpm:
        recs = rel_purchase_counts.head(nof_recs).index.tolist()
        recs = [
            Item(id=str(x), type=str(y), url=str(z)) for (x, y, z, _) in recs
        ]
        return recs

    else:
        print("Extracting BPMs for recommended tracks...")
        print("bpm range: " + str(bpm_range))
        # drop non-tracks
        recs = rel_purchase_counts.index.tolist()
        recs = [rec for rec in recs if rec[1] == "track"]
        all_recs = []
        for i in range(0, len(purchase_counts), 10):
            recs = recs[i : i + 10]
            urls = [x[2] for x in recs]
            url2bpm = await process_bpm_urls(
                urls
            )  # Assuming process_bpm_urls is also asycn
            for url, bpm in url2bpm.items():
                if (bpm_range.min <= bpm - 4) <= (bpm_range.max + 4):
                    org_item = next(x for x in recs if x[2] == url)
                    all_recs.append(org_item)
                    if len(all_recs) >= nof_recs:
                        recs = [
                            Item(id=str(x), type=str(y), url=str(z))
                            for (x, y, z, _) in recs
                        ][:nof_recs]
                        return recs

        # If we didn't return earlier, return whatever we have
        recs = [
            Item(id=str(x), type=str(y), url=str(z))
            for (x, y, z, _) in all_recs
        ][:nof_recs]
        return recs


def main():
    url = "https://hassanaboualam.bandcamp.com/album/mesh-mafhoom"
    recommendations = get_recommendations(
        [Item("album", "123", url)],
        BpmRange(130, 160),
        max_supporters=15,
    )

    print("\nTop recommendations:")
    for i, rec in enumerate(recommendations):
        print(f"{i+1}. {rec}")


if __name__ == "__main__":
    main()
