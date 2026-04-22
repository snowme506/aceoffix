// AceOffix Shared Utilities

function $(sel) { return document.querySelector(sel); }
function $$(sel) { return document.querySelectorAll(sel); }

function fmtPrice(cents) {
  return '¥' + (cents / 100).toFixed(2);
}

function showToast(msg, type = 'info') {
  let container = $('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function setLoading(el, loading) {
  if (!el) return;
  if (loading) {
    el.dataset.original = el.innerHTML;
    el.innerHTML = '<div class="spinner"></div>';
    el.disabled = true;
  } else {
    el.innerHTML = el.dataset.original || '';
    el.disabled = false;
  }
}

function createEl(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function formatDate(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function formatDateTime(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[m]));
}

// Simple router state helpers
function getQueryParam(key) {
  return new URLSearchParams(location.search).get(key);
}

function isLoggedIn() {
  return !!localStorage.getItem('user_token');
}

function logout() {
  localStorage.removeItem('user_token');
  localStorage.removeItem('user_info');
  location.href = 'index.html';
}

function adminLogout() {
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin');
  location.reload();
}

// Render pagination
function renderPagination(container, page, pageSize, total, onChange) {
  const totalPages = Math.ceil(total / pageSize) || 1;
  container.innerHTML = '';
  if (totalPages <= 1) return;

  const prev = createEl('button', 'page-btn', '上一页');
  prev.disabled = page <= 1;
  prev.onclick = () => onChange(page - 1);

  const info = createEl('span', 'page-info', `${page} / ${totalPages}`);

  const next = createEl('button', 'page-btn', '下一页');
  next.disabled = page >= totalPages;
  next.onclick = () => onChange(page + 1);

  container.appendChild(prev);
  container.appendChild(info);
  container.appendChild(next);
}

// Shared product list renderer
window.renderProducts = function(container, items) {
  if (!items || !items.length) {
    container.innerHTML = '<div class="empty">暂无商品</div>';
    return;
  }
  container.innerHTML = items.map(function(p) {
    var rawImg = (p.images && p.images.length) ? p.images[0] : '';
    var imgSrc = rawImg.replace(/^\/frontend\//, '/');
    var img = imgSrc ? '<img src="' + escapeHtml(imgSrc) + '" alt="' + escapeHtml(p.name) + '">' : '<div class="prod-no-img">📷</div>';
    return '<a class="prod-card" href="product.html?id=' + p.id + '">' +
      '<div class="prod-img">' + img + '</div>' +
      '<div class="prod-name">' + escapeHtml(p.name) + '</div>' +
      '<div class="prod-price">' + (p.original_price ? '<span class="prod-price-main">¥' + Math.round(p.price/100) + '</span>' : '') + '</div>' +
    '</a>';
  }).join('');
};
