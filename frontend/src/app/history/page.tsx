"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Calendar, CheckCircle, Clock, Archive } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function HistoryPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [completedAppointments, setCompletedAppointments] = useState<any[]>([]);
  const [completedBicycles, setCompletedBicycles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }
    if (isAuthenticated && user && (user.role === "ADMIN" || user.role === "SUPER_ADMIN")) {
      fetchData();
    }
  }, [authLoading, isAuthenticated, user, router]);

  const fetchData = async () => {
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [appointmentsRes, bikesRes] = await Promise.all([
        axios.get(`${API_URL}/appointments/completed`, { headers }),
        axios.get(`${API_URL}/bicycles/`, { headers }),
      ]);

      // 过滤已售出的自行车
      const soldBikes = bikesRes.data.filter((b: any) => b.status === 'SOLD');
      
      setCompletedAppointments(appointmentsRes.data);
      setCompletedBicycles(soldBikes);
    } catch (err: any) {
      console.error("Failed to fetch history data", err);
      setError(`获取历史记录失败：${err.response?.data?.detail || err.message || "未知错误"}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (isoString: string) => {
    if (!isoString) return "未设置";
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading || authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500 text-lg font-medium">加载中...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2 flex items-center">
              <Archive className="w-10 h-10 mr-3 text-emerald-500" />
              历史记录
            </h1>
            <p className="text-gray-600">查看已完成的预约和已售出的自行车</p>
          </div>
          <Link href="/admin">
            <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-bold hover:bg-gray-300 transition">
              返回管理后台
            </button>
          </Link>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Completed Appointments */}
        <section className="mb-12 bg-white rounded-2xl shadow-xl p-8 border-t-4 border-blue-400">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <CheckCircle className="mr-3 text-blue-500" />
            已完成预约
          </h2>
          <div className="space-y-4">
            {completedAppointments.length > 0 ? completedAppointments.map((apt: any) => {
              const bike = completedBicycles.find((b: any) => b.id === apt.bicycle_id);
              return (
                <div key={apt.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <p className="font-bold text-gray-800 mr-4">预约 ID: {apt.id.slice(0, 8)}...</p>
                        <span className="px-3 py-1 text-xs font-bold rounded-full bg-green-100 text-green-700">
                          {apt.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-1">
                        自行车：{bike ? `${bike.brand} - ${bike.color}` : '未知'} (ID: {apt.bicycle_id.slice(0, 8)}...)
                      </p>
                      <p className="text-sm text-gray-600 mb-1">
                        类型：{apt.type === 'pick-up' ? '🚴 买家提车' : '📦 卖家交车'}
                      </p>
                      <p className="text-sm text-gray-600 mb-1">
                        预约时间：{formatDateTime(apt.appointment_time)}
                      </p>
                      <p className="text-sm text-gray-600">
                        创建时间：{formatDateTime(apt.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              );
            }) : (
              <p className="text-gray-500 text-center py-8">暂无已完成的预约记录</p>
            )}
          </div>
        </section>

        {/* Sold Bicycles */}
        <section className="bg-white rounded-2xl shadow-xl p-8 border-t-4 border-purple-400">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Calendar className="mr-3 text-purple-500" />
            已售出自行车
          </h2>
          <div className="space-y-4">
            {completedBicycles.length > 0 ? completedBicycles.map((bike: any) => (
              <div key={bike.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <p className="font-bold text-gray-800 mr-4">{bike.brand} - {bike.color}</p>
                      <span className="px-3 py-1 text-xs font-bold rounded-full bg-purple-100 text-purple-700">
                        SOLD
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">
                      ID: {bike.id.slice(0, 8)}...
                    </p>
                    <p className="text-sm text-gray-600 mb-1">
                      成色：{bike.condition}/10
                    </p>
                    <p className="text-sm text-gray-600">
                      上架时间：{formatDateTime(bike.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            )) : (
              <p className="text-gray-500 text-center py-8">暂无已售出的自行车</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
