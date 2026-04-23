const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://pku-campus-cycle-cycle.onrender.com";

export const API_ENDPOINTS = {
  login: `${API_BASE_URL}/auth/login`,
  register: `${API_BASE_URL}/auth/register`,
  me: `${API_BASE_URL}/auth/me`,
  bicycles: `${API_BASE_URL}/bicycles/`,
  posts: `${API_BASE_URL}/posts/`,
  appointments: `${API_BASE_URL}/appointments/`,
  users: `${API_BASE_URL}/users/`,
};

export default API_BASE_URL;
