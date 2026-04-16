"use client";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { User, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

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
          <h3 className="text-4xl font-black mb-2">1,200+</h3>
          <p className="text-green-100 font-medium tracking-wide">成功回收爱车</p>
        </div>
        <div>
          <h3 className="text-4xl font-black mb-2">850 kg</h3>
          <p className="text-green-100 font-medium tracking-wide">拯救废旧金属资源</p>
        </div>
      </section>
    </div>
  );
}
