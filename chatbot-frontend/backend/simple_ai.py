from typing import Dict, Any, List
import asyncio

class SimpleCaregiverAI:
    """Simplified AI that provides intelligent responses without external API calls"""
    
    def __init__(self):
        self.scenario_responses = {
            "Schedule Issue": {
                "greeting": "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!",
                "main_response": "I see you clocked in but there seems to be no schedule on your Calendar, can you confirm the client you are working with today?",
                "follow_up": "No, please do not leave. Unfortunately, the app can malfunction at times and remove Caregivers from schedules. I will add you to the schedule and clock you in, if for any reason this causes an error your coordinator will reach out to you to clarify.",
                "suggestions": ["Provide client name", "Check app again", "Contact coordinator"]
            },
            "Location Issue": {
                "greeting": "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!",
                "main_response": "I have noticed you have clocked in outside of the client's service area, which is not close to your client's house. Can you please clock in again once you are at your client's house, because we are not able to accept this clock in.",
                "follow_up": "Remember it is state law that a Home Care agency cannot bill for visits that are rendered outside of the client's home.",
                "suggestions": ["I'm at client's house", "I stopped for supplies", "GPS isn't working"]
            },
            "Phone Issue": {
                "greeting": "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!",
                "main_response": "I have noticed that you used the IVR number to clock in today, but you used your phone to call that number instead of the client's house phone. Can you please clock in again using the client's house phone?",
                "follow_up": "If the client won't allow you to use their phone, I would recommend you use the HHA app to clock in. If your app doesn't work, I can have one of our care coordinators give you a call and get your HHA app set up.",
                "suggestions": ["Use client's phone", "My app isn't working", "Help set up app"]
            },
            "Timing Issue": {
                "greeting": "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!",
                "main_response": "I have noticed that you clocked in late for your shift today, I just wanted to confirm what was the reason for that?",
                "follow_up": "Would you be willing to make up for the hours you missed today by staying late on your shift today? Or any other day throughout the week?",
                "suggestions": ["I can stay late", "Make up hours tomorrow", "Had an emergency"]
            },
            "General Inquiry": {
                "greeting": "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!",
                "main_response": "Thank you for contacting us. I'm here to help you with any questions or concerns you may have.",
                "follow_up": "Could you tell me more about what you're looking for so I can provide the best assistance?",
                "suggestions": ["Tell me more", "What should I do?", "Who can help?"]
            }
        }
    
    def analyze_scenario(self, message: str, reason: str) -> str:
        """Analyze user input to determine scenario"""
        combined = f"{reason} {message}".lower()
        
        if any(word in combined for word in ["schedule", "calendar", "missing", "not showing", "removed"]):
            return "Schedule Issue"
        elif any(word in combined for word in ["location", "gps", "outside", "range", "distance", "address"]):
            return "Location Issue"
        elif any(word in combined for word in ["phone", "number", "call", "ivr", "registered"]):
            return "Phone Issue"
        elif any(word in combined for word in ["late", "early", "time", "clock", "hours", "forgot"]):
            return "Timing Issue"
        else:
            return "General Inquiry"
    
    async def process_message(self, user_info: Dict, message: str) -> Dict:
        """Process message and return intelligent response"""
        print(f"🔍 Processing: {message}")
        
        # Determine scenario
        scenario = self.analyze_scenario(message, user_info.get('reason_for_contact', ''))
        print(f"🎯 Scenario: {scenario}")
        
        # Get appropriate response template
        template = self.scenario_responses[scenario]
        
        # Build response
        if "initial contact" in message.lower():
            # First message - use greeting + main response
            response = f"{template['greeting']}\n\n{template['main_response']}"
        else:
            # Follow-up message - use follow-up response
            response = template['follow_up']
        
        print(f"✅ Response ready")
        
        return {
            'response': response,
            'scenario_detected': scenario,
            'suggestions': template['suggestions']
        }

# Global instance
simple_ai = SimpleCaregiverAI() 