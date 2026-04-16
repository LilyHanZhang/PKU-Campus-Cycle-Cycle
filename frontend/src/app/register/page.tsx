"use client";
import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await axios.post(`${API_URL}/auth/register`, formData);
      router.push("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "注册失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-green-50 flex items-center justify-center p-8">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border-t-4 border-[#2ab26a]">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-[#1f874c] mb-2">燕园易骑</h1>
          <p className="text-gray-500">校园自行车循环回收平台</p>
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">注册账号</h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-bold mb-2">姓名</label>
            <input
              type="text"
              required
              placeholder="张三"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">邮箱</label>
            <input
              type="email"
              required
              placeholder="your@pku.edu.cn"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">密码</label>
            <input
              type="password"
              required
              minLength={6}
              placeholder="至少6位字符"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#2ab26a] text-white py-3 rounded-full font-bold hover:bg-[#1f874c] transition shadow-md disabled:bg-gray-400"
          >
            {loading ? "注册中..." : "注册"}
          </button>
        </form>

        <p className="text-center mt-6 text-gray-600">
          已有账号？{" "}
          <Link href="/login" className="text-[#2ab26a] font-bold hover:underline">
            立即登录
          </Link>
        </p>
      </div>
    </div>
  );
}
