from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class News(BaseModel):
    id: int = Field(gt=0)
    title: str
    date: datetime
    body: str
    deleted: bool
    comments_count: int = 0


class Comment(BaseModel):
    id: int = Field(gt=0)
    news_id: int = Field(gt=0)
    title: str
    date: datetime
    comment: str


class ListNewsResponse(BaseModel):
    news: List[News]
    new_count: int


class NewsDetailResponse(BaseModel):
    id: int = Field(gt=0)
    title: str
    date: datetime
    body: str
    deleted: bool
    comments: List[Comment]
    comments_count: int
