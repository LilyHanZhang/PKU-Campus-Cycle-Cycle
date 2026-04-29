from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
import re

from ..database import get_db
from ..models import Post, Comment, Like, User, Bookmark
from ..schemas import (
    PostCreate, PostUpdate, PostResponse,
    CommentCreate, CommentResponse, BookmarkCreate, BookmarkResponse
)
from ..auth import get_current_user

router = APIRouter(prefix="/posts", tags=["社区论坛"])

def extract_hashtags(content: str) -> List[str]:
    """从内容中提取话题标签"""
    hashtags = re.findall(r'#(\w+)', content)
    return hashtags

def get_post_with_stats(db: Session, post: Post, current_user_id: str = None) -> dict:
    """获取帖子的完整信息，包括统计数据"""
    like_count = db.query(func.count(Like.post_id)).filter(Like.post_id == post.id).scalar() or 0
    comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar() or 0
    bookmark_count = db.query(func.count(Bookmark.post_id)).filter(Bookmark.post_id == post.id).scalar() or 0
    
    is_bookmarked = False
    if current_user_id:
        is_bookmarked = db.query(Bookmark).filter(
            Bookmark.post_id == post.id,
            Bookmark.user_id == UUID(current_user_id)
        ).first() is not None
    
    author = db.query(User).filter(User.id == post.author_id).first()
    
    return {
        **PostResponse.model_validate(post).model_dump(),
        "like_count": like_count,
        "comment_count": comment_count,
        "bookmark_count": bookmark_count,
        "is_bookmarked": is_bookmarked,
        "author_name": author.name if author else None,
        "author_avatar_url": author.avatar_url if author else None,
        "hashtags": extract_hashtags(post.content)
    }

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
    
    return get_post_with_stats(db, db_post, current_user["user_id"])

@router.get("/", response_model=List[PostResponse])
def list_posts(
    skip: int = 0,
    limit: int = 50,
    hashtag: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    
    if hashtag:
        posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        filtered_posts = [post for post in posts if hashtag in extract_hashtags(post.content)]
        result = [get_post_with_stats(db, post) for post in filtered_posts]
    else:
        posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        result = [get_post_with_stats(db, post) for post in posts]
    
    return result

@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    return get_post_with_stats(db, post, current_user["user_id"])

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
    
    author = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    return {
        **CommentResponse.model_validate(db_comment).model_dump(),
        "author_name": author.name if author else None,
        "author_avatar_url": author.avatar_url if author else None
    }

@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def list_comments(post_id: UUID, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).all()
    
    result = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.author_id).first()
        result.append({
            **CommentResponse.model_validate(comment).model_dump(),
            "author_name": author.name if author else None,
            "author_avatar_url": author.avatar_url if author else None
        })
    
    return result

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

@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if str(comment.author_id) != current_user["user_id"] and current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="无权限删除")

    db.delete(comment)
    db.commit()
    return {"message": "删除成功"}

@router.post("/{post_id}/bookmarks")
def toggle_bookmark(
    post_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.post_id == post_id,
        Bookmark.user_id == UUID(current_user["user_id"])
    ).first()

    if existing_bookmark:
        db.delete(existing_bookmark)
        db.commit()
        return {"message": "取消收藏", "bookmarked": False}
    else:
        new_bookmark = Bookmark(
            post_id=post_id,
            user_id=UUID(current_user["user_id"])
        )
        db.add(new_bookmark)
        db.commit()
        db.refresh(new_bookmark)
        return new_bookmark

@router.get("/bookmarks/my", response_model=List[PostResponse])
def get_my_bookmarks(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmarks = db.query(Bookmark).filter(
        Bookmark.user_id == UUID(current_user["user_id"])
    ).order_by(Bookmark.created_at.desc()).offset(skip).limit(limit).all()
    
    posts = [db.query(Post).filter(Post.id == bookmark.post_id).first() for bookmark in bookmarks]
    posts = [post for post in posts if post]
    
    result = [get_post_with_stats(db, post, current_user["user_id"]) for post in posts]
    return result

@router.get("/hashtags/trending", response_model=List[str])
def get_trending_hashtags(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(100).all()
    hashtag_count = {}
    
    for post in posts:
        hashtags = extract_hashtags(post.content)
        for tag in hashtags:
            hashtag_count[tag] = hashtag_count.get(tag, 0) + 1
    
    sorted_hashtags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)
    return [tag for tag, count in sorted_hashtags[:limit]]
