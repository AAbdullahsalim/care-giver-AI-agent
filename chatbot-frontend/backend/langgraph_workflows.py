from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from pydantic import BaseModel
import json
from config import Config

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=Config.get_google_api_key(),
    temperature=0.7
)

class ConversationState(BaseModel):
    """State management for LangGraph workflows"""
    messages: List[Dict[str, str]] = []
    user_info: Dict[str, Any] = {}
    scenario_type: Optional[str] = None
    current_step: str = "start"
    collected_data: Dict[str, Any] = {}
    next_action: Optional[str] = None
    suggestions: List[str] = []
    workflow_complete: bool = False

class LangGraphWorkflows:
    """LangGraph workflow manager for caregiver scenarios"""
    
    def __init__(self):
        self.workflows = {
            "schedule_issue": self.create_schedule_workflow(),
            "location_issue": self.create_location_workflow(), 
            "phone_issue": self.create_phone_workflow(),
            "timing_issue": self.create_timing_workflow(),
            "general": self.create_general_workflow()
        }
    
    def analyze_scenario(self, user_message: str, reason: str) -> str:
        """Analyze user input to determine which workflow to use"""
        combined_text = f"{reason} {user_message}".lower()
        
        # Schedule-related keywords
        if any(word in combined_text for word in ["schedule", "calendar", "missing", "not showing", "removed"]):
            return "schedule_issue"
        
        # Location/GPS keywords  
        if any(word in combined_text for word in ["location", "gps", "address", "outside", "range", "distance"]):
            return "location_issue"
            
        # Phone/communication keywords
        if any(word in combined_text for word in ["phone", "number", "call", "ivr", "registered"]):
            return "phone_issue"
            
        # Timing keywords
        if any(word in combined_text for word in ["late", "early", "time", "clock", "hours"]):
            return "timing_issue"
            
        return "general"
    
    def create_schedule_workflow(self) -> StateGraph:
        """Workflow for schedule-related issues"""
        
        def start_schedule_analysis(state: Dict) -> Dict:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a schedule issue.
            
            User Info: {state['user_info']}
            Issue: {state['messages'][-1]['content']}
            
            Analyze the schedule problem and ask the appropriate first question to help resolve it.
            Be professional, empathetic, and follow the company scripts.
            
            Determine if this is:
            1. Missing schedule (no client showing)
            2. Wrong schedule (different client/time)
            3. Schedule conflict
            
            Respond as Rosella would, asking for clarification.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'gather_details'
            state['suggestions'] = [
                "Check your current schedule",
                "Contact your coordinator", 
                "Report the issue"
            ]
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        def gather_schedule_details(state: Dict) -> Dict:
            prompt = f"""
            Continue the conversation as Rosella. The caregiver is providing more details about their schedule issue.
            
            Previous conversation: {state['messages']}
            
            Based on their response, either:
            1. Ask for more specific details if needed
            2. Provide the appropriate solution/next steps
            3. Escalate to coordinator if necessary
            
            Use the Independence Care scripts and be helpful and professional.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            # Determine if we need more info or can provide solution
            if len(state['messages']) < 6:  # Continue gathering info
                state['current_step'] = 'gather_details'
                state['suggestions'] = [
                    "Provide client name",
                    "Confirm usual schedule",
                    "Check app again"
                ]
            else:  # Provide solution
                state['current_step'] = 'provide_solution'
                state['suggestions'] = [
                    "I understand, what should I do?",
                    "Can you add me to the schedule?",
                    "Should I contact the client?"
                ]
                state['workflow_complete'] = True
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        # Build the workflow graph
        workflow = StateGraph(dict)
        workflow.add_node("start_analysis", start_schedule_analysis)
        workflow.add_node("gather_details", gather_schedule_details)
        
        workflow.set_entry_point("start_analysis")
        workflow.add_edge("start_analysis", "gather_details")
        workflow.add_conditional_edges(
            "gather_details",
            lambda x: "gather_details" if not x.get('workflow_complete') else END,
            {"gather_details": "gather_details", END: END}
        )
        
        return workflow.compile()
    
    def create_location_workflow(self) -> StateGraph:
        """Workflow for GPS/location issues"""
        
        def analyze_location_issue(state: Dict) -> Dict:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a location/GPS issue.
            
            User Info: {state['user_info']}
            Issue: {state['messages'][-1]['content']}
            
            This could be:
            1. GPS showing wrong location
            2. Can't clock in due to location
            3. Clocked in/out outside service area
            
            Respond professionally as Rosella, following company policy about location verification.
            Ask appropriate questions to understand the situation.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'verify_location'
            state['suggestions'] = [
                "I'm at the client's house",
                "My GPS isn't working properly",
                "I had to stop somewhere first"
            ]
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        def verify_location_details(state: Dict) -> Dict:
            prompt = f"""
            Continue as Rosella handling the location issue.
            
            Conversation: {state['messages']}
            
            Based on their explanation, provide appropriate guidance:
            - If legitimate reason (picking up supplies), verify with client
            - If GPS error, guide them to try again from correct location
            - If policy violation, explain compliance requirements
            
            Be firm but helpful about location requirements.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'provide_solution'
            state['suggestions'] = [
                "I'll try clocking in again",
                "Can you verify with the client?",
                "What should I do next?"
            ]
            state['workflow_complete'] = True
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        workflow = StateGraph(dict)
        workflow.add_node("analyze_location", analyze_location_issue)
        workflow.add_node("verify_location", verify_location_details)
        
        workflow.set_entry_point("analyze_location")
        workflow.add_edge("analyze_location", "verify_location")
        workflow.add_edge("verify_location", END)
        
        return workflow.compile()
    
    def create_phone_workflow(self) -> StateGraph:
        """Workflow for phone/IVR issues"""
        
        def analyze_phone_issue(state: Dict) -> Dict:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a phone/IVR issue.
            
            User Info: {state['user_info']}
            Issue: {state['messages'][-1]['content']}
            
            This could be:
            1. Phone number not registered
            2. Using wrong phone (personal vs client's)
            3. IVR system not working
            
            Ask appropriate questions to diagnose the phone issue.
            Be helpful and guide them to the right solution.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'diagnose_phone'
            state['suggestions'] = [
                "I'm using the client's phone",
                "My personal phone isn't working",
                "The number isn't recognized"
            ]
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        def resolve_phone_issue(state: Dict) -> Dict:
            prompt = f"""
            Continue as Rosella resolving the phone issue.
            
            Conversation: {state['messages']}
            
            Provide the appropriate solution:
            - Guide them to use client's house phone
            - Help update phone number in system
            - Escalate to technical support if needed
            - Suggest using the mobile app as alternative
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'provide_solution'
            state['suggestions'] = [
                "I'll try the client's phone",
                "Can you update my number?",
                "Should I use the app instead?"
            ]
            state['workflow_complete'] = True
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        workflow = StateGraph(dict)
        workflow.add_node("analyze_phone", analyze_phone_issue)
        workflow.add_node("resolve_phone", resolve_phone_issue)
        
        workflow.set_entry_point("analyze_phone")
        workflow.add_edge("analyze_phone", "resolve_phone")
        workflow.add_edge("resolve_phone", END)
        
        return workflow.compile()
    
    def create_timing_workflow(self) -> StateGraph:
        """Workflow for timing/late arrival issues"""
        
        def analyze_timing_issue(state: Dict) -> Dict:
            prompt = f"""
            You are Rosella from Independence Care. A caregiver has a timing issue.
            
            User Info: {state['user_info']}
            Issue: {state['messages'][-1]['content']}
            
            This could be:
            1. Clocked in late
            2. Clocked in early
            3. Forgot to clock in on time
            4. Schedule timing conflict
            
            Ask about the reason for the timing issue and offer solutions.
            Be understanding but explain policy requirements.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'understand_reason'
            state['suggestions'] = [
                "I was stuck in traffic",
                "I forgot to clock in",
                "The client asked me to come late"
            ]
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        def resolve_timing_issue(state: Dict) -> Dict:
            prompt = f"""
            Continue as Rosella handling the timing issue.
            
            Conversation: {state['messages']}
            
            Based on their reason, offer appropriate solutions:
            - Suggest making up hours later in the week
            - Adjust today's schedule if possible
            - Explain policy about time adjustments
            - Get client confirmation if needed
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'provide_solution'
            state['suggestions'] = [
                "I can stay late today",
                "Can I make up hours tomorrow?",
                "Should I speak with the client?"
            ]
            state['workflow_complete'] = True
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        workflow = StateGraph(dict)
        workflow.add_node("analyze_timing", analyze_timing_issue)
        workflow.add_node("resolve_timing", resolve_timing_issue)
        
        workflow.set_entry_point("analyze_timing")
        workflow.add_edge("analyze_timing", "resolve_timing")
        workflow.add_edge("resolve_timing", END)
        
        return workflow.compile()
    
    def create_general_workflow(self) -> StateGraph:
        """General workflow for other issues"""
        
        def handle_general_issue(state: Dict) -> Dict:
            prompt = f"""
            You are Rosella from Independence Care. Handle this general caregiver inquiry.
            
            User Info: {state['user_info']}
            Issue: {state['messages'][-1]['content']}
            
            Provide helpful, professional assistance. If it's not a standard scenario,
            offer to connect them with the appropriate department or supervisor.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            
            state['current_step'] = 'provide_assistance'
            state['suggestions'] = [
                "Can you help me with this?",
                "Who should I contact?",
                "What's the next step?"
            ]
            state['workflow_complete'] = True
            
            return {
                **state,
                'messages': state['messages'] + [{'role': 'assistant', 'content': response.content}]
            }
        
        workflow = StateGraph(dict)
        workflow.add_node("handle_general", handle_general_issue)
        workflow.set_entry_point("handle_general")
        workflow.add_edge("handle_general", END)
        
        return workflow.compile()
    
    async def process_message(self, user_info: Dict, message: str, conversation_history: List[Dict] = None) -> Dict:
        """Process a message through the appropriate LangGraph workflow"""
        
        # Determine scenario
        scenario_type = self.analyze_scenario(message, user_info.get('reason_for_contact', ''))
        
        # Initialize state
        state = {
            'user_info': user_info,
            'messages': conversation_history or [{'role': 'user', 'content': message}],
            'scenario_type': scenario_type,
            'current_step': 'start',
            'collected_data': {},
            'suggestions': [],
            'workflow_complete': False
        }
        
        # Get appropriate workflow
        workflow = self.workflows.get(scenario_type, self.workflows['general'])
        
        # Execute workflow
        result = workflow.invoke(state)
        
        return {
            'response': result['messages'][-1]['content'],
            'scenario_detected': scenario_type,
            'suggestions': result.get('suggestions', []),
            'workflow_complete': result.get('workflow_complete', False),
            'next_step': result.get('current_step', 'complete')
        } 