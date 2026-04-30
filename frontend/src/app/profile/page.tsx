"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { 
  User, 
  Bike, 
  Calendar, 
  LogOut, 
  Shield, 
  MessageSquare, 
  Bookmark,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Bell
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
  created_at: string;
  hashtags: string[];
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const [myBikes, setMyBikes] = useState([]);
  const [myAppointments, setMyAppointments] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [myBookmarks, setMyBookmarks] = useState<Post[]>([]);
  const [activeTab, setActiveTab] = useState<'bikes' | 'appointments' | 'bookmarks'>('bikes');
  const [stats, setStats] = useState({
    totalBikes: 0,
    pendingBikes: 0,
    totalAppointments: 0,
    pendingAppointments: 0,
    completedAppointments: 0
  });

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (user) {
      fetchData();
      fetchMessages();
      fetchBookmarks();
      calculateStats();
    }
  }, [user, myBikes, myAppointments]);

  const calculateStats = () => {
    const totalBikes = myBikes.length;
    const pendingBikes = myBikes.filter((b: any) => 
      b.status === 'PENDING_APPROVAL' || b.status === 'PENDING_SELLER_SLOT_SELECTION'
    ).length;
    
    const totalAppointments = myAppointments.length;
    const pendingAppointments = myAppointments.filter((a: any) => 
      a.status === 'PENDING' && !a.time_slot_id
    ).length;
    const completedAppointments = myAppointments.filter((a: any) => 
      a.status === 'COMPLETED'
    ).length;

    setStats({
      totalBikes,
      pendingBikes,
      totalAppointments,
      pendingAppointments,
      completedAppointments
    });
  };

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
    }
  };

  const fetchMessages = async () => {
    if (!user) return;
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const unreadRes = await axios.get(`${API_URL}/messages/unread`, { headers });
      setUnreadCount(unreadRes.data);
    } catch (error) {
      console.error("Failed to fetch messages", error);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-700 font-medium">加载中...</p>
        </div>
      </div>
    );
  }

  const pendingTimeSlotCount = stats.pendingAppointments;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl p-6 md:p-8 border border-white/20">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h1 className="text-4xl font-black text-gray-900 mb-2">个人中心</h1>
                <p className="text-gray-600">管理您的车辆、预约和消息</p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <Link href="/">
                  <button className="px-6 py-3 bg-white border-2 border-blue-500 text-blue-600 rounded-full font-bold hover:bg-blue-50 transition-all flex items-center">
                    <ArrowRight className="w-5 h-5 mr-2 rotate-180" />
                    返回首页
                  </button>
                </Link>
                <button 
                  onClick={handleLogout}
                  className="px-6 py-3 bg-red-500 text-white rounded-full font-bold hover:bg-red-600 transition-all flex items-center shadow-lg"
                >
                  <LogOut className="w-5 h-5 mr-2" />
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Quick Actions Bar */}
        <section className="mb-8">
          <div className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-3xl shadow-xl p-6 md:p-8 text-white">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <div className="bg-white/20 backdrop-blur-sm p-4 rounded-2xl">
                  <Sparkles className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-black mb-1">快捷操作</h2>
                  <p className="text-blue-100">快速访问常用功能</p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Time Slot Selection */}
              <Link href="/my-time-slots">
                <div className="group bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-2xl p-6 transition-all hover:scale-105 cursor-pointer">
                  <div className="flex items-center justify-between mb-3">
                    <div className="bg-white/30 p-3 rounded-xl">
                      <Clock className="w-6 h-6" />
                    </div>
                    {pendingTimeSlotCount > 0 && (
                      <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {pendingTimeSlotCount}
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-lg mb-1">时间段选择</h3>
                  <p className="text-blue-100 text-sm">选择交易时间</p>
                  <div className="mt-3 flex items-center text-sm font-bold">
                    立即选择 <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>

              {/* Messages */}
              <Link href="/messages">
                <div className="group bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-2xl p-6 transition-all hover:scale-105 cursor-pointer relative">
                  <div className="flex items-center justify-between mb-3">
                    <div className="bg-white/30 p-3 rounded-xl">
                      <MessageSquare className="w-6 h-6" />
                    </div>
                    {unreadCount > 0 && (
                      <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full absolute top-3 right-3">
                        {unreadCount}
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-lg mb-1">私信</h3>
                  <p className="text-blue-100 text-sm">查看消息</p>
                  <div className="mt-3 flex items-center text-sm font-bold">
                    查看消息 <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>

              {/* My Bikes */}
              <Link href="/profile?tab=bikes">
                <div 
                  onClick={() => setActiveTab('bikes')}
                  className="group bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-2xl p-6 transition-all hover:scale-105 cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="bg-white/30 p-3 rounded-xl">
                      <Bike className="w-6 h-6" />
                    </div>
                    {stats.pendingBikes > 0 && (
                      <span className="bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {stats.pendingBikes}
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-lg mb-1">我的车辆</h3>
                  <p className="text-blue-100 text-sm">共 {stats.totalBikes} 辆</p>
                  <div className="mt-3 flex items-center text-sm font-bold">
                    查看详情 <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>

              {/* My Appointments */}
              <Link href="/profile?tab=appointments">
                <div 
                  onClick={() => setActiveTab('appointments')}
                  className="group bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-2xl p-6 transition-all hover:scale-105 cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="bg-white/30 p-3 rounded-xl">
                      <Calendar className="w-6 h-6" />
                    </div>
                    {pendingTimeSlotCount > 0 && (
                      <span className="bg-purple-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {pendingTimeSlotCount}
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-lg mb-1">我的预约</h3>
                  <p className="text-blue-100 text-sm">共 {stats.totalAppointments} 个</p>
                  <div className="mt-3 flex items-center text-sm font-bold">
                    查看详情 <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </section>

        {/* Stats Cards */}
        <section className="mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-3">
                <div className="bg-gradient-to-br from-emerald-500 to-green-500 p-3 rounded-xl">
                  <Bike className="w-6 h-6 text-white" />
                </div>
                <TrendingUp className="w-5 h-5 text-emerald-600" />
              </div>
              <p className="text-gray-600 text-sm font-medium mb-1">我的车辆</p>
              <p className="text-3xl font-black text-gray-900">{stats.totalBikes}</p>
              <p className="text-xs text-gray-500 mt-2">{stats.pendingBikes} 辆待处理</p>
            </div>

            <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-3">
                <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-3 rounded-xl">
                  <Calendar className="w-6 h-6 text-white" />
                </div>
                <Clock className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-gray-600 text-sm font-medium mb-1">我的预约</p>
              <p className="text-3xl font-black text-gray-900">{stats.totalAppointments}</p>
              <p className="text-xs text-gray-500 mt-2">{pendingTimeSlotCount} 个待选择</p>
            </div>

            <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-3">
                <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-xl">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <Bell className="w-5 h-5 text-purple-600" />
              </div>
              <p className="text-gray-600 text-sm font-medium mb-1">未读消息</p>
              <p className="text-3xl font-black text-gray-900">{unreadCount}</p>
              <p className="text-xs text-gray-500 mt-2">及时查看</p>
            </div>

            <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-3">
                <div className="bg-gradient-to-br from-orange-500 to-red-500 p-3 rounded-xl">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
                <TrendingUp className="w-5 h-5 text-orange-600" />
              </div>
              <p className="text-gray-600 text-sm font-medium mb-1">已完成预约</p>
              <p className="text-3xl font-black text-gray-900">{stats.completedAppointments}</p>
              <p className="text-xs text-gray-500 mt-2">交易成功</p>
            </div>
          </div>
        </section>

        {/* User Info Card */}
        <section className="mb-8">
          <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl overflow-hidden border border-white/20">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-white/20 backdrop-blur-sm p-4 rounded-2xl">
                    <User className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-1">{user.name || "未设置姓名"}</h2>
                    <p className="text-blue-100">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                  <Shield size={20} className={user.role === "SUPER_ADMIN" ? "text-purple-300" : user.role === "ADMIN" ? "text-blue-300" : "text-gray-300"} />
                  <span className={`text-sm font-bold ${
                    user.role === "SUPER_ADMIN" ? "text-purple-200" :
                    user.role === "ADMIN" ? "text-blue-200" :
                    "text-gray-200"
                  }`}>
                    {user.role === "SUPER_ADMIN" ? "主负责人" : user.role === "ADMIN" ? "管理员" : "普通用户"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Content Tabs */}
        <section>
          <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl border border-white/20 overflow-hidden">
            {/* Tab Headers */}
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setActiveTab('bikes')}
                className={`flex-1 px-6 py-4 font-bold transition-all flex items-center justify-center ${
                  activeTab === 'bikes'
                    ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Bike className="w-5 h-5 mr-2" />
                我的车辆
                {stats.pendingBikes > 0 && (
                  <span className="ml-2 bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {stats.pendingBikes}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('appointments')}
                className={`flex-1 px-6 py-4 font-bold transition-all flex items-center justify-center ${
                  activeTab === 'appointments'
                    ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Calendar className="w-5 h-5 mr-2" />
                我的预约
                {pendingTimeSlotCount > 0 && (
                  <span className="ml-2 bg-purple-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {pendingTimeSlotCount}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('bookmarks')}
                className={`flex-1 px-6 py-4 font-bold transition-all flex items-center justify-center ${
                  activeTab === 'bookmarks'
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Bookmark className="w-5 h-5 mr-2" />
                我的收藏
                {myBookmarks.length > 0 && (
                  <span className="ml-2 bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {myBookmarks.length}
                  </span>
                )}
              </button>
            </div>

            {/* Tab Content */}
            <div className="p-6 md:p-8">
              {/* Bikes Tab */}
              {activeTab === 'bikes' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                    <Bike className="w-6 h-6 mr-2 text-emerald-600" />
                    我的车辆
                  </h3>
                  {myBikes.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="bg-gradient-to-br from-gray-100 to-gray-200 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Bike className="w-10 h-10 text-gray-400" />
                      </div>
                      <p className="text-gray-600 font-medium mb-4">暂无车辆</p>
                      <Link href="/bicycles/new">
                        <button className="bg-gradient-to-r from-emerald-500 to-green-500 text-white px-6 py-3 rounded-full font-bold hover:shadow-lg transition-all">
                          登记第一辆车
                        </button>
                      </Link>
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {myBikes.map((bike: any) => (
                        <div key={bike.id} className="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-bold text-lg text-gray-900 mb-2">
                                {bike.brand} - {bike.color}
                              </h4>
                              <p className="text-sm text-gray-600 mb-2">
                                状态：<span className="font-bold">
                                  {bike.status === 'PENDING_APPROVAL' ? '待审核' :
                                   bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? '待选择时间段' :
                                   bike.status === 'AVAILABLE' ? '可售' :
                                   bike.status === 'SOLD' ? '已售' : bike.status}
                                </span>
                              </p>
                              <p className="text-sm text-gray-500">
                                登记时间：{new Date(bike.created_at).toLocaleDateString('zh-CN')}
                              </p>
                            </div>
                            <Link href={`/bicycles/${bike.id}`}>
                              <button className="px-4 py-2 bg-emerald-500 text-white rounded-full font-bold hover:bg-emerald-600 transition-all">
                                查看详情
                              </button>
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Appointments Tab */}
              {activeTab === 'appointments' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                    <Calendar className="w-6 h-6 mr-2 text-blue-600" />
                    我的预约
                  </h3>
                  {myAppointments.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="bg-gradient-to-br from-gray-100 to-gray-200 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Calendar className="w-10 h-10 text-gray-400" />
                      </div>
                      <p className="text-gray-600 font-medium mb-4">暂无预约</p>
                      <Link href="/bicycles">
                        <button className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-full font-bold hover:shadow-lg transition-all">
                          浏览车辆
                        </button>
                      </Link>
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {myAppointments.map((apt: any) => (
                        <div key={apt.id} className="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="flex items-center space-x-3 mb-2">
                                <h4 className="font-bold text-lg text-gray-900">
                                  预约 {apt.id.slice(0, 8)}...
                                </h4>
                                <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                                  apt.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                  apt.status === 'CONFIRMED' ? 'bg-blue-100 text-blue-700' :
                                  apt.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {apt.status === 'PENDING' ? '待处理' :
                                   apt.status === 'CONFIRMED' ? '已确认' :
                                   apt.status === 'COMPLETED' ? '已完成' : apt.status}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mb-1">
                                类型：{apt.type === 'pick-up' ? '🚴 自提' : '📦 送货'}
                              </p>
                              {!apt.time_slot_id && apt.status === 'PENDING' && (
                                <div className="mt-3 flex items-center text-sm text-orange-600 font-bold bg-orange-50 px-3 py-2 rounded-lg">
                                  <AlertCircle className="w-4 h-4 mr-2" />
                                  待选择时间段
                                </div>
                              )}
                            </div>
                            <Link href={`/appointments/${apt.id}`}>
                              <button className="px-4 py-2 bg-blue-500 text-white rounded-full font-bold hover:bg-blue-600 transition-all">
                                查看详情
                              </button>
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Bookmarks Tab */}
              {activeTab === 'bookmarks' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                    <Bookmark className="w-6 h-6 mr-2 text-purple-600" />
                    我的收藏
                  </h3>
                  {myBookmarks.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="bg-gradient-to-br from-gray-100 to-gray-200 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Bookmark className="w-10 h-10 text-gray-400" />
                      </div>
                      <p className="text-gray-600 font-medium mb-4">暂无收藏</p>
                      <Link href="/posts">
                        <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-full font-bold hover:shadow-lg transition-all">
                          浏览帖子
                        </button>
                      </Link>
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {myBookmarks.map((post: any) => (
                        <div key={post.id} className="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all">
                          <h4 className="font-bold text-lg text-gray-900 mb-2">{post.title}</h4>
                          <p className="text-sm text-gray-600 mb-2 line-clamp-2">{post.content}</p>
                          <div className="flex items-center justify-between">
                            <p className="text-xs text-gray-500">
                              {new Date(post.created_at).toLocaleDateString('zh-CN')}
                            </p>
                            <Link href={`/posts/${post.id}`}>
                              <button className="px-4 py-2 bg-purple-500 text-white rounded-full text-sm font-bold hover:bg-purple-600 transition-all">
                                查看详情
                              </button>
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
