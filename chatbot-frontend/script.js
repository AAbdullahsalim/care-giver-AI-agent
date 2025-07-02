// Global variables
let userInfo = {};
let conversationStarted = false;
let messageHistory = [];

// DOM elements
const userForm = document.getElementById('userForm');
const formSuccess = document.getElementById('formSuccess');
const chatInputContainer = document.getElementById('chatInputContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendMessage');
const chatMessages = document.getElementById('chatMessages');
const clearChatBtn = document.getElementById('clearChat');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Form submission handler
    userForm.addEventListener('submit', handleFormSubmission);
    
    // Chat input handlers
    messageInput.addEventListener('keypress', handleKeyPress);
    sendButton.addEventListener('click', sendMessage);
    
    // Clear chat handler
    clearChatBtn.addEventListener('click', clearChat);
    
    // Auto-resize textarea
    const textarea = document.getElementById('reasonForContact');
    textarea.addEventListener('input', autoResizeTextarea);
    
    console.log('🤖 Chatbot Frontend Initialized');
}

// Handle form submission
async function handleFormSubmission(e) {
    e.preventDefault();
    
    // Show loading
    showLoading('Processing your information...');
    
    // Get form data
    const formData = new FormData(userForm);
    userInfo = {
        name: formData.get('userName').trim(),
        contact: formData.get('contactNumber').trim(),
        reason: formData.get('reasonForContact').trim(),
        timestamp: new Date().toISOString()
    };
    
    // Validate form data
    if (!validateFormData(userInfo)) {
        hideLoading();
        return;
    }
    
    // Simulate processing delay (in real app, this would be API call)
    await simulateProcessing(1500);
    
    // Hide form and show success
    userForm.style.display = 'none';
    formSuccess.style.display = 'block';
    
    // Update success display
    document.getElementById('welcomeName').textContent = userInfo.name;
    document.getElementById('displayContact').textContent = userInfo.contact;
    document.getElementById('displayReason').textContent = 
        userInfo.reason.length > 50 ? userInfo.reason.substring(0, 50) + '...' : userInfo.reason;
    
    // Enable chat
    enableChat();
    
    // Send initial scenario analysis message
    await analyzeScenario(userInfo.reason);
    
    hideLoading();
    
    console.log('✅ User registration completed:', userInfo);
}

// Validate form data
function validateFormData(data) {
    if (!data.name || data.name.length < 2) {
        showNotification('Please enter a valid name (at least 2 characters)', 'error');
        return false;
    }
    
    if (!data.contact || !isValidPhoneNumber(data.contact)) {
        showNotification('Please enter a valid contact number', 'error');
        return false;
    }
    
    if (!data.reason || data.reason.length < 10) {
        showNotification('Please provide more details about your reason for contact (at least 10 characters)', 'error');
        return false;
    }
    
    return true;
}

// Validate phone number
function isValidPhoneNumber(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    return phoneRegex.test(cleanPhone) && cleanPhone.length >= 10;
}

// Enable chat functionality
function enableChat() {
    conversationStarted = true;
    chatInputContainer.style.display = 'block';
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
    
    // Add welcome message
    addMessage(
        'bot',
        `Great to meet you, ${userInfo.name}! I've analyzed your request and I'm ready to help. What would you like to know more about?`,
        'now'
    );
}

// Analyze scenario based on user's reason for contact
async function analyzeScenario(reason) {
    showLoading('Analyzing your request...');
    
    // Simulate AI analysis (in real app, this would call your LangGraph backend)
    await simulateProcessing(2000);
    
    // Mock scenario analysis
    const scenario = determineScenario(reason);
    
    hideLoading();
    
    // Send scenario-specific response
    addMessage(
        'bot',
        `Based on your message: "${reason.substring(0, 100)}${reason.length > 100 ? '...' : ''}", I've identified this as a **${scenario.category}** inquiry. ${scenario.response}`,
        'now'
    );
    
    console.log('🎯 Scenario Analysis:', scenario);
}

// Determine scenario based on keywords (mock implementation)
function determineScenario(reason) {
    const lowerReason = reason.toLowerCase();
    
    // Technical Support
    if (lowerReason.includes('bug') || lowerReason.includes('error') || lowerReason.includes('not working') || 
        lowerReason.includes('problem') || lowerReason.includes('issue') || lowerReason.includes('broken')) {
        return {
            category: 'Technical Support',
            response: 'I can help you troubleshoot technical issues. Could you provide more specific details about what\'s not working as expected?'
        };
    }
    
    // Sales/Pricing
    if (lowerReason.includes('price') || lowerReason.includes('cost') || lowerReason.includes('buy') || 
        lowerReason.includes('purchase') || lowerReason.includes('subscription') || lowerReason.includes('plan')) {
        return {
            category: 'Sales & Pricing',
            response: 'I\'d be happy to help you with pricing information and finding the right plan for your needs. What specific features are you interested in?'
        };
    }
    
    // Account/Billing
    if (lowerReason.includes('account') || lowerReason.includes('billing') || lowerReason.includes('invoice') || 
        lowerReason.includes('payment') || lowerReason.includes('refund') || lowerReason.includes('charge')) {
        return {
            category: 'Account & Billing',
            response: 'I can assist you with account and billing related questions. For security purposes, I may need to verify some information with you.'
        };
    }
    
    // General Information
    if (lowerReason.includes('how') || lowerReason.includes('what') || lowerReason.includes('information') || 
        lowerReason.includes('learn') || lowerReason.includes('tutorial') || lowerReason.includes('guide')) {
        return {
            category: 'General Information',
            response: 'I\'m here to provide information and guidance. What specific topic would you like to learn more about?'
        };
    }
    
    // Default category
    return {
        category: 'General Inquiry',
        response: 'Thank you for reaching out! I\'m here to help with any questions or concerns you may have. Could you tell me more about what you\'re looking for?'
    };
}

