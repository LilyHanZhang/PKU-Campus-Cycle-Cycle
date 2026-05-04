"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { 
  Truck, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Calendar,
  ChevronRight,
  Package
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface Bicycle {
  id: string;
  brand: string;
  model?: string;
  color: string;
  price: number;
  condition: number;
  status: string;
  created_at: string;
  time_slots?: any[];
}

export default function MyBicyclesPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [myBikes, setMyBikes] = useState<Bicycle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (user) {
      fetchMyBicycles();
    }
  }, [user]);

  const fetchMyBicycles = async () => {
    if (!user) return;
    
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const { data } = await axios.get(`${API_URL}/bicycles/`, { headers });
      setMyBikes(data);
    } catch (err: any) {
      console.error("Failed to fetch bicycles:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { color: string; label: string; icon: any }> = {
      PENDING_APPROVAL: { color: "bg-amber-100 text-amber-700", label: "待审核", icon: Clock },
      IN_STOCK: { color: "bg-green-100 text-green-700", label: "在库", icon: CheckCircle },
      PENDING_SELLER_SLOT_SELECTION: { color: "bg-blue-100 text-blue-700", label: "待选时间段", icon: Calendar },
      PENDING_ADMIN_CONFIRMATION_SELLER: { color: "bg-purple-100 text-purple-700", label: "待管理员确认", icon: Clock },
      RESERVED: { color: "bg-indigo-100 text-indigo-700", label: "已预留", icon: Package },
      SOLD: { color: "bg-gray-100 text-gray-700", label: "已售", icon: CheckCircle },
      PENDING_BUYER_SLOT_SELECTION: { color: "bg-blue-100 text-blue-700", label: "待选时间段", icon: Calendar },
      PENDING_ADMIN_CONFIRMATION_BUYER: { color: "bg-purple-100 text-purple-700", label: "待管理员确认", icon: Clock },
      PENDING_PICKUP: { color: "bg-indigo-100 text-indigo-700", label: "待提车", icon: Clock },
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

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-emerald-200 border-t-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">正在加载我的车辆...</p>
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
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg">
                <Truck size={28} className="text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">我的车辆</h1>
                <p className="text-sm text-gray-500 mt-1">管理您的自行车登记和交易状态</p>
              </div>
            </div>
            <Link href="/profile" className="text-gray-600 font-medium hover:text-emerald-600 transition-colors flex items-center">
              返回个人中心
              <ChevronRight size={16} className="ml-1" />
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-slate-100">
            <p className="text-sm text-gray-500 mb-2">总车辆数</p>
            <p className="text-4xl font-extrabold text-gray-800">{myBikes.length}</p>
          </div>
          <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-2xl shadow-lg p-6">
            <p className="text-sm text-amber-100 mb-2">待审核</p>
            <p className="text-4xl font-extrabold">{myBikes.filter(b => b.status === 'PENDING_APPROVAL').length}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl shadow-lg p-6">
            <p className="text-sm text-blue-100 mb-2">待选时间段</p>
            <p className="text-4xl font-extrabold">{myBikes.filter(b => 
              b.status === 'PENDING_SELLER_SLOT_SELECTION' || 
              b.status === 'PENDING_BUYER_SLOT_SELECTION'
            ).length}</p>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl shadow-lg p-6">
            <p className="text-sm text-green-100 mb-2">已完成</p>
            <p className="text-4xl font-extrabold">{myBikes.filter(b => b.status === 'SOLD').length}</p>
          </div>
        </div>

        {/* Bikes List */}
        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
            <h2 className="text-2xl font-bold text-gray-800">车辆列表</h2>
          </div>
          
          {myBikes.length === 0 ? (
            <div className="p-12 text-center">
              <Truck size={64} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium mb-6">您还没有登记任何车辆</p>
              <Link 
                href="/bicycles/new" 
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl font-bold hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-lg"
              >
                登记第一辆车
                <ChevronRight size={18} className="ml-1" />
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {myBikes.map((bike) => (
                <div key={bike.id} className="p-6 hover:bg-slate-50 transition-all">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                        <Truck size={32} className="text-slate-500" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-bold text-gray-800">{bike.brand} {bike.model}</h3>
                          {getStatusBadge(bike.status)}
                        </div>
                        <div className="flex items-center space-x-6 text-sm text-gray-600">
                          <span>颜色：<span className="font-bold">{bike.color}</span></span>
                          <span>价格：<span className="font-bold text-green-600">¥{bike.price}</span></span>
                          <span>车况：<span className="font-bold">{bike.condition}/10</span></span>
                          <span>登记时间：<span className="font-bold">{new Date(bike.created_at).toLocaleDateString('zh-CN')}</span></span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {bike.status === 'PENDING_APPROVAL' && (
                        <span className="text-sm text-amber-600 font-medium flex items-center">
                          <Clock size={16} className="mr-1" />
                          等待管理员审核
                        </span>
                      )}
                      {(bike.status === 'PENDING_SELLER_SLOT_SELECTION' || bike.status === 'PENDING_BUYER_SLOT_SELECTION') && (
                        <Link 
                          href="/my-time-slots"
                          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-bold text-sm hover:from-blue-600 hover:to-blue-700 transition-all"
                        >
                          选择时间段
                        </Link>
                      )}
                      {bike.status === 'SOLD' && (
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
