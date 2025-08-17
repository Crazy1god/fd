from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict

Grade = Literal["1A", "1B", "2A", "2B", "3A", "3B"]


class UserIn(BaseModel):
    email: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=64)
    fam: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    otc: Optional[str] = Field(None, max_length=255)


class CoordsIn(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    height: Optional[int] = Field(None, ge=-500, le=9000)


class LevelIn(BaseModel):
    winter: Optional[Grade] = None
    spring: Optional[Grade] = None
    summer: Optional[Grade] = None
    autumn: Optional[Grade] = None


class ImageIn(BaseModel):
    title: Optional[str] = None
    url: str


class SubmitIn(BaseModel):
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None

    user: UserIn
    coords: CoordsIn
    level: Optional[LevelIn] = None
    images: List[ImageIn] = Field(default_factory=list)


class SubmitResponse(BaseModel):
    status: int
    message: str
    id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)