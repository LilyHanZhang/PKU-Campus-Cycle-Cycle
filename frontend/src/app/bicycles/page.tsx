"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { ThumbsUp, Tag } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pku-campus-cycle-cycle.onrender.com";

interface Bicycle {
  id: string;
  brand: string;
  condition: number;
  price: number;
  status: string;
}

export default function BicyclesList() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [bicycles, setBicycles] = useState<Bicycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [claiming, setClaiming] = useState<string | null>(null);

  useEffect(() => {
    fetchBicycles();
  }, []);

  const fetchBicycles = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/bicycles/`);
      setBicycles(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (id: string, status: string) => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    if (status !== "IN_STOCK") return;
    setClaiming(id);
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(
        `${API_URL}/appointments/`,
        { bicycle_id: id, type: "pick-up" },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("预约成功！车辆已为您锁定！");
      fetchBicycles();
    } catch (err: any) {
      if (err.response && err.response.status === 400) {
         alert("手慢啦！刚被其他同学抢走了。看看别的车吧！");
      } else {
         alert("网络出错，请重试。");
      }
      fetchBicycles();
    } finally {
      setClaiming(null);
    }
  };

  return (
    <div className="min-h-screen bg-green-50 p-8 flex flex-col items-center">
      <div className="flex justify-between w-full max-w-5xl mb-12 items-center">
         <h1 className="text-4xl font-extrabold text-[#1f874c]">自行车库存 <span className="text-emerald-500 font-medium text-lg ml-2">找到属于你的"座驾"</span></h1>
         <Link href="/">
           <button className="text-emerald-600 font-bold hover:underline">返回首页</button>
         </Link>
      </div>

      {loading ? (
        <p className="text-gray-500 font-bold text-xl">稍等，拉取仓库中...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-5xl">
          {bicycles.map(bike => (
             <div
               key={bike.id}
               className={`bg-white rounded-2xl p-6 shadow-xl border-t-8 flex flex-col justify-between hover:-translate-y-2 transition-transform duration-300
                  ${bike.status === 'IN_STOCK' ? 'border-[#2ab26a] relative' : 'border-gray-300 opacity-60 grayscale'}`}
             >
                <div className="absolute top-4 right-4">
                  {bike.status === 'IN_STOCK'
                    ? <span className="bg-green-100 text-green-700 font-bold px-3 py-1 rounded-full text-xs shadow-sm">在库待认领</span>
                    : <span className="bg-gray-200 text-gray-700 font-bold px-3 py-1 rounded-full text-xs shadow-sm">已锁定</span>
                  }
                </div>

                <div>
                   <h3 className="text-2xl font-black text-gray-800 mb-4 pr-16 mt-2">{bike.brand}</h3>

                   <div className="flex items-center space-x-2 text-gray-600 mb-3 bg-gray-50 p-3 rounded-lg">
                      <ThumbsUp className="w-5 h-5 text-emerald-500" />
                      <span className="font-semibold">成色评分:</span>
                      <span className="text-xl font-bold text-gray-800">{bike.condition} <span className="text-sm font-normal">/ 10</span></span>
                   </div>

                   <div className="flex items-center space-x-2 text-gray-600 mb-6 bg-gray-50 p-3 rounded-lg">
                      <Tag className="w-5 h-5 text-emerald-500" />
                      <span className="font-semibold">转让价:</span>
                      {bike.price === 0 ? (
                         <span className="text-xl font-bold text-green-600">公益捐赠 (免费)</span>
                      ) : (
                         <span className="text-xl font-bold text-gray-800">¥ {bike.price}</span>
                      )}
                   </div>
                </div>

                <button
                  onClick={() => handleClaim(bike.id, bike.status)}
                  disabled={bike.status !== "IN_STOCK" || claiming === bike.id}
                  className={`w-full py-4 rounded-xl font-bold text-lg transition-all shadow-md mt-4
                    ${bike.status === 'IN_STOCK'
                       ? 'bg-[#2ab26a] text-white hover:bg-[#1f874c] cursor-pointer'
                       : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
                >
                  {claiming === bike.id ? "锁定中..." : (bike.status === "IN_STOCK" ? "一键抢先锁定试骑" : "已被预约")}
                </button>
             </div>
          ))}
          {bicycles.length === 0 && (
            <p className="text-gray-500 text-center col-span-full py-16 text-lg font-bold">阿哦, 目前仓库里没有闲置的自行车登记呢。</p>
          )}
        </div>
      )}
    </div>
  );
}
