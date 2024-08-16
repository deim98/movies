from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import crud, schema, auth
from app.database import get_db
from app.auth import create_access_token, authenticate_user

router = APIRouter()

#endpoints/comment
@router.post("/{movie_id}/", response_model=schema.Comment)
def create_comment(movie_id: int, comment: schema.CommentCreate, db: Session = Depends(get_db), current_user: schema.User = Depends(auth.get_current_user)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Check if parent_comment_id is provided and exists
    if comment.parent_comment_id:
        parent_comment = crud.get_comment(db, comment.parent_comment_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    
    return crud.create_comment(db=db, comment=comment, movie_id=movie_id, user_id=current_user.id)

@router.get("/{movie_id}/", response_model=list[schema.Comment])
def read_comments(movie_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    comments= crud.get_comments(db, movie_id=movie_id, skip=skip, limit=limit)
    
    return comments
