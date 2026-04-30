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
  TrendingUp,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Plus,
  Search,
  Bell,
  Settings,
  LogOut,
  User as UserIcon
} from "lucide-react";

// 生产环境 API 地址
const API_URL = "https://pku-campus-cycle-cycle.onrender.com";

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
  const [searchQuery, setSearchQuery] = useState("");
  const [showUserMenu, setShowUserMenu] = useState(false);

  // 权限检查
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        window.location.href = "/login";
        return;
      }
      if (user.role === "USER") {
        alert("您没有权限访问此页面");
        window.location.href = "/";
        return;
      }
    }
  }, [authLoading, isAuthenticated, user]);

  // 加载数据
  useEffect(() => {
    if (user && (user.role === "ADMIN" || user.role === "SUPER_ADMIN")) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [pendingRes, usersRes, bikesRes, appointmentsRes, dashboardRes] = await Promise.all([
        axios.get(`${API_URL}/bicycles/?status=PENDING_APPROVAL`, { headers }),
        axios.get(`${API_URL}/users/`, { headers }),
        axios.get(`${API_URL}/bicycles/`, { headers }),
        axios.get(`${API_URL}/appointments/`, { headers }),
        axios.get(`${API_URL}/bicycles/admin/dashboard`, { headers }),
      ]);
      
      setPendingBikes(pendingRes.data);
      setAllUsers(usersRes.data);
      setAllBikes(bikesRes.data);
      const activeAppointments = appointmentsRes.data.filter((apt: any) => 
        apt.status === 'PENDING' || apt.status === 'CONFIRMED'
      );
      setAllAppointments(activeAppointments);
      setDashboardData(dashboardRes.data);
    } catch (err: any) {
      setError(`获取数据失败：${err.response?.data?.detail || err.message || "未知错误"}`);
    } finally {
      setLoading(false);
    }
  };

  // 处理审核通过
  const handleApprove = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(`${API_URL}/bicycles/${bikeId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("✓ 车辆已批准上架！");
      fetchData();
    } catch (err) {
      alert("操作失败，请重试。");
    }
  };

  // 处理审核拒绝
  const handleReject = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(`${API_URL}/bicycles/${bikeId}/reject`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("✓ 已拒绝并删除");
      fetchData();
    } catch (err) {
      alert("操作失败，请重试。");
    }
  };

  // 处理提出时间段
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

    // 添加时间段按钮
    document.getElementById('addSlotBtn')!.addEventListener('click', addSlotInput);

    // 取消按钮
    document.getElementById('cancelBtn')!.addEventListener('click', () => {
      document.body.removeChild(tempDiv);
    });

    // 提交按钮
    document.getElementById('submitBtn')!.addEventListener('click', async () => {
      const startTimeInputs = document.querySelectorAll('.startTime') as NodeListOf<HTMLInputElement>;
      const endTimeInputs = document.querySelectorAll('.endTime') as NodeListOf<HTMLInputElement>;
      
      const timeSlots: Array<{start_time: string; end_time: string}> = [];
      let hasError = false;

      for (let i = 0; i < startTimeInputs.length; i++) {
        const startTime = startTimeInputs[i].value;
        const endTime = endTimeInputs[i].value;

        if (!startTime || !endTime) {
          alert(`请填写第 ${i + 1} 个时间段的开始和结束时间`);
          hasError = true;
          break;
        }

        if (new Date(startTime) >= new Date(endTime)) {
          alert(`第 ${i + 1} 个时间段的开始时间必须早于结束时间`);
          hasError = true;
          break;
        }

        timeSlots.push({
          start_time: new Date(startTime).toISOString(),
          end_time: new Date(endTime).toISOString()
        });
      }
      
      if (hasError || timeSlots.length === 0) {
        return;
      }

      try {
        await axios.post(
          `${API_URL}/bicycles/${bikeId}/propose-slots`,
          timeSlots,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        alert(`✓ 已提出 ${timeSlots.length} 个时间段，等待卖家选择！`);
        document.body.removeChild(tempDiv);
        fetchData();
      } catch (err: any) {
        console.error("Failed to propose time slots", err);
        alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
      }
    });
  };

  // 确认时间段（买家已选择时间段后）
  const handleConfirmTimeSlot = async (aptId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/time_slots/confirm/${aptId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("✓ 已确认时间段！");
      fetchData();
    } catch (err: any) {
      console.error("Failed to confirm time slot", err);
      alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
    }
  };

  // 确认提车
  const handleConfirmPickup = async (aptId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.put(
        `${API_URL}/time_slots/confirm-pickup/${aptId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("✓ 已确认提车！");
      fetchData();
    } catch (err: any) {
      console.error("Failed to confirm pickup", err);
      alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
    }
  };

  // 确认自行车交易（卖家已选择时间段后）
  const handleConfirmBicycle = async (bikeId: string) => {
    const token = localStorage.getItem("access_token");
    try {
      await axios.post(
        `${API_URL}/bicycles/${bikeId}/confirm`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("✓ 已确认自行车交易！");
      fetchData();
    } catch (err: any) {
      console.error("Failed to confirm bicycle", err);
      alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
    }
  };

  // 为预约提出时间段
  const handleProposeAppointmentSlots = async (aptId: string) => {
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
        <h3 style="margin-bottom: 15px; font-size: 20px; font-weight: bold; color: #1f2937;">为预约提出时间段</h3>
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

    // 添加时间段按钮
    document.getElementById('addSlotBtn')!.addEventListener('click', addSlotInput);

    // 取消按钮
    document.getElementById('cancelBtn')!.addEventListener('click', () => {
      document.body.removeChild(tempDiv);
    });

    // 提交按钮
    document.getElementById('submitBtn')!.addEventListener('click', async () => {
      const startTimeInputs = document.querySelectorAll('.startTime') as NodeListOf<HTMLInputElement>;
      const endTimeInputs = document.querySelectorAll('.endTime') as NodeListOf<HTMLInputElement>;
      
      const timeSlots: Array<{start_time: string; end_time: string}> = [];
      let hasError = false;

      for (let i = 0; i < startTimeInputs.length; i++) {
        const startTime = startTimeInputs[i].value;
        const endTime = endTimeInputs[i].value;

        if (!startTime || !endTime) {
          alert(`请填写第 ${i + 1} 个时间段的开始和结束时间`);
          hasError = true;
          break;
        }

        if (new Date(startTime) >= new Date(endTime)) {
          alert(`第 ${i + 1} 个时间段的开始时间必须早于结束时间`);
          hasError = true;
          break;
        }

        timeSlots.push({
          start_time: new Date(startTime).toISOString(),
          end_time: new Date(endTime).toISOString()
        });
      }
      
      if (hasError || timeSlots.length === 0) {
        return;
      }

      try {
        await axios.post(
          `${API_URL}/appointments/${aptId}/propose-slots`,
          timeSlots,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        alert(`✓ 已提出 ${timeSlots.length} 个时间段，等待用户选择！`);
        document.body.removeChild(tempDiv);
        fetchData();
      } catch (err: any) {
        console.error("Failed to propose appointment time slots", err);
        alert(`操作失败：${err.response?.data?.detail || "请重试"}`);
      }
    });
  };

  // 过滤数据
  const filteredUsers = allUsers.filter((user: any) =>
    user.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredBikes = allBikes.filter((bike: any) =>
    bike.brand?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    bike.model?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredAppointments = allAppointments.filter((apt: any) =>
    apt.bicycle?.brand?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 渲染统计卡片
  const renderStatCard = (title: string, value: number, icon: any, color: string, trend?: string) => (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {trend && (
            <div className="flex items-center mt-2">
              <TrendingUp size={16} className="text-green-500 mr-1" />
              <span className="text-xs font-medium text-green-600">{trend}</span>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-xl ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  );

  // 渲染待审核列表
  const renderPendingBikes = () => (
    <div className="space-y-4">
      {pendingBikes.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <CheckCircle size={48} className="mx-auto text-green-500 mb-4" />
          <p className="text-gray-600 font-medium">没有待审核的车辆</p>
          <p className="text-sm text-gray-400 mt-2">所有车辆都已审核完毕</p>
        </div>
      ) : (
        pendingBikes.map((bike: any) => (
          <div key={bike.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                {bike.image_url ? (
                  <img src={bike.image_url} alt={bike.brand} className="w-24 h-24 rounded-xl object-cover" />
                ) : (
                  <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
                    <Truck size={32} className="text-blue-600" />
                  </div>
                )}
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">
                    {bike.brand} {bike.model}
                  </h3>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                    <div className="flex items-center text-gray-600">
                      <span className="w-20 text-gray-400">颜色:</span>
                      <span className="font-medium">{bike.color}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="w-20 text-gray-400">价格:</span>
                      <span className="font-medium">¥{bike.price}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="w-20 text-gray-400">车况:</span>
                      <span className="font-medium">{bike.condition}/10</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="w-20 text-gray-400">时间:</span>
                      <span className="font-medium">{new Date(bike.created_at).toLocaleDateString('zh-CN')}</span>
                    </div>
                  </div>
                  {bike.description && (
                    <p className="text-sm text-gray-500 mt-3 line-clamp-2">{bike.description}</p>
                  )}
                </div>
              </div>
              <div className="flex flex-col space-y-2 ml-4">
                <button
                  onClick={() => handleApprove(bike.id)}
                  className="flex items-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium text-sm"
                >
                  <CheckCircle size={16} className="mr-1" />
                  通过
                </button>
                <button
                  onClick={() => handleProposeTimeSlots(bike.id)}
                  className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium text-sm"
                >
                  <Calendar size={16} className="mr-1" />
                  提出时间段
                </button>
                <button
                  onClick={() => handleReject(bike.id)}
                  className="flex items-center px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-medium text-sm"
                >
                  <XCircle size={16} className="mr-1" />
                  拒绝
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );

  // 渲染用户列表
  const renderUsers = () => (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">用户</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">邮箱</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">角色</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">注册时间</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredUsers.map((userItem: any) => (
              <tr key={userItem.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm">
                      {userItem.name?.charAt(0).toUpperCase() || userItem.email.charAt(0).toUpperCase()}
                    </div>
                    <span className="ml-3 font-medium text-gray-900">{userItem.name || '未设置昵称'}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{userItem.email}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    userItem.role === 'SUPER_ADMIN' ? 'bg-purple-100 text-purple-700' :
                    userItem.role === 'ADMIN' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {userItem.role === 'SUPER_ADMIN' ? '主负责人' :
                     userItem.role === 'ADMIN' ? '管理员' : '普通用户'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {new Date(userItem.created_at).toLocaleDateString('zh-CN')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // 渲染车辆列表
  const renderBikes = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredBikes.map((bike: any) => (
        <div key={bike.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all">
          {bike.image_url ? (
            <img src={bike.image_url} alt={bike.brand} className="w-full h-48 object-cover" />
          ) : (
            <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
              <Truck size={64} className="text-blue-600" />
            </div>
          )}
          <div className="p-4">
            <h3 className="text-lg font-bold text-gray-900 mb-2">{bike.brand} {bike.model}</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">颜色</span>
                <span className="font-medium text-gray-900">{bike.color}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">价格</span>
                <span className="font-medium text-green-600">¥{bike.price}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">车况</span>
                <span className="font-medium text-gray-900">{bike.condition}/10</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">状态</span>
                <span className={`font-medium ${
                  bike.status === 'AVAILABLE' ? 'text-green-600' :
                  bike.status === 'PENDING_APPROVAL' ? 'text-yellow-600' :
                  bike.status === 'IN_STOCK' ? 'text-blue-600' :
                  'text-gray-600'
                }`}>
                  {bike.status === 'AVAILABLE' ? '可售' :
                   bike.status === 'PENDING_APPROVAL' ? '待审核' :
                   bike.status === 'IN_STOCK' ? '在库' :
                   bike.status === 'SOLD' ? '已售' : '其他'}
                </span>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              {bike.status === 'IN_STOCK' && (
                <button
                  onClick={() => handleProposeTimeSlots(bike.id)}
                  className="flex-1 flex items-center justify-center px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium text-sm"
                >
                  <Calendar size={16} className="mr-1" />
                  提出时间段
                </button>
              )}
              <Link href={`/bicycles/${bike.id}`}>
                <button className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm">
                  详情
                </button>
              </Link>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  // 渲染预约列表
  const renderAppointments = () => (
    <div className="space-y-4">
      {filteredAppointments.map((apt: any) => (
        <div key={apt.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4 flex-1">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <Calendar size={24} className="text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="text-lg font-bold text-gray-900">
                    {apt.bicycle?.brand} {apt.bicycle?.model}
                  </h3>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    apt.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                    apt.status === 'CONFIRMED' ? 'bg-blue-100 text-blue-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {apt.status === 'PENDING' ? '待确认' :
                     apt.status === 'CONFIRMED' ? '已确认' : '已完成'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <span className="w-20 text-gray-400">类型:</span>
                    <span className="font-medium">{apt.type === 'buyer' ? '买家取车' : '卖家还车'}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <span className="w-20 text-gray-400">用户:</span>
                    <span className="font-medium">{apt.user_name || '未知'}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <span className="w-20 text-gray-400">时间:</span>
                    <span className="font-medium">{new Date(apt.created_at).toLocaleDateString('zh-CN')}</span>
                  </div>
                </div>
                
                {/* 操作按钮 */}
                <div className="mt-4 flex gap-2">
                  {apt.status === 'PENDING' && (
                    <button
                      onClick={() => handleProposeAppointmentSlots(apt.id)}
                      className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium text-sm"
                    >
                      📅 提出时间段
                    </button>
                  )}
                  {apt.status === 'CONFIRMED' && apt.type === 'pick-up' && (
                    <button
                      onClick={() => handleConfirmPickup(apt.id)}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium text-sm"
                    >
                      ✓ 确认提车
                    </button>
                  )}
                  {apt.status === 'CONFIRMED' && apt.type === 'drop-off' && (
                    <span className="text-sm text-gray-500">等待线下交车完成</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  // 加载状态
  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">正在加载管理后台...</p>
        </div>
      </div>
    );
  }

  // 未登录或无权限
  if (!user || user.role === "USER") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle size={64} className="mx-auto text-red-500 mb-4" />
          <p className="text-red-600 font-medium mb-4">您没有权限访问此页面</p>
          <Link href="/" className="text-blue-600 font-medium hover:underline">
            返回首页
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo 和标题 */}
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
                <LayoutDashboard size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">管理后台</h1>
                <p className="text-xs text-gray-500">燕园易骑</p>
              </div>
            </div>

            {/* 导航标签 */}
            <nav className="hidden md:flex items-center space-x-1">
              {[
                { id: 'dashboard', label: '仪表盘', icon: LayoutDashboard },
                { id: 'pending', label: '待审核', icon: CheckCircle },
                { id: 'users', label: '用户', icon: Users },
                { id: 'bikes', label: '车辆', icon: Truck },
                { id: 'appointments', label: '预约', icon: Calendar },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <tab.icon size={16} className="mr-2" />
                  {tab.label}
                  {tab.id === 'pending' && pendingBikes.length > 0 && (
                    <span className="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
                      {pendingBikes.length}
                    </span>
                  )}
                </button>
              ))}
              <Link href="/history">
                <button className="flex items-center px-4 py-2 rounded-lg font-medium text-sm text-gray-600 hover:bg-gray-50 transition-all">
                  <History size={16} className="mr-2" />
                  历史记录
                </button>
              </Link>
            </nav>

            {/* 右侧用户菜单 */}
            <div className="flex items-center space-x-3">
              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all relative">
                <Bell size={20} />
                {dashboardData?.pending_bicycles_count > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>
              
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm">
                    {user.name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
                  </div>
                  <ChevronDown size={16} className={`text-gray-600 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user.name || '管理员'}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                    <div className="px-4 py-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.role === 'SUPER_ADMIN' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                      }`}>
                        {user.role === 'SUPER_ADMIN' ? '主负责人' : '管理员'}
                      </span>
                    </div>
                    <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
                      <Settings size={16} className="mr-2" />
                      设置
                    </button>
                    <button className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center">
                      <LogOut size={16} className="mr-2" />
                      退出
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 flex items-center">
            <AlertCircle size={20} className="mr-2" />
            {error}
          </div>
        )}

        {/* 仪表盘 */}
        {activeTab === 'dashboard' && dashboardData && (
          <div className="space-y-6">
            {/* 统计卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {renderStatCard(
                '待处理自行车登记',
                dashboardData.pending_bicycles_count,
                <Truck size={24} className="text-white" />,
                'bg-gradient-to-br from-blue-500 to-blue-600',
                '+12%'
              )}
              {renderStatCard(
                '等待确认预约',
                dashboardData.pending_appointments_count,
                <Clock size={24} className="text-white" />,
                'bg-gradient-to-br from-purple-500 to-purple-600',
                '+5%'
              )}
              {renderStatCard(
                '总用户数',
                allUsers.length,
                <Users size={24} className="text-white" />,
                'bg-gradient-to-br from-green-500 to-green-600',
                '+24%'
              )}
              {renderStatCard(
                '总车辆数',
                allBikes.length,
                <Truck size={24} className="text-white" />,
                'bg-gradient-to-br from-orange-500 to-orange-600',
                '+18%'
              )}
            </div>

            {/* 快捷操作 */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">快捷操作</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button
                  onClick={() => setActiveTab('pending')}
                  className="flex flex-col items-center p-4 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors"
                >
                  <CheckCircle size={32} className="text-blue-600 mb-2" />
                  <span className="text-sm font-medium text-gray-900">审核车辆</span>
                  <span className="text-xs text-gray-500 mt-1">{pendingBikes.length} 辆待审核</span>
                </button>
                <button
                  onClick={() => setActiveTab('appointments')}
                  className="flex flex-col items-center p-4 rounded-xl bg-purple-50 hover:bg-purple-100 transition-colors"
                >
                  <Calendar size={32} className="text-purple-600 mb-2" />
                  <span className="text-sm font-medium text-gray-900">管理预约</span>
                  <span className="text-xs text-gray-500 mt-1">{allAppointments.length} 个进行中</span>
                </button>
                <button
                  onClick={() => setActiveTab('users')}
                  className="flex flex-col items-center p-4 rounded-xl bg-green-50 hover:bg-green-100 transition-colors"
                >
                  <Users size={32} className="text-green-600 mb-2" />
                  <span className="text-sm font-medium text-gray-900">用户管理</span>
                  <span className="text-xs text-gray-500 mt-1">{allUsers.length} 位用户</span>
                </button>
                <button
                  onClick={() => setActiveTab('bikes')}
                  className="flex flex-col items-center p-4 rounded-xl bg-orange-50 hover:bg-orange-100 transition-colors"
                >
                  <Truck size={32} className="text-orange-600 mb-2" />
                  <span className="text-sm font-medium text-gray-900">车辆管理</span>
                  <span className="text-xs text-gray-500 mt-1">{allBikes.length} 辆车</span>
                </button>
              </div>
            </div>

            {/* 待审核车辆预览 */}
            {pendingBikes.length > 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-gray-900">待审核车辆</h2>
                  <button
                    onClick={() => setActiveTab('pending')}
                    className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    查看全部
                    <ChevronDown size={16} className="ml-1 rotate-[-90deg]" />
                  </button>
                </div>
                <div className="space-y-3">
                  {pendingBikes.slice(0, 3).map((bike: any) => (
                    <div key={bike.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                          <Truck size={24} className="text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{bike.brand} {bike.model}</p>
                          <p className="text-sm text-gray-500">¥{bike.price} · {bike.color}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleApprove(bike.id)}
                          className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
                        >
                          <CheckCircle size={18} />
                        </button>
                        <button
                          onClick={() => handleReject(bike.id)}
                          className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                        >
                          <XCircle size={18} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 等待确认的预约（买家已选时间段） */}
            {dashboardData.waiting_appointments && dashboardData.waiting_appointments.length > 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-gray-900">⏳ 等待确认的预约（买家已选时间段）</h2>
                  <button
                    onClick={() => setActiveTab('appointments')}
                    className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    查看全部
                    <ChevronDown size={16} className="ml-1 rotate-[-90deg]" />
                  </button>
                </div>
                <div className="space-y-3">
                  {dashboardData.waiting_appointments.slice(0, 3).map((apt: any) => (
                    <div key={apt.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">预约 ID: {apt.id.slice(0, 8)}...</p>
                        <p className="text-sm text-gray-500">用户：{apt.username} | 车辆：{apt.bicycle_brand}</p>
                        <p className="text-sm text-gray-500">类型：{apt.type === 'pick-up' ? '取车' : '还车'}</p>
                      </div>
                      <button
                        onClick={() => handleConfirmTimeSlot(apt.id)}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium text-sm"
                      >
                        ✓ 确认时间段
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 等待确认的自行车（卖家已选时间段） */}
            {dashboardData.waiting_bicycles && dashboardData.waiting_bicycles.length > 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-gray-900">⏳ 等待确认的自行车（卖家已选时间段）</h2>
                  <button
                    onClick={() => setActiveTab('bikes')}
                    className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    查看全部
                    <ChevronDown size={16} className="ml-1 rotate-[-90deg]" />
                  </button>
                </div>
                <div className="space-y-3">
                  {dashboardData.waiting_bicycles.slice(0, 3).map((bike: any) => (
                    <div key={bike.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">车辆：{bike.brand}</p>
                        <p className="text-sm text-gray-500">卖家：{bike.owner_username} | ID: {bike.id.slice(0, 8)}...</p>
                      </div>
                      <button
                        onClick={() => handleConfirmBicycle(bike.id)}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium text-sm"
                      >
                        ✓ 确认交易
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 待审核 */}
        {activeTab === 'pending' && renderPendingBikes()}

        {/* 用户管理 */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">用户管理</h2>
              <div className="relative">
                <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜索用户..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            {renderUsers()}
          </div>
        )}

        {/* 车辆管理 */}
        {activeTab === 'bikes' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">车辆管理</h2>
              <div className="relative">
                <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜索车辆..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            {renderBikes()}
          </div>
        )}

        {/* 预约管理 */}
        {activeTab === 'appointments' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">预约管理</h2>
              <div className="relative">
                <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜索预约..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            {renderAppointments()}
          </div>
        )}
      </main>
    </div>
  );
}
