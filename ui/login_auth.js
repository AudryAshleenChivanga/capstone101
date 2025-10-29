/**
 * H. pylori CDSS - Authentication Module
 * Handles login and registration functionality
 */

// Dynamic API URL detection
const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : window.location.origin;

// Show message function
function showMessage(elementId, message, type) {
    const messageArea = document.getElementById(elementId);
    if (messageArea) {
        messageArea.textContent = message;
        messageArea.className = `message-area ${type}`;
    }
}

// Toggle between login and register cards
function showLoginCard() {
    document.getElementById('loginCard').style.display = 'block';
    document.getElementById('registerCard').style.display = 'none';
    document.getElementById('messageArea').className = 'message-area';
    document.getElementById('registerMessageArea').className = 'message-area';
}

function showRegisterCard() {
    document.getElementById('loginCard').style.display = 'none';
    document.getElementById('registerCard').style.display = 'block';
    document.getElementById('messageArea').className = 'message-area';
    document.getElementById('registerMessageArea').className = 'message-area';
}

// Event Listeners
document.getElementById('showRegisterBtn').addEventListener('click', showRegisterCard);
document.getElementById('showLoginBtn').addEventListener('click', showLoginCard);

// Login Form Handler
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const spinner = loginBtn.querySelector('.spinner');
    const arrow = loginBtn.querySelector('.btn-arrow');

    // Validation
    if (!username || !password) {
        showMessage('messageArea', 'Please enter both username and password.', 'error');
        return;
    }

    // Show loading state
    loginBtn.disabled = true;
    btnText.textContent = 'Signing in...';
    spinner.style.display = 'block';
    arrow.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();

            // Store JWT in localStorage
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            showMessage('messageArea', 'Login successful! Redirecting...', 'success');

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/ui/dashboard_new.html?v=' + Date.now();
            }, 800);
        } else {
            const error = await response.json();
            showMessage('messageArea', error.detail || 'Invalid credentials. Please try again.', 'error');
        }
    } catch (error) {
        showMessage('messageArea', 'Network error. Please check your connection and try again.', 'error');
        console.error('Login error:', error);
    } finally {
        loginBtn.disabled = false;
        btnText.textContent = 'Sign In to Dashboard';
        spinner.style.display = 'none';
        arrow.style.display = 'block';
    }
});

// Registration Form Handler
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const registerBtn = document.getElementById('registerBtn');
    const btnText = registerBtn.querySelector('.btn-text');
    const spinner = registerBtn.querySelector('.spinner');
    const arrow = registerBtn.querySelector('.btn-arrow');

    // Validation
    if (!username || !email || !password) {
        showMessage('registerMessageArea', 'Please fill in all fields.', 'error');
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage('registerMessageArea', 'Please enter a valid email address.', 'error');
        return;
    }

    // Password strength validation
    if (password.length < 6) {
        showMessage('registerMessageArea', 'Password must be at least 6 characters long.', 'error');
        return;
    }

    // Show loading state
    registerBtn.disabled = true;
    btnText.textContent = 'Creating account...';
    spinner.style.display = 'block';
    arrow.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/auth/register/first`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                username, 
                email, 
                password, 
                full_name: username, 
                role: 'admin' 
            })
        });

        if (response.ok) {
            const data = await response.json();
            showMessage('registerMessageArea', 'Account created successfully! Redirecting to sign in...', 'success');

            // Switch to login form after success
            setTimeout(() => {
                showLoginCard();
                document.getElementById('username').value = username;
                document.getElementById('registerForm').reset();
                showMessage('messageArea', 'Registration successful! Please sign in with your credentials.', 'success');
            }, 1500);
        } else {
            const error = await response.json();
            showMessage('registerMessageArea', error.detail || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        showMessage('registerMessageArea', 'Network error. Please check your connection and try again.', 'error');
        console.error('Registration error:', error);
    } finally {
        registerBtn.disabled = false;
        btnText.textContent = 'Create Account';
        spinner.style.display = 'none';
        arrow.style.display = 'block';
    }
});

// Auto-focus on username field when page loads
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('username').focus();
});

// Enter key navigation between fields
document.getElementById('username').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('password').focus();
    }
});

document.getElementById('regUsername').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('regEmail').focus();
    }
});

document.getElementById('regEmail').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('regPassword').focus();
    }
});

