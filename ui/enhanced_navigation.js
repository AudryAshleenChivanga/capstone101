/**
 * Enhanced Navigation & Dashboard Features
 * - Collapsible sidebar with animations
 * - Breadcrumbs
 * - Keyboard shortcuts
 * - Page transitions
 * - Mobile responsive
 */

// Navigation state
const navigationState = {
    currentPage: 'dashboard',
    previousPage: null,
    history: ['dashboard'],
    sidebarExpanded: true
};

/**
 * Initialize Enhanced Navigation
 */
function initializeEnhancedNavigation() {
    setupSidebarToggle();
    setupBreadcrumbs();
    setupKeyboardShortcuts();
    setupPageTransitions();
    setupMobileNavigation();
    setupSearchNavigation();
    restoreNavigationState();
}

/**
 * Enhanced Sidebar Toggle
 */
function setupSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const mainContent = document.querySelector('.main-content');
    
    if (!toggleBtn) return;
    
    // Create toggle button if it doesn't exist properly
    toggleBtn.innerHTML = `
        <svg class="toggle-icon" viewBox="0 0 24 24" width="24" height="24">
            <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
            <line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
            <line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
        </svg>
    `;
    
    // Toggle sidebar
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleSidebar();
    });
    
    // Close sidebar on outside click (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && sidebar.classList.contains('expanded')) {
                collapseSidebar();
            }
        }
    });
    
    // Hover to expand (desktop only)
    if (window.innerWidth > 768) {
        sidebar.addEventListener('mouseenter', () => {
            if (sidebar.classList.contains('collapsed')) {
                sidebar.classList.add('hover-expanded');
            }
        });
        
        sidebar.addEventListener('mouseleave', () => {
            sidebar.classList.remove('hover-expanded');
        });
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const isCollapsed = sidebar.classList.toggle('collapsed');
    
    navigationState.sidebarExpanded = !isCollapsed;
    localStorage.setItem('sidebarExpanded', navigationState.sidebarExpanded);
    
    // Adjust main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        if (isCollapsed) {
            mainContent.style.marginLeft = '80px';
        } else {
            mainContent.style.marginLeft = '280px';
        }
    }
    
    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('sidebarToggled', { 
        detail: { expanded: !isCollapsed } 
    }));
}

function collapseSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.add('collapsed');
    navigationState.sidebarExpanded = false;
    localStorage.setItem('sidebarExpanded', false);
}

function expandSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('collapsed');
    navigationState.sidebarExpanded = true;
    localStorage.setItem('sidebarExpanded', true);
}

/**
 * Breadcrumbs Navigation
 */
function setupBreadcrumbs() {
    // Create breadcrumb container if it doesn't exist
    let breadcrumbContainer = document.getElementById('breadcrumbNav');
    if (!breadcrumbContainer) {
        const header = document.querySelector('.main-content header') || 
                      document.querySelector('.dashboard-header');
        if (header) {
            breadcrumbContainer = document.createElement('nav');
            breadcrumbContainer.id = 'breadcrumbNav';
            breadcrumbContainer.className = 'breadcrumb-nav';
            breadcrumbContainer.setAttribute('aria-label', 'Breadcrumb');
            header.insertBefore(breadcrumbContainer, header.firstChild);
        }
    }
    
    updateBreadcrumbs('Dashboard');
}

function updateBreadcrumbs(currentPageName) {
    const breadcrumbContainer = document.getElementById('breadcrumbNav');
    if (!breadcrumbContainer) return;
    
    const breadcrumbs = ['Home'];
    
    // Add workflow context
    if (navigationState.currentPage === 'lab-screening' || navigationState.currentPage === 'staging') {
        breadcrumbs.push('Screening');
    }
    
    breadcrumbs.push(currentPageName);
    
    breadcrumbContainer.innerHTML = `
        <ol class="breadcrumb">
            ${breadcrumbs.map((crumb, index) => {
                if (index === breadcrumbs.length - 1) {
                    return `<li class="breadcrumb-item active">${crumb}</li>`;
                } else {
                    return `<li class="breadcrumb-item"><a href="#" onclick="navigateToBreadcrumb('${crumb.toLowerCase()}'); return false;">${crumb}</a></li>`;
                }
            }).join('<li class="breadcrumb-separator">/</li>')}
        </ol>
    `;
}

