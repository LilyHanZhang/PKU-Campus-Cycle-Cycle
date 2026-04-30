"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { 
  LayoutDashboard, 
  Truck, 
  Users, 
  Calendar, 
  History, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  ChevronRight,
  Package,
  Timer,
  UserCheck
} from "lucide-react";

// 生产环境 API 地址
const API_URL = "https://pku-campus-cycle-cycle.onrender.com";

// Countdown Timer Component
function CountdownTimer({ slot }: { slot: any }) {
  const [timeLeft, setTimeLeft] = useState(slot.countdown_seconds);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev: number) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const days = Math.floor(seconds / (3600 * 24));
    const hours = Math.floor((seconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (days > 0) {
      return `${days}天 ${hours}小时 ${minutes}分钟`;
    } else if (hours > 0) {
      return `${hours}小时 ${minutes}分钟 ${secs}秒`;
    } else if (minutes > 0) {
      return `${minutes}分钟 ${secs}秒`;
    } else {
      return `${secs}秒`;
    }
  };

  const isUrgent = timeLeft < 3600; // Less than 1 hour

  return (
    <div className={`p-5 rounded-2xl border-2 transition-all ${
      isUrgent 
        ? 'border-red-300 bg-red-50 shadow-lg shadow-red-100' 
        : 'border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100'
    }`}>
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <Clock size={18} className={isUrgent ? 'text-red-500' : 'text-slate-400'} />
            <p className="font-bold text-gray-800">时间段：{new Date(slot.start_time).toLocaleString('zh-CN')}</p>
          </div>
          <p className="text-sm text-gray-500 ml-7">
            类型：<span className={`font-bold ${
              slot.appointment_type === 'pick-up' ? 'text-amber-600' : 'text-blue-600'
            }`}>
              {slot.appointment_type === 'pick-up' ? '取车' : '还车'}
            </span>
          </p>
        </div>
        <div className={`text-3xl font-black ${
          isUrgent ? 'text-red-600' : 'text-emerald-600'
        }`}>
          {timeLeft > 0 ? formatTime(timeLeft) : '已过期'}
        </div>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [pendingBikes, setPendingBikes] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [allBikes, setAllBikes] = useState([]);
  const [allAppointments, setAllAppointments] = useState([]);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [error, setError] = useState("");

  useEffect(() => {
    console.log('Auth state:', { authLoading, isAuthenticated, user });
    if (!authLoading) {
      if (!user) {
        console.log('No user, redirecting to login');
        window.location.href = "/login";
        return;
      }
      if (user.role === "USER") {
        console.log('User role is USER, redirecting');
        alert("您没有权限访问此页面");
        window.location.href = "/";
        return;
      }
      // 管理员权限，继续加载
      console.log('Admin user detected:', user.role);
    }
  }, [authLoading, isAuthenticated, user]);

  useEffect(() => {
    if (user && (user.role === "ADMIN" || user.role === "SUPER_ADMIN")) {
      console.log('Fetching data for admin user');
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      console.log('Fetching admin dashboard data...');
      const [pendingRes, usersRes, bikesRes, appointmentsRes, dashboardRes] = await Promise.all([
        axios.get(`${API_URL}/bicycles/?status=PENDING_APPROVAL`, { headers }),
        axios.get(`${API_URL}/users/`, { headers }),
        axios.get(`${API_URL}/bicycles/`, { headers }),
        axios.get(`${API_URL}/appointments/`, { headers }),
        axios.get(`${API_URL}/bicycles/admin/dashboard`, { headers }),
      ]);
      console.log('Dashboard data loaded:', {
        pending: pendingRes.data.length,
        users: usersRes.data.length,
        bikes: bikesRes.data.length,
        appointments: appointmentsRes.data.length,
        dashboard: dashboardRes.data
      });
      setPendingBikes(pendingRes.data);
      setAllUsers(usersRes.data);
      setAllBikes(bikesRes.data);
      // 只显示 PENDING 和 CONFIRMED 状态的预约
      const activeAppointments = appointmentsRes.data.filter((apt: any) => 
        apt.status === 'PENDING' || apt.status === 'CONFIRMED'
      );
      setAllAppointments(activeAppointments);
      setDashboardData(dashboardRes.data);
    } catch (err: any) {
      console.error("Failed to fetch data", err);
      console.error("Error response:", err.response?.data);
      setError(`获取数据失败：${err.response?.data?.detail || err.message || "未知错误"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleProposeTimeSlots = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    
    // 创建多个时间段输入框
    const tempDiv = document.createElement('div');
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    
    tempDiv.innerHTML = `
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); z-index: 9999; max-height: 80vh; overflow-y: auto; min-width: 550px;">
        <h3 style="margin-bottom: 15px; font-size: 20px; font-weight: bold; color: #1f2937;">为卖家提出时间段</h3>
        <p style="margin-bottom: 15px; color: #6b7280; font-size: 14px; line-height: 1.6;">
          <strong>使用说明：</strong><br/>
          1. 点击日期时间输入框，会弹出日期选择器<br/>
          2. 选择日期后，在时间部分可以直接点击小时或分钟数字进行选择<br/>
          3. 也可以直接在输入框中手动输入时间（格式：YYYY-MM-DD HH:MM）<br/>
          4. 请至少提出 1 个时间段（可添加多个）
        </p>
        <div id="slotsContainer" style="max-height: 350px; overflow-y: auto; margin-bottom: 15px;"></div>
        <button id="addSlotBtn" style="width: 100%; padding: 10px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; margin-bottom: 15px; font-weight: 600;">+ 添加时间段</button>
        <div style="display: flex; gap: 10px;">
          <button id="submitBtn" style="flex: 1; padding: 12px; background: #2ab26a; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">提交</button>
          <button id="cancelBtn" style="flex: 1; padding: 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">取消</button>
        </div>
      </div>
      <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9998;"></div>
    `;
    document.body.appendChild(tempDiv);

    const slotsContainer = document.getElementById('slotsContainer')!;
    let slotCount = 0;

    const addSlotInput = () => {
      slotCount++;
      const slotDiv = document.createElement('div');
      slotDiv.className = 'slot-input';
      slotDiv.style.cssText = 'margin-bottom: 12px; padding: 12px; background: #f9fafb; border-radius: 6px; border: 1px solid #e5e7eb;';
      slotDiv.innerHTML = `
        <div style="display: flex; gap: 12px; align-items: center;">
          <div style="flex: 1;">
            <label style="display: block; margin-bottom: 6px; font-size: 13px; font-weight: 600; color: #374151;">开始时间</label>
            <input type="datetime-local" class="startTime" min="${minDateTime}" step="60" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" />
          </div>
          <div style="flex: 1;">
            <label style="display: block; margin-bottom: 6px; font-size: 13px; font-weight: 600; color: #374151;">结束时间</label>
            <input type="datetime-local" class="endTime" min="${minDateTime}" step="60" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" />
          </div>
          ${slotCount > 1 ? '<button class="removeSlot" style="padding: 8px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold;">×</button>' : ''}
        </div>
      `;
      slotsContainer.appendChild(slotDiv);

      // 移除按钮事件
      const removeBtn = slotDiv.querySelector('.removeSlot');
      if (removeBtn) {
        removeBtn.addEventListener('click', () => {
          if (slotsContainer.children.length > 1) {
            slotsContainer.removeChild(slotDiv);
          } else {
            alert("至少需要一个时间段");
          }
        });
      }
    };

    // 添加第一个时间段
    addSlotInput();

    const addSlotBtn = document.getElementById('addSlotBtn');
    addSlotBtn?.addEventListener('click', addSlotInput);

    const cancelBtn = document.getElementById('cancelBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    const cleanup = () => {
      document.body.removeChild(tempDiv);
    };

    cancelBtn?.addEventListener('click', cleanup);

    submitBtn?.addEventListener('click', async () => {
      const startTimeInputs = document.querySelectorAll('.startTime') as NodeListOf<HTMLInputElement>;
      const endTimeInputs = document.querySelectorAll('.endTime') as NodeListOf<HTMLInputElement>;
      
      const timeSlots = [];
      let hasError = false;
      
      for (let i = 0; i < startTimeInputs.length; i++) {
        const startTime = startTimeInputs[i].value.trim();
        const endTime = endTimeInputs[i].value.trim();
        
        console.log(`Slot ${i}: start="${startTime}", end="${endTime}"`);
        
        // 检查是否为空
        if (!startTime || !endTime) {
          alert("请填写所有时间段");
          hasError = true;
          break;
        }
        
        // 验证时间格式 - datetime-local 返回 "YYYY-MM-DDTHH:mm" 格式
        const start = new Date(startTime);
        const end = new Date(endTime);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
          alert("时间格式不正确，请重新选择时间");
          hasError = true;
          break;
        }
        
        if (start >= end) {
          alert("开始时间必须早于结束时间");
          hasError = true;
          break;
        }
        
        // 验证时间不是过去的时间
        if (start < new Date()) {
          alert("开始时间不能是过去的时间");
          hasError = true;
          break;
        }
        
        timeSlots.push({
          start_time: start.toISOString(),
          end_time: end.toISOString()
        });
      }
      
      if (hasError || timeSlots.length === 0) {
        console.log("Validation failed:", { hasError, timeSlots: timeSlots.length });
        return;
      }

      try {
        await axios.post(
          `${API_URL}/bicycles/${bikeId}/propose-slots`,
          timeSlots,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        alert(`✓ 已提出 ${timeSlots.length} 个时间段，等待卖家选择！`);
        cleanup();
        fetchData();
      } catch (err: any) {
        console.error("Failed to propose time slots", err);
        alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
      }
    });
  };

  const handleApprove = async (bikeId: string) => {
    // 买家场景：直接批准上架
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(`${API_URL}/bicycles/${bikeId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("车辆已批准上架！");
      fetchData();
    } catch (err) {
      console.error("Failed to approve bike", err);
      alert("操作失败，请重试。");
    }
  };

  const handleReject = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(`${API_URL}/bicycles/${bikeId}/reject`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("已拒绝并删除");
      fetchData();
    } catch (err) {
      console.error("Failed to reject bike", err);
      alert("操作失败，请重试。");
    }
  };

  const handleUpdateRole = async (userId: string, newRole: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/users/${userId}/role`,
        { role: newRole },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("角色更新成功！");
      fetchData();
    } catch (err) {
      console.error("Failed to update role", err);
      alert("操作失败，只有主负责人可以修改管理员权限。");
    }
  };

  const handleProposeAppointmentSlots = async (aptId: string) => {
    const token = localStorage.getItem("access_token");
    
    console.log("=== 提出时间段调试信息 ===");
    console.log("预约 ID:", aptId);
    console.log("预约 ID 类型:", typeof aptId);
    console.log("预约 ID 长度:", aptId.length);
    console.log("API URL:", `${API_URL}/appointments/${aptId}/propose-slots`);
    
    // 创建多个时间段输入框
    const tempDiv = document.createElement('div');
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    
    tempDiv.innerHTML = `
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); z-index: 9999; max-height: 80vh; overflow-y: auto; min-width: 550px;">
        <h3 style="margin-bottom: 15px; font-size: 20px; font-weight: bold; color: #1f2937;">为买家预约提出时间段</h3>
        <p style="margin-bottom: 15px; color: #6b7280; font-size: 14px; line-height: 1.6;">
          <strong>使用说明：</strong><br/>
          1. 点击日期时间输入框，会弹出日期选择器<br/>
          2. 选择日期后，在时间部分可以直接点击小时或分钟数字进行选择<br/>
          3. 也可以直接在输入框中手动输入时间（格式：YYYY-MM-DD HH:MM）<br/>
          4. 请至少提出 1 个时间段（可添加多个）
        </p>
        <div id="slotsContainer" style="max-height: 350px; overflow-y: auto; margin-bottom: 15px;"></div>
        <button id="addSlotBtn" style="width: 100%; padding: 10px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; margin-bottom: 15px; font-weight: 600;">+ 添加时间段</button>
        <div style="display: flex; gap: 10px;">
          <button id="submitBtn" style="flex: 1; padding: 12px; background: #2ab26a; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">提交</button>
          <button id="cancelBtn" style="flex: 1; padding: 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">取消</button>
        </div>
      </div>
      <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9998;"></div>
    `;
    document.body.appendChild(tempDiv);

    const slotsContainer = document.getElementById('slotsContainer')!;
    let slotCount = 0;

    const addSlotInput = () => {
      slotCount++;
      const slotDiv = document.createElement('div');
      slotDiv.className = 'slot-input';
      slotDiv.style.cssText = 'margin-bottom: 12px; padding: 12px; background: #f9fafb; border-radius: 6px; border: 1px solid #e5e7eb;';
      slotDiv.innerHTML = `
        <div style="display: flex; gap: 12px; align-items: center;">
          <div style="flex: 1;">
            <label style="display: block; margin-bottom: 6px; font-size: 13px; font-weight: 600; color: #374151;">开始时间</label>
            <input type="datetime-local" class="startTime" min="${minDateTime}" step="60" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" />
          </div>
          <div style="flex: 1;">
            <label style="display: block; margin-bottom: 6px; font-size: 13px; font-weight: 600; color: #374151;">结束时间</label>
            <input type="datetime-local" class="endTime" min="${minDateTime}" step="60" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" />
          </div>
          ${slotCount > 1 ? '<button class="removeSlot" style="padding: 8px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold;">×</button>' : ''}
        </div>
      `;
      slotsContainer.appendChild(slotDiv);

      const removeBtn = slotDiv.querySelector('.removeSlot');
      if (removeBtn) {
        removeBtn.addEventListener('click', () => {
          if (slotsContainer.children.length > 1) {
            slotsContainer.removeChild(slotDiv);
          } else {
            alert("至少需要一个时间段");
          }
        });
      }
    };

    addSlotInput();

    const addSlotBtn = document.getElementById('addSlotBtn');
    addSlotBtn?.addEventListener('click', addSlotInput);

    const cancelBtn = document.getElementById('cancelBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    const cleanup = () => {
      document.body.removeChild(tempDiv);
    };

    cancelBtn?.addEventListener('click', cleanup);

    submitBtn?.addEventListener('click', async () => {
      const startTimeInputs = document.querySelectorAll('.startTime') as NodeListOf<HTMLInputElement>;
      const endTimeInputs = document.querySelectorAll('.endTime') as NodeListOf<HTMLInputElement>;
      
      const timeSlots = [];
      let hasError = false;
      
      for (let i = 0; i < startTimeInputs.length; i++) {
        const startTime = startTimeInputs[i].value.trim();
        const endTime = endTimeInputs[i].value.trim();
        
        console.log(`Slot ${i}: start="${startTime}", end="${endTime}"`);
        
        // 检查是否为空
        if (!startTime || !endTime) {
          alert("请填写所有时间段");
          hasError = true;
          break;
        }
        
        // 验证时间格式 - datetime-local 返回 "YYYY-MM-DDTHH:mm" 格式
        const start = new Date(startTime);
        const end = new Date(endTime);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
          alert("时间格式不正确，请重新选择时间");
          hasError = true;
          break;
        }
        
        if (start >= end) {
          alert("开始时间必须早于结束时间");
          hasError = true;
          break;
        }
        
        // 验证时间不是过去的时间
        if (start < new Date()) {
          alert("开始时间不能是过去的时间");
          hasError = true;
          break;
        }
        
        timeSlots.push({
          start_time: start.toISOString(),
          end_time: end.toISOString()
        });
      }
      
      if (hasError || timeSlots.length === 0) {
        console.log("Validation failed:", { hasError, timeSlots: timeSlots.length });
        return;
      }

      try {
        console.log("发送请求...");
        await axios.post(
          `${API_URL}/appointments/${aptId}/propose-slots`,
          timeSlots,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        console.log("请求成功！");
        alert(`✓ 已提出 ${timeSlots.length} 个时间段，等待买家选择！`);
        cleanup();
        fetchData();
      } catch (err: any) {
        console.error("请求失败:", err);
        console.error("错误响应:", err.response?.data);
        console.error("错误状态码:", err.response?.status);
        alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
      }
    });
  };

  const handleConfirmTimeSlot = async (aptId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/time_slots/confirm/${aptId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("已确认时间段！");
      fetchData();
    } catch (err) {
      console.error("Failed to confirm time slot", err);
      alert("操作失败，请重试。");
    }
  };

  const handleConfirmPickup = async (aptId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/time_slots/confirm-pickup/${aptId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("已确认提车！");
      fetchData();
    } catch (err) {
      console.error("Failed to confirm pickup", err);
      alert("操作失败，请重试。");
    }
  };

  const handleConfirmBicycle = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(
        `${API_URL}/bicycles/${bikeId}/confirm`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("已确认自行车交易！");
      fetchData();
    } catch (err) {
      console.error("Failed to confirm bicycle", err);
      alert("操作失败，请重试。");
    }
  };

  const handleStoreInInventory = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/bicycles/${bikeId}/store-inventory`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("自行车已存入库存！");
      fetchData();
    } catch (err) {
      console.error("Failed to store bicycle", err);
      alert("操作失败，请重试。");
    }
  };

  // 显示加载状态
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载管理后台...</p>
        </div>
      </div>
    );
  }

  // 用户未登录
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">请先登录</p>
          <Link href="/login" className="text-green-600 font-bold hover:underline">
            前往登录
          </Link>
        </div>
      </div>
    );
  }

  // 用户没有权限
  if (user.role === "USER") {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">您没有权限访问此页面</p>
          <Link href="/" className="text-green-600 font-bold hover:underline">
            返回首页
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-3xl shadow-xl p-6 mb-8 border border-slate-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg">
                <LayoutDashboard size={28} className="text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">管理后台</h1>
                <p className="text-sm text-gray-500 mt-1">燕园易骑 · 校园自行车交易平台</p>
              </div>
              <span className={`ml-4 px-4 py-1.5 rounded-full text-sm font-bold ${
                user.role === "SUPER_ADMIN" ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"
              }`}>
                {user.role === "SUPER_ADMIN" ? "主负责人" : "管理员"}
              </span>
            </div>
            <Link href="/" className="text-gray-600 font-medium hover:text-emerald-600 transition-colors flex items-center">
              返回首页
              <ChevronRight size={16} className="ml-1" />
            </Link>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-2xl mb-6 flex items-center shadow-lg">
            <AlertCircle size={20} className="mr-3" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-2 mb-8 bg-white rounded-2xl p-2 shadow-lg border border-slate-100">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all flex items-center justify-center ${
              activeTab === "dashboard" 
                ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-md" 
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            <LayoutDashboard size={18} className="mr-2" />
            仪表盘 ({dashboardData?.pending_bicycles_count || 0})
          </button>
          <button
            onClick={() => setActiveTab("pending")}
            className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all flex items-center justify-center ${
              activeTab === "pending" 
                ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-md" 
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            <CheckCircle size={18} className="mr-2" />
            待审核车辆 ({pendingBikes.length})
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all flex items-center justify-center ${
              activeTab === "users" 
                ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-md" 
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            <Users size={18} className="mr-2" />
            用户管理 ({allUsers.length})
          </button>
          <button
            onClick={() => setActiveTab("bikes")}
            className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all flex items-center justify-center ${
              activeTab === "bikes" 
                ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-md" 
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            <Truck size={18} className="mr-2" />
            车辆管理 ({allBikes.length})
          </button>
          <button
            onClick={() => setActiveTab("appointments")}
            className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all flex items-center justify-center ${
              activeTab === "appointments" 
                ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-md" 
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            <Calendar size={18} className="mr-2" />
            预约管理 ({allAppointments.length})
          </button>
          <Link href="/history">
            <button className="flex-1 py-3 px-4 rounded-xl font-bold text-sm transition-all bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:from-purple-600 hover:to-purple-700 shadow-md flex items-center justify-center">
              <History size={18} className="mr-2" />
              历史记录
            </button>
          </Link>
        </div>

        {loading ? (
          <p className="text-center py-10">加载中...</p>
        ) : (
          <>
            {/* Dashboard Tab */}
            {activeTab === "dashboard" && dashboardData && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-3xl shadow-xl p-6 hover:shadow-2xl transition-all hover:-translate-y-1">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                        <Package size={24} />
                      </div>
                      <span className="text-xs font-bold bg-white/20 backdrop-blur-sm px-2 py-1 rounded-lg">待处理</span>
                    </div>
                    <h3 className="text-sm font-medium text-blue-100 mb-2">待处理自行车登记</h3>
                    <p className="text-5xl font-extrabold">{dashboardData.pending_bicycles_count}</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-3xl shadow-xl p-6 hover:shadow-2xl transition-all hover:-translate-y-1">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                        <Clock size={24} />
                      </div>
                      <span className="text-xs font-bold bg-white/20 backdrop-blur-sm px-2 py-1 rounded-lg">等待中</span>
                    </div>
                    <h3 className="text-sm font-medium text-purple-100 mb-2">等待确认预约</h3>
                    <p className="text-5xl font-extrabold">{dashboardData.pending_appointments_count}</p>
                  </div>
                  <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-3xl shadow-xl p-6 hover:shadow-2xl transition-all hover:-translate-y-1">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                        <Truck size={24} />
                      </div>
                      <span className="text-xs font-bold bg-white/20 backdrop-blur-sm px-2 py-1 rounded-lg">待确认</span>
                    </div>
                    <h3 className="text-sm font-medium text-amber-100 mb-2">等待确认自行车</h3>
                    <p className="text-5xl font-extrabold">{dashboardData.waiting_bicycles ? dashboardData.waiting_bicycles.length : 0}</p>
                  </div>
                  <div className="bg-gradient-to-br from-rose-500 to-rose-600 text-white rounded-3xl shadow-xl p-6 hover:shadow-2xl transition-all hover:-translate-y-1">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                        <Timer size={24} />
                      </div>
                      <span className="text-xs font-bold bg-white/20 backdrop-blur-sm px-2 py-1 rounded-lg">已锁定</span>
                    </div>
                    <h3 className="text-sm font-medium text-rose-100 mb-2">已锁定时间段</h3>
                    <p className="text-5xl font-extrabold">{dashboardData.locked_slots_with_countdown.length}</p>
                  </div>
                </div>

                {/* Countdown Timer */}
                {dashboardData.locked_slots_with_countdown.length > 0 && (
                  <div className="bg-white rounded-3xl shadow-xl p-6 border border-slate-100">
                    <div className="flex items-center mb-6">
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-rose-500 to-rose-600 flex items-center justify-center mr-3">
                        <Timer size={20} className="text-white" />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-800">⏰ 即将到期的时间段</h2>
                    </div>
                    <div className="space-y-4">
                      {dashboardData.locked_slots_with_countdown.map((slot: any) => (
                        <CountdownTimer key={slot.id} slot={slot} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Pending Bicycles List */}
                {dashboardData.pending_bicycles.length > 0 && (
                  <div className="bg-white rounded-3xl shadow-xl p-6 border border-slate-100">
                    <div className="flex items-center mb-6">
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mr-3">
                        <Package size={20} className="text-white" />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-800">待处理自行车登记</h2>
                    </div>
                    <div className="space-y-3">
                      {dashboardData.pending_bicycles.map((bike: any) => (
                        <div key={bike.id} className="p-5 bg-gradient-to-r from-slate-50 to-slate-100 rounded-2xl flex justify-between items-center hover:shadow-md transition-all">
                          <div>
                            <p className="font-bold text-gray-800 text-lg">{bike.brand}</p>
                            <p className="text-sm text-gray-500 mt-1">ID: {bike.id.slice(0, 8)}...</p>
                          </div>
                          <button
                            onClick={() => setActiveTab("pending")}
                            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 font-bold shadow-md transition-all flex items-center"
                          >
                            处理
                            <ChevronRight size={16} className="ml-1" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pending Appointments List */}
                {dashboardData.waiting_appointments && dashboardData.waiting_appointments.length > 0 && (
                  <div className="bg-white rounded-3xl shadow-xl p-6 border border-slate-100">
                    <div className="flex items-center mb-6">
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center mr-3">
                        <Clock size={20} className="text-white" />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-800">⏳ 等待确认的预约（买家已选时间段）</h2>
                    </div>
                    <div className="space-y-3">
                      {dashboardData.waiting_appointments.map((apt: any) => (
                        <div key={apt.id} className="p-5 bg-gradient-to-r from-purple-50 to-purple-100/50 rounded-2xl flex justify-between items-center hover:shadow-md transition-all">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="px-3 py-1 bg-purple-200 text-purple-700 rounded-full text-xs font-bold">预约</span>
                              <p className="font-bold text-gray-800">ID: {apt.id.slice(0, 8)}...</p>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                              <span>用户：<span className="font-bold">{apt.username}</span></span>
                              <span>车辆：<span className="font-bold">{apt.bicycle_brand}</span></span>
                              <span className={`px-2 py-1 rounded ${
                                apt.type === 'pick-up' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'
                              }`}>
                                {apt.type === 'pick-up' ? '取车' : '还车'}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500 mt-2">时间段 ID: {apt.time_slot_id?.slice(0, 8)}...</p>
                          </div>
                          <button
                            onClick={() => handleConfirmTimeSlot(apt.id)}
                            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 font-bold shadow-md transition-all flex items-center"
                          >
                            <CheckCircle size={18} className="mr-2" />
                            确认时间段
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Waiting Bicycles List */}
                {dashboardData.waiting_bicycles && dashboardData.waiting_bicycles.length > 0 && (
                  <div className="bg-white rounded-3xl shadow-xl p-6 border border-slate-100">
                    <div className="flex items-center mb-6">
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center mr-3">
                        <Truck size={20} className="text-white" />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-800">⏳ 等待确认的自行车（卖家已选时间段）</h2>
                    </div>
                    <div className="space-y-3">
                      {dashboardData.waiting_bicycles.map((bike: any) => (
                        <div key={bike.id} className="p-5 bg-gradient-to-r from-amber-50 to-amber-100/50 rounded-2xl flex justify-between items-center hover:shadow-md transition-all">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="px-3 py-1 bg-amber-200 text-amber-700 rounded-full text-xs font-bold">车辆</span>
                              <p className="font-bold text-gray-800">车辆：{bike.brand}</p>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                              <span>卖家：<span className="font-bold">{bike.owner_username}</span></span>
                              <span>ID: {bike.id.slice(0, 8)}...</span>
                            </div>
                            <p className="text-xs text-gray-500 mt-2">时间段 ID: {bike.time_slot_id?.slice(0, 8)}...</p>
                          </div>
                          <button
                            onClick={() => handleConfirmBicycle(bike.id)}
                            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 font-bold shadow-md transition-all flex items-center"
                          >
                            <CheckCircle size={18} className="mr-2" />
                            确认交易
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pending Appointments List (old name for backward compatibility) */}
                {dashboardData.waiting_appointments && dashboardData.waiting_appointments.length > 0 && (
                  <div className="bg-white rounded-2xl shadow-xl p-6">
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">待处理预约</h2>
                    <div className="space-y-3">
                      {dashboardData.waiting_appointments.map((apt: any) => (
                        <div key={apt.id} className="p-4 bg-gray-50 rounded-lg flex justify-between items-center">
                          <div>
                            <p className="font-bold text-gray-800">预约 ID: {apt.id.slice(0, 8)}...</p>
                            <p className="text-sm text-gray-500">类型：{apt.type === 'pick-up' ? '取车' : '还车'}</p>
                          </div>
                          <button
                            onClick={() => setActiveTab("appointments")}
                            className="px-4 py-2 bg-[#2ab26a] text-white rounded-lg hover:bg-[#249a5c]"
                          >
                            处理
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Pending Bikes Tab */}
            {activeTab === "pending" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">待审核车辆</h2>
                {pendingBikes.length > 0 ? (
                      <div className="space-y-4">
                        {pendingBikes.map((bike: any) => (
                          <div key={bike.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-bold text-gray-700">{bike.brand}</p>
                              <p className="text-sm text-gray-500">
                                车主 ID: {bike.owner_id?.substring(0, 8)}... | 价格：¥{bike.price} | 成色：{bike.condition}/10
                              </p>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleProposeTimeSlots(bike.id)}
                                className="bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-600 transition"
                                title="卖家场景：提出时间段，等待卖家选择"
                              >
                                提出时间段
                              </button>
                              <button
                                onClick={() => handleApprove(bike.id)}
                                className="bg-green-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-600 transition"
                                title="买家场景：直接批准上架"
                              >
                                批准上架
                              </button>
                              <button
                                onClick={() => handleReject(bike.id)}
                                className="bg-red-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-red-600 transition"
                              >
                                拒绝
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">当前没有待审核的车辆。</p>
                    )}
              </div>
            )}

            {/* Users Tab */}
            {activeTab === "users" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Users className="mr-3 text-emerald-500" />用户管理
                </h2>
                {user.role === "SUPER_ADMIN" ? (
                  <div className="space-y-4">
                    {allUsers.map((u: any) => (
                      <div key={u.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="bg-gradient-to-br from-blue-400 to-blue-600 p-3 rounded-full text-white font-bold">
                            {(u.name || u.email).charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="font-bold text-gray-700">{u.name || "未命名"}</p>
                            <p className="text-sm text-gray-500">{u.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                            u.role === "SUPER_ADMIN" ? "bg-purple-100 text-purple-700" :
                            u.role === "ADMIN" ? "bg-blue-100 text-blue-700" :
                            "bg-gray-200 text-gray-600"
                          }`}>
                            {u.role === "SUPER_ADMIN" ? "主负责人" : u.role === "ADMIN" ? "管理员" : "普通用户"}
                          </span>
                          {u.role !== "SUPER_ADMIN" && (
                            <select
                              value={u.role}
                              onChange={(e) => handleUpdateRole(u.id, e.target.value)}
                              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            >
                              <option value="USER">设为普通用户</option>
                              <option value="ADMIN">设为管理员</option>
                            </select>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">您没有权限管理用户，只有主负责人可以。</p>
                )}
              </div>
            )}

            {/* Bikes Tab */}
            {activeTab === "bikes" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Truck className="mr-3 text-emerald-500" />所有车辆
                </h2>
                <div className="space-y-4">
                  {allBikes.map((bike: any) => (
                    <div key={bike.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                            <p className="font-bold text-gray-700">{bike.brand}</p>
                            <p className="text-sm text-gray-500">
                              ¥{bike.price} | 成色 {bike.condition}/10 | 状态：{
                                bike.status === 'PENDING_APPROVAL' ? '待审核' :
                                bike.status === 'IN_STOCK' ? '在库' :
                                bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? '等待卖家选择' :
                                bike.status === 'PENDING_BUYER_SLOT_SELECTION' ? '等待买家选择' :
                                bike.status === 'PENDING_ADMIN_CONFIRMATION_SELLER' ? '等待管理员确认（卖家）' :
                                bike.status === 'PENDING_ADMIN_CONFIRMATION_BUYER' ? '等待管理员确认（买家）' :
                                bike.status === 'RESERVED' ? '已预约' : '已售出'
                              }
                            </p>
                          </div>
                          <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                            bike.status === 'IN_STOCK' ? 'bg-green-100 text-green-700' :
                            bike.status === 'PENDING_APPROVAL' ? 'bg-yellow-100 text-yellow-700' :
                            bike.status === 'PENDING_SELLER_SLOT_SELECTION' || bike.status === 'PENDING_BUYER_SLOT_SELECTION' ? 'bg-orange-100 text-orange-700' :
                            bike.status === 'PENDING_ADMIN_CONFIRMATION_SELLER' || bike.status === 'PENDING_ADMIN_CONFIRMATION_BUYER' ? 'bg-purple-100 text-purple-700' :
                            bike.status === 'RESERVED' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-200 text-gray-600'
                          }`}>
                            {bike.status}
                          </span>
                          {bike.status === 'RESERVED' && (
                            <button
                              onClick={() => handleStoreInInventory(bike.id)}
                              className="ml-2 bg-green-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-600 transition"
                              title="线下交易完成，将自行车存入库存"
                            >
                              ✓ 确认入库
                            </button>
                          )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Appointments Tab */}
            {activeTab === "appointments" && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Calendar className="mr-3 text-emerald-500" />活跃预约
                </h2>
                <div className="space-y-4">
                  {allAppointments.map((apt: any) => {
                    // 查找对应的自行车信息
                    const bike = (allBikes as any[]).find((b: any) => b.id === apt.bicycle_id);
                    return (
                    <div key={apt.id} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-center mb-3">
                        <div>
                          <p className="font-bold text-gray-700">预约 ID: {apt.id.substring(0, 8)}...</p>
                          <p className="text-sm text-gray-500">
                            车辆：{bike ? bike.brand : '未知'} (ID: {apt.bicycle_id.substring(0, 8)}...) | 类型：{apt.type === 'drop-off' ? '交车' : '提车'}
                          </p>
                          <p className="text-sm text-gray-500">
                            状态：<span className={`px-2 py-1 rounded text-xs font-bold ${
                              apt.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                              apt.status === 'CONFIRMED' ? 'bg-blue-100 text-blue-700' :
                              apt.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>{apt.status}</span>
                          </p>
                        </div>
                        {apt.status === 'CONFIRMED' && apt.type === 'pick-up' && (
                          <button
                            onClick={() => handleConfirmPickup(apt.id)}
                            className="bg-green-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-600 transition"
                          >
                            确认提车
                          </button>
                        )}
                        {apt.status === 'CONFIRMED' && apt.type === 'drop-off' && (
                          <p className="text-sm text-gray-500">等待线下交车完成</p>
                        )}
                      </div>
                      
                      {/* 时间段管理 */}
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-sm font-bold text-gray-600 mb-2">时间段管理：</p>
                        {apt.status === 'PENDING' && (
                          <button
                            onClick={() => handleProposeAppointmentSlots(apt.id)}
                            className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-600 transition"
                          >
                            提出时间段
                          </button>
                        )}
                        {apt.status === 'CONFIRMED' && (
                          <p className="text-sm text-gray-500">时间段已确认，等待交易完成</p>
                        )}
                      </div>
                    </div>
                  );})}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
