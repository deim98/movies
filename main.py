from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from app.auth import authenticate_user, create_access_token, get_current_user
import app.crud as crud, app.schema as schema
from app.database import engine, Base, get_db, init_db
from app.auth import pwd_context
from typing import Optional, List
from app.endpoints import users, ratings, comments, movies
from app.models import User, Movie, Comment, Rating 
# import sentry_sdk
from app.logger import get_logger
from typing import List

logger = get_logger(__name__)

def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

app = FastAPI()


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(movies.router, prefix="/movies", tags=["movies"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(ratings.router, prefix="/ratings", tags=["ratings"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the movie API!"}



@app.post("/signup", response_model=schema.User)
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    logger.info('Creating user...')
    db_user = crud.get_user_by_username(db, username=user.username)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        logger.warning(f"User with {user.username} already exists.")
        raise HTTPException(status_code=400, detail="Username already registered")
    logger.info('User successfully created.')
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    logger.info("Generating authentication token...")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Token generated for {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/movies/")
def get_movies(
    db: Session = Depends(get_db),
    movie_id= int
):
    movies = crud.get_movies(db,movie_id)
    return movies

@app.get("/movie/{movie_id}", response_model=schema.Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    logger.info(f'Getting movie with ID: {movie_id}')
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.error(f'Movie with ID {movie_id} not found.')
        raise HTTPException(status_code=404, detail="Movie not found")
    logger.info(f'Movie with ID {movie_id} retrieved successfully.')
    return movie

@app.post("/movies", response_model=schema.Movie)
def create_movie(
    payload: schema.MovieCreate,
    user: schema.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    movie = crud.create_movie(db, payload, user_id=user.id)
    return {"message": "success", "data": movie}

@app.put("/movies/{movie_id}", response_model=schema.Movie)
def update_movie(
    movie_id: int, payload: schema.MovieUpdate, db: Session = Depends(get_db), user: schema.User = Depends(get_current_user)
):
    movie = crud.update_movie(db, movie_id, payload, user_id=user.id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "success", "data": movie}

@app.delete("/movies/{movie_id}", response_model=schema.Movie)
def delete_movie(
    movie_id: int, db: Session = Depends(get_db), user: schema.User = Depends(get_current_user)
):
    movie = crud.delete_movie(db, movie_id, user_id=user.id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "success", "data": movie}

@app.post("/movies/{movie_id}/ratings", response_model=schema.Rating)
def create_rating(
    movie_id: int, 
    rating: schema.RatingCreate,
    db: Session = Depends(get_db),
    user: schema.User = Depends(get_current_user)
):
    db_rating = crud.create_rating(db, rating, movie_id=movie_id, user_id=user.id)
    return db_rating


@app.get("/movies/{movie_id}/ratings", response_model=List[schema.Rating])
def get_ratings(movie_id: int, db: Session = Depends(get_db)):
    ratings = crud.get_ratings(db, movie_id)
    return ratings

@app.post("/movies/{movie_id}/comments", response_model=schema.Comment)
def create_comment(
    movie_id: int,
    comment: schema.CommentCreate,
    db: Session = Depends(get_db),
    user: schema.User = Depends(get_current_user)
):
    db_comment = crud.create_comment(db, comment, movie_id=movie_id, user_id=user.id)
    return db_comment

@app.get("/movies/{movie_id}/comments", response_model=List[schema.Comment])
def get_comments(
    movie_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    comments = crud.get_comments(db, movie_id, skip=skip, limit=limit)
    return comments

@app.post("/comments/{parent_comment_id}/replies", response_model=schema.Comment)
def create_nested_comment(
    parent_comment_id: int,
    comment: schema.CommentCreate,
    db: Session = Depends(get_db),
    user: schema.User = Depends(get_current_user)
):
    parent_comment = crud.get_comment(db, parent_comment_id)
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Parent comment not found")
    
    db_comment = crud.create_comment(
        db, 
        comment, 
        movie_id=parent_comment.movie_id, 
        user_id=user.id
    )
    return db_comment

@app.get("/health")
def health_check():
    return {"status": "healthy"}

