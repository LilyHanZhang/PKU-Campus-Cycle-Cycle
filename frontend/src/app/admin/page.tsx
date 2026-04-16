"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { User, Bike, Calendar, Shield, Trash2, Edit } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function AdminDashboard() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [pendingBikes, setPendingBikes] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [allBikes, setAllBikes] = useState([]);
  const [allAppointments, setAllAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("pending");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || user?.role === "USER")) {
      alert("您没有权限访问此页面");
      window.location.href = "/";
    }
  }, [authLoading, isAuthenticated, user]);

  useEffect(() => {
    if (user && (user.role === "ADMIN" || user.role === "SUPER_ADMIN")) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [pendingRes, usersRes, bikesRes, appointmentsRes] = await Promise.all([
        axios.get(`${API_URL}/bicycles/?status=PENDING_APPROVAL`, { headers }),
        axios.get(`${API_URL}/users/`, { headers }),
        axios.get(`${API_URL}/bicycles/`, { headers }),
        axios.get(`${API_URL}/appointments/`, { headers }),
      ]);
      setPendingBikes(pendingRes.data);
      setAllUsers(usersRes.data);
      setAllBikes(bikesRes.data);
      setAllAppointments(appointmentsRes.data);
    } catch (err) {
      console.error("Failed to fetch data", err);
      setError("获取数据失败");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(`${API_URL}/bicycles/${bikeId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("车辆已批准上架！");
      fetchData();
    } catch (err) {
      console.error("Failed to approve bike", err);
      alert("操作失败，请重试。");
    }
  };

  const handleReject = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(`${API_URL}/bicycles/${bikeId}/reject`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("已拒绝并删除");
      fetchData();
    } catch (err) {
      console.error("Failed to reject bike", err);
      alert("操作失败，请重试。");
    }
  };

  const handleUpdateRole = async (userId: string, newRole: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/users/${userId}/role`,
        { role: newRole },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("角色更新成功！");
      fetchData();
    } catch (err) {
      console.error("Failed to update role", err);
      alert("操作失败，只有主负责人可以修改管理员权限。");
    }
  };

  if (authLoading || !user) {
    return <div className="min-h-screen bg-gray-100 flex items-center justify-center"><p>加载中...</p></div>;
  }

  if (user.role === "USER") {
    return <div className="min-h-screen bg-gray-100 flex items-center justify-center"><p>您没有权限访问此页面</p></div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <h1 className="text-4xl font-extrabold text-gray-800">管理后台</h1>
            <span className={`text-sm font-bold px-3 py-1 rounded-full ${
              user.role === "SUPER_ADMIN" ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"
            }`}>
              {user.role === "SUPER_ADMIN" ? "主负责人" : "管理员"}
            </span>
          </div>
          <Link href="/" className="text-gray-600 font-bold hover:underline">返回首页</Link>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 bg-white rounded-xl p-2 shadow-lg">
          <button
            onClick={() => setActiveTab("pending")}
            className={`flex-1 py-3 px-6 rounded-lg font-bold transition ${
              activeTab === "pending" ? "bg-[#2ab26a] text-white" : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            待审核车辆 ({pendingBikes.length})
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`flex-1 py-3 px-6 rounded-lg font-bold transition ${
              activeTab === "users" ? "bg-[#2ab26a] text-white" : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            用户管理 ({allUsers.length})
          </button>
          <button
            onClick={() => setActiveTab("bikes")}
            className={`flex-1 py-3 px-6 rounded-lg font-bold transition ${
              activeTab === "bikes" ? "bg-[#2ab26a] text-white" : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            车辆管理 ({allBikes.length})
          </button>
          <button
            onClick={() => setActiveTab("appointments")}
            className={`flex-1 py-3 px-6 rounded-lg font-bold transition ${
              activeTab === "appointments" ? "bg-[#2ab26a] text-white" : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            预约管理 ({allAppointments.length})
          </button>
        </div>

        {loading ? (
          <p className="text-center py-10">加载中...</p>
        ) : (
          <>
            {/* Pending Bikes Tab */}
            {activeTab === "pending" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">待审核车辆</h2>
                {pendingBikes.length > 0 ? (
                  <div className="space-y-4">
                    {pendingBikes.map((bike: any) => (
                      <div key={bike.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-bold text-gray-700">{bike.brand}</p>
                          <p className="text-sm text-gray-500">
                            车主ID: {bike.owner_id?.substring(0, 8)}... | 价格: ¥{bike.price} | 成色: {bike.condition}/10
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleApprove(bike.id)}
                            className="bg-green-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-600 transition"
                          >
                            批准上架
                          </button>
                          <button
                            onClick={() => handleReject(bike.id)}
                            className="bg-red-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-red-600 transition"
                          >
                            拒绝
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">当前没有待审核的车辆。</p>
                )}
              </div>
            )}

            {/* Users Tab */}
            {activeTab === "users" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <User className="mr-3 text-emerald-500" />用户管理
                </h2>
                {user.role === "SUPER_ADMIN" ? (
                  <div className="space-y-4">
                    {allUsers.map((u: any) => (
                      <div key={u.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="bg-gray-200 p-3 rounded-full">
                            <User size={24} className="text-gray-600" />
                          </div>
                          <div>
                            <p className="font-bold text-gray-700">{u.name || "未命名"}</p>
                            <p className="text-sm text-gray-500">{u.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                            u.role === "SUPER_ADMIN" ? "bg-purple-100 text-purple-700" :
                            u.role === "ADMIN" ? "bg-blue-100 text-blue-700" :
                            "bg-gray-200 text-gray-600"
                          }`}>
                            {u.role === "SUPER_ADMIN" ? "主负责人" : u.role === "ADMIN" ? "管理员" : "普通用户"}
                          </span>
                          {u.role !== "SUPER_ADMIN" && (
                            <select
                              value={u.role}
                              onChange={(e) => handleUpdateRole(u.id, e.target.value)}
                              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            >
                              <option value="USER">设为普通用户</option>
                              <option value="ADMIN">设为管理员</option>
                            </select>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">您没有权限管理用户，只有主负责人可以。</p>
                )}
              </div>
            )}

            {/* Bikes Tab */}
            {activeTab === "bikes" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Bike className="mr-3 text-emerald-500" />所有车辆
                </h2>
                <div className="space-y-4">
                  {allBikes.map((bike: any) => (
                    <div key={bike.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-bold text-gray-700">{bike.brand}</p>
                        <p className="text-sm text-gray-500">
                          ¥{bike.price} | 成色 {bike.condition}/10 | 状态: {
                            bike.status === 'PENDING_APPROVAL' ? '待审核' :
                            bike.status === 'IN_STOCK' ? '在库' :
                            bike.status === 'LOCKED' ? '已锁定' : '已售出'
                          }
                        </p>
                      </div>
                      <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                        bike.status === 'IN_STOCK' ? 'bg-green-100 text-green-700' :
                        bike.status === 'PENDING_APPROVAL' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-200 text-gray-600'
                      }`}>
                        {bike.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Appointments Tab */}
            {activeTab === "appointments" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Calendar className="mr-3 text-emerald-500" />所有预约
                </h2>
                <div className="space-y-4">
                  {allAppointments.map((apt: any) => (
                    <div key={apt.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-bold text-gray-700">预约ID: {apt.id.substring(0, 8)}...</p>
                        <p className="text-sm text-gray-500">
                          车辆ID: {apt.bicycle_id.substring(0, 8)}... | 类型: {apt.type === 'drop-off' ? '交车' : '提车'}
                        </p>
                      </div>
                      <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-100 text-blue-700">
                        {apt.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
