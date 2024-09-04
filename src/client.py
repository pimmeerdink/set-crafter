import asyncio
from schemas import BPMRange, Item
from bandcamp_api import Bandcamp
from set import Set
from recommend_tracks import get_recommendations

ITEMS = [
    Item(
        id="631070714",
        type="track",
        url="https://jerryhorny.bandcamp.com/track/business-visa",
        sales=0,
    ),
]

TESTTRALBUMS = [
    "https://lowincomesquad.bandcamp.com/track/siu-mata-psyro",
    "https://jerryhorny.bandcamp.com/track/business-visa",
]


async def test_recommendations():
    bpm_range = BPMRange(min=100, max=160)

    try:
        recommendations = await get_recommendations(
            items=ITEMS,
            bpm_range=bpm_range,
            max_supporters=15,
            nof_recs=20,
            filter_bpm=False,
            sort_by="relevance",
        )
        print(
            "Recommendations:",
        )
        for rec in recommendations:
            print(rec.url)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(test_recommendations())
