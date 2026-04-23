"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pku-campus-cycle-cycle.onrender.com";

export default function NewBicycle() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [formData, setFormData] = useState({
    brand: "",
    condition: 8,
    price: 0,
    description: "",
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    setLoading(true);
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(`${API_URL}/bicycles/`, formData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("信息登记成功！等待管理员审核。");
      router.push("/profile");
    } catch (error) {
      console.error(error);
      alert("发布失败请重试。");
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !isAuthenticated) {
    return <div className="min-h-screen bg-green-50 flex items-center justify-center"><p>加载中...</p></div>;
  }

  return (
    <div className="min-h-screen bg-green-50 flex items-center justify-center p-8">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-lg border-t-4 border-[#2ab26a]">
        <h2 className="text-3xl font-extrabold text-[#1f874c] mb-6 text-center">登记闲置自行车</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-bold mb-2">品牌 / 描述</label>
            <input
              required
              type="text"
              placeholder="e.g. 捷安特 Giant 去年代步车"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              value={formData.brand}
              onChange={e => setFormData({...formData, brand: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">新旧程度 (1-10分)</label>
            <input
              required
              type="number"
              min="1" max="10"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              value={formData.condition}
              onChange={e => setFormData({...formData, condition: parseInt(e.target.value)})}
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">转让价格 (元)</label>
            <p className="text-xs text-gray-500 mb-2">填 0 即表示免费捐赠，传递爱心。</p>
            <input
              required
              type="number"
              min="0"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              value={formData.price}
              onChange={e => setFormData({...formData, price: parseFloat(e.target.value)})}
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">详细描述（可选）</label>
            <textarea
              placeholder="补充车辆信息，如：车身颜色、入手渠道、有无维修记录等"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              rows={3}
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <button
             type="submit"
             disabled={loading}
             className="w-full bg-[#2ab26a] text-white py-3 rounded-full font-bold hover:bg-[#1f874c] transition shadow-md disabled:bg-gray-400"
          >
            {loading ? "提交中..." : "确认发布出车"}
          </button>
        </form>
      </div>
    </div>
  );
}
