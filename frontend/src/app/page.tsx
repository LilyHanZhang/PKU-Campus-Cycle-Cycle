"use client";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { User, LogOut } from "lucide-react";
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

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-green-50 flex flex-col items-center p-8">
      <header className="w-full max-w-5xl flex justify-between items-center mb-12">
        <h1 className="text-5xl font-extrabold text-[#1f874c] tracking-tight">
          燕园易骑
        </h1>
        <div className="flex items-center space-x-6">
          <Link
            href="/forum"
            className="text-gray-600 hover:text-emerald-600 font-semibold transition"
          >
            社区广场
          </Link>
          {isAuthenticated ? (
            <>
              {(user?.role === "ADMIN" || user?.role === "SUPER_ADMIN") && (
                <Link
                  href="/admin"
                  className="text-gray-600 hover:text-emerald-600 font-semibold transition"
                >
                  管理后台
                </Link>
              )}
              <Link href="/profile">
                <div className="flex items-center space-x-2 text-gray-700 hover:text-emerald-700 cursor-pointer">
                  <User />
                  <span className="font-bold">{user?.name || "个人中心"}</span>
                </div>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-red-500 hover:text-red-600"
              >
                <LogOut size={18} />
                <span className="font-bold">退出</span>
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-gray-600 hover:text-emerald-600 font-semibold transition"
              >
                登录
              </Link>
              <Link
                href="/register"
                className="text-gray-600 hover:text-emerald-600 font-semibold transition"
              >
                注册
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition hover:-translate-y-1 cursor-pointer border-t-4 border-[#2ab26a]">
          <div className="flex items-center space-x-4 mb-4">
            <div className="bg-green-100 p-4 rounded-full">
              <span className="text-3xl text-[#1f874c]">🚲</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800">我要出车 / 捐赠</h2>
          </div>
          <p className="text-gray-600 mb-6">
            即将离校？将不再使用的自行车交由新生，减少资源浪费，传递绿色环保理念。
          </p>
          <Link href="/bicycles/new">
            <button className="w-full bg-[#2ab26a] text-white py-3 rounded-full font-bold hover:bg-[#1f874c] transition shadow-md">
              一键登记车辆
            </button>
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition hover:-translate-y-1 cursor-pointer border-t-4 border-emerald-400">
          <div className="flex items-center space-x-4 mb-4">
            <div className="bg-emerald-100 p-4 rounded-full">
              <span className="text-3xl text-emerald-600">🔎</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800">寻找座驾</h2>
          </div>
          <p className="text-gray-600 mb-6">
            新生报道缺少座驾？在这里寻找高性价比、经过核验的二手自行车，省钱又省心。
          </p>
          <Link href="/bicycles">
            <button className="w-full bg-emerald-500 text-white py-3 rounded-full font-bold hover:bg-emerald-600 transition shadow-md">
              浏览目前库存
            </button>
          </Link>
        </div>
      </main>

      <section className="mt-16 w-full max-w-4xl bg-[#1f874c] text-white rounded-2xl p-8 py-10 shadow-lg text-center flex flex-col md:flex-row justify-around items-center">
        <div className="mb-6 md:mb-0">
          <h3 className="text-4xl font-black mb-2">{stats.sold_bicycles}</h3>
          <p className="text-green-100 font-medium tracking-wide">成功回收爱车</p>
        </div>
        <div>
          <h3 className="text-4xl font-black mb-2">{stats.total_bicycles}</h3>
          <p className="text-green-100 font-medium tracking-wide">平台车辆总数</p>
        </div>
        <div>
          <h3 className="text-4xl font-black mb-2">{stats.total_users}</h3>
          <p className="text-green-100 font-medium tracking-wide">注册用户</p>
        </div>
      </section>

      {/* 宣传部分 */}
      <section className="mt-12 w-full max-w-4xl bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-2xl p-8 shadow-xl">
        <h2 className="text-3xl font-black mb-4 text-center">♻️ 让爱传递，让资源循环</h2>
        <p className="text-lg text-green-50 text-center mb-6">
          北大校园自行车循环计划致力于减少资源浪费，促进绿色环保。
          每辆回收的自行车都承载着毕业生的美好回忆，也将为新生提供便捷的校园出行体验。
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-4xl mb-2">🌱</div>
            <h3 className="font-bold text-xl mb-1">绿色环保</h3>
            <p className="text-green-100 text-sm">减少废旧金属污染</p>
          </div>
          <div>
            <div className="text-4xl mb-2">💚</div>
            <h3 className="font-bold text-xl mb-1">爱心传递</h3>
            <p className="text-green-100 text-sm">毕业生与新生互助</p>
          </div>
          <div>
            <div className="text-4xl mb-2">🔄</div>
            <h3 className="font-bold text-xl mb-1">资源循环</h3>
            <p className="text-green-100 text-sm">提高资源利用效率</p>
          </div>
        </div>
      </section>

      {/* 平台使用说明 */}
      <section className="mt-12 w-full max-w-4xl bg-white rounded-2xl shadow-xl p-8">
        <h2 className="text-3xl font-black text-gray-800 mb-6 text-center">📖 平台使用说明</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border-l-4 border-[#2ab26a] pl-4">
            <h3 className="font-bold text-xl text-[#1f874c] mb-2">🚲 我要出车</h3>
            <ol className="text-gray-600 space-y-2 list-decimal list-inside">
              <li>点击"一键登记车辆"填写车辆信息</li>
              <li>等待管理员审核（1-2 个工作日）</li>
              <li>审核通过后，选择线下交付时间</li>
              <li>按约定时间交付车辆</li>
              <li>交易完成后可进行评价</li>
            </ol>
          </div>
          <div className="border-l-4 border-emerald-400 pl-4">
            <h3 className="font-bold text-xl text-emerald-600 mb-2">🔎 我要购车</h3>
            <ol className="text-gray-600 space-y-2 list-decimal list-inside">
              <li>浏览库存车辆，筛选心仪座驾</li>
              <li>提交预约申请</li>
              <li>选择管理员提供的空闲时间</li>
              <li>按约定时间线下提车</li>
              <li>提车完成后可进行评价</li>
            </ol>
          </div>
        </div>
        <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <p className="text-yellow-800">
            <strong>💡 温馨提示：</strong> 所有交易均支持随时取消。在交易完成前，您可以随时取消预约；管理员也可拒绝交易并说明理由。
          </p>
        </div>
      </section>
    </div>
  );
}
