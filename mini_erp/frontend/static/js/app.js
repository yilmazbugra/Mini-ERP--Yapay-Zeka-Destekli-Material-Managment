// Mini ERP Frontend JavaScript

// API Base URL - moved to individual pages to avoid conflicts

// Axios configuration
axios.defaults.baseURL = '/api';
axios.defaults.withCredentials = true; // Enable cookies for CORS
axios.interceptors.request.use(function (config) {
    // JWT token is now handled via cookies, no need to add Authorization header
    return config;
});

axios.interceptors.response.use(
    function (response) {
        return response;
    },
    function (error) {
        if (error.response?.status === 401) {
            // Unauthorized - redirect to login
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('tr-TR');
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('tr-TR');
}

// Authentication functions
function logout() {
    localStorage.removeItem('user');
    // Clear JWT cookies by making a logout request
    axios.post('/api/auth/logout').finally(() => {
        window.location.href = '/';
    });
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function updateUserDisplay() {
    const user = getCurrentUser();
    const userNameElement = document.getElementById('user-name');
    if (userNameElement && user) {
        userNameElement.textContent = user.username;
    }
}

// Table utilities
function createDataTable(containerId, data, columns, actions = []) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-light">
                    <tr>
    `;
    
    columns.forEach(col => {
        html += `<th>${col.title}</th>`;
    });
    
    if (actions.length > 0) {
        html += `<th width="120">İşlemler</th>`;
    }
    
    html += `
                    </tr>
                </thead>
                <tbody>
    `;
    
    if (data.length === 0) {
        html += `
            <tr>
                <td colspan="${columns.length + (actions.length > 0 ? 1 : 0)}" class="text-center text-muted">
                    Veri bulunamadı
                </td>
            </tr>
        `;
    } else {
        data.forEach(item => {
            html += '<tr>';
            columns.forEach(col => {
                let value = item[col.key];
                if (col.formatter) {
                    value = col.formatter(value, item);
                }
                html += `<td>${value || '-'}</td>`;
            });
            
            if (actions.length > 0) {
                html += '<td>';
                actions.forEach(action => {
                    const disabled = action.disabled ? action.disabled(item) : false;
                    html += `
                        <button class="btn btn-sm ${action.class}" 
                                onclick="${action.onclick}" 
                                ${disabled ? 'disabled' : ''}
                                title="${action.title}">
                            <i class="${action.icon}"></i>
                        </button>
                    `;
                });
                html += '</td>';
            }
            
            html += '</tr>';
        });
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
}

// Form utilities
function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    return data;
}

function populateForm(form, data) {
    Object.keys(data).forEach(key => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) {
            if (field.type === 'checkbox') {
                field.checked = data[key];
            } else {
                field.value = data[key];
            }
        }
    });
}

// Modal utilities
function showModal(modalId, title, content, onConfirm = null) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    const confirmBtn = modal.querySelector('.btn-primary');
    
    if (modalTitle) modalTitle.textContent = title;
    if (modalBody) modalBody.innerHTML = content;
    
    if (confirmBtn && onConfirm) {
        confirmBtn.onclick = onConfirm;
    }
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

// Pagination utilities
function createPagination(containerId, currentPage, totalPages, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container || totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<nav><ul class="pagination justify-content-center">';
    
    // Previous button
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="onPageChange(${currentPage - 1})">Önceki</a>
        </li>
    `;
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="onPageChange(${i})">${i}</a>
            </li>
        `;
    }
    
    // Next button
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="onPageChange(${currentPage + 1})">Sonraki</a>
        </li>
    `;
    
    html += '</ul></nav>';
    container.innerHTML = html;
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    updateUserDisplay();
    setupRoleBasedAccess();
    
    // Check if user is logged in (for pages other than login)
    const user = getCurrentUser();
    if (!user && !window.location.pathname.includes('/')) {
        window.location.href = '/';
    }
});

function setupRoleBasedAccess() {
    const user = getCurrentUser();
    if (!user) return;
    
    const role = user.role;
    
    // Hide/show menu items based on role
    const stockMenu = document.getElementById('stock-menu');
    const ordersMenu = document.getElementById('orders-menu');
    const partnersMenu = document.getElementById('partners-menu');
    const reportsMenu = document.getElementById('reports-menu');
    
    // Admin: Full access
    if (role === 'admin') {
        return; // Show all menus
    }
    
    // Warehouse Manager: Stock, Orders, Partners, Reports
    if (role === 'warehouse_manager') {
        return; // Show all menus
    }
    
    // Clerk: Limited access
    if (role === 'clerk') {
        // Hide reports menu
        if (reportsMenu) {
            reportsMenu.style.display = 'none';
        }
        return;
    }
    
    // Viewer: Only dashboard and inventory view
    if (role === 'viewer') {
        if (stockMenu) {
            // Only show inventory
            const dropdown = stockMenu.querySelector('.dropdown-menu');
            if (dropdown) {
                dropdown.innerHTML = '<li><a class="dropdown-item" href="/inventory">Envanter</a></li>';
            }
        }
        
        // Hide other menus
        if (ordersMenu) ordersMenu.style.display = 'none';
        if (partnersMenu) partnersMenu.style.display = 'none';
        if (reportsMenu) reportsMenu.style.display = 'none';
    }
}

// Export functions for global use
window.MiniERP = {
    showAlert,
    formatCurrency,
    formatDate,
    formatDateTime,
    logout,
    getCurrentUser,
    createDataTable,
    serializeForm,
    populateForm,
    showModal,
    createPagination
};
