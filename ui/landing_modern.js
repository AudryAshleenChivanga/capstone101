// ========================================
// Modern Landing Page JavaScript
// H. pylori CDSS
// ========================================

// Initialize 3D Background with Vanta.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize 3D animated background
    if (typeof VANTA !== 'undefined') {
        VANTA.CELLS({
            el: "#vanta-bg",
            mouseControls: true,
            touchControls: true,
            gyroControls: false,
            minHeight: 200.00,
            minWidth: 200.00,
            scale: 1.00,
            color1: 0x8b5cf6,
            color2: 0x7c3aed,
            size: 1.50,
            speed: 1.00
        });
    } else {
        // Fallback gradient if Vanta.js doesn't load
        document.getElementById('vanta-bg').style.background = 
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }

    // Navbar background change on scroll
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        }
    });

    // Animate elements on scroll
    observeElements();
});

// ========================================
// Function: Open Scheduling Modal
// ========================================
function openScheduling() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        // Redirect to login/dashboard
        if (confirm('You need to be logged in to schedule an appointment. Would you like to go to the dashboard?')) {
            window.location.href = 'dashboard_new.html';
        }
        return;
    }
    
    // Open scheduling interface in dashboard
    window.location.href = 'dashboard_new.html#scheduling';
}

// ========================================
// Function: Book Consultation with Doctor
// ========================================
function bookConsultation(doctorName) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        if (confirm(`Schedule a consultation with ${doctorName}? You'll need to login first.`)) {
            // Store doctor preference
            sessionStorage.setItem('preferred_doctor', doctorName);
            window.location.href = 'dashboard_new.html';
        }
        return;
    }
    
    // Store preferred doctor and go to dashboard
    sessionStorage.setItem('preferred_doctor', doctorName);
    window.location.href = 'dashboard_new.html#scheduling';
    
    showNotification(`Opening consultation booking for ${doctorName}...`, 'success');
}

// ========================================
// Function: Handle Contact Form Submission
// ========================================
async function handleContactSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name') || e.target[0].value,
        email: formData.get('email') || e.target[1].value,
        message: formData.get('message') || e.target[2].value
    };
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;
    
    try {
        // Simulate API call (replace with actual endpoint)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
        e.target.reset();
    } catch (error) {
        showNotification('Failed to send message. Please try again.', 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ========================================
// Function: Show Notification Toast
// ========================================
function showNotification(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    toast.textContent = message;
    
    // Style the toast
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6',
        color: 'white',
        padding: '1rem 2rem',
        borderRadius: '10px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
        zIndex: '10000',
        animation: 'slideIn 0.3s ease-out',
        fontWeight: '600'
    });
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ========================================
// Function: Observe Elements for Scroll Animation
// ========================================
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observe all service cards and doctor profiles
    document.querySelectorAll('.service-card, .doctor-profile, .stat').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });
}

// ========================================
// Add CSS animations for toasts
// ========================================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .nav-menu.active {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
`;
document.head.appendChild(style);

// ========================================
// Preload images for better performance
// ========================================
function preloadImages() {
    const images = [
        '../images/Dr_Angie.webp',
        '../images/Dr_Mugisha.webp',
        '../images/Dr_Tatenda.webp',
        '../images/Dr_Ishimwe.webp'
    ];
    
    images.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

preloadImages();

// ========================================
// Handle page visibility for performance
// ========================================
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause animations when page is not visible
        if (window.vantaEffect) {
            window.vantaEffect.pause();
        }
    } else {
        // Resume animations
        if (window.vantaEffect) {
            window.vantaEffect.play();
        }
    }
});

console.log('🚀 H. pylori CDSS Landing Page Loaded Successfully!');

