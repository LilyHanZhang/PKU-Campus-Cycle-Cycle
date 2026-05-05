"use client";
import { useState } from "react";
import axios from "axios";
import { X, Upload, User, Mail, Lock } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any;
  onUpdate: () => void;
}

export default function EditProfileModal({ isOpen, onClose, user, onUpdate }: EditProfileModalProps) {
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [avatarUploading, setAvatarUploading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      if (activeTab === 'profile') {
        // 更新个人资料
        const updateData: any = {};
        if (formData.name !== user.name) updateData.name = formData.name;
        if (formData.email !== user.email) updateData.email = formData.email;

        if (Object.keys(updateData).length > 0) {
          await axios.put(`${API_URL}/users/${user.id}`, updateData, { headers });
          setSuccess('个人信息更新成功！');
        } else {
          setSuccess('没有更改任何信息');
        }
      } else {
        // 更新密码
        if (formData.newPassword !== formData.confirmPassword) {
          setError('两次输入的新密码不一致');
          setLoading(false);
          return;
        }

        if (formData.newPassword.length < 6) {
          setError('新密码长度至少为 6 位');
          setLoading(false);
          return;
        }

        await axios.put(
          `${API_URL}/users/${user.id}/password`,
          {
            current_password: formData.currentPassword,
            new_password: formData.newPassword
          },
          { headers }
        );

        setSuccess('密码修改成功！');
        setFormData(prev => ({
          ...prev,
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }));
      }

      setTimeout(() => {
        onUpdate();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      setError('请上传图片文件');
      return;
    }

    // 验证文件大小（5MB）
    if (file.size > 5 * 1024 * 1024) {
      setError('图片大小不能超过 5MB');
      return;
    }

    setAvatarUploading(true);
    setError('');
    setSuccess('');

    const token = localStorage.getItem("access_token");
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(
        `${API_URL}/users/${user.id}/upload-avatar`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setSuccess('头像上传成功！');
      setTimeout(() => {
        onUpdate();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || '头像上传失败，请重试');
    } finally {
      setAvatarUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">编辑个人资料</h2>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex-1 px-6 py-3 font-bold transition-all flex items-center justify-center ${
              activeTab === 'profile'
                ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <User size={18} className="mr-2" />
            个人资料
          </button>
          <button
            onClick={() => setActiveTab('password')}
            className={`flex-1 px-6 py-3 font-bold transition-all flex items-center justify-center ${
              activeTab === 'password'
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Lock size={18} className="mr-2" />
            修改密码
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {activeTab === 'profile' ? (
            <div className="space-y-4">
              {/* Avatar Upload */}
              <div className="flex flex-col items-center mb-6">
                <div className="relative">
                  <img
                    src={user.avatar_url || `https://ui-avatars.com/api/?name=${user.name}&background=10b981&color=fff`}
                    alt="Avatar"
                    className="w-24 h-24 rounded-full object-cover border-4 border-emerald-200"
                  />
                  <label
                    className={`absolute bottom-0 right-0 w-10 h-10 rounded-full bg-gradient-to-r from-emerald-500 to-emerald-600 flex items-center justify-center cursor-pointer hover:from-emerald-600 hover:to-emerald-700 transition-all ${
                      avatarUploading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    <Upload size={18} className="text-white" />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarUpload}
                      className="hidden"
                      disabled={avatarUploading}
                    />
                  </label>
                </div>
                <p className="text-sm text-gray-500 mt-2">点击上传新头像</p>
              </div>

              {/* Name */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  <User size={16} className="inline mr-1" />
                  用户名
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  placeholder="请输入用户名"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  <Mail size={16} className="inline mr-1" />
                  邮箱
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  placeholder="请输入邮箱"
                />
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Current Password */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  <Lock size={16} className="inline mr-1" />
                  当前密码
                </label>
                <input
                  type="password"
                  value={formData.currentPassword}
                  onChange={(e) => setFormData(prev => ({ ...prev, currentPassword: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入当前密码"
                  required
                />
              </div>

              {/* New Password */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  <Lock size={16} className="inline mr-1" />
                  新密码
                </label>
                <input
                  type="password"
                  value={formData.newPassword}
                  onChange={(e) => setFormData(prev => ({ ...prev, newPassword: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入新密码（至少 6 位）"
                  required
                  minLength={6}
                />
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  <Lock size={16} className="inline mr-1" />
                  确认新密码
                </label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请再次输入新密码"
                  required
                  minLength={6}
                />
              </div>
            </div>
          )}

          {/* Error/Success Messages */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          {success && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
              {success}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || avatarUploading}
            className={`w-full mt-6 py-3 rounded-lg font-bold text-white transition-all ${
              activeTab === 'profile'
                ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700'
                : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {loading ? '保存中...' : avatarUploading ? '上传中...' : '保存更改'}
          </button>
        </form>
      </div>
    </div>
  );
}
