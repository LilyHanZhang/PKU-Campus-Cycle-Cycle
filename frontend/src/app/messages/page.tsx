"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";
import {
  Search,
  Send,
  Trash2,
  MessageSquare,
  ArrowLeft,
  Image,
  Smile,
  Plus,
  X,
  Check,
  CheckCheck
} from "lucide-react";

interface User {
  id: string;
  name: string;
  avatar_url?: string;
  email: string;
}

interface Message {
  id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  is_read: boolean;
  created_at: string;
  sender_name?: string;
  sender_avatar_url?: string;
}

interface Conversation {
  user_id: string;
  user_name: string;
  user_avatar_url?: string;
  last_message: Message;
  unread_count: number;
  last_message_time: string;
}

export default function MessagesPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showMobileList, setShowMobileList] = useState(true);
  const [showNewMessageModal, setShowNewMessageModal] = useState(false);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const API_URL = "https://pku-campus-cycle-cycle.onrender.com";

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchConversations();
    fetchAllUsers();
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation);
      setShowMobileList(false);
    }
  }, [selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchConversations = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.get(`${API_URL}/messages/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(response.data);
    } catch (error) {
      console.error("获取会话列表失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllUsers = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.get(`${API_URL}/users/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // 过滤掉自己
      const filteredUsers = response.data.filter((u: User) => u.id !== user?.id);
      setAllUsers(filteredUsers);
    } catch (error) {
      console.error("获取用户列表失败:", error);
    }
  };

  const fetchMessages = async (userId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.get(`${API_URL}/messages/conversation/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data);
    } catch (error) {
      console.error("获取消息失败:", error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;

    setSending(true);
    try {
      const token = localStorage.getItem("access_token");
      await axios.post(
        `${API_URL}/messages/`,
        {
          receiver_id: selectedConversation,
          content: newMessage
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setNewMessage("");
      await fetchMessages(selectedConversation);
      await fetchConversations();
    } catch (error) {
      console.error("发送消息失败:", error);
    } finally {
      setSending(false);
    }
  };

  const startNewConversation = async () => {
    if (!selectedUserId) return;
    
    try {
      const token = localStorage.getItem("access_token");
      // 先发送一条消息创建对话
      await axios.post(
        `${API_URL}/messages/`,
        {
          receiver_id: selectedUserId,
          content: "你好！"
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      await fetchConversations();
      setSelectedConversation(selectedUserId);
      setShowNewMessageModal(false);
      setSelectedUserId("");
      setNewMessage("");
    } catch (error) {
      console.error("创建对话失败:", error);
    }
  };

  const deleteConversation = async (userId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("确定要删除与该用户的所有消息吗？")) return;

    try {
      const token = localStorage.getItem("access_token");
      await axios.delete(`${API_URL}/messages/conversation/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(conversations.filter(c => c.user_id !== userId));
      if (selectedConversation === userId) {
        setSelectedConversation(null);
        setMessages([]);
        setShowMobileList(true);
      }
    } catch (error) {
      console.error("删除对话失败:", error);
      alert("删除失败，请重试");
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
    } else if (days === 1) {
      return "昨天";
    } else if (days < 7) {
      return date.toLocaleDateString("zh-CN", { weekday: "long" });
    } else {
      return date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.user_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedUserData = conversations.find(c => c.user_id === selectedConversation);

  if (!isAuthenticated) return null;

  return (
    <div className="h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col">
      {/* 顶部导航栏 */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          {selectedConversation && (
            <button
              onClick={() => setShowMobileList(true)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-full transition"
            >
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
          )}
          <h1 className="text-xl font-bold text-gray-800 flex items-center">
            <MessageSquare className="mr-2 text-purple-500" size={24} />
            我的私信
          </h1>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowNewMessageModal(true)}
            className="flex items-center space-x-1 bg-purple-500 text-white px-4 py-2 rounded-full hover:bg-purple-600 transition text-sm font-medium"
          >
            <Plus size={18} />
            <span className="hidden sm:inline">新建对话</span>
          </button>
          <button
            onClick={() => router.push("/profile")}
            className="text-gray-600 hover:bg-gray-100 px-4 py-2 rounded-full transition font-medium"
          >
            返回个人中心
          </button>
        </div>
      </div>

      {/* 主要内容区 - 左右分栏布局 */}
      <div className="flex-1 flex overflow-hidden max-w-7xl mx-auto w-full">
        {/* 左侧：会话列表 */}
        <div className={`${showMobileList ? 'flex' : 'hidden'} lg:flex w-full lg:w-80 xl:w-96 flex-col bg-white border-r border-gray-200`}>
          {/* 搜索框 */}
          <div className="p-4 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="搜索联系人..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              />
            </div>
          </div>

          {/* 会话列表 */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
              </div>
            ) : filteredConversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <MessageSquare size={48} className="mb-4 opacity-20" />
                <p className="text-sm">暂无会话</p>
                <button
                  onClick={() => setShowNewMessageModal(true)}
                  className="mt-4 text-purple-500 hover:text-purple-600 font-medium"
                >
                  发起新对话
                </button>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {filteredConversations.map((conv) => (
                  <div
                    key={conv.user_id}
                    onClick={() => setSelectedConversation(conv.user_id)}
                    className={`p-4 hover:bg-gray-50 cursor-pointer transition relative group ${
                      selectedConversation === conv.user_id ? 'bg-purple-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      {/* 头像 */}
                      <div className="relative flex-shrink-0">
                        <img
                          src={conv.user_avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(conv.user_name)}&background=8b5cf6&color=fff`}
                          alt={conv.user_name}
                          className="w-12 h-12 rounded-full object-cover ring-2 ring-gray-100"
                        />
                        {conv.unread_count > 0 && (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full border-2 border-white flex items-center justify-center">
                            <span className="text-white text-xs font-bold">{conv.unread_count > 9 ? '9+' : conv.unread_count}</span>
                          </div>
                        )}
                      </div>

                      {/* 消息内容 */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="font-semibold text-gray-900 truncate">{conv.user_name}</h3>
                          <span className="text-xs text-gray-500 flex-shrink-0">
                            {formatTime(conv.last_message_time)}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <p className={`text-sm truncate ${conv.unread_count > 0 ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
                            {conv.last_message.content}
                          </p>
                          {conv.last_message.sender_id === user?.id && (
                            <div className="flex-shrink-0 ml-2">
                              {conv.last_message.is_read ? (
                                <CheckCheck size={16} className="text-blue-500" />
                              ) : (
                                <Check size={16} className="text-gray-400" />
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* 删除按钮（悬停显示） */}
                    <button
                      onClick={(e) => deleteConversation(conv.user_id, e)}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 右侧：聊天窗口 */}
        <div className={`${!showMobileList ? 'flex' : 'hidden'} lg:flex flex-1 flex-col bg-white`}>
          {selectedConversation ? (
            <>
              {/* 聊天头部 */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
                <div className="flex items-center space-x-3">
                  <img
                    src={selectedUserData?.user_avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedUserData?.user_name || '')}&background=8b5cf6&color=fff`}
                    alt={selectedUserData?.user_name}
                    className="w-10 h-10 rounded-full object-cover ring-2 ring-purple-100"
                  />
                  <div>
                    <h2 className="font-bold text-gray-900">{selectedUserData?.user_name}</h2>
                    <p className="text-xs text-gray-500">在线</p>
                  </div>
                </div>
                <button
                  onClick={(e) => selectedConversation && deleteConversation(selectedConversation, e)}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition"
                  title="删除对话"
                >
                  <Trash2 size={20} />
                </button>
              </div>

              {/* 消息列表 */}
              <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-gray-50 to-white">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-400">
                    <MessageSquare size={64} className="mb-4 opacity-20" />
                    <p>暂无消息，发送第一条消息吧！</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((msg) => {
                      const isMe = msg.sender_id === user?.id;
                      return (
                        <div
                          key={msg.id}
                          className={`flex ${isMe ? 'justify-end' : 'justify-start'} animate-fade-in`}
                        >
                          <div className={`flex items-end space-x-2 max-w-[70%] ${isMe ? 'flex-row-reverse space-x-reverse' : ''}`}>
                            {/* 头像 */}
                            {!isMe && (
                              <img
                                src={msg.sender_avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(msg.sender_name || 'User')}&background=8b5cf6&color=fff`}
                                alt={msg.sender_name}
                                className="w-8 h-8 rounded-full object-cover ring-2 ring-gray-100"
                              />
                            )}
                            
                            {/* 消息气泡 */}
                            <div className={`group relative`}>
                              <div
                                className={`px-4 py-2.5 rounded-2xl shadow-sm ${
                                  isMe
                                    ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-br-md'
                                    : 'bg-white text-gray-900 border border-gray-200 rounded-bl-md'
                                }`}
                              >
                                <p className="text-sm leading-relaxed">{msg.content}</p>
                              </div>
                              
                              {/* 时间和已读状态 */}
                              <div className={`flex items-center space-x-1 mt-1 text-xs ${isMe ? 'justify-end' : 'justify-start'}`}>
                                <span className="text-gray-400">
                                  {new Date(msg.created_at).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}
                                </span>
                                {isMe && (
                                  <span>
                                    {msg.is_read ? (
                                      <CheckCheck size={14} className="text-blue-500" />
                                    ) : (
                                      <Check size={14} className="text-gray-400" />
                                    )}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* 输入框 */}
              <div className="p-4 border-t border-gray-200 bg-white">
                <div className="flex items-end space-x-2">
                  <button className="p-2 text-gray-400 hover:text-purple-500 hover:bg-purple-50 rounded-full transition">
                    <Image size={20} />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-purple-500 hover:bg-purple-50 rounded-full transition">
                    <Smile size={20} />
                  </button>
                  <div className="flex-1 relative">
                    <textarea
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          sendMessage();
                        }
                      }}
                      placeholder="输入消息..."
                      rows={1}
                      className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition max-h-32"
                      style={{ minHeight: '44px' }}
                    />
                  </div>
                  <button
                    onClick={sendMessage}
                    disabled={sending || !newMessage.trim()}
                    className="p-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-full hover:from-purple-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:scale-105 active:scale-95"
                  >
                    {sending ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    ) : (
                      <Send size={20} />
                    )}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageSquare size={80} className="mb-4 opacity-20" />
              <p className="text-lg font-medium">选择一个对话开始聊天</p>
            </div>
          )}
        </div>
      </div>

      {/* 新建对话弹窗 */}
      {showNewMessageModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">新建对话</h2>
              <button
                onClick={() => setShowNewMessageModal(false)}
                className="text-gray-400 hover:text-gray-600 p-2 hover:bg-gray-100 rounded-full transition"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  选择用户
                </label>
                <select
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">请选择一个用户</option>
                  {allUsers.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name || u.email} ({u.role === 'ADMIN' || u.role === 'SUPER_ADMIN' ? '管理员' : '用户'})
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowNewMessageModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                >
                  取消
                </button>
                <button
                  onClick={startNewConversation}
                  disabled={!selectedUserId}
                  className="flex-1 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
                >
                  开始对话
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 自定义动画样式 */}
      <style jsx global>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
