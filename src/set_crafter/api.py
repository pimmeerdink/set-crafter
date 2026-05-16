import traceback
from typing import List

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analyze_bpm import process_bpm_urls
from .bandcamp_user import BcUser, get_fan_id_from_profile
from .constants import BpmRange
from .recommend_tracks import get_recommendations
from .schemas import (
    BandcampUrl,
    DetectBpmRequest,
    DetectBpmResponse,
    Item,
    ProfileItemsRequest,
    RecommendationRequest,
)
from .utils import get_json_from_html

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:4321",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4321",
        "https://set-crafter.socialtechnologylab.nl",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single User-Agent everywhere so the bandcamp API doesn't think we're a bot.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


@app.post("/generate-recommendations", response_model=List[Item])
async def generate_recommendations(request: RecommendationRequest):
    try:
        return await get_recommendations(
            request.set_input.items,
            BpmRange(request.bpm_range.min, request.bpm_range.max),
            30,
            nof_recs=20,
            filter_bpm=request.filter_bpm,
            sort_by=request.sort_by,
            tags=request.tags,
            tag_match=request.tag_match,
            exclude_owned_by_profile=request.exclude_owned_by_profile,
        )
    except Exception as e:
        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-bandcamp-id", response_model=Item)
async def get_bandcamp_id(input: BandcampUrl):
    try:
        url = input.url
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://" + url
        props = get_json_from_html(url)
        if props.get("album_id"):
            return Item(id=str(props["album_id"]), type="album", url=input.url)
        if props.get("track_id"):
            return Item(id=str(props["track_id"]), type="track", url=input.url)
        raise HTTPException(status_code=404, detail="Unable to find Bandcamp ID")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-profile-items", response_model=List[Item])
async def get_profile_items(request: ProfileItemsRequest):
    """Return items from a bandcamp profile's collection or wishlist."""
    profile_url = request.profile_url
    if not profile_url.startswith(("https://", "http://")):
        profile_url = "https://" + profile_url
    try:
        async with aiohttp.ClientSession(headers=_HEADERS) as session:
            fan_id = await get_fan_id_from_profile(session, profile_url)
            if not fan_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"Could not resolve bandcamp profile: {profile_url}",
                )
            user = BcUser(fan_id, session)
            if request.source == "wishlist":
                return await user.scrape_wishlist_items(count=request.limit)
            return await user.scrape_collection_items(count=request.limit)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-bpm", response_model=DetectBpmResponse)
async def detect_bpm(request: DetectBpmRequest):
    """Run the BPM extractor on a single track and return its tempo."""
    try:
        async with aiohttp.ClientSession(headers=_HEADERS) as session:
            results = await process_bpm_urls(
                [(request.id, request.url)], session
            )
        bpm = results.get(request.url)
        if bpm is None:
            return DetectBpmResponse(bpm=None, error="could not extract bpm")
        return DetectBpmResponse(bpm=bpm)
    except Exception as e:
        print(f"Stack trace: {traceback.format_exc()}")
        return DetectBpmResponse(bpm=None, error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
