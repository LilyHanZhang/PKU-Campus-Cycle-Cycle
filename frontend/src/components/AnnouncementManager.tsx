"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { X, Upload, Image as ImageIcon, FileText, Pin, Trash2, Edit2, Plus } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Announcement {
  id: string;
  title: string;
  content: string;
  image_url?: string;
  attachment_url?: string;
  is_pinned: boolean;
  author_id: string;
  author_name?: string;
  author_avatar_url?: string;
  created_at: string;
  updated_at?: string;
}

interface AnnouncementManagerProps {
  onClose: () => void;
}

export default function AnnouncementManager({ onClose }: AnnouncementManagerProps) {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null);
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    image_url: "",
    attachment_url: "",
    is_pinned: false
  });
  const [uploadingImage, setUploadingImage] = useState(false);
  const [uploadingAttachment, setUploadingAttachment] = useState(false);

  // 处理文件 URL，如果是相对路径则添加 API URL
  const getFileUrl = (url?: string) => {
    if (!url) return undefined;
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    return `${API_URL}${url}`;
  };

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      const response = await axios.get(`${API_URL}/announcements/`);
      setAnnouncements(response.data);
    } catch (error) {
      console.error("Failed to fetch announcements", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingImage(true);
    const formDataUpload = new FormData();
    formDataUpload.append("file", file);

    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.post(`${API_URL}/announcements/upload/image`, formDataUpload, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      setFormData(prev => ({ ...prev, image_url: response.data.file_url }));
    } catch (error) {
      console.error("Failed to upload image", error);
      alert("图片上传失败");
    } finally {
      setUploadingImage(false);
    }
  };

  const handleAttachmentUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingAttachment(true);
    const formDataUpload = new FormData();
    formDataUpload.append("file", file);

    try {
      const token = localStorage.getItem("access_token");
      const response = await axios.post(`${API_URL}/announcements/upload/attachment`, formDataUpload, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      setFormData(prev => ({ ...prev, attachment_url: response.data.file_url }));
    } catch (error) {
      console.error("Failed to upload attachment", error);
      alert("附件上传失败");
    } finally {
      setUploadingAttachment(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.title || !formData.content) {
      alert("请填写标题和内容");
      return;
    }

    try {
      const token = localStorage.getItem("access_token");
      if (editingAnnouncement) {
        await axios.put(`${API_URL}/announcements/${editingAnnouncement.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API_URL}/announcements/`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      fetchAnnouncements();
      setShowCreateModal(false);
      setEditingAnnouncement(null);
      setFormData({ title: "", content: "", image_url: "", attachment_url: "", is_pinned: false });
    } catch (error: any) {
      console.error("Failed to save announcement", error);
      alert(error.response?.data?.detail || "操作失败");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个公告吗？")) return;

    try {
      const token = localStorage.getItem("access_token");
      await axios.delete(`${API_URL}/announcements/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchAnnouncements();
    } catch (error: any) {
      console.error("Failed to delete announcement", error);
      alert(error.response?.data?.detail || "删除失败");
    }
  };

  const handlePinToggle = async (id: string, currentPinned: boolean) => {
    try {
      const token = localStorage.getItem("access_token");
      const endpoint = currentPinned ? "unpin" : "pin";
      await axios.put(`${API_URL}/announcements/${id}/${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchAnnouncements();
    } catch (error: any) {
      console.error("Failed to toggle pin", error);
      alert(error.response?.data?.detail || "操作失败");
    }
  };

  const handleEdit = (announcement: Announcement) => {
    setEditingAnnouncement(announcement);
    setFormData({
      title: announcement.title,
      content: announcement.content,
      image_url: announcement.image_url || "",
      attachment_url: announcement.attachment_url || "",
      is_pinned: announcement.is_pinned
    });
    setShowCreateModal(true);
  };

  const resetModal = () => {
    setShowCreateModal(false);
    setEditingAnnouncement(null);
    setFormData({ title: "", content: "", image_url: "", attachment_url: "", is_pinned: false });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-emerald-500 to-green-600 text-white p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold flex items-center">
            <FileText className="mr-3" size={28} />
            公告管理
          </h2>
          <button onClick={onClose} className="hover:bg-white/20 rounded-full p-2 transition">
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-800">公告列表</h3>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-emerald-500 to-green-600 text-white px-6 py-3 rounded-full font-semibold hover:shadow-lg hover:-translate-y-0.5 transition-all flex items-center"
            >
              <Plus size={20} className="mr-2" />
              发布公告
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-12 text-gray-500">加载中...</div>
          ) : announcements.length === 0 ? (
            <div className="text-center py-12 text-gray-500">暂无公告</div>
          ) : (
            <div className="space-y-4">
              {announcements.map((announcement) => (
                <div
                  key={announcement.id}
                  className={`border-2 rounded-2xl p-5 transition-all ${
                    announcement.is_pinned
                      ? "border-yellow-400 bg-yellow-50"
                      : "border-gray-200 bg-white"
                  }`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-3">
                      {announcement.is_pinned && (
                        <Pin size={20} className="text-yellow-600 fill-yellow-600" />
                      )}
                      <h4 className="text-lg font-bold text-gray-900">{announcement.title}</h4>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handlePinToggle(announcement.id, announcement.is_pinned)}
                        className={`p-2 rounded-full transition ${
                          announcement.is_pinned
                            ? "bg-yellow-200 text-yellow-700 hover:bg-yellow-300"
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                        }`}
                        title={announcement.is_pinned ? "取消置顶" : "置顶"}
                      >
                        <Pin size={18} />
                      </button>
                      <button
                        onClick={() => handleEdit(announcement)}
                        className="p-2 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition"
                        title="编辑"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => handleDelete(announcement.id)}
                        className="p-2 rounded-full bg-red-100 text-red-600 hover:bg-red-200 transition"
                        title="删除"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-700 mb-3 line-clamp-2">{announcement.content}</p>
                  {announcement.image_url && (
                    <div className="mb-3">
                      <img
                        src={getFileUrl(announcement.image_url)}
                        alt="公告图片"
                        className="rounded-xl max-h-48 object-cover"
                      />
                    </div>
                  )}
                  {announcement.attachment_url && (
                    <a
                      href={getFileUrl(announcement.attachment_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-emerald-600 hover:text-emerald-700 font-medium"
                    >
                      <FileText size={16} className="mr-2" />
                      查看附件
                    </a>
                  )}
                  <div className="mt-3 text-xs text-gray-500">
                    发布者：{announcement.author_name || "管理员"} | 
                    发布时间：{new Date(announcement.created_at).toLocaleString("zh-CN")}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="bg-gradient-to-r from-emerald-500 to-green-600 text-white p-6 flex justify-between items-center sticky top-0">
                <h2 className="text-2xl font-bold">
                  {editingAnnouncement ? "编辑公告" : "发布公告"}
                </h2>
                <button onClick={resetModal} className="hover:bg-white/20 rounded-full p-2 transition">
                  <X size={24} />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    标题 *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-emerald-500 focus:outline-none transition"
                    placeholder="请输入公告标题"
                    maxLength={200}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    内容 *
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-emerald-500 focus:outline-none transition"
                    placeholder="请输入公告内容"
                    rows={6}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    图片
                  </label>
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl cursor-pointer transition">
                      <Upload size={18} />
                      <span>上传图片</span>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="hidden"
                        disabled={uploadingImage}
                      />
                    </label>
                    {uploadingImage && <span className="text-sm text-gray-500">上传中...</span>}
                    {formData.image_url && (
                      <span className="text-sm text-emerald-600 flex items-center">
                        <ImageIcon size={16} className="mr-1" />
                        已上传
                      </span>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    附件
                  </label>
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl cursor-pointer transition">
                      <Upload size={18} />
                      <span>上传附件</span>
                      <input
                        type="file"
                        onChange={handleAttachmentUpload}
                        className="hidden"
                        disabled={uploadingAttachment}
                      />
                    </label>
                    {uploadingAttachment && <span className="text-sm text-gray-500">上传中...</span>}
                    {formData.attachment_url && (
                      <span className="text-sm text-emerald-600 flex items-center">
                        <FileText size={16} className="mr-1" />
                        已上传
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_pinned"
                    checked={formData.is_pinned}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_pinned: e.target.checked }))}
                    className="w-4 h-4 text-emerald-600 rounded focus:ring-emerald-500"
                  />
                  <label htmlFor="is_pinned" className="text-sm font-semibold text-gray-700">
                    置顶此公告
                  </label>
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    onClick={handleSubmit}
                    className="flex-1 bg-gradient-to-r from-emerald-500 to-green-600 text-white py-3 rounded-full font-semibold hover:shadow-lg hover:-translate-y-0.5 transition-all"
                  >
                    {editingAnnouncement ? "保存修改" : "发布公告"}
                  </button>
                  <button
                    onClick={resetModal}
                    className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-full font-semibold hover:bg-gray-200 transition"
                  >
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
