// Chat functionality
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : '';

let currentUser = null;
let currentConversationId = null;
let conversations = [];
let allUsers = [];
let allPatients = [];
let pollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
    loadConversations();
    startPolling();
});

// Authentication
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Get current user info
    fetch(`${API_BASE}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Unauthorized');
        return response.json();
    })
    .then(user => {
        currentUser = user;
        document.getElementById('userName').textContent = user.full_name || user.username;
        document.getElementById('userRole').textContent = user.role;
    })
    .catch(() => {
        localStorage.removeItem('access_token');
        window.location.href = 'login.html';
    });
}

// Event Listeners
function setupEventListeners() {
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('access_token');
        window.location.href = 'login.html';
    });

    // New conversation buttons
    document.getElementById('newConversationBtn').addEventListener('click', openNewConversationModal);
    document.getElementById('startChatBtn').addEventListener('click', openNewConversationModal);

    // Search conversations
    document.getElementById('searchConversations').addEventListener('input', filterConversations);

    // Message input
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('input', updateCharCount);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send message button
    document.getElementById('sendMessageBtn').addEventListener('click', sendMessage);

    // Archive conversation
    document.getElementById('archiveChatBtn').addEventListener('click', archiveConversation);

    // Modal close
    document.querySelector('.close').addEventListener('click', closeNewConversationModal);
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('newConversationModal');
        if (e.target === modal) {
            closeNewConversationModal();
        }
    });

    // New conversation form
    document.getElementById('newConversationForm').addEventListener('submit', createNewConversation);
    document.getElementById('recipientType').addEventListener('change', handleRecipientTypeChange);
}

// Load conversations
async function loadConversations() {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`${API_BASE}/chat/conversations`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load conversations');

        conversations = await response.json();
        renderConversations(conversations);

    } catch (error) {
        console.error('Error loading conversations:', error);
        document.getElementById('conversationsList').innerHTML = `
            <div class="loading-conversations">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load conversations</p>
            </div>
        `;
    }
}

// Render conversations
function renderConversations(convos) {
    const conversationsList = document.getElementById('conversationsList');
    
    if (convos.length === 0) {
        conversationsList.innerHTML = `
            <div class="loading-conversations">
                <i class="fas fa-inbox"></i>
                <p>No conversations yet</p>
                <button onclick="openNewConversationModal()" class="btn-primary" style="margin-top: 15px;">
                    Start New Conversation
                </button>
            </div>
        `;
        return;
    }

    conversationsList.innerHTML = convos.map(conv => `
        <div class="conversation-item ${conv.id === currentConversationId ? 'active' : ''}" 
             onclick="loadConversation(${conv.id})">
            <div class="conversation-header">
                <span class="conversation-name">${conv.other_participant_name || 'Unknown'}</span>
                <span class="conversation-time">${formatTime(conv.last_message_at)}</span>
            </div>
            <div class="conversation-preview">
                ${conv.last_message || 'No messages yet'}
            </div>
            <div class="conversation-meta">
                ${conv.other_participant_role ? `<span class="participant-role-badge">${conv.other_participant_role}</span>` : ''}
                ${conv.unread_count > 0 ? `<span class="unread-badge">${conv.unread_count} new</span>` : ''}
            </div>
        </div>
    `).join('');
}

// Filter conversations
function filterConversations() {
    const searchTerm = document.getElementById('searchConversations').value.toLowerCase();
    const filtered = conversations.filter(conv => 
        (conv.other_participant_name || '').toLowerCase().includes(searchTerm) ||
        (conv.last_message || '').toLowerCase().includes(searchTerm)
    );
    renderConversations(filtered);
}

// Load specific conversation
async function loadConversation(conversationId) {
    const token = localStorage.getItem('access_token');
    currentConversationId = conversationId;

    try {
        const response = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load conversation');

        const data = await response.json();
        
        // Update UI
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('activeChat').style.display = 'flex';
        
        // Update header
        document.getElementById('chatParticipantName').textContent = data.other_participant_name || 'Unknown';
        document.getElementById('chatParticipantRole').textContent = data.other_participant_role || '';
        
        // Render messages
        renderMessages(data.messages);
        
        // Mark messages as read
        const unreadIds = data.messages.filter(msg => !msg.is_read && msg.sender_id !== currentUser.id).map(msg => msg.id);
        if (unreadIds.length > 0) {
            markMessagesAsRead(unreadIds);
        }

        // Update conversation list to show active
        renderConversations(conversations);

    } catch (error) {
        console.error('Error loading conversation:', error);
        alert('Failed to load conversation');
    }
}

// Render messages
function renderMessages(messages) {
    const messagesArea = document.getElementById('messagesArea');
    
    if (messages.length === 0) {
        messagesArea.innerHTML = `
            <div class="loading-conversations">
                <i class="fas fa-comment-dots"></i>
                <p>No messages yet. Start the conversation!</p>
            </div>
        `;
        return;
    }

    let lastDate = null;
    const messagesHTML = messages.map(msg => {
        const messageDate = new Date(msg.created_at).toDateString();
        let dateSeparator = '';
        
        if (messageDate !== lastDate) {
            dateSeparator = `
                <div class="date-separator">
                    <span>${formatDate(msg.created_at)}</span>
                </div>
            `;
            lastDate = messageDate;
        }

        const isSent = msg.sender_id === currentUser.id;
        return `
            ${dateSeparator}
            <div class="message ${isSent ? 'sent' : 'received'}">
                <div class="message-content">
                    ${!isSent ? `<div class="message-sender">${msg.sender_name}</div>` : ''}
                    <div class="message-bubble">
                        ${escapeHtml(msg.content)}
                    </div>
                    <div class="message-time">${formatTime(msg.created_at)}</div>
                </div>
            </div>
        `;
    }).join('');

    messagesArea.innerHTML = messagesHTML;
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Send message
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();

    if (!content || !currentConversationId) return;

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/chat/messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                content: content,
                message_type: 'text'
            })
        });

        if (!response.ok) throw new Error('Failed to send message');

        // Clear input
        messageInput.value = '';
        updateCharCount();

        // Reload conversation
        await loadConversation(currentConversationId);
        await loadConversations();

    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message');
    }
}

// Mark messages as read
async function markMessagesAsRead(messageIds) {
    const token = localStorage.getItem('access_token');

    try {
        await fetch(`${API_BASE}/chat/messages/read`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_ids: messageIds
            })
        });

        // Update unread count in navbar if exists
        loadConversations();

    } catch (error) {
        console.error('Error marking messages as read:', error);
    }
}

// Archive conversation
async function archiveConversation() {
    if (!currentConversationId) return;

    if (!confirm('Are you sure you want to archive this conversation?')) return;

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/chat/conversations/${currentConversationId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to archive conversation');

        // Reset UI
        currentConversationId = null;
        document.getElementById('emptyState').style.display = 'flex';
        document.getElementById('activeChat').style.display = 'none';

        // Reload conversations
        await loadConversations();

        alert('Conversation archived successfully');

    } catch (error) {
        console.error('Error archiving conversation:', error);
        alert('Failed to archive conversation');
    }
}

// New conversation modal
function openNewConversationModal() {
    const modal = document.getElementById('newConversationModal');
    modal.style.display = 'block';
    
    // Load users and patients
    loadUsersForModal();
    loadPatientsForModal();
}

function closeNewConversationModal() {
    const modal = document.getElementById('newConversationModal');
    modal.style.display = 'none';
    document.getElementById('newConversationForm').reset();
    document.getElementById('userSelectGroup').style.display = 'none';
    document.getElementById('patientSelectGroup').style.display = 'none';
}

function handleRecipientTypeChange() {
    const type = document.getElementById('recipientType').value;
    const userGroup = document.getElementById('userSelectGroup');
    const patientGroup = document.getElementById('patientSelectGroup');

    if (type === 'user') {
        userGroup.style.display = 'block';
        patientGroup.style.display = 'none';
    } else if (type === 'patient') {
        userGroup.style.display = 'none';
        patientGroup.style.display = 'block';
    } else {
        userGroup.style.display = 'none';
        patientGroup.style.display = 'none';
    }
}

async function loadUsersForModal() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load users');

        allUsers = await response.json();
        const userSelect = document.getElementById('userSelect');
        
        userSelect.innerHTML = '<option value="">-- Select User --</option>' +
            allUsers
                .filter(u => u.id !== currentUser.id)
                .map(u => `<option value="${u.id}">${u.full_name || u.username} (${u.role})</option>`)
                .join('');

    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('userSelect').innerHTML = '<option value="">Failed to load users</option>';
    }
}

async function loadPatientsForModal() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/patients/list`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load patients');

        allPatients = await response.json();
        const patientSelect = document.getElementById('patientSelect');
        
        patientSelect.innerHTML = '<option value="">-- Select Patient --</option>' +
            allPatients.map(p => `<option value="${p.id}">${p.full_name || p.patient_id} (${p.patient_id})</option>`)
                .join('');

    } catch (error) {
        console.error('Error loading patients:', error);
        document.getElementById('patientSelect').innerHTML = '<option value="">Failed to load patients</option>';
    }
}

