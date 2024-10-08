# app/crud.py
from sqlalchemy.orm import Session
from app import models, schema
from app.models import User 
from app.logger import get_logger

logger = get_logger(__name__)

#Users
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id ==user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schema.UserCreate, hashed_password: str):
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#Movies
def get_movie(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if movie:
        # Ensure all fields are populated correctly
        for comment in movie.comments:
            if comment.user_id is None:
                comment.user_id = 0  # or another default value, depending on your use case
        return movie
    return None


def get_movies(db: Session, movie_id:int):
    """Fetch a list of movies with pagination support."""
    return db.query(models.Movie).filter(models.Movie.id==movie_id).all()

def create_movie(db: Session, movie: schema.MovieCreate, user_id: int):
    db_movie = models.Movie(title= movie.title,description=movie.description, user_id=user_id)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def update_movie(db: Session, movie_id: int, movie: schema.MovieUpdate, user_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id, models.Movie.user_id == user_id).first()
    if db_movie:
        for key, value in movie.model_dump().items():
            setattr(db_movie, key, value)
        db.commit()
        db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, movie_id: int, user_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id, models.Movie.user_id == user_id).first()
    if db_movie:
        db.delete(db_movie)
        db.commit()
    return db_movie

#Comments
def create_comment(db: Session, comment: schema.CommentCreate, movie_id: int, user_id: int):
    db_comment = models.Comment(content=comment.content, movie_id=movie_id, user_id=user_id, parent_comment_id=comment.parent_comment_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

#fetching comments with nested replies
def get_comments(db: Session, movie_id: int, skip: int = 0, limit: int = 10):
    comments = db.query(models.Comment).filter(models.Comment.movie_id == movie_id).offset(skip).limit(limit).all()
    # Optionally, exclude the replies field or limit the depth
    for comment in comments:
        comment.replies = []  # or implement logic to limit the depth of replies
    return comments

#get comment by ID
def get_comment(db: Session, comment_id: int, depth: int = 1):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment:
        # Limit the depth of replies based on the 'depth' parameter
        if depth > 1:
            for reply in comment.replies:
                reply.replies = []  # or recursively call get_comment_with_replies with depth-1
    return comment


#Ratings
def create_rating(db: Session, rating: schema.RatingCreate, movie_id: int, user_id: int= None):
    db_rating = models.Rating(score=rating.score, movie_id=movie_id, user_id=user_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def get_ratings(db: Session, movie_id: int):
    return db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
