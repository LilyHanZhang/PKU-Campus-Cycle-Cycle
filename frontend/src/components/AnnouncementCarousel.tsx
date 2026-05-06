"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { ChevronLeft, ChevronRight, FileText, Pin, Image as ImageIcon, File as FileIcon, X } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Announcement {
  id: string;
  title: string;
  content: string;
  image_url?: string;
  attachment_url?: string;
  is_pinned: boolean;
  author_name?: string;
  created_at: string;
}

export default function AnnouncementCarousel() {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const [showAll, setShowAll] = useState(false);

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

  useEffect(() => {
    if (isAutoPlaying && announcements.length > 1 && !showAll) {
      const interval = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % announcements.length);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isAutoPlaying, announcements.length, showAll]);

  const fetchAnnouncements = async () => {
    try {
      const response = await axios.get(`${API_URL}/announcements/`);
      setAnnouncements(response.data);
    } catch (error) {
      console.error("Failed to fetch announcements", error);
    }
  };

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % announcements.length);
    setIsAutoPlaying(false);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + announcements.length) % announcements.length);
    setIsAutoPlaying(false);
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
    setIsAutoPlaying(false);
  };

  if (announcements.length === 0) {
    return null;
  }

  if (showAll) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          <div className="bg-gradient-to-r from-emerald-500 to-green-600 text-white p-6 flex justify-between items-center">
            <h2 className="text-2xl font-bold flex items-center">
              <FileText className="mr-3" size={28} />
              所有公告
            </h2>
            <button onClick={() => setShowAll(false)} className="hover:bg-white/20 rounded-full p-2 transition">
              <X size={24} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-4">
              {announcements.map((announcement) => (
                <div
                  key={announcement.id}
                  className={`border-2 rounded-2xl p-5 ${
                    announcement.is_pinned ? "border-yellow-400 bg-yellow-50" : "border-gray-200"
                  }`}
                >
                  <div className="flex items-center space-x-3 mb-3">
                    {announcement.is_pinned && <Pin size={20} className="text-yellow-600 fill-yellow-600" />}
                    <h4 className="text-lg font-bold text-gray-900">{announcement.title}</h4>
                  </div>
                  <p className="text-gray-700 mb-3">{announcement.content}</p>
                  {announcement.image_url && (
                    <img src={getFileUrl(announcement.image_url)} alt="" className="rounded-xl max-h-64 object-cover mb-3" />
                  )}
                  {announcement.attachment_url && (
                    <a
                      href={getFileUrl(announcement.attachment_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-emerald-600 hover:text-emerald-700 font-medium"
                    >
                      <FileIcon size={16} className="mr-2" />
                      查看附件
                    </a>
                  )}
                  <div className="mt-3 text-xs text-gray-500">
                    {announcement.author_name || "管理员"} · {new Date(announcement.created_at).toLocaleString("zh-CN")}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentAnnouncement = announcements[currentIndex];

  return (
    <>
      <div className="bg-gradient-to-r from-emerald-500 to-green-600 rounded-3xl shadow-2xl overflow-hidden relative">
        <div className="absolute top-4 right-4 z-10 flex items-center space-x-2">
          <span className="bg-white/20 backdrop-blur-sm text-white px-3 py-1 rounded-full text-xs font-medium">
            {currentIndex + 1} / {announcements.length}
          </span>
          <button
            onClick={() => setShowAll(true)}
            className="bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white px-3 py-1 rounded-full text-xs font-medium transition"
          >
            查看全部
          </button>
        </div>

        <div className="p-6 md:p-8">
          <div className="flex items-start space-x-3 mb-4">
            {currentAnnouncement.is_pinned && (
              <Pin size={24} className="text-yellow-300 fill-yellow-300 flex-shrink-0 mt-1" />
            )}
            <h3 className="text-2xl md:text-3xl font-black text-white pr-20">
              {currentAnnouncement.title}
            </h3>
          </div>

          <p className="text-white/90 text-base md:text-lg mb-4 line-clamp-3">
            {currentAnnouncement.content}
          </p>

          {currentAnnouncement.image_url && (
            <div className="mb-4">
              <img
                src={getFileUrl(currentAnnouncement.image_url)}
                alt="公告图片"
                className="rounded-2xl w-full h-48 md:h-64 object-cover shadow-lg"
              />
            </div>
          )}

          {currentAnnouncement.attachment_url && (
            <a
              href={getFileUrl(currentAnnouncement.attachment_url)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white px-4 py-2 rounded-full font-medium transition"
            >
              <FileIcon size={18} className="mr-2" />
              查看附件
            </a>
          )}
        </div>

        {announcements.length > 1 && (
          <>
            <button
              onClick={prevSlide}
              className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white rounded-full p-3 transition"
            >
              <ChevronLeft size={24} />
            </button>
            <button
              onClick={nextSlide}
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white rounded-full p-3 transition"
            >
              <ChevronRight size={24} />
            </button>

            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
              {announcements.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={`w-3 h-3 rounded-full transition-all ${
                    index === currentIndex ? "bg-white w-8" : "bg-white/40 hover:bg-white/60"
                  }`}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
}
