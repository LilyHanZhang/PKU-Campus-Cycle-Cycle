"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  ChevronRight,
  Timer,
  Bell
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// 将 ISO 时间转换为北京时间显示（UTC+8）
const formatToBeijingTime = (isoString: string) => {
  // 如果时间字符串没有时区信息，强制视为 UTC
  const date = new Date(isoString.endsWith('Z') ? isoString : isoString + 'Z');
  // 获取 UTC 时间
  const utcYear = date.getUTCFullYear();
  const utcMonth = date.getUTCMonth() + 1;
  const utcDay = date.getUTCDate();
  const utcHours = date.getUTCHours();
  const utcMinutes = date.getUTCMinutes();
  
  // 转换为北京时间（UTC+8）
  let beijingHours = utcHours + 8;
  let beijingDay = utcDay;
  let beijingMonth = utcMonth;
  let beijingYear = utcYear;
  
  if (beijingHours >= 24) {
    beijingHours -= 24;
    beijingDay += 1;
    // 处理月份和年份的进位
    const daysInMonth = new Date(beijingYear, beijingMonth, 0).getDate();
    if (beijingDay > daysInMonth) {
      beijingDay = 1;
      beijingMonth += 1;
      if (beijingMonth > 12) {
        beijingMonth = 1;
        beijingYear += 1;
      }
    }
  }
  
  return `${beijingYear}/${String(beijingMonth).padStart(2, '0')}/${String(beijingDay).padStart(2, '0')} ${String(beijingHours).padStart(2, '0')}:${String(utcMinutes).padStart(2, '0')}`;
};

interface Appointment {
  id: string;
  type: string;
  status: string;
  bicycle_id: string;
  bicycle_brand: string;
  bicycle_model?: string;
  user_name?: string;
  appointment_time?: string;
  time_slot_id?: string;
  created_at: string;
  time_slot?: {
    start_time: string;
    end_time: string;
    appointment_type: string;
  };
}

export default function MyAppointmentsPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [myAppointments, setMyAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (user) {
      fetchMyAppointments();
    }
  }, [user]);

  const fetchMyAppointments = async () => {
    if (!user) return;
    
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const { data } = await axios.get(`${API_URL}/appointments/user/${user.id}`, { headers });
      setMyAppointments(data);
    } catch (err: any) {
      console.error("Failed to fetch appointments:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { color: string; label: string; icon: any }> = {
      PENDING: { color: "bg-amber-100 text-amber-700", label: "待处理", icon: Clock },
      CONFIRMED: { color: "bg-green-100 text-green-700", label: "已确认", icon: CheckCircle },
      COMPLETED: { color: "bg-blue-100 text-blue-700", label: "已完成", icon: CheckCircle },
      CANCELLED: { color: "bg-gray-100 text-gray-700", label: "已取消", icon: XCircle },
    };

    const config = statusConfig[status] || { color: "bg-gray-100 text-gray-700", label: status, icon: AlertCircle };
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${config.color}`}>
        <Icon size={12} className="mr-1" />
        {config.label}
      </span>
    );
  };

  const getTypeBadge = (type: string) => {
    return type === 'pick-up' 
      ? <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold">取车</span>
      : <span className="inline-flex items-center px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-bold">还车</span>;
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-emerald-200 border-t-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">正在加载我的预约...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-3xl shadow-xl p-6 mb-8 border border-slate-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
                <Calendar size={28} className="text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">我的预约</h1>
                <p className="text-sm text-gray-500 mt-1">查看和管理您的预约记录</p>
              </div>
            </div>
            <Link href="/profile" className="text-gray-600 font-medium hover:text-blue-600 transition-colors flex items-center">
              返回个人中心
              <ChevronRight size={16} className="ml-1" />
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-slate-100">
            <p className="text-sm text-gray-500 mb-2">总预约数</p>
            <p className="text-4xl font-extrabold text-gray-800">{myAppointments.length}</p>
          </div>
          <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-2xl shadow-lg p-6">
            <p className="text-sm text-amber-100 mb-2">待处理</p>
            <p className="text-4xl font-extrabold">{myAppointments.filter(a => a.status === 'PENDING').length}</p>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl shadow-lg p-6">
            <p className="text-sm text-green-100 mb-2">已确认</p>
            <p className="text-4xl font-extrabold">{myAppointments.filter(a => a.status === 'CONFIRMED').length}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl shadow-lg p-6">
            <p className="text-sm text-blue-100 mb-2">已完成</p>
            <p className="text-4xl font-extrabold">{myAppointments.filter(a => a.status === 'COMPLETED').length}</p>
          </div>
        </div>

        {/* Appointments List */}
        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
            <h2 className="text-2xl font-bold text-gray-800">预约列表</h2>
          </div>
          
          {myAppointments.length === 0 ? (
            <div className="p-12 text-center">
              <Calendar size={64} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium mb-6">您还没有任何预约</p>
              <Link 
                href="/bicycles" 
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-bold hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg"
              >
                查看可售自行车
                <ChevronRight size={18} className="ml-1" />
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {myAppointments.map((apt) => (
                <div key={apt.id} className="p-6 hover:bg-slate-50 transition-all">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                        <Calendar size={32} className="text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-bold text-gray-800">{apt.bicycle_brand}</h3>
                          {getStatusBadge(apt.status)}
                          {getTypeBadge(apt.type)}
                        </div>
                        <div className="flex items-center space-x-6 text-sm text-gray-600">
                          <span>预约 ID: <span className="font-mono text-xs">{apt.id.slice(0, 8)}...</span></span>
                          <span>创建时间：<span className="font-bold">{new Date(apt.created_at).toLocaleDateString('zh-CN')}</span></span>
                          {apt.appointment_time && (
                            <span>预约时间：<span className="font-bold">{new Date(apt.appointment_time).toLocaleString('zh-CN')}</span></span>
                          )}
                        </div>
                        {apt.time_slot && (
                          <div className="mt-2 flex items-center text-sm text-gray-600">
                            <Timer size={14} className="mr-1" />
                            时间段：{formatToBeijingTime(apt.time_slot.start_time)} - {formatToBeijingTime(apt.time_slot.end_time)}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {apt.status === 'PENDING' && !apt.time_slot_id && (
                        <span className="text-sm text-amber-600 font-medium flex items-center">
                          <Bell size={16} className="mr-1" />
                          等待管理员提出时间段
                        </span>
                      )}
                      {apt.status === 'PENDING' && apt.time_slot_id && (
                        <span className="text-sm text-blue-600 font-medium flex items-center">
                          <Clock size={16} className="mr-1" />
                          等待管理员确认
                        </span>
                      )}
                      {apt.status === 'CONFIRMED' && (
                        <span className="text-sm text-green-600 font-medium flex items-center">
                          <CheckCircle size={16} className="mr-1" />
                          已确认，等待线下交易
                        </span>
                      )}
                      {apt.status === 'COMPLETED' && (
                        <span className="text-sm text-gray-500 font-medium">交易已完成</span>
                      )}
                      <ChevronRight size={20} className="text-gray-400" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
