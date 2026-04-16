from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Post, Comment, Like, User
from ..schemas import (
    PostCreate, PostUpdate, PostResponse,
    CommentCreate, CommentResponse
)
from ..auth import get_current_user

router = APIRouter(prefix="/posts", tags=["社区论坛"])

@router.post("/", response_model=PostResponse)
def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = Post(
        author_id=UUID(current_user["user_id"]),
        title=post.title,
        content=post.content
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    result = db.query(
        Post,
        func.count(Comment.id).label("comment_count"),
        func.count(Like.post_id).label("like_count")
    ).outerjoin(Comment).outerjoin(Like).filter(Post.id == db_post.id).group_by(Post.id).first()

    return {
        **PostResponse.model_validate(db_post).model_dump(),
        "like_count": result.comment_count if result else 0,
        "comment_count": result.like_count if result else 0
    }

@router.get("/", response_model=List[PostResponse])
def list_posts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for post in posts:
        like_count = db.query(func.count(Like.post_id)).filter(Like.post_id == post.id).scalar() or 0
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar() or 0
        result.append({
            **PostResponse.model_validate(post).model_dump(),
            "like_count": like_count,
            "comment_count": comment_count
        })
    return result

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: UUID, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    like_count = db.query(func.count(Like.post_id)).filter(Like.post_id == post.id).scalar() or 0
    comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar() or 0

    return {
        **PostResponse.model_validate(post).model_dump(),
        "like_count": like_count,
        "comment_count": comment_count
    }

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: UUID,
    post_update: PostUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    if str(post.author_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="只能修改自己的帖子")

    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content

    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    if str(post.author_id) != current_user["user_id"] and current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="无权限删除")

    db.delete(post)
    db.commit()
    return {"message": "删除成功"}

@router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: UUID,
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    db_comment = Comment(
        post_id=post_id,
        author_id=UUID(current_user["user_id"]),
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def list_comments(post_id: UUID, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).all()
    return comments

@router.post("/{post_id}/likes")
def toggle_like(
    post_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == UUID(current_user["user_id"])
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"message": "取消点赞", "liked": False}
    else:
        new_like = Like(
            post_id=post_id,
            user_id=UUID(current_user["user_id"])
        )
        db.add(new_like)
        db.commit()
        return {"message": "点赞成功", "liked": True}

@router.get("/{post_id}/likes/count")
def get_like_count(post_id: UUID, db: Session = Depends(get_db)):
    count = db.query(func.count(Like.post_id)).filter(Like.post_id == post_id).scalar() or 0
    return {"count": count}
