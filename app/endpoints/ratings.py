from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import schema
from app.database import get_db
from app.auth import create_access_token, authenticate_user
from app import auth, crud

router = APIRouter()

#endpoints/ratings
@router.post("/{movie_id}/", response_model=schema.Rating)
def create_rating(movie_id: int, rating: schema.RatingCreate, db: Session = Depends(get_db), current_user: schema.User = Depends(auth.get_current_user)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db_rating = crud.create_rating(db=db, rating=rating, movie_id=movie_id, user_id=current_user.id)
    return db_rating

@router.get("/{movie_id}/", response_model=list[schema.Rating])
def read_ratings(movie_id: int, db: Session = Depends(get_db)):
    ratings = crud.get_ratings(db, movie_id=movie_id)
    return ratings 
    