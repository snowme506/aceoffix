// AceOffix API Client
const API_BASE = 'http://101.201.181.170';

function getToken() {
  return localStorage.getItem('user_token') || '';
}

function getAdminToken() {
  return localStorage.getItem('admin_token') || '';
}

async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  try {
    const res = await fetch(url, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.message || `HTTP ${res.status}`);
    }
    return data;
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
}

async function adminFetch(path, options = {}, skipContentType) {
  const url = `${API_BASE}${path}`;
  const headers = skipContentType ? { ...options.headers } : {
    'Content-Type': 'application/json',
    ...options.headers
  };
  const token = getAdminToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  try {
    const res = await fetch(url, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.message || `HTTP ${res.status}`);
    }
    return data;
  } catch (err) {
    console.error('Admin API Error:', err);
    throw err;
  }
}

/* Public API */
const PublicAPI = {
  home: () => apiFetch('/api/home'),
  products: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/api/products?${qs}`);
  },
  productDetail: (id) => apiFetch(`/api/products/detail/${id}`),
  stores: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/api/stores/list?${qs}`);
  },
  storeDetail: (id) => apiFetch(`/api/stores/detail/${id}`),
  categories: () => apiFetch('/api/categories/list'),
  pointsRules: () => apiFetch('/api/points/rules'),
  banners: () => apiFetch('/api/banners'),
};

/* Auth API */
const AuthAPI = {
  sendCode: (phone) => apiFetch('/api/auth/send-code', {
    method: 'POST',
    body: JSON.stringify({ phone })
  }),
  login: (phone, code) => apiFetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ phone, code })
  }),
};

/* User API */
const UserAPI = {
  profile: () => apiFetch('/api/users/profile'),
  pointsLogs: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/api/users/points/logs?${qs}`);
  },
  pointsBalance: () => apiFetch('/api/users/points/balance'),
};

/* Order API */
const OrderAPI = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/api/orders/list?${qs}`);
  },
  detail: (id) => apiFetch(`/api/orders/detail/${id}`),
  create: (body) => apiFetch('/api/orders/create', {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  pay: (orderId, paymentMethod = 'mock') => apiFetch('/api/orders/pay', {
    method: 'POST',
    body: JSON.stringify({ order_id: orderId, payment_method: paymentMethod })
  }),
};

/* Admin API */
const AdminAPI = {
  login: (username, password) => adminFetch('/api/admin/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),
  profile: () => adminFetch('/api/admin/auth/profile'),
  statsOverview: () => adminFetch('/api/admin/stats/overview'),
  statsChart: (days = 7) => adminFetch(`/api/admin/stats/chart?days=${days}`),
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return adminFetch('/api/admin/upload/image', { method: 'POST', body: formData }, true /* no content-type for multipart */);
  },
  productList: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return adminFetch(`/api/admin/products/list?${qs}`);
  },
  productCreate: (body) => adminFetch('/api/admin/products/create', {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  productUpdate: (id, body) => adminFetch(`/api/admin/products/update/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body)
  }),
  productDelete: (id) => adminFetch(`/api/admin/products/delete/${id}`, {
    method: 'DELETE'
  }),
  categoryList: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return adminFetch(`/api/admin/categories/list?${qs}`);
  },
  categoryCreate: (body) => adminFetch('/api/admin/categories/create', {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  categoryUpdate: (id, body) => adminFetch(`/api/admin/categories/update/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body)
  }),
  categoryDelete: (id) => adminFetch(`/api/admin/categories/delete/${id}`, {
    method: 'DELETE'
  }),
  storeList: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return adminFetch(`/api/admin/stores/list?${qs}`);
  },
  storeCreate: (body) => adminFetch('/api/admin/stores/create', {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  storeUpdate: (id, body) => adminFetch(`/api/admin/stores/update/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body)
  }),
  storeDelete: (id) => adminFetch(`/api/admin/stores/delete/${id}`, {
    method: 'DELETE'
  }),
  orderList: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return adminFetch(`/api/admin/orders/list?${qs}`);
  },
  memberList: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return adminFetch(`/api/admin/members/list?${qs}`);
  },
  bannerList: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return adminFetch(`/api/admin/banners/list?${qs}`);
  },
  bannerCreate: (body) => adminFetch('/api/admin/banners/create', {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  bannerUpdate: (id, body) => adminFetch(`/api/admin/banners/update/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body)
  }),
  bannerDelete: (id) => adminFetch(`/api/admin/banners/delete/${id}`, {
    method: 'DELETE'
  }),
};
