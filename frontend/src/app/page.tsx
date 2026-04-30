"use client";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { 
  LogOut, 
  Clock, 
  AlertCircle, 
  MessageCircle,
  BookOpen,
  X,
  CheckCircle,
  ArrowRight,
  Bike,
  ShoppingCart,
  HelpCircle,
  User,
  Calendar,
  MessageSquare,
  Bookmark,
  Shield
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState({
    total_bicycles: 0,
    sold_bicycles: 0,
    in_stock_bicycles: 0,
    total_users: 0
  });
  const [countdowns, setCountdowns] = useState([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [unreadMessageCount, setUnreadMessageCount] = useState(0);
  const [showGuide, setShowGuide] = useState(false);

  useEffect(() => {
    // 获取统计数据
    axios.get(`${API_URL}/bicycles/stats/summary`)
      .then(response => {
        setStats(response.data);
      })
      .catch(error => {
        console.error("Failed to fetch stats", error);
      });
  }, []);

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchCountdown();
      fetchUnreadMessages();
      const interval = setInterval(fetchCountdown, 1000);
      const messageInterval = setInterval(fetchUnreadMessages, 5000);
      return () => {
        clearInterval(interval);
        clearInterval(messageInterval);
      };
    }
  }, [isAuthenticated, user]);

  const fetchCountdown = async () => {
    if (!isAuthenticated) return;
    const token = localStorage.getItem("access_token");
    try {
      const response = await axios.get(`${API_URL}/time_slots/my/countdown`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCountdowns(response.data.countdowns || []);
      setPendingCount(response.data.pending_count || 0);
    } catch (error) {
      console.error("Failed to fetch countdown", error);
    }
  };

  const fetchUnreadMessages = async () => {
    if (!isAuthenticated) return;
    const token = localStorage.getItem("access_token");
    try {
      const response = await axios.get(`${API_URL}/messages/unread`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUnreadMessageCount(response.data || 0);
    } catch (error) {
      console.error("Failed to fetch unread messages", error);
    }
  };

  const formatTimeLeft = (seconds: number) => {
    if (seconds <= 0) return "已过期";
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden" 
         style={{
           backgroundImage: `url('https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop')`,
           backgroundSize: 'cover',
           backgroundPosition: 'center',
           backgroundAttachment: 'fixed'
         }}>
      {/* Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-50/95 via-white/90 to-emerald-50/95 backdrop-blur-sm"></div>
      
      {/* Content */}
      <div className="relative z-10 flex flex-col">
        {/* Header */}
        <header className="w-full bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-md">
                    <Bike size={20} className="text-white" />
                  </div>
                  <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-green-600">
                    燕园易骑
                  </h1>
                </div>
              
              <div className="flex items-center space-x-4">
                <Link
                  href="/forum"
                  className="hidden sm:flex items-center text-gray-600 hover:text-emerald-600 font-medium transition"
                >
                  社区广场
                </Link>
                {isAuthenticated ? (
                  <>
                    {(user?.role === "ADMIN" || user?.role === "SUPER_ADMIN") && (
                      <Link
                        href="/admin"
                        className="hidden sm:flex items-center text-gray-600 hover:text-emerald-600 font-medium transition"
                      >
                        管理后台
                      </Link>
                    )}
                    <Link href="/profile">
                      <div className="flex items-center space-x-2 text-gray-700 hover:text-emerald-700 cursor-pointer relative">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white font-bold text-sm">
                          {user?.name?.charAt(0).toUpperCase() || user?.email.charAt(0).toUpperCase()}
                        </div>
                        <span className="hidden sm:inline font-medium">{user?.name || "个人中心"}</span>
                        {unreadMessageCount > 0 && (
                          <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
                            {unreadMessageCount > 9 ? '9+' : unreadMessageCount}
                          </div>
                        )}
                      </div>
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 text-red-500 hover:text-red-600 font-medium transition"
                    >
                      <LogOut size={18} />
                      <span className="hidden sm:inline font-medium">退出</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="text-gray-600 hover:text-emerald-600 font-medium transition"
                    >
                      登录
                    </Link>
                    <Link
                      href="/register"
                      className="bg-gradient-to-r from-emerald-500 to-green-600 text-white px-5 py-2 rounded-full font-semibold hover:shadow-lg hover:-translate-y-0.5 transition-all"
                    >
                      注册
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
          {/* Hero Section with Guide Button */}
          <section className="text-center mb-12">
            <h2 className="text-5xl md:text-6xl font-black text-gray-900 mb-4 tracking-tight">
              让爱传递，让资源循环
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              北大校园自行车循环计划，连接毕业生与新生，促进绿色环保
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/bicycles/new">
                <button className="w-full sm:w-auto bg-gradient-to-r from-emerald-500 to-green-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center">
                  <Bike size={24} className="mr-2" />
                  一键登记车辆
                </button>
              </Link>
              <Link href="/bicycles">
                <button className="w-full sm:w-auto bg-white text-emerald-600 border-2 border-emerald-500 px-8 py-4 rounded-full font-bold text-lg hover:bg-emerald-50 hover:-translate-y-1 transition-all flex items-center justify-center">
                  <ShoppingCart size={24} className="mr-2" />
                  浏览库存
                </button>
              </Link>
              <button
                onClick={() => setShowGuide(true)}
                className="w-full sm:w-auto bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-8 py-4 rounded-full font-bold text-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center"
              >
                <BookOpen size={24} className="mr-2" />
                使用说明
              </button>
            </div>
          </section>

          {/* Countdown Module */}
          {isAuthenticated && (countdowns.length > 0 || pendingCount > 0) && (
            <section className="w-full mb-8">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-3xl p-8 shadow-2xl">
                <h2 className="text-2xl font-black mb-6 flex items-center">
                  <Clock className="mr-3" size={28} />
                  交易倒计时
                </h2>
                {countdowns.length > 0 ? (
                  <div className="space-y-4">
                    {countdowns.map((cd: any) => (
                      <div key={cd.appointment_id} className="bg-white/20 backdrop-blur-sm rounded-2xl p-5">
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-bold text-sm mb-1">
                              {cd.type === 'drop-off' ? '🚲 交车预约' : '🔎 提车预约'}
                            </p>
                            <p className="text-xs text-blue-100 mb-1">
                              车辆 ID: {cd.bicycle_id.substring(0, 8)}...
                            </p>
                            <p className="text-xs text-blue-100">
                              {new Date(cd.start_time).toLocaleString('zh-CN')}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-4xl font-mono font-bold">
                              {formatTimeLeft(cd.time_left_seconds)}
                            </p>
                            <p className={`text-xs ${cd.status === 'overdue' ? 'text-red-200' : 'text-green-200'}`}>
                              {cd.status === 'overdue' ? '已过期' : '剩余时间'}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : pendingCount > 0 ? (
                  <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-5 flex items-center">
                    <AlertCircle className="mr-4 text-yellow-300" size={32} />
                    <div>
                      <p className="font-bold text-lg">您有 {pendingCount} 笔待确认的交易</p>
                      <p className="text-sm text-blue-100">请等待管理员审核并提供可选时间段</p>
                    </div>
                  </div>
                ) : null}
              </div>
            </section>
          )}

          {/* Messages Module */}
          {isAuthenticated && unreadMessageCount > 0 && (
            <section className="w-full mb-8">
              <div 
                className="bg-gradient-to-r from-emerald-500 to-green-500 text-white rounded-3xl p-8 shadow-2xl cursor-pointer hover:shadow-3xl transition-all hover:-translate-y-1"
                onClick={() => router.push('/profile')}
              >
                <h2 className="text-2xl font-black mb-6 flex items-center">
                  <MessageCircle className="mr-3" size={28} />
                  您有新的消息
                </h2>
                <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-5 flex items-center">
                  <div className="text-5xl font-bold mr-5 animate-bounce">📩</div>
                  <div className="flex-1">
                    <p className="font-bold text-lg">您有 {unreadMessageCount} 条未读消息</p>
                    <p className="text-sm text-green-100">点击查看管理员通知和交易提醒</p>
                  </div>
                  <ArrowRight size={40} className="ml-4" />
                </div>
              </div>
            </section>
          )}

          {/* Main Action Cards */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="bg-white rounded-3xl shadow-xl p-8 hover:shadow-2xl transition-all hover:-translate-y-2 cursor-pointer border-t-4 border-emerald-500">
              <div className="flex items-center space-x-4 mb-4">
                <div className="bg-gradient-to-br from-emerald-100 to-green-100 p-5 rounded-2xl">
                  <Bike size={40} className="text-emerald-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-800">我要出车 / 捐赠</h2>
              </div>
              <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                即将离校？将不再使用的自行车交由新生，减少资源浪费，传递绿色环保理念。
              </p>
              <Link href="/bicycles/new">
                <button className="w-full bg-gradient-to-r from-emerald-500 to-green-600 text-white py-4 rounded-full font-bold text-lg hover:shadow-lg hover:-translate-y-1 transition-all">
                  一键登记车辆
                </button>
              </Link>
            </div>

            <div className="bg-white rounded-3xl shadow-xl p-8 hover:shadow-2xl transition-all hover:-translate-y-2 cursor-pointer border-t-4 border-cyan-500">
              <div className="flex items-center space-x-4 mb-4">
                <div className="bg-gradient-to-br from-cyan-100 to-blue-100 p-5 rounded-2xl">
                  <ShoppingCart size={40} className="text-cyan-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-800">寻找座驾</h2>
              </div>
              <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                新生报道缺少座驾？在这里寻找高性价比、经过核验的二手自行车，省钱又省心。
              </p>
              <Link href="/bicycles">
                <button className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 rounded-full font-bold text-lg hover:shadow-lg hover:-translate-y-1 transition-all">
                  浏览目前库存
                </button>
              </Link>
            </div>
          </section>

          {/* Stats Section */}
          <section className="bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-3xl p-10 shadow-2xl mb-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div>
                <p className="text-6xl font-black mb-3">{stats.sold_bicycles}</p>
                <p className="text-green-100 font-medium text-lg">成功回收爱车</p>
              </div>
              <div>
                <p className="text-6xl font-black mb-3">{stats.total_bicycles}</p>
                <p className="text-green-100 font-medium text-lg">平台车辆总数</p>
              </div>
              <div>
                <p className="text-6xl font-black mb-3">{stats.total_users}</p>
                <p className="text-green-100 font-medium text-lg">注册用户</p>
              </div>
            </div>
          </section>

          {/* Values Section */}
          <section className="bg-white rounded-3xl shadow-xl p-10 mb-12">
            <h2 className="text-4xl font-black text-gray-800 mb-8 text-center">♻️ 让爱传递，让资源循环</h2>
            <p className="text-lg text-gray-600 text-center mb-10 max-w-3xl mx-auto leading-relaxed">
              北大校园自行车循环计划致力于减少资源浪费，促进绿色环保。
              每辆回收的自行车都承载着毕业生的美好回忆，也将为新生提供便捷的校园出行体验。
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div className="p-6 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50">
                <div className="text-5xl mb-4">🌱</div>
                <h3 className="font-bold text-xl mb-2 text-gray-900">绿色环保</h3>
                <p className="text-gray-600">减少废旧金属污染</p>
              </div>
              <div className="p-6 rounded-2xl bg-gradient-to-br from-pink-50 to-rose-50">
                <div className="text-5xl mb-4">💚</div>
                <h3 className="font-bold text-xl mb-2 text-gray-900">爱心传递</h3>
                <p className="text-gray-600">毕业生与新生互助</p>
              </div>
              <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50">
                <div className="text-5xl mb-4">🔄</div>
                <h3 className="font-bold text-xl mb-2 text-gray-900">资源循环</h3>
                <p className="text-gray-600">提高资源利用效率</p>
              </div>
            </div>
          </section>

          {/* Quick Guide Section */}
          <section className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-3xl shadow-xl p-10 mb-12">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-4xl font-black text-gray-800 flex items-center">
                <HelpCircle size={40} className="mr-4 text-blue-600" />
                快速指南
              </h2>
              <button
                onClick={() => setShowGuide(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-full font-bold hover:bg-blue-700 transition-all flex items-center"
              >
                查看详细
                <ArrowRight size={20} className="ml-2" />
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-6 shadow-md">
                <h3 className="font-bold text-xl text-emerald-600 mb-3 flex items-center">
                  <Bike size={24} className="mr-2" />
                  我要出车
                </h3>
                <ol className="space-y-3 text-gray-700">
                  <li className="flex items-start">
                    <span className="bg-emerald-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">1</span>
                    <span>登记车辆信息，等待审核</span>
                  </li>
                  <li className="flex items-start">
                    <span className="bg-emerald-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">2</span>
                    <span>审核通过后选择交付时间</span>
                  </li>
                  <li className="flex items-start">
                    <span className="bg-emerald-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">3</span>
                    <span>按约定时间交付车辆</span>
                  </li>
                </ol>
              </div>
              <div className="bg-white rounded-2xl p-6 shadow-md">
                <h3 className="font-bold text-xl text-cyan-600 mb-3 flex items-center">
                  <ShoppingCart size={24} className="mr-2" />
                  我要购车
                </h3>
                <ol className="space-y-3 text-gray-700">
                  <li className="flex items-start">
                    <span className="bg-cyan-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">1</span>
                    <span>浏览库存，筛选心仪座驾</span>
                  </li>
                  <li className="flex items-start">
                    <span className="bg-cyan-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">2</span>
                    <span>提交预约并选择时间</span>
                  </li>
                  <li className="flex items-start">
                    <span className="bg-cyan-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">3</span>
                    <span>按约定时间线下提车</span>
                  </li>
                </ol>
              </div>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="bg-white/80 backdrop-blur-md border-t border-gray-200 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
            <p className="font-medium">© 2024 燕园易骑 - 北大校园自行车循环计划</p>
            <p className="text-sm mt-2">让爱传递，让资源循环 ♻️</p>
          </div>
        </footer>
      </div>

      {/* Guide Modal */}
      {showGuide && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowGuide(false)}>
          <div className="bg-white rounded-3xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-500 to-cyan-500 text-white p-6 rounded-t-3xl flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <BookOpen size={32} />
                <h2 className="text-3xl font-black">燕园易骑 - 详细使用说明</h2>
              </div>
              <button
                onClick={() => setShowGuide(false)}
                className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition-all"
              >
                <X size={28} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-8">
              {/* Welcome Section */}
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">欢迎来到燕园易骑！</h3>
                <p className="text-gray-700 leading-relaxed text-lg">
                  燕园易骑是北京大学校园自行车循环计划平台，旨在连接毕业生与新生，促进资源循环利用，减少浪费，传递绿色环保理念。
                  无论您是要出车的毕业生，还是寻找座驾的新生，都可以在这里找到合适的解决方案。
                </p>
              </div>

              {/* Two Main Flows */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Sell Flow */}
                <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-2xl p-8 border-2 border-emerald-200">
                  <div className="flex items-center mb-6">
                    <div className="bg-emerald-500 text-white p-4 rounded-xl mr-4">
                      <Bike size={32} />
                    </div>
                    <h3 className="text-2xl font-bold text-emerald-800">我要出车 / 捐赠</h3>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-emerald-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">1</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">登记车辆信息</h4>
                          <p className="text-gray-600 leading-relaxed">
                            点击首页"一键登记车辆"按钮，填写自行车品牌、型号、颜色、价格、车况等信息，并上传清晰照片。
                            确保信息真实准确，有助于更快通过审核。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-emerald-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">2</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">等待管理员审核</h4>
                          <p className="text-gray-600 leading-relaxed">
                            提交后，管理员将在 1-2 个工作日内审核您的车辆信息。审核通过后，您会收到系统通知。
                            如审核未通过，请根据反馈修改后重新提交。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-emerald-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">3</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">选择交付时间</h4>
                          <p className="text-gray-600 leading-relaxed">
                            审核通过后，您可以选择方便的线下交付时间段。系统会显示管理员提供的可选时间。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-emerald-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">4</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">交付车辆</h4>
                          <p className="text-gray-600 leading-relaxed">
                            按约定时间地点交付车辆，完成交易。交易完成后，您可以对买家进行评价。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Buy Flow */}
                <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl p-8 border-2 border-cyan-200">
                  <div className="flex items-center mb-6">
                    <div className="bg-cyan-500 text-white p-4 rounded-xl mr-4">
                      <ShoppingCart size={32} />
                    </div>
                    <h3 className="text-2xl font-bold text-cyan-800">我要购车</h3>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-cyan-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">1</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">浏览库存车辆</h4>
                          <p className="text-gray-600 leading-relaxed">
                            点击首页"浏览库存"按钮，查看所有可售自行车。您可以使用筛选功能，根据品牌、价格、颜色等条件找到心仪的座驾。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-cyan-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">2</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">提交预约申请</h4>
                          <p className="text-gray-600 leading-relaxed">
                            找到心仪的车辆后，点击"预约看车"提交申请。申请中可填写您的联系方式和特殊需求。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-cyan-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">3</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">选择时间段</h4>
                          <p className="text-gray-600 leading-relaxed">
                            管理员审核您的预约后，会提供可选的时间段。选择您方便的时间进行线下提车。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <div className="flex items-start">
                        <span className="bg-cyan-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">4</span>
                        <div>
                          <h4 className="font-bold text-gray-900 mb-2">线下提车</h4>
                          <p className="text-gray-600 leading-relaxed">
                            按约定时间地点提车，检查车辆状况，完成交易。提车完成后，您可以对卖家进行评价。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Important Notes */}
              <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-2xl p-8 border-2 border-yellow-300 mb-8">
                <div className="flex items-center mb-6">
                  <AlertCircle size={32} className="text-yellow-600 mr-4" />
                  <h3 className="text-2xl font-bold text-yellow-800">重要提示</h3>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-start">
                    <CheckCircle size={20} className="text-yellow-600 mr-3 mt-1 flex-shrink-0" />
                    <p className="text-gray-700 leading-relaxed">
                      <strong>随时取消：</strong>在交易完成前，您可以随时取消预约，无需承担任何责任。
                    </p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle size={20} className="text-yellow-600 mr-3 mt-1 flex-shrink-0" />
                    <p className="text-gray-700 leading-relaxed">
                      <strong>审核拒绝：</strong>管理员有权拒绝不符合要求的交易申请，并会说明拒绝理由。
                    </p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle size={20} className="text-yellow-600 mr-3 mt-1 flex-shrink-0" />
                    <p className="text-gray-700 leading-relaxed">
                      <strong>信息真实：</strong>请确保填写的车辆信息和联系方式真实准确，虚假信息可能导致审核不通过。
                    </p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle size={20} className="text-yellow-600 mr-3 mt-1 flex-shrink-0" />
                    <p className="text-gray-700 leading-relaxed">
                      <strong>线下交易：</strong>所有交易均为线下进行，请注意人身和财产安全，选择人多的公共场所交易。
                    </p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle size={20} className="text-yellow-600 mr-3 mt-1 flex-shrink-0" />
                    <p className="text-gray-700 leading-relaxed">
                      <strong>评价系统：</strong>交易完成后，您可以对对方进行评价，帮助其他用户建立信任。
                    </p>
                  </div>
                </div>
              </div>

              {/* Personal Center Features */}
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-8 border-2 border-indigo-200 mb-8">
                <div className="flex items-center mb-6">
                  <User size={32} className="text-indigo-600 mr-4" />
                  <h3 className="text-2xl font-bold text-indigo-800">个人主页功能说明</h3>
                </div>
                
                <div className="space-y-6">
                  {/* Time Slot Selection */}
                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <div className="flex items-start mb-3">
                      <Calendar size={24} className="text-indigo-600 mr-3 mt-1 flex-shrink-0" />
                      <h4 className="font-bold text-gray-900 text-lg">时间段选择</h4>
                    </div>
                    <div className="space-y-3 ml-10">
                      <p className="text-gray-700 leading-relaxed">
                        <strong className="text-indigo-600">使用场景：</strong>当您的预约审核通过后，需要选择线下交易的具体时间段。
                      </p>
                      <div className="bg-indigo-50 rounded-lg p-4">
                        <p className="font-bold text-indigo-900 mb-2">操作步骤：</p>
                        <ol className="space-y-2 text-gray-700">
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">1</span>
                            <span>进入个人主页，查看"我的预约"</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">2</span>
                            <span>找到状态为"待选择时间"的预约</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">3</span>
                            <span>点击"选择时间段"按钮</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">4</span>
                            <span>从管理员提供的可选时间段中选择合适的</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">5</span>
                            <span>确认选择，等待管理员确认</span>
                          </li>
                        </ol>
                      </div>
                      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mt-3">
                        <p className="text-yellow-800 text-sm">
                          <strong>⚠️ 注意：</strong>选择时间段后，系统会自动发送私信通知管理员。请及时关注消息通知。
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Private Messaging */}
                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <div className="flex items-start mb-3">
                      <MessageSquare size={24} className="text-indigo-600 mr-3 mt-1 flex-shrink-0" />
                      <h4 className="font-bold text-gray-900 text-lg">私信功能</h4>
                    </div>
                    <div className="space-y-3 ml-10">
                      <p className="text-gray-700 leading-relaxed">
                        <strong className="text-indigo-600">功能说明：</strong>与管理员或其他用户进行私信沟通，支持文本、表情和图片。
                      </p>
                      <div className="bg-indigo-50 rounded-lg p-4">
                        <p className="font-bold text-indigo-900 mb-2">使用方法：</p>
                        <ol className="space-y-2 text-gray-700">
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">1</span>
                            <span>进入个人主页，点击"私信"标签</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">2</span>
                            <span>在左侧列表选择联系人（或点击"新建对话"）</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">3</span>
                            <span>在输入框输入消息内容</span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">4</span>
                            <span>
                              点击表情图标 <span className="inline-flex items-center justify-center w-5 h-5 bg-indigo-200 rounded text-xs">😊</span> 发送表情
                            </span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">5</span>
                            <span>
                              点击图片图标 <span className="inline-flex items-center justify-center w-5 h-5 bg-indigo-200 rounded text-xs">🖼️</span> 上传图片
                            </span>
                          </li>
                          <li className="flex items-start">
                            <span className="bg-indigo-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-0.5">6</span>
                            <span>点击发送按钮或按 Enter 键发送</span>
                          </li>
                        </ol>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                        <div className="bg-green-50 border-l-4 border-green-400 p-3">
                          <p className="text-green-800 text-sm">
                            <strong className="text-green-600">✓ 系统通知：</strong>
                            预约状态变更、时间段确认等操作会自动发送系统私信通知。
                          </p>
                        </div>
                        <div className="bg-blue-50 border-l-4 border-blue-400 p-3">
                          <p className="text-blue-800 text-sm">
                            <strong className="text-blue-600">💡 提示：</strong>
                            未读消息会在个人中心和个人主页显示红色数字徽章。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Other Features */}
                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <div className="flex items-start mb-3">
                      <Bookmark size={24} className="text-indigo-600 mr-3 mt-1 flex-shrink-0" />
                      <h4 className="font-bold text-gray-900 text-lg">其他功能</h4>
                    </div>
                    <div className="space-y-3 ml-10">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-indigo-50 rounded-lg p-4">
                          <p className="font-bold text-indigo-900 mb-2 flex items-center">
                            <Bike size={18} className="mr-2" />
                            我的车辆
                          </p>
                          <p className="text-gray-700 text-sm leading-relaxed">
                            查看您登记的所有车辆，包括审核中、可售、已售等状态。可随时编辑或删除。
                          </p>
                        </div>
                        <div className="bg-indigo-50 rounded-lg p-4">
                          <p className="font-bold text-indigo-900 mb-2 flex items-center">
                            <Calendar size={18} className="mr-2" />
                            我的预约
                          </p>
                          <p className="text-gray-700 text-sm leading-relaxed">
                            查看所有预约记录，包括待审核、待选择时间、已确认、已完成等状态。
                          </p>
                        </div>
                        <div className="bg-indigo-50 rounded-lg p-4">
                          <p className="font-bold text-indigo-900 mb-2 flex items-center">
                            <Bookmark size={18} className="mr-2" />
                            我的收藏
                          </p>
                          <p className="text-gray-700 text-sm leading-relaxed">
                            查看您在社区广场收藏的帖子，方便快速访问感兴趣的内容。
                          </p>
                        </div>
                        <div className="bg-indigo-50 rounded-lg p-4">
                          <p className="font-bold text-indigo-900 mb-2 flex items-center">
                            <Shield size={18} className="mr-2" />
                            个人信息
                          </p>
                          <p className="text-gray-700 text-sm leading-relaxed">
                            查看和编辑个人昵称、邮箱等信息。管理员可在此查看管理功能入口。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* FAQ Section */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border-2 border-purple-200">
                <div className="flex items-center mb-6">
                  <HelpCircle size={32} className="text-purple-600 mr-4" />
                  <h3 className="text-2xl font-bold text-purple-800">常见问题</h3>
                </div>
                
                <div className="space-y-6">
                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 审核需要多长时间？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 通常情况下，审核会在 1-2 个工作日内完成。如遇高峰期（如毕业季），可能需要更长时间，请耐心等待。
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 车辆价格如何确定？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 车辆价格由卖家自行设定。建议参考车辆品牌、车况、购买年限等因素，设定合理价格。管理员会审核价格的合理性。
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 如何保证交易安全？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 平台会对所有车辆进行审核，确保信息真实。交易双方可在校内公共场所见面，建议结伴而行。交易前仔细检查车辆状况。
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 交易完成后发现问题怎么办？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 建议交易双方当场确认车辆状况。如事后发现问题，可通过平台联系对方协商解决，或联系管理员协助处理。
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 可以同时进行多个预约吗？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 为避免资源浪费，建议同一时间只保持一个有效预约。如需取消预约，请及时操作以便其他用户使用。
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 时间段选择后还能修改吗？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 时间段选择后，如需修改，请及时联系管理员协商。管理员确认后可以为您的预约重新提供可选时间段。
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-900 mb-2">Q: 私信可以发送什么内容？</h4>
                    <p className="text-gray-600 leading-relaxed">
                      A: 私信支持发送文本消息、表情符号和图片。请注意文明用语，不要发送不当内容。
                    </p>
                  </div>
                </div>
              </div>

              {/* Contact Section */}
              <div className="mt-8 text-center">
                <p className="text-gray-600 mb-4">
                  如有其他问题，请联系管理员或在社区广场提问
                </p>
                <button
                  onClick={() => setShowGuide(false)}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-4 rounded-full font-bold text-lg hover:shadow-xl hover:-translate-y-1 transition-all"
                >
                  关闭说明
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
