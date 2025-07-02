from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import Config
import asyncio

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=Config.get_google_api_key(),
    temperature=0.7
)

class CaregiverWorkflows:
    """LangGraph-style workflow manager for caregiver scenarios"""
    
    def __init__(self):
        self.conversation_memory = {}  # In-memory storage for conversations
    
    def analyze_scenario(self, user_message: str, reason: str) -> str:
        """Analyze user input to determine which workflow to use"""
        combined_text = f"{reason} {user_message}".lower()
        
        # Schedule-related keywords
        if any(word in combined_text for word in ["schedule", "calendar", "missing", "not showing", "removed"]):
            return "Schedule Issue"
        
        # Location/GPS keywords  
        if any(word in combined_text for word in ["location", "gps", "address", "outside", "range", "distance"]):
            return "Location Issue"
            
        # Phone/communication keywords
        if any(word in combined_text for word in ["phone", "number", "call", "ivr", "registered"]):
            return "Phone Issue"
            
        # Timing keywords
        if any(word in combined_text for word in ["late", "early", "time", "clock", "hours"]):
            return "Timing Issue"
            
        return "General Inquiry"
    
    async def process_schedule_issue(self, user_info: Dict, message: str, conversation_id: str) -> Dict:
        """Handle schedule-related issues with multi-step workflow"""
        
        # Get conversation history
        history = self.conversation_memory.get(conversation_id, [])
        
        if len(history) == 0:  # First message in this workflow
            prompt = f"""
            You are Rosella from Independence Care. A caregiver named {user_info.get('user_name', 'the caregiver')} 
            has contacted you about a schedule issue.
            
            Their initial concern: "{message}"
            Contact: {user_info.get('contact_number', 'N/A')}
            
            Respond exactly as Rosella would from the company scripts:
            "Hello, this is Rosella, I am calling from Independence Care, how are you doing today?
            
            I see you clocked in but there seems to be no schedule on your Calendar, can you 
            confirm the client you are working with today?"
            
            Be professional, empathetic, and follow the exact scripts provided.
            """
        else:
            # Continue the conversation based on history
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            prompt = f"""
            Continue this conversation as Rosella from Independence Care.
            
            Conversation so far:
            {conversation_context}
            
            Caregiver's latest message: "{message}"
            
            Respond appropriately based on what they've said. If they've provided the client name,
            follow the script: "No, please do not leave. Unfortunately, the app can malfunction at 
            times and remove Caregivers from schedules. I will add you to the schedule and clock you in, 
            if for any reason this causes an error your coordinator will reach out to you to clarify."
            
            If they need different guidance, provide it professionally.
            """
        
        # Get AI response
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Update conversation memory
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': response.content})
        self.conversation_memory[conversation_id] = history
        
        # Determine suggestions based on conversation stage
        if len(history) <= 2:
            suggestions = [
                "Provide client name",
                "Check app again", 
                "Contact coordinator"
            ]
        else:
            suggestions = [
                "Thank you for helping",
                "What should I do next?",
                "Is there anything else?"
            ]
        
        return {
            'response': response.content,
            'scenario_detected': 'Schedule Issue',
            'suggestions': suggestions,
            'conversation_step': len(history) // 2
        }
    
    async def process_location_issue(self, user_info: Dict, message: str, conversation_id: str) -> Dict:
        """Handle GPS/location issues with multi-step workflow"""
        
        history = self.conversation_memory.get(conversation_id, [])
        
        if len(history) == 0:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a location/GPS issue.
            
            Caregiver: {user_info.get('user_name', 'the caregiver')}
            Issue: "{message}"
            
            Respond with the appropriate script:
            "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!
            
            I have noticed you have clocked in outside of the client's service area, which is not close 
            to your client's house. Can you please clock in again once you are at your client's house, 
            because we are not able to accept this clock in."
            
            Be professional and follow company policy about location verification.
            """
        else:
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            prompt = f"""
            Continue as Rosella handling the location issue.
            
            Conversation:
            {conversation_context}
            
            Latest message: "{message}"
            
            If they explain they stopped to pick up supplies for the client, ask them to verify with the client.
            If it's a GPS error, guide them to try again from the correct location.
            Always remind them: "Remember it is state law that a Home Care agency cannot bill for visits 
            that are rendered outside of the client's home."
            """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': response.content})
        self.conversation_memory[conversation_id] = history
        
        suggestions = [
            "I'm at the client's house",
            "I stopped to pick up supplies",
            "My GPS isn't working right"
        ]
        
        return {
            'response': response.content,
            'scenario_detected': 'Location Issue',
            'suggestions': suggestions,
            'conversation_step': len(history) // 2
        }
    
    async def process_phone_issue(self, user_info: Dict, message: str, conversation_id: str) -> Dict:
        """Handle phone/IVR issues"""
        
        history = self.conversation_memory.get(conversation_id, [])
        
        if len(history) == 0:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a phone issue.
            
            Caregiver: {user_info.get('user_name', 'the caregiver')}
            Issue: "{message}"
            
            Respond with the script:
            "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!
            
            I have noticed that you used the IVR number to clock in today, but you used your phone 
            to call that number instead of the client's house phone. Can you please clock in again 
            using the client's house phone?"
            
            Or if it's an unregistered number:
            "I have noticed that you have clocked in using a phone number that is not registered 
            with us. Can you confirm whose number this is?"
            """
        else:
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            prompt = f"""
            Continue as Rosella handling the phone issue.
            
            Conversation:
            {conversation_context}
            
            Latest message: "{message}"
            
            Provide appropriate guidance based on their response. If they can't use the client's phone,
            suggest using the HHA app. If the app doesn't work, offer to have a coordinator help set it up.
            """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': response.content})
        self.conversation_memory[conversation_id] = history
        
        suggestions = [
            "I'll use the client's phone",
            "My app isn't working",
            "Can you help me set it up?"
        ]
        
        return {
            'response': response.content,
            'scenario_detected': 'Phone Issue',
            'suggestions': suggestions,
            'conversation_step': len(history) // 2
        }
    
    async def process_timing_issue(self, user_info: Dict, message: str, conversation_id: str) -> Dict:
        """Handle timing/late arrival issues"""
        
        history = self.conversation_memory.get(conversation_id, [])
        
        if len(history) == 0:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a timing issue.
            
            Caregiver: {user_info.get('user_name', 'the caregiver')}
            Issue: "{message}"
            
            Respond with the script:
            "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!
            
            I have noticed that you clocked in late for your shift today, I just wanted to confirm 
            what was the reason for that?"
            
            Be understanding but professional about timing policies.
            """
        else:
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            prompt = f"""
            Continue as Rosella handling the timing issue.
            
            Conversation:
            {conversation_context}
            
            Latest message: "{message}"
            
            Based on their reason, offer solutions:
            "Would you be willing to make up for the hours you missed today by staying late on your 
            shift today? Or any other day throughout the week?"
            
            If they agree, help adjust the schedule. If not, be understanding but note the policy.
            """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': response.content})
        self.conversation_memory[conversation_id] = history
        
        suggestions = [
            "I can stay late today",
            "Can I make up hours tomorrow?",
            "I had an emergency"
        ]
        
        return {
            'response': response.content,
            'scenario_detected': 'Timing Issue',
            'suggestions': suggestions,
            'conversation_step': len(history) // 2
        }
    
    async def process_general_inquiry(self, user_info: Dict, message: str, conversation_id: str) -> Dict:
        """Handle general inquiries"""
        
        prompt = f"""
        You are Rosella from Independence Care. Handle this general caregiver inquiry professionally.
        
        Caregiver: {user_info.get('user_name', 'the caregiver')}
        Contact: {user_info.get('contact_number', 'N/A')}
        Original reason: {user_info.get('reason_for_contact', 'General inquiry')}
        Current message: "{message}"
        
        Provide helpful, professional assistance. If it's not a standard scenario,
        offer to connect them with the appropriate department or supervisor.
        
        Start with: "Hello, this is Rosella, I am calling from Independence Care, how are you doing today!"
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        return {
            'response': response.content,
            'scenario_detected': 'General Inquiry',
            'suggestions': [
                "Can you help me with this?",
                "Who should I contact?",
                "What's the next step?"
            ],
            'conversation_step': 1
        }
    
    async def process_message(self, user_info: Dict, message: str, conversation_id: str = None) -> Dict:
        """Main entry point - routes to appropriate workflow"""
        
        if not conversation_id:
            conversation_id = f"{user_info.get('user_name', 'unknown')}_{len(self.conversation_memory)}"
        
        # Determine scenario type
        scenario_type = self.analyze_scenario(message, user_info.get('reason_for_contact', ''))
        
        # Route to appropriate workflow
        if scenario_type == "Schedule Issue":
            return await self.process_schedule_issue(user_info, message, conversation_id)
        elif scenario_type == "Location Issue":
            return await self.process_location_issue(user_info, message, conversation_id)
        elif scenario_type == "Phone Issue":
            return await self.process_phone_issue(user_info, message, conversation_id)
        elif scenario_type == "Timing Issue":
            return await self.process_timing_issue(user_info, message, conversation_id)
        else:
            return await self.process_general_inquiry(user_info, message, conversation_id)

# Global instance
caregiver_workflows = CaregiverWorkflows() 