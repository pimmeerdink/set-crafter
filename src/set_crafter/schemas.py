from pydantic import BaseModel
from typing import Optional, List, Literal


class Item(BaseModel):
    id: str
    type: str  # 'album' or 'track'
    url: str
    sales: Optional[int] = None


class Set(BaseModel):
    items: List[Item]


class BandcampUrl(BaseModel):
    url: str


class BPMRange(BaseModel):
    min: int
    max: int


class RecommendationRequest(BaseModel):
    set_input: Set
    bpm_range: BPMRange
    filter_bpm: bool
    sort_by: Literal["relevance", "popularity", "random"]
    tags: List[str] = []
    tag_match: Literal["any", "all"] = "any"
    exclude_owned_by_profile: Optional[str] = None


class ProfileItemsRequest(BaseModel):
    profile_url: str
    source: Literal["collection", "wishlist"] = "collection"
    limit: int = 50


class DetectBpmRequest(BaseModel):
    id: str
    url: str


class DetectBpmResponse(BaseModel):
    bpm: Optional[float] = None
    error: Optional[str] = None
