from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from schemas import Item, Set, BandcampUrl, BPMRange, RecommendationRequest
from constants import BpmRange
import traceback
from recommend_tracks import get_recommendations
from utils import get_json_from_html

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-recommendations", response_model=List[Item])
async def generate_recommendations(request: RecommendationRequest):
    try:
        recs = await get_recommendations(
            request.set_input.items,
            BpmRange(request.bpm_range.min, request.bpm_range.max),
            30,
            nof_recs=20,
            filter_bpm=request.filter_bpm,
            sort_by=request.sort_by,
        )
        return recs
    except Exception as e:
        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-bandcamp-id", response_model=Item)
async def get_bandcamp_id(input: BandcampUrl):
    try:
        props = get_json_from_html(input.url)
        if props.get("album_id"):
            print(f"Found album_id: {props['album_id']}")
            return Item(
                id=str(props.get("album_id")), type="album", url=input.url
            )
        elif props.get("track_id"):
            print(f"Found track_id: {props['track_id']}")

            return Item(
                id=str(props.get("track_id")), type="track", url=input.url
            )
        else:
            raise HTTPException(
                status_code=404, detail="Unable to find Bandcamp ID"
            )
    except Exception as e:
        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
