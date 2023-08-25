from .. import models, schemas, oath2
from fastapi import Depends, HTTPException, status, Response, APIRouter
from ..database import get_db, get_rd
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oath2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = None,
):
    query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
    )
    if not search:
        posts = query.limit(limit).offset(skip).all()
    else:
        posts = (
            query.filter(models.Post.title.contains(search))
            .limit(limit)
            .offset(skip)
            .all()
        )
    return posts


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oath2.get_current_user),
    rd=Depends(get_rd),
):
    key_name = f"user-{current_user.id}:post-{id}"
    cache = rd.get(key_name)
    if cache:
        print("cache hit for", key_name)
        post = schemas.PostOut(**json.loads(cache))
        return post

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .where(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post with this id was not found",
        )
    post_model, votes_count = post
    post_out = schemas.PostOut(Post=post_model, votes=votes_count)
    cache = post_out.model_dump_json()
    rd.set(key_name, cache)
    rd.expire(key_name, 10)
    return post


@router.post("/", status_code=201, response_model=schemas.Post)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oath2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=204)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oath2.get_current_user),
):
    post_query = db.query(models.Post).where(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.owner_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oath2.get_current_user),
):
    query = db.query(models.Post).filter(models.Post.id == id)
    post_query = query.first()
    if not post_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post_query.owner_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    query.update(post.model_dump(), synchronize_session=False)  # type: ignore
    db.commit()
    return query.first()
