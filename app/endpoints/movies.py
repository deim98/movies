from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import schema
from app.database import get_db
from app.auth import create_access_token, authenticate_user, get_current_user
from app import auth, crud

router = APIRouter()

#endpoints/movies
@router.post("/", response_model=schema.Movie)
def create_movie(movie: schema.MovieCreate, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    return crud.create_movie(db=db, movie=movie, user_id=current_user.id)


@router.get("/{movie_id}", response_model=schema.Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@router.get("/", response_model=list[schema.Movie])
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_movies(db=db)

@router.put("/{movie_id}", response_model=schema.Movie)
def update_movie(movie_id: int, movie: schema.MovieCreate, db: Session = Depends(get_db), current_user: schema.User = Depends(auth.get_current_user)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if db_movie.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this movie")
    updated_movie = crud.update_movie(db=db, movie_id=movie_id, movie=movie, user_id=current_user.id)
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated_movie
    

@router.delete("/{movie_id}", response_model=schema.Movie)
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(auth.get_current_user)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if db_movie.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this movie")
    return crud.delete_movie(db=db, movie_id=movie_id, user_id=current_user.id)
