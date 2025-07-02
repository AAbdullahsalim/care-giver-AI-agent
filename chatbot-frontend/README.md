# AI Chatbot Frontend

A modern, responsive chatbot interface built with vanilla HTML, CSS, and JavaScript. This frontend provides an intuitive user experience with form-based user registration and real-time chat functionality.

## 🌟 Features

### Visual Design
- **Modern UI/UX** with gradient backgrounds and glassmorphism effects
- **Split-screen layout** - chat on the left, user form on the right
- **Responsive design** that works on desktop, tablet, and mobile
- **Smooth animations** and transitions throughout the interface
- **Professional color scheme** with purple/blue gradients

### User Experience
- **User Registration Form** collecting:
  - Full Name
  - Contact Number (with validation)
  - Reason for Contact (detailed description)
- **Real-time Chat Interface** with:
  - Bot and user message differentiation
  - Typing indicators
  - Message timestamps
  - Auto-scroll to latest messages
- **Smart Scenario Detection** based on user input keywords
- **Form Validation** with helpful error messages
- **Loading states** and progress indicators

### Technical Features
- **Vanilla JavaScript** - no external frameworks required
- **Modern CSS** with flexbox, grid, and CSS custom properties
- **Font Awesome icons** for enhanced visual appeal
- **Google Fonts (Inter)** for typography
- **Local storage ready** for data persistence
- **Modular code structure** for easy maintenance

## 🚀 Quick Start

### Option 1: Direct File Opening
1. Clone or download this repository
2. Open `index.html` directly in your web browser
3. Start using the chatbot immediately!

### Option 2: Local Server (Recommended)
```bash
# Navigate to the project directory
cd chatbot-frontend

# Start a simple HTTP server (Python)
python -m http.server 8000

# Or using Node.js (if you have it installed)
npx serve .

# Open your browser and go to:
# http://localhost:8000
```

## 📋 How to Use

### Step 1: Fill Out the Registration Form
1. Enter your **Full Name** (minimum 2 characters)
2. Provide a valid **Contact Number** (minimum 10 digits)
3. Describe your **Reason for Contact** (minimum 10 characters)
4. Click **"Start Conversation"**

### Step 2: Chat with the AI Assistant
1. After form submission, the chat interface becomes active
2. The AI will analyze your reason for contact and provide an initial response
3. Type your messages in the input field at the bottom
4. Press **Enter** or click the **send button** to send messages
5. Use the **trash icon** to clear the chat history

## 🎯 Scenario Detection

The chatbot automatically categorizes user inquiries into these scenarios:

### Technical Support
**Keywords:** bug, error, not working, problem, issue, broken
**Response:** Troubleshooting assistance and detailed problem analysis

### Sales & Pricing
**Keywords:** price, cost, buy, purchase, subscription, plan
**Response:** Pricing information and feature explanations

### Account & Billing
**Keywords:** account, billing, invoice, payment, refund, charge
**Response:** Account management and billing support

### General Information
**Keywords:** how, what, information, learn, tutorial, guide
**Response:** Educational content and guidance

### General Inquiry
**Default category** for other types of requests

## 🔧 Customization

### Styling
- Edit `styles.css` to modify colors, fonts, and layout
- Key CSS custom properties are defined at the top for easy theming
- Responsive breakpoints: 1024px and 768px

### Functionality
- Modify `script.js` to change behavior or add new features
- Update `determineScenario()` function to add new categories
- Customize `generateBotResponse()` for different response patterns

### Content
- Edit `index.html` to change form fields or layout structure
- Update welcome messages and placeholder text
- Modify form validation rules in the JavaScript

## 📱 Browser Compatibility

- **Chrome** 80+ ✅
- **Firefox** 75+ ✅
- **Safari** 13+ ✅
- **Edge** 80+ ✅
- **Mobile browsers** (iOS Safari, Chrome Mobile) ✅

## 🏗️ Backend Integration

This frontend is designed to integrate with a backend API. To connect to your LangGraph backend:

### 1. Update API Endpoints
```javascript
// In script.js, replace mock functions with actual API calls:

async function analyzeScenario(reason) {
    try {
        const response = await fetch('/api/analyze-scenario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason, userInfo })
        });
        const data = await response.json();
        // Handle response...
    } catch (error) {
        console.error('API Error:', error);
    }
}
```

### 2. User Registration
```javascript
async function handleFormSubmission(e) {
    // Send user data to backend for processing
    const response = await fetch('/api/register-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userInfo)
    });
    // Handle response...
}
```

### 3. Chat Messages
```javascript
async function sendMessage() {
    // Send message to LangGraph backend
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: userMessage,
            userInfo,
            conversationHistory: messageHistory
        })
    });
    // Handle bot response...
}
```

## 📊 Data Structure

### User Information
```javascript
{
    name: "John Doe",
    contact: "+1234567890",
    reason: "I need help with pricing",
    timestamp: "2024-07-03T00:00:00.000Z"
}
```

### Message History
```javascript
[
    {
        user: "What are your pricing plans?",
        bot: "I'd be happy to help you with pricing...",
        timestamp: "2024-07-03T00:00:00.000Z"
    }
]
```

## 🔍 Debugging

### Console Commands
Open browser developer tools and use these commands:

```javascript
// Export all user data
exportUserData()

// Check current user info
console.log(userInfo)

// View message history
console.log(messageHistory)

// Check if conversation started
console.log(conversationStarted)
```

### Common Issues
1. **Form not submitting:** Check browser console for validation errors
2. **Chat not working:** Ensure form was submitted successfully first
3. **Styling issues:** Clear browser cache and check CSS file path
4. **JavaScript errors:** Open developer tools console for error details

## 🚀 Future Enhancements

- WebSocket integration for real-time communication
- Voice input/output capabilities
- File upload support
- Multi-language support
- Dark/light theme toggle
- Chat export functionality
- Message search and filtering
- Emoji and reaction support

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**Ready to connect to your LangGraph backend!** 🎉 