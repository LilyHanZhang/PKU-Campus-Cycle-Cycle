"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import axios from "axios";
import Image from "next/image";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://10.129.245.117:8000";

interface Post {
  id: string;
  title: string;
  content: string;
  author_id: string;
  author_name?: string;
  author_avatar_url?: string;
  image_urls?: string[];
  like_count: number;
  comment_count: number;
  bookmark_count: number;
  created_at: string;
  is_liked?: boolean;
  is_bookmarked?: boolean;
}

interface Comment {
  id: string;
  content: string;
  author_id: string;
  author_name?: string;
  author_avatar_url?: string;
  created_at: string;
}

export default function PostDetailPage() {
  const params = useParams();
  const router = useRouter();
  const postId = params.id as string;

  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [commentContent, setCommentContent] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPostDetail();
  }, [postId]);

  const fetchPostDetail = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.get(`${API_URL}/posts/${postId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPost(response.data);
    } catch (error) {
      console.error("获取帖子详情失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!post) return;
    try {
      const token = localStorage.getItem("access_token");
      await axios.post(
        `${API_URL}/posts/${postId}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPost({ ...post, is_liked: !post.is_liked, like_count: post.is_liked ? post.like_count - 1 : post.like_count + 1 });
    } catch (error) {
      console.error("点赞失败:", error);
    }
  };

  const handleBookmark = async () => {
    if (!post) return;
    try {
      const token = localStorage.getItem("access_token");
      await axios.post(
        `${API_URL}/posts/${postId}/bookmark`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPost({ ...post, is_bookmarked: !post.is_bookmarked, bookmark_count: post.is_bookmarked ? post.bookmark_count - 1 : post.bookmark_count + 1 });
    } catch (error) {
      console.error("收藏失败:", error);
    }
  };

  const handleAddComment = async () => {
    if (!commentContent.trim()) return;
    setSubmitting(true);
    try {
      const token = localStorage.getItem("access_token");
      await axios.post(
        `${API_URL}/posts/${postId}/comments`,
        { content: commentContent },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCommentContent("");
      fetchPostDetail();
    } catch (error) {
      console.error("评论失败:", error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">帖子不存在</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* 返回按钮 */}
        <button
          onClick={() => router.back()}
          className="mb-4 text-gray-600 hover:text-gray-900 flex items-center"
        >
          ← 返回
        </button>

        {/* 帖子内容 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">{post.title}</h1>
          
          {/* 作者信息 */}
          <div className="flex items-center mb-6">
            {post.author_avatar_url ? (
              <Image
                src={post.author_avatar_url}
                alt={post.author_name || "作者"}
                width={40}
                height={40}
                className="w-10 h-10 rounded-full object-cover"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500 text-sm">
                  {post.author_name?.charAt(0).toUpperCase() || "A"}
                </span>
              </div>
            )}
            <div className="ml-3">
              <div className="font-semibold text-gray-900">{post.author_name || "匿名用户"}</div>
              <div className="text-sm text-gray-500">
                {new Date(post.created_at).toLocaleString("zh-CN")}
              </div>
            </div>
          </div>

          {/* 帖子内容 */}
          <div className="prose max-w-none mb-6">
            <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{post.content}</p>
          </div>

          {/* 帖子图片 */}
          {post.image_urls && post.image_urls.length > 0 && (
            <div className="grid grid-cols-2 gap-4 mb-6">
              {post.image_urls.map((url, index) => (
                <div key={index} className="relative aspect-square">
                  <Image
                    src={url}
                    alt={`图片 ${index + 1}`}
                    fill
                    className="object-cover rounded-lg"
                  />
                </div>
              ))}
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <button
              onClick={handleLike}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full transition ${
                post.is_liked
                  ? "text-red-600 bg-red-50"
                  : "text-gray-600 hover:text-red-600 hover:bg-red-50"
              }`}
            >
              <span>👍</span>
              <span>{post.like_count}</span>
            </button>

            <button
              onClick={handleBookmark}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full transition ${
                post.is_bookmarked
                  ? "text-amber-600 bg-amber-50"
                  : "text-gray-600 hover:text-amber-600 hover:bg-amber-50"
              }`}
            >
              <span>⭐</span>
              <span>{post.bookmark_count}</span>
            </button>
          </div>
        </div>

        {/* 评论区 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">评论 ({post.comment_count})</h2>

          {/* 发表评论 */}
          <div className="mb-6">
            <textarea
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              placeholder="写下你的评论..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
              rows={3}
            />
            <button
              onClick={handleAddComment}
              disabled={submitting || !commentContent.trim()}
              className="mt-2 bg-[#1f874c] text-white px-6 py-2 rounded-full hover:bg-[#155f35] transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "提交中..." : "发表评论"}
            </button>
          </div>

          {/* 评论列表 */}
          <div className="space-y-4">
            {comments.map((comment) => (
              <div key={comment.id} className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-0">
                {comment.author_avatar_url ? (
                  <Image
                    src={comment.author_avatar_url}
                    alt={comment.author_name || "评论者"}
                    width={32}
                    height={32}
                    className="w-8 h-8 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-gray-500 text-xs">
                      {comment.author_name?.charAt(0).toUpperCase() || "A"}
                    </span>
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm text-gray-900">
                      {comment.author_name || "匿名用户"}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.created_at).toLocaleString("zh-CN")}
                    </span>
                  </div>
                  <p className="text-gray-800 text-sm mt-1">{comment.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
