"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { User, Bike, Calendar, LogOut, Shield, MessageSquare, Send, Bookmark } from "lucide-react";

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
  created_at: string;
  hashtags: string[];
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const [myBikes, setMyBikes] = useState([]);
  const [myAppointments, setMyAppointments] = useState([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showMessages, setShowMessages] = useState(false);
  const [newMessage, setNewMessage] = useState("");
  const [selectedReceiver, setSelectedReceiver] = useState("");
  const [allUsers, setAllUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [myBookmarks, setMyBookmarks] = useState<Post[]>([]);
  const [activeTab, setActiveTab] = useState<'bikes' | 'appointments' | 'bookmarks'>('bikes');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (user) {
      fetchData();
      fetchMessages();
      fetchUsers();
      fetchBookmarks();
    }
  }, [user]);

  const fetchBookmarks = async () => {
    if (!user) return;
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const { data } = await axios.get(`${API_URL}/posts/bookmarks/my`, { headers });
      setMyBookmarks(data);
    } catch (error) {
      console.error("Failed to fetch bookmarks", error);
    }
  };

  const fetchData = async () => {
    if (!user) return;
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [bikesRes, appointmentsRes] = await Promise.all([
        axios.get(`${API_URL}/bicycles/`, { headers }),
        axios.get(`${API_URL}/appointments/user/${user.id}`, { headers }),
      ]);

      setMyBikes(bikesRes.data.filter((b: any) => b.owner_id === user.id));
      setMyAppointments(appointmentsRes.data);
    } catch (error) {
      console.error("Failed to fetch profile data", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async () => {
    if (!user) return;
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [messagesRes, unreadRes] = await Promise.all([
        axios.get(`${API_URL}/messages/`, { headers }),
        axios.get(`${API_URL}/messages/unread`, { headers }),
      ]);

      setMessages(messagesRes.data);
      setUnreadCount(unreadRes.data);
    } catch (error) {
      console.error("Failed to fetch messages", error);
    }
  };

  const fetchUsers = async () => {
    if (!user) return;
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const usersRes = await axios.get(`${API_URL}/users/`, { headers });
      setAllUsers(usersRes.data);
    } catch (error) {
      console.error("Failed to fetch users", error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedReceiver) return;

    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      await axios.post(`${API_URL}/messages/`, {
        receiver_id: selectedReceiver,
        content: newMessage
      }, { headers });

      setNewMessage("");
      setSelectedReceiver("");
      fetchMessages();
      alert("消息发送成功！");
    } catch (error) {
      console.error("Failed to send message", error);
      alert("发送失败，请重试");
    }
  };

  const markMessageAsRead = async (messageId: string) => {
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      await axios.put(`${API_URL}/messages/${messageId}/read`, {}, { headers });
      fetchMessages();
    } catch (error) {
      console.error("Failed to mark as read", error);
    }
  };

  const markAllAsRead = async () => {
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      await axios.put(`${API_URL}/messages/read-all`, {}, { headers });
      fetchMessages();
      alert("已标记所有消息为已读");
    } catch (error) {
      console.error("Failed to mark all as read", error);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (authLoading || !user) {
    return <div className="min-h-screen bg-green-50 flex items-center justify-center"><p>加载个人信息中...</p></div>;
  }

  return (
    <div className="min-h-screen bg-green-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-12">
          <h1 className="text-4xl font-extrabold text-[#1f874c]">个人中心</h1>
          <div className="flex items-center space-x-4">
            <Link href="/my-time-slots" className="text-emerald-600 font-bold hover:underline flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              时间段选择
            </Link>
            <Link href="/" className="text-emerald-600 font-bold hover:underline">返回首页</Link>
            <button onClick={handleLogout} className="flex items-center space-x-2 text-red-500 hover:text-red-600">
              <LogOut size={18} />
              <span>退出登录</span>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border-t-4 border-[#2ab26a]">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="bg-green-100 p-4 rounded-full">
                <User size={48} className="text-[#1f874c]" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-800">{user.name || "未设置姓名"}</h2>
                <p className="text-gray-500">{user.email}</p>
                <div className="flex items-center mt-2 space-x-2">
                  <Shield size={16} className={user.role === "SUPER_ADMIN" ? "text-purple-500" : user.role === "ADMIN" ? "text-blue-500" : "text-gray-500"} />
                  <span className={`text-sm font-bold px-3 py-1 rounded-full ${
                    user.role === "SUPER_ADMIN" ? "bg-purple-100 text-purple-700" :
                    user.role === "ADMIN" ? "bg-blue-100 text-blue-700" :
                    "bg-gray-100 text-gray-700"
                  }`}>
                    {user.role === "SUPER_ADMIN" ? "主负责人" : user.role === "ADMIN" ? "管理员" : "普通用户"}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowMessages(!showMessages)}
              className="relative flex items-center space-x-2 bg-emerald-500 text-white px-4 py-2 rounded-full hover:bg-emerald-600 transition"
            >
              <MessageSquare size={20} />
              <span>私信</span>
              {unreadCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* 私信模块 */}
        {showMessages && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border-t-4 border-purple-400">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                <MessageSquare className="mr-3 text-purple-500"/>
                我的私信
              </h2>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="flex items-center space-x-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition font-bold"
                >
                  <span>✓ 一键已读</span>
                  <span className="bg-white text-purple-500 px-2 py-1 rounded-full text-sm">
                    {unreadCount}
                  </span>
                </button>
              )}
            </div>
            
            {/* 发送新消息 */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-bold text-gray-700 mb-3">发送新消息</h3>
              <div className="space-y-3">
                <select
                  value={selectedReceiver}
                  onChange={(e) => setSelectedReceiver(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="">选择接收者</option>
                  {allUsers.filter((u: any) => u.id !== user.id).map((u: any) => (
                    <option key={u.id} value={u.id}>
                      {u.name || u.email} ({u.role === 'ADMIN' || u.role === 'SUPER_ADMIN' ? '管理员' : '用户'})
                    </option>
                  ))}
                </select>
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="输入消息内容..."
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  rows={3}
                />
                <button
                  onClick={sendMessage}
                  className="flex items-center space-x-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition"
                >
                  <Send size={18} />
                  <span>发送消息</span>
                </button>
              </div>
            </div>

            {/* 消息列表 */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {messages.length > 0 ? (
                messages.map((msg: any) => (
                  <div
                    key={msg.id}
                    onClick={() => !msg.is_read && markMessageAsRead(msg.id)}
                    className={`p-4 rounded-lg border-l-4 ${
                      msg.is_read ? 'bg-gray-50 border-gray-300' : 'bg-blue-50 border-blue-500'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-sm text-gray-600 mb-1">
                          {msg.sender_id === user.id ? '发送给' : '来自'}: {
                            allUsers.find((u: any) => u.id === (msg.sender_id === user.id ? msg.receiver_id : msg.sender_id))?.name || '用户'
                          }
                        </p>
                        <p className="text-gray-800">{msg.content}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(msg.created_at).toLocaleString('zh-CN')}
                        </p>
                      </div>
                      {!msg.is_read && msg.receiver_id === user.id && (
                        <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                          未读
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">暂无私信</p>
              )}
            </div>
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border-t-4 border-emerald-400">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center"><Bike className="mr-3 text-emerald-500"/>我的内容</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('bikes')}
                className={`px-4 py-2 rounded-full font-semibold transition ${
                  activeTab === 'bikes' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                我的发布
              </button>
              <button
                onClick={() => setActiveTab('appointments')}
                className={`px-4 py-2 rounded-full font-semibold transition ${
                  activeTab === 'appointments' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                我的预约
              </button>
              <button
                onClick={() => setActiveTab('bookmarks')}
                className={`px-4 py-2 rounded-full font-semibold transition ${
                  activeTab === 'bookmarks' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                我的收藏
              </button>
            </div>
          </div>

          {/* 我的发布 */}
          {activeTab === 'bikes' && (
            <div className="space-y-4">
              {myBikes.length > 0 ? myBikes.map((bike: any) => (
                <div key={bike.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-bold text-gray-700">{bike.brand}</p>
                    <p className="text-sm text-gray-500">¥{bike.price} | 成色 {bike.condition}/10</p>
                  </div>
                  <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                      bike.status === 'IN_STOCK' ? 'bg-green-100 text-green-700' :
                      bike.status === 'PENDING_APPROVAL' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-200 text-gray-600'
                  }`}>
                    {bike.status === 'PENDING_APPROVAL' ? '等待审核' : bike.status === 'IN_STOCK' ? '已上架' : '已锁定/售出'}
                  </span>
                </div>
              )) : <p className="text-gray-500">您还没有发布过任何自行车。</p>}
            </div>
          )}

          {/* 我的预约 */}
          {activeTab === 'appointments' && (
            <div className="space-y-4">
              {myAppointments.length > 0 ? myAppointments.map((apt: any) => (
                <div key={apt.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-bold text-gray-700">预约车辆 ID: {apt.bicycle_id.substring(0, 8)}...</p>
                    <p className="text-sm text-gray-500">{apt.type === 'drop-off' ? '交车' : '提车'}</p>
                  </div>
                  <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-100 text-blue-700">
                    {apt.status}
                  </span>
                </div>
              )) : <p className="text-gray-500">您还没有任何预约记录。</p>}
            </div>
          )}

          {/* 我的收藏 */}
          {activeTab === 'bookmarks' && (
            <div className="space-y-4">
              {myBookmarks.length > 0 ? myBookmarks.map((post) => (
                <div key={post.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">{post.title}</h3>
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">{post.content}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{post.author_name || `用户${post.author_id?.substring(0, 6)}`}</span>
                        <span>•</span>
                        <span>{new Date(post.created_at).toLocaleDateString('zh-CN')}</span>
                      </div>
                      {post.hashtags && post.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {post.hashtags.map((tag) => (
                            <span key={tag} className="text-emerald-600 text-xs">#{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <Bookmark className="text-amber-500 flex-shrink-0 ml-4" size={20} />
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>👍 {post.like_count}</span>
                    <span>💬 {post.comment_count}</span>
                    <span>🔖 {post.bookmark_count}</span>
                  </div>
                </div>
              )) : <p className="text-gray-500">您还没有收藏任何帖子。</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