function navigateToBreadcrumb(pageName) {
    const pageMap = {
        'home': 'dashboard',
        'screening': 'screening'
    };
    
    const pageId = pageMap[pageName] || pageName;
    const navItem = document.querySelector(`[data-page="${pageId}"]`);
    
    if (navItem) {
        navItem.click();
    }
}

/**
 * Keyboard Shortcuts
 */
function setupKeyboardShortcuts() {
    const shortcuts = {
        'Ctrl+1': 'dashboard',
        'Ctrl+2': 'screening',
        'Ctrl+3': 'lab-screening',
        'Ctrl+4': 'staging',
        'Ctrl+5': 'cases',
        'Ctrl+b': 'toggleSidebar',
        'Escape': 'closeModals',
        'Ctrl+s': 'quickSave',
        'Ctrl+f': 'focusSearch'
    };
    
    document.addEventListener('keydown', (e) => {
        // Build shortcut string
        const shortcut = 
            (e.ctrlKey ? 'Ctrl+' : '') +
            (e.shiftKey ? 'Shift+' : '') +
            (e.altKey ? 'Alt+' : '') +
            e.key.toLowerCase();
        
        const action = shortcuts[shortcut];
        
        if (action) {
            e.preventDefault();
            
            if (action === 'toggleSidebar') {
                toggleSidebar();
            } else if (action === 'closeModals') {
                closeAllModals();
            } else if (action === 'quickSave') {
                quickSaveCurrentPage();
            } else if (action === 'focusSearch') {
                focusSearchInput();
            } else {
                // Navigate to page
                const navItem = document.querySelector(`[data-page="${action}"]`);
                if (navItem) navItem.click();
            }
        }
    });
    
    // Show keyboard shortcuts help
    createShortcutsHelp();
}

function createShortcutsHelp() {
    // Add keyboard shortcuts indicator
    const helpBtn = document.createElement('button');
    helpBtn.className = 'shortcuts-help-btn';
    helpBtn.innerHTML = '⌨️';
    helpBtn.title = 'Keyboard Shortcuts (?)';
    helpBtn.onclick = showShortcutsModal;
    
    document.body.appendChild(helpBtn);
    
    // Also listen for ? key
    document.addEventListener('keydown', (e) => {
        if (e.key === '?' && !e.ctrlKey && !e.altKey) {
            const activeElement = document.activeElement;
            if (!['INPUT', 'TEXTAREA', 'SELECT'].includes(activeElement.tagName)) {
                e.preventDefault();
                showShortcutsModal();
            }
        }
    });
}