async function createNewConversation(e) {
    e.preventDefault();

    const recipientType = document.getElementById('recipientType').value;
    const userId = document.getElementById('userSelect').value;
    const patientId = document.getElementById('patientSelect').value;
    const caseId = document.getElementById('caseIdInput').value || null;
    const initialMessage = document.getElementById('initialMessage').value.trim();

    if (!recipientType || !initialMessage) {
        alert('Please fill in all required fields');
        return;
    }

    if (recipientType === 'user' && !userId) {
        alert('Please select a user');
        return;
    }

    if (recipientType === 'patient' && !patientId) {
        alert('Please select a patient');
        return;
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/chat/conversations`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                receiver_id: recipientType === 'user' ? parseInt(userId) : null,
                patient_id: recipientType === 'patient' ? parseInt(patientId) : null,
                case_id: caseId ? parseInt(caseId) : null,
                initial_message: initialMessage
            })
        });

        if (!response.ok) throw new Error('Failed to create conversation');

        const newConversation = await response.json();

        // Close modal
        closeNewConversationModal();

        // Reload conversations and open new one
        await loadConversations();
        await loadConversation(newConversation.id);

    } catch (error) {
        console.error('Error creating conversation:', error);
        alert('Failed to create conversation');
    }
}

// Polling for new messages
function startPolling() {
    // Poll every 5 seconds
    pollInterval = setInterval(() => {
        if (currentConversationId) {
            loadConversation(currentConversationId);
        }
        loadConversations();
    }, 5000);
}

// Utility functions
function updateCharCount() {
    const messageInput = document.getElementById('messageInput');
    const charCount = document.getElementById('charCount');
    charCount.textContent = `${messageInput.value.length}/5000`;
}

function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        return date.toLocaleDateString();
    } else if (hours > 0) {
        return `${hours}h ago`;
    } else if (minutes > 0) {
        return `${minutes}m ago`;
    } else {
        return 'Just now';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});

