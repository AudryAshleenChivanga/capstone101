/**
 * Mobile Navigation Script for H. pylori CDSS
 * Handles hamburger menu, sidebar toggle, and touch gestures
 */

(function() {
    'use strict';

    // ==================================
    // MOBILE MENU INITIALIZATION
    // ==================================
    
    function initMobileMenu() {
        // Create mobile menu toggle button if it doesn't exist
        if (!document.querySelector('.nav-toggle') && window.innerWidth < 768) {
            const navToggle = document.createElement('button');
            navToggle.className = 'nav-toggle';
            navToggle.setAttribute('aria-label', 'Toggle navigation menu');
            navToggle.innerHTML = '☰';
            document.body.appendChild(navToggle);

            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'nav-overlay';
            document.body.appendChild(overlay);

            // Find navigation element
            const nav = document.querySelector('nav') || 
                       document.querySelector('.navigation') || 
                       document.querySelector('.nav-menu');

            if (nav) {
                // Toggle menu
                navToggle.addEventListener('click', function() {
                    nav.classList.toggle('active');
                    overlay.classList.toggle('active');
                    navToggle.innerHTML = nav.classList.contains('active') ? '✕' : '☰';
                });

                // Close menu when overlay clicked
                overlay.addEventListener('click', function() {
                    nav.classList.remove('active');
                    overlay.classList.remove('active');
                    navToggle.innerHTML = '☰';
                });

                // Close menu when link clicked
                const navLinks = nav.querySelectorAll('a');
                navLinks.forEach(link => {
                    link.addEventListener('click', function() {
                        nav.classList.remove('active');
                        overlay.classList.remove('active');
                        navToggle.innerHTML = '☰';
                    });
                });
            }
        }
    }

    // ==================================
    // MOBILE SIDEBAR TOGGLE
    // ==================================
    
    function initMobileSidebar() {
        const sidebar = document.querySelector('.sidebar') || 
                       document.querySelector('.dashboard-sidebar');
        
        if (sidebar && window.innerWidth < 768) {
            // Create sidebar toggle button
            let sidebarToggle = document.querySelector('.sidebar-toggle');
            
            if (!sidebarToggle) {
                sidebarToggle = document.createElement('button');
                sidebarToggle.className = 'sidebar-toggle nav-toggle';
                sidebarToggle.setAttribute('aria-label', 'Toggle sidebar');
                sidebarToggle.innerHTML = '☰';
                document.body.appendChild(sidebarToggle);
            }

            // Create overlay if it doesn't exist
            let overlay = document.querySelector('.nav-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'nav-overlay';
                document.body.appendChild(overlay);
            }

            // Toggle sidebar
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
            });

            // Close sidebar when overlay clicked
            overlay.addEventListener('click', function() {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });

            // Close sidebar on link click
            const sidebarLinks = sidebar.querySelectorAll('a');
            sidebarLinks.forEach(link => {
                link.addEventListener('click', function() {
                    if (window.innerWidth < 768) {
                        sidebar.classList.remove('active');
                        overlay.classList.remove('active');
                    }
                });
            });
        }
    }

    // ==================================
    // TOUCH GESTURES (SWIPE TO CLOSE)
    // ==================================
    
    function initTouchGestures() {
        let touchStartX = 0;
        let touchEndX = 0;

        document.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        document.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50;
            const nav = document.querySelector('nav.active') || 
                       document.querySelector('.navigation.active');
            const sidebar = document.querySelector('.sidebar.active');
            const overlay = document.querySelector('.nav-overlay');

            // Swipe right to open
            if (touchEndX - touchStartX > swipeThreshold) {
                if (nav) {
                    nav.classList.add('active');
                    if (overlay) overlay.classList.add('active');
                }
                if (sidebar) {
                    sidebar.classList.add('active');
                    if (overlay) overlay.classList.add('active');
                }
            }

            // Swipe left to close
            if (touchStartX - touchEndX > swipeThreshold) {
                if (nav) {
                    nav.classList.remove('active');
                    if (overlay) overlay.classList.remove('active');
                    const navToggle = document.querySelector('.nav-toggle');
                    if (navToggle) navToggle.innerHTML = '☰';
                }
                if (sidebar) {
                    sidebar.classList.remove('active');
                    if (overlay) overlay.classList.remove('active');
                }
            }
        }
    }

    // ==================================
    // RESPONSIVE TABLES
    // ==================================
    
    function makeTablesResponsive() {
        const tables = document.querySelectorAll('table:not(.no-responsive)');
        
        tables.forEach(table => {
            // Wrap table in scrollable container if not already wrapped
            if (!table.parentElement.classList.contains('table-container')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-container';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }

            // Add mobile-friendly attributes
            if (window.innerWidth < 768) {
                const headers = table.querySelectorAll('th');
                const rows = table.querySelectorAll('tbody tr');

                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    cells.forEach((cell, index) => {
                        if (headers[index]) {
                            cell.setAttribute('data-label', headers[index].textContent);
                        }
                    });
                });
            }
        });
    }

    // ==================================
    // HANDLE ORIENTATION CHANGE
    // ==================================
    
    function handleOrientationChange() {
        window.addEventListener('orientationchange', function() {
            // Close any open menus on orientation change
            const nav = document.querySelector('nav.active');
            const sidebar = document.querySelector('.sidebar.active');
            const overlay = document.querySelector('.nav-overlay.active');

            if (nav) nav.classList.remove('active');
            if (sidebar) sidebar.classList.remove('active');
            if (overlay) overlay.classList.remove('active');

            // Reinitialize based on new orientation
            setTimeout(function() {
                init();
            }, 300);
        });
    }

    // ==================================
    // HANDLE WINDOW RESIZE
    // ==================================
    
    function handleResize() {
        let resizeTimer;
        
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                // Remove mobile elements on desktop
                if (window.innerWidth >= 768) {
                    const navToggle = document.querySelector('.nav-toggle');
                    const overlay = document.querySelector('.nav-overlay');
                    const nav = document.querySelector('nav, .navigation');
                    const sidebar = document.querySelector('.sidebar, .dashboard-sidebar');

                    if (navToggle && !navToggle.classList.contains('sidebar-toggle')) {
                        navToggle.remove();
                    }
                    if (overlay) overlay.remove();
                    if (nav) nav.classList.remove('active');
                    if (sidebar) sidebar.classList.remove('active');
                } else {
                    // Reinitialize mobile elements
                    init();
                }
            }, 250);
        });
    }

    // ==================================
    // IMPROVE FORM ACCESSIBILITY
    // ==================================
    
    function improveForms() {
        // Prevent zoom on iOS when focusing on inputs
        const inputs = document.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Ensure minimum font size of 16px to prevent iOS zoom
            const computedStyle = window.getComputedStyle(input);
            const fontSize = parseFloat(computedStyle.fontSize);
            
            if (fontSize < 16) {
                input.style.fontSize = '16px';
            }

            // Add autocomplete attributes for better mobile experience
            if (input.type === 'email' && !input.hasAttribute('autocomplete')) {
                input.setAttribute('autocomplete', 'email');
            }
            if (input.type === 'tel' && !input.hasAttribute('autocomplete')) {
                input.setAttribute('autocomplete', 'tel');
            }
            if (input.name === 'name' && !input.hasAttribute('autocomplete')) {
                input.setAttribute('autocomplete', 'name');
            }
        });
    }

    // ==================================
    // ADD LOADING INDICATOR FOR SLOW CONNECTIONS
    // ==================================
    
    function addLoadingIndicators() {
        // Add loading indicator to forms
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.textContent || submitBtn.value;
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Loading...';
                    submitBtn.style.opacity = '0.6';

                    // Reset after 10 seconds (fallback)
                    setTimeout(function() {
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalText;
                        submitBtn.style.opacity = '1';
                    }, 10000);
                }
            });
        });
    }

    // ==================================
    // MAIN INITIALIZATION
    // ==================================
    
    function init() {
        // Only run on mobile devices
        if (window.innerWidth < 768) {
            initMobileMenu();
            initMobileSidebar();
            initTouchGestures();
        }
        
        makeTablesResponsive();
        handleOrientationChange();
        handleResize();
        improveForms();
        addLoadingIndicators();
    }

    // ==================================
    // AUTO-INITIALIZE ON DOM READY
    // ==================================
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose init function globally for manual initialization
    window.initMobileNavigation = init;

})();

// ==================================
// SERVICE WORKER FOR PWA (Progressive Web App)
// ==================================

if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker registered:', registration.scope);
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

