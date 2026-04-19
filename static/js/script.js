/* ═══════════════════════════════════════════════════════════
   FoodBridge — Shared JavaScript Utilities
   Common helper functions used across all pages.
   ═══════════════════════════════════════════════════════════ */

/**
 * API Fetch wrapper — handles GET/POST/PUT/DELETE with JSON
 */
async function apiFetch(url, method = 'GET', body = null) {
    try {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body && method !== 'GET') {
            opts.body = JSON.stringify(body);
        }
        const response = await fetch(url, opts);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast show toast-${type}`;
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

/**
 * Get urgency info from expiry date string
 */
function getUrgencyFromExpiry(expiryStr) {
    if (!expiryStr) return { label: 'Unknown', class: 'expired' };
    const now = new Date();
    const expiry = new Date(expiryStr);
    const diffMs = expiry - now;
    const diffMin = diffMs / (1000 * 60);

    if (diffMin <= 0) return { label: 'Expired', class: 'expired' };
    if (diffMin <= 60) return { label: 'Critical', class: 'critical' };
    if (diffMin <= 180) return { label: 'Soon', class: 'soon' };
    return { label: 'Fresh', class: 'fresh' };
}

/**
 * Get countdown string from expiry date
 */
function getCountdown(expiryStr) {
    if (!expiryStr) return '--:--:--';
    const now = new Date();
    const expiry = new Date(expiryStr);
    const diff = expiry - now;

    if (diff <= 0) return 'EXPIRED';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diff % (1000 * 60)) / 1000);

    if (hours > 24) {
        const days = Math.floor(hours / 24);
        return `${days}d ${hours % 24}h`;
    }

    return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/**
 * Format ISO date string to readable format
 */
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}
