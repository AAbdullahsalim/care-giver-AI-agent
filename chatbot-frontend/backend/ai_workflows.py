from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import Config

class CaregiverAI:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=Config.get_google_api_key(),
            temperature=0.7
        )
        self.conversations = {}
    
    def analyze_scenario(self, message: str, reason: str) -> str:
        combined = f"{reason} {message}".lower()
        
        if any(word in combined for word in ["schedule", "calendar", "missing"]):
            return "Schedule Issue"
        elif any(word in combined for word in ["location", "gps", "outside"]):
            return "Location Issue"
        elif any(word in combined for word in ["phone", "number", "call"]):
            return "Phone Issue"
        elif any(word in combined for word in ["late", "early", "time"]):
            return "Timing Issue"
        else:
            return "General Inquiry"
    
    async def process_message(self, user_info: Dict, message: str) -> Dict:
        print(f"🔍 Processing message: {message}")
        print(f"👤 User info: {user_info}")
        
        scenario = self.analyze_scenario(message, user_info.get('reason_for_contact', ''))
        print(f"🎯 Detected scenario: {scenario}")
        
        prompt = f"""
        You are Rosella from Independence Care. A caregiver needs help.
        
        Caregiver: {user_info.get('user_name')}
        Issue Type: {scenario}
        Message: "{message}"
        
        Respond professionally as Rosella following company scripts.
        Start with: "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!"
        
        Then address their specific {scenario.lower()} appropriately.
        """
        
        print("🤖 Calling Gemini API...")
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            print("✅ Gemini API responded successfully")
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            raise e
        
        suggestions = {
            "Schedule Issue": ["Check current schedule", "Contact coordinator", "Provide client name"],
            "Location Issue": ["I'm at client's house", "GPS isn't working", "I stopped for supplies"],
            "Phone Issue": ["Use client's phone", "My app isn't working", "Update phone number"],
            "Timing Issue": ["I can stay late", "Make up hours tomorrow", "Had an emergency"],
            "General Inquiry": ["Can you help?", "Who should I contact?", "What's next?"]
        }
        
        return {
            'response': response.content,
            'scenario_detected': scenario,
            'suggestions': suggestions.get(scenario, [])
        }

ai_assistant = CaregiverAI() 