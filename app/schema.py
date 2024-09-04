from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    movies: Optional[List['Movie']] = []
    comments: Optional[List['Comment']] = []
    ratings: Optional[List['Rating']] = []
    
    
    model_config= ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class MovieBase(BaseModel):
    title: str
    description:str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    user_id: int
    comments: Optional[List['Comment']] = []
    ratings: Optional[List['Rating']] = []
    
    
    model_config= ConfigDict(from_attributes=True)
    
class MovieUpdate(MovieBase):
    pass

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    movie_id: int
    parent_comment_id: Optional[int] = None
    

class Comment(CommentBase):
    id: int
    movie_id: int
    user_id: Optional[int]
    replies: List['Comment'] = []
    
    model_config= ConfigDict(from_attributes=True)

class RatingBase(BaseModel):
    score: float

class RatingCreate(RatingBase):
    movie_id: int
    

class Rating(RatingBase):
    id: int
    score: float
    movie_id: int
    user_id: int
    
    model_config= ConfigDict(from_attributes=True)
    
# Handle forward references for self-referencing models
Movie.model_rebuild()
Comment.model_rebuild()