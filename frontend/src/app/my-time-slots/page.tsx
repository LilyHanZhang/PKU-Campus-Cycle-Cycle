"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function MyTimeSlotsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [pendingBicycles, setPendingBicycles] = useState<any[]>([]);
  const [pendingAppointments, setPendingAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchData();
  }, [isAuthenticated, router]);

  const fetchData = async () => {
    if (!user) return;
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      // 获取我的自行车
      const bikesResponse = await axios.get(`${API_URL}/bicycles/`, { headers });
      const myBikes = bikesResponse.data.filter((b: any) => 
        String(b.owner_id) === user.id && 
        (b.status === 'PENDING_SELLER_SLOT_SELECTION' || b.status === 'PENDING_APPROVAL')
      );
      
      // 获取我的预约
      const appointmentsResponse = await axios.get(`${API_URL}/appointments/user/${user.id}`, { headers });
      const myAppointments = appointmentsResponse.data.filter((apt: any) => 
        (apt.status === 'PENDING' || apt.status === 'CONFIRMED') &&
        !apt.time_slot_id  // 只显示还未选择时间段的预约
      );

      // 获取每个自行车/预约的可选时间段
      const bikesWithSlots = await Promise.all(
        myBikes.map(async (bike: any) => {
          try {
            const slotsResponse = await axios.get(
              `${API_URL}/time_slots/bicycle/${bike.id}`,
              { headers }
            );
            return { ...bike, availableSlots: slotsResponse.data };
          } catch (error) {
            console.error(`Failed to fetch slots for bike ${bike.id}`, error);
            return { ...bike, availableSlots: [] };
          }
        })
      );

      const appointmentsWithSlots = await Promise.all(
        myAppointments.map(async (apt: any) => {
          try {
            const slotsResponse = await axios.get(
              `${API_URL}/time_slots/appointment/${apt.id}`,
              { headers }
            );
            return { ...apt, availableSlots: slotsResponse.data };
          } catch (error) {
            console.error(`Failed to fetch slots for appointment ${apt.id}`, error);
            return { ...apt, availableSlots: [] };
          }
        })
      );

      setPendingBicycles(bikesWithSlots);
      setPendingAppointments(appointmentsWithSlots);
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTimeSlot = async (item: any, slotId: string, type: 'bicycle' | 'appointment') => {
    if (!confirm("确定选择这个时间段吗？")) return;

    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const endpoint = type === 'bicycle' 
        ? `${API_URL}/time_slots/select-bicycle/${item.id}`
        : `${API_URL}/time_slots/select/${item.id}`;
      
      await axios.put(endpoint, 
        { time_slot_id: slotId },
        { headers }
      );
      
      alert("✓ 时间段选择成功！等待管理员确认。");
      fetchData();
    } catch (error: any) {
      console.error("Failed to select time slot", error);
      alert(`操作失败：${error.response?.data?.detail || "请重试"}`);
    }
  };

  const formatDateTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">我的时间段选择</h1>
          <p className="text-gray-600">查看并选择管理员提出的时间段</p>
        </header>

        {/* 卖家自行车时间段 */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
            <Clock className="w-6 h-6 mr-2" />
            我的自行车登记
          </h2>
          
          {pendingBicycles.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
              <AlertCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p>暂无待处理的自行车登记</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {pendingBicycles.map((bike) => (
                <div key={bike.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">
                        {bike.brand} - {bike.color}
                      </h3>
                      <p className="text-sm text-gray-600">
                        状态：{bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? '待选择时间段' : '待审核'}
                      </p>
                    </div>
                    {bike.status === 'PENDING_SELLER_SLOT_SELECTION' && (
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                        请选择时间段
                      </span>
                    )}
                  </div>

                  {bike.availableSlots && bike.availableSlots.length > 0 ? (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-3">可选时间段：</p>
                      <div className="space-y-2">
                        {bike.availableSlots.map((slot: any) => (
                          <div
                            key={slot.id}
                            className="flex justify-between items-center p-3 bg-gray-50 rounded border hover:border-blue-500 transition-colors"
                          >
                            <div className="flex-1">
                              <p className="text-sm text-gray-800">
                                {formatDateTime(slot.start_time)} - {formatDateTime(slot.end_time)}
                              </p>
                            </div>
                            <button
                              onClick={() => handleSelectTimeSlot(bike, slot.id, 'bicycle')}
                              className="ml-4 px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 transition-colors flex items-center"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              选择
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? (
                    <div className="text-center py-4 text-gray-500">
                      <AlertCircle className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
                      <p>管理员还未提出时间段，请耐心等待</p>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* 买家预约时间段 */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
            <Clock className="w-6 h-6 mr-2" />
            我的自行车预约
          </h2>
          
          {pendingAppointments.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
              <AlertCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p>暂无待处理的自行车预约</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {pendingAppointments.map((apt) => (
                <div key={apt.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">
                        预约 ID: {apt.id.slice(0, 8)}...
                      </h3>
                      <p className="text-sm text-gray-600">
                        类型：{apt.type === 'pick-up' ? '自提' : '送货'}
                        {' · '}
                        状态：{apt.status === 'PENDING' ? '待选择时间段' : '已确认'}
                      </p>
                    </div>
                    {apt.status === 'PENDING' && (
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                        请选择时间段
                      </span>
                    )}
                  </div>

                  {apt.availableSlots && apt.availableSlots.length > 0 ? (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-3">可选时间段：</p>
                      <div className="space-y-2">
                        {apt.availableSlots.map((slot: any) => (
                          <div
                            key={slot.id}
                            className="flex justify-between items-center p-3 bg-gray-50 rounded border hover:border-blue-500 transition-colors"
                          >
                            <div className="flex-1">
                              <p className="text-sm text-gray-800">
                                {formatDateTime(slot.start_time)} - {formatDateTime(slot.end_time)}
                              </p>
                            </div>
                            <button
                              onClick={() => handleSelectTimeSlot(apt, slot.id, 'appointment')}
                              className="ml-4 px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 transition-colors flex items-center"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              选择
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : apt.status === 'PENDING' ? (
                    <div className="text-center py-4 text-gray-500">
                      <AlertCircle className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
                      <p>管理员还未提出时间段，请耐心等待</p>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
