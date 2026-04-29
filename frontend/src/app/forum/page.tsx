"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { 
  ThumbsUp, 
  MessageCircle, 
  Bookmark, 
  Share2, 
  MoreHorizontal,
  Hash,
  Send,
  Image as ImageIcon,
  X
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface Post {
  id: string;
  author_id: string;
  author_name: string;
  author_avatar_url: string;
  title: string;
  content: string;
  like_count: number;
  comment_count: number;
  bookmark_count: number;
  is_bookmarked: boolean;
  created_at: string;
  updated_at: string;
  hashtags: string[];
}

interface Comment {
  id: string;
  author_id: string;
  author_name: string;
  author_avatar_url: string;
  content: string;
  created_at: string;
}

export default function ForumPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState({ title: "", content: "" });
  const [posting, setPosting] = useState(false);
  const [expandedComments, setExpandedComments] = useState<{[key: string]: boolean}>({});
  const [comments, setComments] = useState<{[key: string]: Comment[]}>({});
  const [newComment, setNewComment] = useState<{[key: string]: string}>({});
  const [liking, setLiking] = useState<{[key: string]: boolean}>({});
  const [bookmarking, setBookmarking] = useState<{[key: string]: boolean}>({});
  const [trendingHashtags, setTrendingHashtags] = useState<string[]>([]);
  const [selectedHashtag, setSelectedHashtag] = useState<string | null>(null);

  useEffect(() => {
    fetchPosts();
    fetchTrendingHashtags();
  }, [selectedHashtag]);

  const fetchPosts = async () => {
    try {
      const url = selectedHashtag 
        ? `${API_URL}/posts/?hashtag=${selectedHashtag}`
        : `${API_URL}/posts/`;
      const { data } = await axios.get(url);
      setPosts(data);
    } catch (error) {
      console.error("Failed to fetch posts", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrendingHashtags = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/posts/hashtags/trending`);
      setTrendingHashtags(data);
    } catch (error) {
      console.error("Failed to fetch trending hashtags", error);
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
    if (liking[postId]) return;
    
    setLiking(prev => ({ ...prev, [postId]: true }));
    const token = localStorage.getItem("access_token");
    try {
      const { data } = await axios.post(`${API_URL}/posts/${postId}/likes`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchPosts();
    } catch (error) {
      console.error("Failed to like post", error);
    } finally {
      setLiking(prev => ({ ...prev, [postId]: false }));
    }
  };

  const handleBookmark = async (postId: string) => {
    if (!isAuthenticated) {
      alert("请先登录后再收藏");
      return;
    }
    if (bookmarking[postId]) return;
    
    setBookmarking(prev => ({ ...prev, [postId]: true }));
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(
        `${API_URL}/posts/${postId}/bookmarks`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchPosts();
    } catch (error) {
      console.error("Failed to bookmark post", error);
    } finally {
      setBookmarking(prev => ({ ...prev, [postId]: false }));
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
    if (!confirm("确定要删除这个评论吗？")) return;
    
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

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return "刚刚";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟前`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时前`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}天前`;
    return date.toLocaleDateString('zh-CN');
  };

  const getDefaultAvatar = (userId: string) => {
    const colors = ['1f874c', '2ab26a', '3498db', '9b59b6', 'e74c3c', 'f39c12'];
    const index = userId.charCodeAt(0) % colors.length;
    const color = colors[index];
    return `https://ui-avatars.com/api/?name=User&background=${color}&color=fff&size=128`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-xl font-bold text-[#1f874c] hover:bg-gray-100 px-3 py-2 rounded-full transition">
                燕园易骑
              </Link>
              <h1 className="text-xl font-bold text-gray-900">社区广场</h1>
            </div>
            <Link 
              href="/" 
              className="text-emerald-600 font-semibold hover:bg-emerald-50 px-4 py-2 rounded-full transition"
            >
              返回首页
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto flex">
        {/* 左侧边栏 - 热门话题 */}
        <div className="hidden lg:block w-80 p-4 sticky top-14 h-[calc(100vh-3.5rem)] overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 mb-4">
            <h2 className="font-bold text-xl mb-4 text-gray-900">发布新帖子</h2>
            {isAuthenticated ? (
              <form onSubmit={handlePostSubmit} className="space-y-3">
                <input
                  type="text"
                  placeholder="帖子标题"
                  value={newPost.title}
                  onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                />
                <textarea
                  placeholder="分享你的建议或使用感受... 支持 #话题标签#"
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition resize-none"
                  rows={4}
                />
                <button
                  type="submit"
                  disabled={posting || !newPost.title || !newPost.content}
                  className="w-full bg-[#1f874c] text-white py-3 rounded-full font-bold hover:bg-[#155f35] transition disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  <Send size={18} />
                  <span>{posting ? "发布中..." : "发布"}</span>
                </button>
              </form>
            ) : (
              <div className="text-center py-6">
                <p className="text-gray-600 mb-3">
                  登录后可以发布帖子和参与讨论
                </p>
                <Link 
                  href="/login" 
                  className="inline-block bg-[#1f874c] text-white px-6 py-2 rounded-full font-semibold hover:bg-[#155f35] transition"
                >
                  立即登录
                </Link>
              </div>
            )}
          </div>

          {/* 热门话题 */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
            <h2 className="font-bold text-xl mb-4 text-gray-900 flex items-center">
              <Hash size={20} className="mr-2 text-emerald-600" />
              热门话题
            </h2>
            <div className="space-y-2">
              <button
                onClick={() => setSelectedHashtag(null)}
                className={`w-full text-left px-3 py-2 rounded-lg transition ${
                  !selectedHashtag 
                    ? 'bg-emerald-50 text-emerald-700' 
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <span className="font-medium">全部话题</span>
              </button>
              {trendingHashtags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => setSelectedHashtag(tag === selectedHashtag ? null : tag)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition ${
                    tag === selectedHashtag 
                      ? 'bg-emerald-50 text-emerald-700' 
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <span className="text-emerald-600 mr-1">#</span>
                  <span className="font-medium">{tag}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 中间信息流 */}
        <div className="flex-1 max-w-2xl mx-auto p-4">
          {/* 移动端发布按钮 */}
          {isAuthenticated && (
            <div className="lg:hidden bg-white rounded-2xl shadow-sm border border-gray-200 p-4 mb-4">
              <form onSubmit={handlePostSubmit} className="space-y-3">
                <input
                  type="text"
                  placeholder="帖子标题"
                  value={newPost.title}
                  onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <textarea
                  placeholder="分享你的建议或使用感受..."
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
                  rows={3}
                />
                <button
                  type="submit"
                  disabled={posting || !newPost.title || !newPost.content}
                  className="w-full bg-[#1f874c] text-white py-3 rounded-full font-bold hover:bg-[#155f35] transition disabled:bg-gray-400"
                >
                  {posting ? "发布中..." : "发布"}
                </button>
              </form>
            </div>
          )}

          {/* 帖子列表 */}
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-10">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
                <p className="text-gray-600 mt-2">加载帖子中...</p>
              </div>
            ) : posts.length > 0 ? (
              posts.map(post => (
                <article 
                  key={post.id} 
                  className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
                >
                  {/* 帖子头部 */}
                  <div className="flex items-start space-x-3 mb-3">
                    <img
                      src={post.author_avatar_url || getDefaultAvatar(post.author_id)}
                      alt={post.author_name || '用户'}
                      className="w-12 h-12 rounded-full object-cover border-2 border-gray-100"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-gray-900 truncate">
                          {post.author_name || `用户${post.author_id?.substring(0, 6)}`}
                        </span>
                        <span className="text-gray-500 text-sm">
                          {formatTimeAgo(post.created_at)}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-900 mt-1">{post.title}</h3>
                    </div>
                    {isAuthenticated && post.author_id === user?.id && (
                      <button
                        onClick={() => handleDeletePost(post.id)}
                        className="text-red-500 hover:text-red-700 transition p-2 hover:bg-red-50 rounded-full"
                        title="删除帖子"
                      >
                        <X size={18} />
                      </button>
                    )}
                  </div>

                  {/* 帖子内容 */}
                  <div className="ml-15 pl-15">
                    <p className="text-gray-800 whitespace-pre-wrap mb-3 leading-relaxed">
                      {post.content}
                    </p>

                    {/* 话题标签 */}
                    {post.hashtags && post.hashtags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {post.hashtags.map((tag) => (
                          <button
                            key={tag}
                            onClick={() => setSelectedHashtag(tag)}
                            className="text-emerald-600 hover:bg-emerald-50 px-3 py-1 rounded-full text-sm font-medium transition"
                          >
                            #{tag}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* 互动按钮 */}
                    <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                      <button
                        onClick={() => handleLike(post.id)}
                        disabled={liking[post.id]}
                        className="flex items-center space-x-2 text-gray-600 hover:text-emerald-600 hover:bg-emerald-50 px-4 py-2 rounded-full transition group"
                      >
                        <ThumbsUp 
                          size={18} 
                          className={`transition-transform ${liking[post.id] ? 'animate-pulse' : 'group-hover:scale-110'}`} 
                        />
                        <span className="text-sm font-medium">{post.like_count || 0}</span>
                      </button>
                      
                      <button
                        onClick={() => toggleComments(post.id)}
                        className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-full transition group"
                      >
                        <MessageCircle 
                          size={18}
                          className="group-hover:scale-110 transition-transform" 
                        />
                        <span className="text-sm font-medium">{post.comment_count || 0}</span>
                      </button>
                      
                      <button
                        onClick={() => handleBookmark(post.id)}
                        disabled={bookmarking[post.id]}
                        className="flex items-center space-x-2 text-gray-600 hover:text-amber-600 hover:bg-amber-50 px-4 py-2 rounded-full transition group"
                      >
                        <Bookmark 
                          size={18}
                          className={`transition-transform ${post.is_bookmarked ? 'fill-amber-500 text-amber-500' : 'group-hover:scale-110'}`} 
                        />
                        <span className="text-sm font-medium">{post.bookmark_count || 0}</span>
                      </button>
                      
                      <button className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-4 py-2 rounded-full transition">
                        <Share2 size={18} />
                      </button>
                    </div>

                    {/* 评论区 */}
                    {expandedComments[post.id] && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <h4 className="font-bold text-gray-700 mb-3 flex items-center">
                          <MessageCircle size={18} className="mr-2" />
                          评论 ({post.comment_count || 0})
                        </h4>
                        
                        {/* 评论列表 */}
                        <div className="space-y-3 mb-4">
                          {comments[post.id]?.map((comment: Comment) => (
                            <div 
                              key={comment.id} 
                              className="bg-gray-50 rounded-xl p-3 hover:bg-gray-100 transition"
                            >
                              <div className="flex items-start space-x-3">
                                <img
                                  src={comment.author_avatar_url || getDefaultAvatar(comment.author_id)}
                                  alt={comment.author_name || '用户'}
                                  className="w-8 h-8 rounded-full object-cover"
                                />
                                <div className="flex-1">
                                  <div className="flex items-center justify-between">
                                    <span className="font-semibold text-sm text-gray-900">
                                      {comment.author_name || `用户${comment.author_id?.substring(0, 6)}`}
                                    </span>
                                    <span className="text-xs text-gray-500">
                                      {formatTimeAgo(comment.created_at)}
                                    </span>
                                  </div>
                                  <p className="text-gray-800 text-sm mt-1">{comment.content}</p>
                                  {isAuthenticated && comment.author_id === user?.id && (
                                    <button
                                      onClick={() => handleDeleteComment(post.id, comment.id)}
                                      className="text-red-500 hover:text-red-700 text-xs mt-2"
                                    >
                                      删除
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* 添加评论 */}
                        {isAuthenticated && (
                          <div className="flex items-center space-x-2">
                            <img
                              src={user?.avatar_url || getDefaultAvatar(user?.id || '')}
                              alt={user?.name || '我'}
                              className="w-8 h-8 rounded-full object-cover"
                            />
                            <input
                              type="text"
                              placeholder="写下你的评论..."
                              value={newComment[post.id] || ""}
                              onChange={(e) => setNewComment(prev => ({ ...prev, [post.id]: e.target.value }))}
                              onKeyPress={(e) => e.key === 'Enter' && handleAddComment(post.id)}
                              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                            />
                            <button
                              onClick={() => handleAddComment(post.id)}
                              className="bg-[#1f874c] text-white p-2 rounded-full hover:bg-[#155f35] transition"
                            >
                              <Send size={18} />
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </article>
              ))
            ) : (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10 text-center">
                <div className="text-6xl mb-4">📝</div>
                <p className="text-gray-600 text-lg mb-2">
                  {selectedHashtag 
                    ? `还没有人发布 #${selectedHashtag}# 话题的帖子`
                    : '还没有人发帖，快来抢占第一个沙发！'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* 右侧边栏 - 预留位置 */}
        <div className="hidden xl:block w-80 p-4 sticky top-14 h-[calc(100vh-3.5rem)] overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
            <h2 className="font-bold text-xl mb-4 text-gray-900">关于社区</h2>
            <p className="text-gray-600 text-sm leading-relaxed">
              燕园易骑社区广场是北大师生分享自行车使用体验、交流心得的平台。
              欢迎发布你的故事、建议和使用感受！
            </p>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                请遵守社区规范，文明发言，共同维护良好的交流环境。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
