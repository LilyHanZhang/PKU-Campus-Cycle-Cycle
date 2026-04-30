"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Calendar,
  Bike,
  Sparkles,
  Timer
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface TimeSlot {
  id: string;
  start_time: string;
  end_time: string;
  is_booked: string;
}

interface Bicycle {
  id: string;
  brand: string;
  color: string;
  status: string;
  availableSlots: TimeSlot[];
}

interface Appointment {
  id: string;
  type: string;
  status: string;
  time_slot_id?: string;
  availableSlots: TimeSlot[];
}

export default function MyTimeSlotsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [pendingBicycles, setPendingBicycles] = useState<Bicycle[]>([]);
  const [pendingAppointments, setPendingAppointments] = useState<Appointment[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<'bicycle' | 'appointment' | null>(null);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

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
      const bikesResponse = await axios.get(`${API_URL}/bicycles/`, { headers });
      const myBikes = bikesResponse.data.filter((b: any) => 
        String(b.owner_id) === user.id && 
        (b.status === 'PENDING_SELLER_SLOT_SELECTION' || b.status === 'PENDING_APPROVAL')
      );
      
      const appointmentsResponse = await axios.get(`${API_URL}/appointments/user/${user.id}`, { headers });
      const myAppointments = appointmentsResponse.data.filter((apt: any) => 
        (apt.status === 'PENDING' || apt.status === 'CONFIRMED') &&
        !apt.time_slot_id
      );

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

  const handleConfirmSelection = async () => {
    if (!selectedSlot || !selectedItem || !selectedType) return;

    setSubmitting(true);
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const endpoint = selectedType === 'bicycle' 
        ? `${API_URL}/time_slots/select-bicycle/${selectedItem.id}`
        : `${API_URL}/time_slots/select/${selectedItem.id}`;
      
      await axios.put(endpoint, 
        { time_slot_id: selectedSlot },
        { headers }
      );
      
      alert("✓ 时间段选择成功！等待管理员确认。");
      setSelectedSlot(null);
      setSelectedType(null);
      setSelectedItem(null);
      fetchData();
    } catch (error: any) {
      console.error("Failed to select time slot", error);
      alert(`操作失败：${error.response?.data?.detail || "请重试"}`);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      weekday: 'short'
    });
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const groupSlotsByDate = (slots: TimeSlot[]) => {
    const grouped: { [key: string]: TimeSlot[] } = {};
    slots.forEach(slot => {
      const dateKey = new Date(slot.start_time).toLocaleDateString('zh-CN');
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(slot);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-700 font-medium">加载中...</p>
        </div>
      </div>
    );
  }

  const hasAvailableSlots = pendingBicycles.some(b => b.availableSlots?.length > 0) || 
                            pendingAppointments.some(a => a.availableSlots?.length > 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl p-8 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center mb-3">
                  <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-4 rounded-2xl shadow-lg mr-4">
                    <Clock className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h1 className="text-4xl font-black text-gray-900 mb-1">时间段选择</h1>
                    <p className="text-gray-600">选择您的交易时间</p>
                  </div>
                </div>
              </div>
              <div className="hidden md:flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-full shadow-lg">
                <Sparkles className="w-5 h-5" />
                <span className="font-bold">快速选择</span>
              </div>
            </div>
          </div>
        </header>

        {/* Confirmation Bar */}
        {selectedSlot && (
          <div className="mb-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-3xl shadow-xl p-6 text-white animate-pulse">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-white/20 backdrop-blur-sm p-3 rounded-full">
                  <CheckCircle className="w-8 h-8" />
                </div>
                <div>
                  <p className="font-bold text-lg">已选择时间段</p>
                  <p className="text-blue-100">
                    {selectedItem && (selectedType === 'bicycle' ? 
                      `${selectedItem.brand} - ${selectedItem.color}` : 
                      `预约 ${selectedItem.id.slice(0, 8)}...`)}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => {
                    setSelectedSlot(null);
                    setSelectedType(null);
                    setSelectedItem(null);
                  }}
                  className="px-6 py-3 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full font-bold transition-all flex items-center"
                >
                  <XCircle className="w-5 h-5 mr-2" />
                  取消
                </button>
                <button
                  onClick={handleConfirmSelection}
                  disabled={submitting}
                  className="px-8 py-3 bg-white text-blue-600 hover:bg-blue-50 rounded-full font-bold shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {submitting ? (
                    <>
                      <Timer className="w-5 h-5 mr-2 animate-spin" />
                      提交中...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5 mr-2" />
                      确认选择
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* No Data State */}
        {!hasAvailableSlots && (
          <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl p-12 text-center">
            <div className="bg-gradient-to-br from-gray-100 to-gray-200 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">暂无可选时间段</h3>
            <p className="text-gray-600 mb-6">管理员还未提出时间段，请耐心等待</p>
            <div className="inline-flex items-center bg-blue-50 text-blue-600 px-6 py-3 rounded-full font-medium">
              <Timer className="w-5 h-5 mr-2" />
              有可用时间段时会自动通知您
            </div>
          </div>
        )}

        {/* Bicycles Section */}
        {pendingBicycles.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center mb-6">
              <div className="bg-gradient-to-br from-emerald-500 to-green-500 p-3 rounded-xl shadow-lg mr-4">
                <Bike className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">我的自行车登记</h2>
            </div>
            
            <div className="grid gap-6">
              {pendingBicycles.map((bike) => (
                <div 
                  key={bike.id} 
                  className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl overflow-hidden border border-white/20 transition-all hover:shadow-2xl"
                >
                  {/* Bike Info Header */}
                  <div className="bg-gradient-to-r from-emerald-500 to-green-500 p-6">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-4">
                        <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
                          <Bike className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold text-white mb-1">
                            {bike.brand} - {bike.color}
                          </h3>
                          <p className="text-emerald-100 font-medium">
                            {bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? '待选择时间段' : '待审核'}
                          </p>
                        </div>
                      </div>
                      {bike.status === 'PENDING_SELLER_SLOT_SELECTION' && (
                        <span className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-full font-bold text-sm flex items-center">
                          <Clock className="w-4 h-4 mr-2" />
                          请选择时间段
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Time Slots Timeline */}
                  {bike.availableSlots && bike.availableSlots.length > 0 ? (
                    <div className="p-6">
                      <div className="flex items-center mb-4">
                        <Calendar className="w-5 h-5 text-blue-600 mr-2" />
                        <span className="font-bold text-gray-700">可选时间段</span>
                      </div>
                      
                      <div className="relative">
                        {/* Timeline Line */}
                        <div className="absolute left-8 top-4 bottom-4 w-1 bg-gradient-to-b from-blue-200 to-cyan-200 rounded-full"></div>
                        
                        <div className="space-y-4">
                          {Object.entries(groupSlotsByDate(bike.availableSlots)).map(([date, slots]) => (
                            <div key={date} className="relative">
                              {/* Date Badge */}
                              <div className="flex items-center mb-3 ml-2">
                                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-2 rounded-full font-bold text-sm shadow-lg z-10">
                                  {date}
                                </div>
                              </div>
                              
                              {/* Slots */}
                              <div className="space-y-3">
                                {slots.map((slot) => {
                                  const isSelected = selectedSlot === slot.id && selectedType === 'bicycle';
                                  return (
                                    <div
                                      key={slot.id}
                                      onClick={() => {
                                        if (bike.status !== 'PENDING_SELLER_SLOT_SELECTION') return;
                                        setSelectedSlot(slot.id);
                                        setSelectedType('bicycle');
                                        setSelectedItem(bike);
                                      }}
                                      className={`relative ml-6 p-5 rounded-2xl border-2 transition-all cursor-pointer ${
                                        isSelected
                                          ? 'bg-gradient-to-r from-blue-500 to-cyan-500 border-blue-500 shadow-xl scale-105'
                                          : 'bg-white border-gray-200 hover:border-blue-400 hover:shadow-lg hover:scale-102'
                                      } ${bike.status !== 'PENDING_SELLER_SLOT_SELECTION' ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    >
                                      {/* Timeline Dot */}
                                      <div className={`absolute -left-10 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-4 ${
                                        isSelected ? 'bg-white border-blue-500' : 'bg-white border-gray-300'
                                      }`}></div>
                                      
                                      <div className="flex justify-between items-center">
                                        <div className="flex items-center space-x-6">
                                          <div className="flex items-center space-x-2">
                                            <Clock className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-blue-600'}`} />
                                            <span className={`text-lg font-bold ${isSelected ? 'text-white' : 'text-gray-800'}`}>
                                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                                            </span>
                                          </div>
                                          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                                            isSelected ? 'bg-white/20 text-white' : 'bg-blue-50 text-blue-600'
                                          }`}>
                                            {formatDate(slot.start_time)}
                                          </div>
                                        </div>
                                        {isSelected && (
                                          <div className="flex items-center text-white font-bold">
                                            <CheckCircle className="w-6 h-6 mr-2" />
                                            已选择
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? (
                    <div className="p-8 text-center">
                      <div className="bg-gradient-to-br from-yellow-100 to-orange-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <AlertCircle className="w-10 h-10 text-yellow-600" />
                      </div>
                      <p className="text-gray-600 font-medium">管理员还未提出时间段，请耐心等待</p>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Appointments Section */}
        {pendingAppointments.length > 0 && (
          <section>
            <div className="flex items-center mb-6">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-xl shadow-lg mr-4">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">我的自行车预约</h2>
            </div>
            
            <div className="grid gap-6">
              {pendingAppointments.map((apt) => (
                <div 
                  key={apt.id} 
                  className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl overflow-hidden border border-white/20 transition-all hover:shadow-2xl"
                >
                  {/* Appointment Info Header */}
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-4">
                        <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
                          <Calendar className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-white mb-1">
                            预约 {apt.id.slice(0, 8)}...
                          </h3>
                          <div className="flex items-center space-x-3 text-purple-100 font-medium">
                            <span>{apt.type === 'pick-up' ? '🚴 自提' : '📦 送货'}</span>
                            <span>•</span>
                            <span>{apt.status === 'PENDING' ? '待选择时间段' : '已确认'}</span>
                          </div>
                        </div>
                      </div>
                      {apt.status === 'PENDING' && (
                        <span className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-full font-bold text-sm flex items-center">
                          <Clock className="w-4 h-4 mr-2" />
                          请选择时间段
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Time Slots Timeline */}
                  {apt.availableSlots && apt.availableSlots.length > 0 ? (
                    <div className="p-6">
                      <div className="flex items-center mb-4">
                        <Calendar className="w-5 h-5 text-blue-600 mr-2" />
                        <span className="font-bold text-gray-700">可选时间段</span>
                      </div>
                      
                      <div className="relative">
                        {/* Timeline Line */}
                        <div className="absolute left-8 top-4 bottom-4 w-1 bg-gradient-to-b from-purple-200 to-pink-200 rounded-full"></div>
                        
                        <div className="space-y-4">
                          {Object.entries(groupSlotsByDate(apt.availableSlots)).map(([date, slots]) => (
                            <div key={date} className="relative">
                              {/* Date Badge */}
                              <div className="flex items-center mb-3 ml-2">
                                <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-full font-bold text-sm shadow-lg z-10">
                                  {date}
                                </div>
                              </div>
                              
                              {/* Slots */}
                              <div className="space-y-3">
                                {slots.map((slot) => {
                                  const isSelected = selectedSlot === slot.id && selectedType === 'appointment';
                                  return (
                                    <div
                                      key={slot.id}
                                      onClick={() => {
                                        if (apt.status !== 'PENDING') return;
                                        setSelectedSlot(slot.id);
                                        setSelectedType('appointment');
                                        setSelectedItem(apt);
                                      }}
                                      className={`relative ml-6 p-5 rounded-2xl border-2 transition-all cursor-pointer ${
                                        isSelected
                                          ? 'bg-gradient-to-r from-purple-500 to-pink-500 border-purple-500 shadow-xl scale-105'
                                          : 'bg-white border-gray-200 hover:border-purple-400 hover:shadow-lg hover:scale-102'
                                      } ${apt.status !== 'PENDING' ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    >
                                      {/* Timeline Dot */}
                                      <div className={`absolute -left-10 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-4 ${
                                        isSelected ? 'bg-white border-purple-500' : 'bg-white border-gray-300'
                                      }`}></div>
                                      
                                      <div className="flex justify-between items-center">
                                        <div className="flex items-center space-x-6">
                                          <div className="flex items-center space-x-2">
                                            <Clock className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-purple-600'}`} />
                                            <span className={`text-lg font-bold ${isSelected ? 'text-white' : 'text-gray-800'}`}>
                                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                                            </span>
                                          </div>
                                          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                                            isSelected ? 'bg-white/20 text-white' : 'bg-purple-50 text-purple-600'
                                          }`}>
                                            {formatDate(slot.start_time)}
                                          </div>
                                        </div>
                                        {isSelected && (
                                          <div className="flex items-center text-white font-bold">
                                            <CheckCircle className="w-6 h-6 mr-2" />
                                            已选择
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : apt.status === 'PENDING' ? (
                    <div className="p-8 text-center">
                      <div className="bg-gradient-to-br from-yellow-100 to-orange-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <AlertCircle className="w-10 h-10 text-yellow-600" />
                      </div>
                      <p className="text-gray-600 font-medium">管理员还未提出时间段，请耐心等待</p>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
