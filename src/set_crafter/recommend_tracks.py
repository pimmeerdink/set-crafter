import asyncio
import random
from urllib.parse import urlparse

import aiohttp
import pandas as pd

from .analyze_bpm import process_bpm_urls
from .bandcamp_user import BcUser
from .constants import BpmRange
from .schemas import Item


def _flatten(xs):
    return [item for sub in xs for item in sub]


_TYPE_TO_LETTER = {"album": "a", "track": "t"}


async def get_supporters(session, item, count=500):
    """Return fan_ids of users who collected the given item.

    Uses bandcamp's tralbumcollectors JSON API rather than scraping the
    album HTML — one POST returns up to `count` fans with fan_ids inline,
    avoiding the per-supporter wishlist lookup we used to do for fan_id.
    """
    tralbum_type = _TYPE_TO_LETTER.get(item.type, item.type)
    host = urlparse(item.url).netloc
    url = f"https://{host}/api/tralbumcollectors/2/thumbs"
    payload = {
        "tralbum_type": tralbum_type,
        "tralbum_id": str(item.id),
        "count": count,
    }
    try:
        async with session.post(url, json=payload) as response:
            data = await response.json(content_type=None)
    except Exception as exc:
        print(f"tralbumcollectors failed for {item.url}: {exc}")
        return []
    results = data.get("results", []) if isinstance(data, dict) else []
    return [r["fan_id"] for r in results if "fan_id" in r]


async def get_user_purchases(session, fan_id):
    user = BcUser(fan_id, session)
    return await user.scrape_collection_items()


async def get_recommendations(
    items,
    bpm_range,
    max_supporters=5,
    nof_recs=20,
    filter_bpm=True,
    sort_by="relevance",
):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        supporter_lists = await asyncio.gather(
            *[get_supporters(session, item) for item in items]
        )
        flat_supporters = _flatten(supporter_lists)
        if not flat_supporters:
            print("No supporters found for input items")
            return []
        all_supporters = pd.Series(flat_supporters)

        weights = all_supporters.value_counts() ** 2
        weights = weights / weights.sum()
        supporters = [
            int(s)
            for s in random.choices(
                weights.index,
                weights=weights.values,
                k=min(max_supporters, len(weights)),
            )
        ]

        purchase_lists = await asyncio.gather(
            *[get_user_purchases(session, s) for s in supporters]
        )
        all_purchases = _flatten(purchase_lists)

        org_urls = {item.url for item in items}
        purchase_tuples = [
            (i.id, i.type, i.url, i.sales) for i in all_purchases
        ]
        counts = pd.Series(purchase_tuples).value_counts()
        counts = counts[~counts.index.map(lambda x: x[2]).isin(org_urls)]

        if sort_by == "random":
            ranked = counts.sample(frac=1)
        elif sort_by == "relevance":
            ranked = counts.sort_values(ascending=False)
        else:  # popularity
            ranked = pd.Series({x: x[3] for x in counts.index}).sort_values(
                ascending=False
            )
        candidates = ranked.index.tolist()

        if not filter_bpm:
            top = candidates[:nof_recs]
            return [
                Item(id=str(x[0]), type=str(x[1]), url=str(x[2])) for x in top
            ]

        # Cap probe set: once we've checked the top ~100 by relevance we'll have
        # accumulated enough hits, and going deeper just wastes CDN/CPU.
        MAX_PROBE = 100
        track_candidates = [c for c in candidates if c[1] == "track"][:MAX_PROBE]
        print(
            f"Extracting BPMs for up to {len(track_candidates)} tracks; "
            f"range {bpm_range.min}-{bpm_range.max}",
            flush=True,
        )

        accepted = []
        batch_size = 20
        for i in range(0, len(track_candidates), batch_size):
            batch = track_candidates[i : i + batch_size]
            url2bpm = await process_bpm_urls(
                [(c[0], c[2]) for c in batch], session
            )
            print(
                f"  batch {i // batch_size}: {len(url2bpm)}/{len(batch)} bpms; "
                f"sample: {list(url2bpm.values())[:5]}",
                flush=True,
            )
            for url, bpm in url2bpm.items():
                if (bpm_range.min - 4) <= bpm <= (bpm_range.max + 4):
                    accepted.append(next(c for c in batch if c[2] == url))
                    if len(accepted) >= nof_recs:
                        break
            if len(accepted) >= nof_recs:
                break

        return [
            Item(id=str(x[0]), type=str(x[1]), url=str(x[2]))
            for x in accepted[:nof_recs]
        ]


def main():
    url = "https://hassanaboualam.bandcamp.com/album/mesh-mafhoom"
    recs = asyncio.run(
        get_recommendations(
            [Item(id="123", type="album", url=url)],
            BpmRange(130, 160),
            max_supporters=15,
        )
    )
    print("\nTop recommendations:")
    for i, rec in enumerate(recs):
        print(f"{i+1}. {rec}")


if __name__ == "__main__":
    main()