function showShortcutsModal() {
    const modal = document.createElement('div');
    modal.className = 'shortcuts-modal';
    modal.innerHTML = `
        <div class="shortcuts-modal-content">
            <div class="shortcuts-header">
                <h3>Keyboard Shortcuts</h3>
                <button class="close-btn" onclick="this.closest('.shortcuts-modal').remove()">×</button>
            </div>
            <div class="shortcuts-list">
                <div class="shortcut-group">
                    <h4>Navigation</h4>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>1</kbd>
                        <span>Dashboard</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>2</kbd>
                        <span>Screening</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>3</kbd>
                        <span>Lab Screening</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>4</kbd>
                        <span>Staging</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>5</kbd>
                        <span>Case History</span>
                    </div>
                </div>
                
                <div class="shortcut-group">
                    <h4>Actions</h4>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>B</kbd>
                        <span>Toggle Sidebar</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>S</kbd>
                        <span>Quick Save</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>F</kbd>
                        <span>Focus Search</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Esc</kbd>
                        <span>Close Modals</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>?</kbd>
                        <span>Show This Help</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    document.body.appendChild(modal);
}

function closeAllModals() {
    document.querySelectorAll('.modal, .shortcuts-modal').forEach(modal => {
        modal.remove();
    });
}

function quickSaveCurrentPage() {
    const currentForm = document.querySelector('.page:not([style*="display: none"]) form');
    if (currentForm) {
        const submitBtn = currentForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            showNotification('Auto-saving...', 'info');
            submitBtn.click();
        }
    }
}

function focusSearchInput() {
    const searchInput = document.querySelector('#filterSearch, input[type="search"], input[placeholder*="search" i]');
    if (searchInput) {
        searchInput.focus();
        searchInput.select();
    }
}

/**
 * Smooth Page Transitions
 */
function setupPageTransitions() {
    // Override existing navigation handler
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', handleSmoothNavigation, true);
    });
}

function handleSmoothNavigation(e) {
    const pageId = e.currentTarget.getAttribute('data-page');
    const pageName = e.currentTarget.querySelector('span').textContent;
    
    // Update navigation state
    navigationState.previousPage = navigationState.currentPage;
    navigationState.currentPage = pageId;
    navigationState.history.push(pageId);
    
    // Keep only last 10 pages in history
    if (navigationState.history.length > 10) {
        navigationState.history.shift();
    }
    
    // Update breadcrumbs
    updateBreadcrumbs(pageName);
    
    // Save state
    localStorage.setItem('lastPage', pageId);
    
    // Add page transition animation
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        if (page.style.display !== 'none') {
            page.style.animation = 'fadeOut 0.2s ease';
            setTimeout(() => {
                page.style.display = 'none';
                page.style.animation = '';
            }, 200);
        }
    });
    
    setTimeout(() => {
        const targetPage = document.getElementById(`page-${pageId}`);
        if (targetPage) {
            targetPage.style.display = 'block';
            targetPage.style.animation = 'fadeIn 0.3s ease';
        }
    }, 200);
    
    // Auto-collapse sidebar on mobile
    if (window.innerWidth <= 768) {
        collapseSidebar();
    }
}

/**
 * Mobile Navigation
 */
function setupMobileNavigation() {
    // Create mobile menu button
    if (window.innerWidth <= 768) {
        const header = document.querySelector('.dashboard-header');
        if (header) {
            const mobileMenuBtn = document.createElement('button');
            mobileMenuBtn.className = 'mobile-menu-btn';
            mobileMenuBtn.innerHTML = '☰';
            mobileMenuBtn.onclick = () => {
                const sidebar = document.getElementById('sidebar');
                sidebar.classList.toggle('mobile-visible');
            };
            header.prepend(mobileMenuBtn);
        }
    }
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            handleResponsiveLayout();
        }, 250);
    });
}

function handleResponsiveLayout() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (window.innerWidth <= 768) {
        // Mobile
        sidebar.classList.add('mobile');
        if (mainContent) mainContent.style.marginLeft = '0';
    } else {
        // Desktop
        sidebar.classList.remove('mobile', 'mobile-visible');
        if (mainContent && !sidebar.classList.contains('collapsed')) {
            mainContent.style.marginLeft = '280px';
        }
    }
}

/**
 * Search Navigation
 */
function setupSearchNavigation() {
    // Create quick search in sidebar
    const sidebar = document.getElementById('sidebar');
    const nav = sidebar.querySelector('.sidebar-nav');
    
    const searchContainer = document.createElement('div');
    searchContainer.className = 'sidebar-search';
    searchContainer.innerHTML = `
        <input type="search" 
               id="sidebarSearch" 
               placeholder="Search pages..." 
               class="sidebar-search-input">
    `;
    
    nav.insertBefore(searchContainer, nav.firstChild);
    
    const searchInput = document.getElementById('sidebarSearch');
    searchInput.addEventListener('input', (e) => {
        filterNavigation(e.target.value);
    });
}

function filterNavigation(query) {
    const navItems = document.querySelectorAll('.nav-item');
    const searchQuery = query.toLowerCase().trim();
    
    navItems.forEach(item => {
        const text = item.querySelector('span').textContent.toLowerCase();
        if (searchQuery === '' || text.includes(searchQuery)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Restore Navigation State
 */
function restoreNavigationState() {
    // Restore sidebar state
    const sidebarExpanded = localStorage.getItem('sidebarExpanded');
    if (sidebarExpanded === 'false') {
        collapseSidebar();
    }
    
    // Restore last page
    const lastPage = localStorage.getItem('lastPage');
    if (lastPage && lastPage !== 'dashboard') {
        const navItem = document.querySelector(`[data-page="${lastPage}"]`);
        if (navItem) {
            setTimeout(() => navItem.click(), 100);
        }
    }
}

/**
 * Utility: Show Notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Initialize when DOM is ready
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedNavigation);
} else {
    initializeEnhancedNavigation();
}

// Export for use in other modules
window.navigationUtils = {
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    updateBreadcrumbs,
    showNotification,
    navigationState
};

