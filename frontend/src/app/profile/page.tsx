"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { User, Bike, Calendar, LogOut, Shield } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const [myBikes, setMyBikes] = useState([]);
  const [myAppointments, setMyAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

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
            <Link href="/" className="text-emerald-600 font-bold hover:underline">返回首页</Link>
            <button onClick={handleLogout} className="flex items-center space-x-2 text-red-500 hover:text-red-600">
              <LogOut size={18} />
              <span>退出登录</span>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border-t-4 border-[#2ab26a]">
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
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border-t-4 border-emerald-400">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center"><Bike className="mr-3 text-emerald-500"/>我的发布</h2>
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
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 border-t-4 border-emerald-400">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center"><Calendar className="mr-3 text-emerald-500"/>我的预约</h2>
          <div className="space-y-4">
            {myAppointments.length > 0 ? myAppointments.map((apt: any) => (
              <div key={apt.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-bold text-gray-700">预约车辆ID: {apt.bicycle_id.substring(0, 8)}...</p>
                  <p className="text-sm text-gray-500">{apt.type === 'drop-off' ? '交车' : '提车'}</p>
                </div>
                <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-100 text-blue-700">
                  {apt.status}
                </span>
              </div>
            )) : <p className="text-gray-500">您还没有任何预约记录。</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
