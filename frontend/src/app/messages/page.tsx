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
  X,
  Check,
  CheckCheck
} from "lucide-react";

interface User {
  id: string;
  name: string;
  avatar_url?: string;
  email: string;
  role?: string;
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
  message_type?: 'text' | 'image';
}

interface Conversation {
  user_id: string;
  user_name: string;
  user_avatar_url?: string;
  last_message?: Message;
  unread_count: number;
  last_message_time?: string;
}

export default function MessagesPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showMobileList, setShowMobileList] = useState(true);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showImageUpload, setShowImageUpload] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const API_URL = "https://pku-campus-cycle-cycle.onrender.com";

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    loadAllUsers();
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

  const loadAllUsers = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.get(`${API_URL}/users/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // 获取所有用户（包括自己）
      const users = response.data;
      setAllUsers(users);
      
      // 同时加载会话列表
      await fetchConversations();
    } catch (error) {
      console.error("获取用户列表失败:", error);
      setLoading(false);
    }
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

  const fetchMessages = async (userId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.get(`${API_URL}/messages/conversation/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data);
      
      // 标记为已读
      await axios.post(
        `${API_URL}/messages/conversation/${userId}/read-all`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
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
      await loadAllUsers(); // 重新加载用户列表以更新最后消息时间
    } catch (error) {
      console.error("发送消息失败:", error);
    } finally {
      setSending(false);
    }
  };

  const selectUser = (userId: string) => {
    setSelectedConversation(userId);
    setShowMobileList(false);
  };

  const handleEmojiClick = (emoji: string) => {
    setNewMessage(prev => prev + emoji);
    setShowEmojiPicker(false);
  };

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !selectedConversation) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }

    // 验证文件大小（最大 5MB）
    if (file.size > 5 * 1024 * 1024) {
      alert('图片大小不能超过 5MB');
      return;
    }

    setSending(true);
    try {
      const token = localStorage.getItem("access_token");
      const formData = new FormData();
      formData.append('file', file);
      formData.append('receiver_id', selectedConversation);

      // 上传图片到后端
      const response = await axios.post(
        `${API_URL}/messages/upload-image`,
        formData,
        {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const imageUrl = response.data.url;
      
      // 发送图片消息
      await axios.post(
        `${API_URL}/messages/`,
        {
          receiver_id: selectedConversation,
          content: imageUrl,
          message_type: 'image'
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      await fetchMessages(selectedConversation);
      await loadAllUsers();
    } catch (error) {
      console.error("上传图片失败:", error);
      alert("上传图片失败，请重试");
    } finally {
      setSending(false);
      setShowImageUpload(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
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
      await loadAllUsers(); // 重新加载用户列表
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

  const formatTime = (dateString: string | undefined) => {
    if (!dateString) return "";
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

  // 合并所有用户和会话信息
  const getUserList = () => {
    const convMap = new Map(conversations.map(c => [c.user_id, c]));
    
    // 为每个用户创建列表项
    const userList = allUsers.map(u => {
      const conv = convMap.get(u.id);
      return {
        user_id: u.id,
        user_name: u.name || u.email,
        user_avatar_url: u.avatar_url,
        last_message: conv?.last_message,
        unread_count: conv?.unread_count || 0,
        last_message_time: conv?.last_message_time
      };
    });
    
    // 按最后消息时间排序（最新的在前，没有消息的在后）
    userList.sort((a, b) => {
      if (a.last_message_time && b.last_message_time) {
        return new Date(b.last_message_time).getTime() - new Date(a.last_message_time).getTime();
      } else if (a.last_message_time) {
        return -1;
      } else if (b.last_message_time) {
        return 1;
      }
      return 0;
    });
    
    return userList;
  };

  const filteredUserList = getUserList().filter(u =>
    u.user_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedUserData = allUsers.find(u => u.id === selectedConversation);

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
        <button
          onClick={() => router.push("/profile")}
          className="text-gray-600 hover:bg-gray-100 px-4 py-2 rounded-full transition font-medium"
        >
          返回个人中心
        </button>
      </div>

      {/* 主要内容区 - 左右分栏布局 */}
      <div className="flex-1 flex overflow-hidden max-w-7xl mx-auto w-full">
        {/* 左侧：用户列表 */}
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

          {/* 用户列表 */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
              </div>
            ) : filteredUserList.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <MessageSquare size={48} className="mb-4 opacity-20" />
                <p className="text-sm">暂无用户</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {filteredUserList.map((u) => (
                  <div
                    key={u.user_id}
                    onClick={() => selectUser(u.user_id)}
                    className={`p-4 hover:bg-gray-50 cursor-pointer transition relative group ${
                      selectedConversation === u.user_id ? 'bg-purple-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      {/* 头像 */}
                      <div className="relative flex-shrink-0">
                        <img
                          src={u.user_avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(u.user_name)}&background=8b5cf6&color=fff`}
                          alt={u.user_name}
                          className="w-12 h-12 rounded-full object-cover ring-2 ring-gray-100"
                        />
                        {u.unread_count > 0 && (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full border-2 border-white flex items-center justify-center">
                            <span className="text-white text-xs font-bold">{u.unread_count > 9 ? '9+' : u.unread_count}</span>
                          </div>
                        )}
                      </div>

                      {/* 消息内容 */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="font-semibold text-gray-900 truncate">{u.user_name}</h3>
                          {u.last_message_time && (
                            <span className="text-xs text-gray-500 flex-shrink-0">
                              {formatTime(u.last_message_time)}
                            </span>
                          )}
                        </div>
                        {u.last_message ? (
                          <div className="flex items-center justify-between">
                            <p className={`text-sm truncate ${u.unread_count > 0 ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
                              {u.last_message.content}
                            </p>
                            {u.last_message.sender_id === user?.id && (
                              <div className="flex-shrink-0 ml-2">
                                {u.last_message.is_read ? (
                                  <CheckCheck size={16} className="text-blue-500" />
                                ) : (
                                  <Check size={16} className="text-gray-400" />
                                )}
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-400">暂无消息</p>
                        )}
                      </div>
                    </div>

                    {/* 删除按钮（悬停显示，只有有对话时才显示） */}
                    {u.last_message && (
                      <button
                        onClick={(e) => deleteConversation(u.user_id, e)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
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
                    src={selectedUserData?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedUserData?.name || '')}&background=8b5cf6&color=fff`}
                    alt={selectedUserData?.name}
                    className="w-10 h-10 rounded-full object-cover ring-2 ring-purple-100"
                  />
                  <div>
                    <h2 className="font-bold text-gray-900">{selectedUserData?.name || selectedUserData?.email}</h2>
                    <p className="text-xs text-gray-500">在线</p>
                  </div>
                </div>
                {conversations.some(c => c.user_id === selectedConversation) && (
                  <button
                    onClick={(e) => deleteConversation(selectedConversation, e)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition"
                    title="删除对话"
                  >
                    <Trash2 size={20} />
                  </button>
                )}
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
                            {!isMe && msg.sender_id && (
                              <img
                                src={msg.sender_avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(msg.sender_name || 'User')}&background=8b5cf6&color=fff`}
                                alt={msg.sender_name}
                                className="w-8 h-8 rounded-full object-cover ring-2 ring-gray-100"
                              />
                            )}
                            
                            {/* 消息气泡 */}
                            <div className={`group relative`}>
                              {msg.message_type === 'image' ? (
                                <div className={`${isMe ? 'rounded-br-md' : 'rounded-bl-md'}`}>
                                  <img
                                    src={msg.content}
                                    alt="图片消息"
                                    className="max-w-full rounded-lg cursor-pointer hover:opacity-90 transition"
                                    style={{ maxWidth: '300px', maxHeight: '300px' }}
                                    onClick={() => window.open(msg.content, '_blank')}
                                  />
                                </div>
                              ) : (
                                <div
                                  className={`px-4 py-2.5 rounded-2xl shadow-sm ${
                                    isMe
                                      ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-br-md'
                                      : msg.sender_id === null
                                      ? 'bg-yellow-50 text-yellow-900 border border-yellow-200 rounded-bl-md'
                                      : 'bg-white text-gray-900 border border-gray-200 rounded-bl-md'
                                  }`}
                                >
                                  <p className="text-sm leading-relaxed">{msg.content}</p>
                                </div>
                              )}
                              
                              {/* 时间和已读状态 */}
                              <div className={`flex items-center space-x-1 mt-1 text-xs ${isMe ? 'justify-end' : 'justify-start'}`}>
                                <span className={isMe ? 'text-purple-100' : 'text-gray-400'}>
                                  {new Date(msg.created_at).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}
                                </span>
                                {isMe && (
                                  <span>
                                    {msg.is_read ? (
                                      <CheckCheck size={14} className="text-blue-300" />
                                    ) : (
                                      <Check size={14} className="text-purple-200" />
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
                <div className="flex items-end space-x-2 relative">
                  {/* 表情按钮 */}
                  <div className="relative">
                    <button
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                      className="p-2 text-gray-400 hover:text-purple-500 hover:bg-purple-50 rounded-full transition"
                    >
                      <Smile size={20} />
                    </button>
                    
                    {/* 表情选择器 */}
                    {showEmojiPicker && (
                      <div className="absolute bottom-full left-0 mb-2 bg-white rounded-lg shadow-xl border border-gray-200 p-3 z-50 w-72 max-h-64 overflow-y-auto">
                        <div className="grid grid-cols-8 gap-2">
                          {['😀', '😂', '🥰', '😎', '🤔', '👍', '❤️', '🎉', '😊', '🙏', '💪', '🔥', '👏', '😭', '😅', '🤣', '😍', '🥺', '😤', '👋', '🌟', '✨', '🎊', '💯', '✅', '❌', '💡', '📱', '💬', '🎵', '🍕', '🚀'].map((emoji) => (
                            <button
                              key={emoji}
                              onClick={() => handleEmojiClick(emoji)}
                              className="text-2xl hover:bg-gray-100 rounded p-1 transition"
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* 图片按钮 */}
                  <button
                    onClick={handleImageClick}
                    className="p-2 text-gray-400 hover:text-purple-500 hover:bg-purple-50 rounded-full transition"
                  >
                    <Image size={20} />
                  </button>
                  
                  {/* 隐藏的文件输入 */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  
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
                    disabled={sending || (!newMessage.trim() && !showImageUpload)}
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
              <p className="text-lg font-medium">选择一个用户开始聊天</p>
            </div>
          )}
        </div>
      </div>

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