// Handle keyboard input
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// Send message function
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || !conversationStarted) return;
    
    // Add user message
    addMessage('user', message, 'now');
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Simulate bot response (in real app, this would call your API)
    await simulateProcessing(1500);
    
    // Remove typing indicator
    removeTypingIndicator();
    
    // Generate bot response
    const botResponse = generateBotResponse(message);
    addMessage('bot', botResponse, 'now');
    
    // Store message in history
    messageHistory.push({
        user: message,
        bot: botResponse,
        timestamp: new Date().toISOString()
    });
    
    console.log('💬 Message Exchange:', { user: message, bot: botResponse });
}

// Generate bot response (mock implementation)
function generateBotResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    // Greeting responses
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        return `Hello ${userInfo.name}! How can I assist you today?`;
    }
    
    // Thank you responses
    if (lowerMessage.includes('thank') || lowerMessage.includes('thanks')) {
        return "You're very welcome! Is there anything else I can help you with?";
    }
    
    // Help requests
    if (lowerMessage.includes('help') || lowerMessage.includes('assist') || lowerMessage.includes('support')) {
        return "I'm here to help! Based on your initial inquiry, I can provide guidance on various topics. What specific area would you like assistance with?";
    }
    
    // Pricing questions
    if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('expensive')) {
        return "I'd be happy to discuss pricing options with you. Our plans are designed to be flexible and cost-effective. Would you like me to explain our different pricing tiers?";
    }
    
    // Technical questions
    if (lowerMessage.includes('how') && (lowerMessage.includes('work') || lowerMessage.includes('use'))) {
        return "Great question! I can walk you through how our system works. The process is quite straightforward - would you like a step-by-step explanation or do you have a specific aspect you'd like to focus on?";
    }
    
    // Default response
    const responses = [
        "That's an interesting point. Could you provide a bit more detail so I can give you the most helpful response?",
        "I understand your concern. Let me help you with that. Can you elaborate on what specifically you're looking for?",
        "Thank you for that information. Based on what you've shared, I can offer some guidance. What would be most helpful for you right now?",
        `${userInfo.name}, I want to make sure I address your needs properly. Could you help me understand your priority here?`,
        "I appreciate you sharing that with me. To provide the best assistance, could you tell me more about your specific situation?"
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

// Add message to chat
function addMessage(sender, message, time) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const messageP = document.createElement('p');
    messageP.innerHTML = formatMessage(message);
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = time === 'now' ? formatTime(new Date()) : time;
    
    contentDiv.appendChild(messageP);
    contentDiv.appendChild(timeSpan);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format message (support for basic markdown)
function formatMessage(message) {
    return message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

// Format time
function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.id = 'typing-indicator';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(avatarDiv);
    typingDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
    
    // Add typing animation CSS if not already added
    if (!document.getElementById('typing-styles')) {
        const style = document.createElement('style');
        style.id = 'typing-styles';
        style.textContent = `
            .typing-dots {
                display: flex;
                gap: 4px;
                padding: 8px 0;
            }
            .typing-dots span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4f46e5;
                animation: typing 1.4s infinite ease-in-out;
            }
            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes typing {
                0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
                40% { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Clear chat
function clearChat() {
    const messages = chatMessages.querySelectorAll('.message:not(.typing-indicator)');
    messages.forEach((message, index) => {
        if (index > 0) { // Keep the first welcome message
            message.remove();
        }
    });
    
    messageHistory = [];
    
    addMessage('bot', 'Chat cleared! How can I help you today?', 'now');
    
    console.log('🗑️ Chat cleared');
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Auto-resize textarea
function autoResizeTextarea(e) {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

// Show loading overlay
function showLoading(message = 'Loading...') {
    const loadingText = loadingOverlay.querySelector('p');
    if (loadingText) {
        loadingText.textContent = message;
    }
    loadingOverlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add notification styles if not already added
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 12px;
                background: white;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                z-index: 1001;
                animation: slideInNotification 0.3s ease;
                border-left: 4px solid #06b6d4;
            }
            .notification-error {
                border-left-color: #ef4444;
                background: #fef2f2;
                color: #991b1b;
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 500;
            }
            @keyframes slideInNotification {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideInNotification 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Simulate processing delay
function simulateProcessing(delay = 1000) {
    return new Promise(resolve => setTimeout(resolve, delay));
}

// Export user data (for debugging or integration)
function exportUserData() {
    return {
        userInfo,
        messageHistory,
        conversationStarted,
        timestamp: new Date().toISOString()
    };
}

// Make exportUserData available globally for debugging
window.exportUserData = exportUserData;

console.log('🚀 Chatbot Frontend Script Loaded Successfully'); 