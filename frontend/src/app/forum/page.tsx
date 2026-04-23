"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { ThumbsUp, MessageCircle, Trash2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pku-campus-cycle-cycle.onrender.com";

interface Post {
  id: string;
  author_id: string;
  title: string;
  content: string;
  like_count: number;
  comment_count: number;
  created_at: string;
}

interface Comment {
  id: string;
  author_id: string;
  content: string;
  created_at: string;
}

export default function ForumPage() {
  const { user, isAuthenticated } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState({ title: "", content: "" });
  const [posting, setPosting] = useState(false);
  const [expandedComments, setExpandedComments] = useState<{[key: string]: boolean}>({});
  const [comments, setComments] = useState<{[key: string]: Comment[]}>({});
  const [newComment, setNewComment] = useState<{[key: string]: string}>({});

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/posts/`);
      setPosts(data);
    } catch (error) {
      console.error("Failed to fetch posts", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async (postId: string) => {
    try {
      const { data } = await axios.get(`${API_URL}/posts/${postId}/comments`);
      setComments(prev => ({ ...prev, [postId]: data }));
    } catch (error) {
      console.error("Failed to fetch comments", error);
    }
  };

  const toggleComments = (postId: string) => {
    if (!expandedComments[postId]) {
      fetchComments(postId);
    }
    setExpandedComments(prev => ({ ...prev, [postId]: !prev[postId] }));
  };

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert("请先登录后再发帖");
      return;
    }
    if (!newPost.title || !newPost.content) return;

    setPosting(true);
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(
        `${API_URL}/posts/`,
        { title: newPost.title, content: newPost.content },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewPost({ title: "", content: "" });
      fetchPosts();
    } catch (error) {
      console.error("Failed to create post", error);
      alert("发布失败，请重试");
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (postId: string) => {
    if (!isAuthenticated) {
      alert("请先登录后再点赞");
      return;
    }
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(`${API_URL}/posts/${postId}/likes`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchPosts();
    } catch (error) {
      console.error("Failed to like post", error);
    }
  };

  const handleAddComment = async (postId: string) => {
    if (!isAuthenticated) {
      alert("请先登录后再评论");
      return;
    }
    const content = newComment[postId]?.trim();
    if (!content) return;

    const token = localStorage.getItem("access_token");
    try {
      await axios.post(
        `${API_URL}/posts/${postId}/comments`,
        { content },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewComment(prev => ({ ...prev, [postId]: "" }));
      fetchComments(postId);
      fetchPosts();
    } catch (error) {
      console.error("Failed to add comment", error);
      alert("评论失败，请重试");
    }
  };

  const handleDeleteComment = async (postId: string, commentId: string) => {
    if (!isAuthenticated) {
      alert("请先登录");
      return;
    }
    const token = localStorage.getItem("access_token");
    try {
      await axios.delete(
        `${API_URL}/posts/${postId}/comments/${commentId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchComments(postId);
      fetchPosts();
    } catch (error) {
      console.error("Failed to delete comment", error);
      alert("删除失败");
    }
  };

  const handleDeletePost = async (postId: string) => {
    if (!isAuthenticated) {
      alert("请先登录");
      return;
    }
    if (!confirm("确定要删除这个帖子吗？")) return;
    
    const token = localStorage.getItem("access_token");
    try {
      await axios.delete(
        `${API_URL}/posts/${postId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchPosts();
    } catch (error) {
      console.error("Failed to delete post", error);
      alert("删除失败");
    }
  };

  return (
    <div className="min-h-screen bg-green-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-12">
          <h1 className="text-4xl font-extrabold text-[#1f874c]">社区广场</h1>
          <Link href="/" className="text-emerald-600 font-bold hover:underline">返回首页</Link>
        </div>

        {isAuthenticated && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-12 border-t-4 border-emerald-400">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">发布新帖子</h2>
            <form onSubmit={handlePostSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="帖子标题"
                value={newPost.title}
                onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <textarea
                placeholder="分享你的建议或使用感受..."
                value={newPost.content}
                onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                rows={4}
              />
              <button
                type="submit"
                disabled={posting}
                className="w-full bg-[#2ab26a] text-white py-3 rounded-full font-bold hover:bg-[#1f874c] transition shadow-md disabled:bg-gray-400"
              >
                {posting ? "发布中..." : "发布"}
              </button>
            </form>
          </div>
        )}

        {!isAuthenticated && (
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-8 text-center">
            <p className="text-gray-600">
              <Link href="/login" className="text-[#2ab26a] font-bold hover:underline">登录</Link>
              后可以发布帖子和参与讨论
            </p>
          </div>
        )}

        <div className="space-y-6">
          {loading ? (
            <p className="text-center py-10">加载帖子中...</p>
          ) : posts.length > 0 ? (
            posts.map(post => (
              <div key={post.id} className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-bold text-gray-800">{post.title}</h3>
                  {isAuthenticated && str(post.author_id) === user?.id && (
                    <button
                      onClick={() => handleDeletePost(post.id)}
                      className="text-red-500 hover:text-red-700 transition"
                      title="删除帖子"
                    >
                      <Trash2 size={18} />
                    </button>
                  )}
                </div>
                <p className="text-gray-600 mb-4">{post.content}</p>
                <div className="flex items-center justify-between text-gray-500 border-t pt-4">
                  <span className="text-xs font-medium">发布者：{post.author_id?.substring(0, 8)}...</span>
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => handleLike(post.id)}
                      className="flex items-center space-x-1 hover:text-emerald-500 transition"
                    >
                      <ThumbsUp size={18} />
                      <span>{post.like_count || 0}</span>
                    </button>
                    <button
                      onClick={() => toggleComments(post.id)}
                      className="flex items-center space-x-1 hover:text-emerald-500 transition"
                    >
                      <MessageCircle size={18} />
                      <span>{post.comment_count || 0}</span>
                    </button>
                  </div>
                </div>

                {/* 评论区 */}
                {expandedComments[post.id] && (
                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-bold text-gray-700 mb-3">评论</h4>
                    
                    {/* 评论列表 */}
                    <div className="space-y-3 mb-4">
                      {comments[post.id]?.map((comment: Comment) => (
                        <div key={comment.id} className="bg-gray-50 rounded-lg p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-sm text-gray-600 mb-1">
                                {comment.author_id?.substring(0, 8)}...
                              </p>
                              <p className="text-gray-700">{comment.content}</p>
                            </div>
                            {isAuthenticated && str(comment.author_id) === user?.id && (
                              <button
                                onClick={() => handleDeleteComment(post.id, comment.id)}
                                className="text-red-500 hover:text-red-700 text-sm"
                              >
                                删除
                              </button>
                            )}
                          </div>
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(comment.created_at).toLocaleString('zh-CN')}
                          </p>
                        </div>
                      ))}
                    </div>

                    {/* 添加评论 */}
                    {isAuthenticated && (
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          placeholder="写下你的评论..."
                          value={newComment[post.id] || ""}
                          onChange={(e) => setNewComment(prev => ({ ...prev, [post.id]: e.target.value }))}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                        <button
                          onClick={() => handleAddComment(post.id)}
                          className="bg-[#2ab26a] text-white px-4 py-2 rounded-lg font-semibold hover:bg-[#1f874c] transition"
                        >
                          评论
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-10">还没有人发帖，快来抢占第一个沙发！</p>
          )}
        </div>
      </div>
    </div>
  );
}

function str(id: string | undefined): string {
  return id || "";
}
