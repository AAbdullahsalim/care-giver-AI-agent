from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime
from enum import Enum
from simple_ai import simple_ai

app = FastAPI(title="Caregiver AI Agent Backend", version="1.0.0")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ScenarioType(str, Enum):
    NO_SCHEDULE = "no_schedule"
    OUT_OF_WINDOW = "out_of_window"
    GPS_OUT_OF_RANGE = "gps_out_of_range"
    WRONG_PHONE_NUMBER = "wrong_phone_number"
    PHONE_NOT_FOUND = "phone_not_found"
    DUPLICATE_CALL = "duplicate_call"

class ChatRequest(BaseModel):
    user_name: str
    contact_number: str
    reason_for_contact: str
    message: str

class ClockInRequest(BaseModel):
    caregiver_name: str
    client_name: Optional[str] = None
    phone_number: str
    location: Dict[str, float]  # {"lat": 40.7128, "lng": -74.0060}
    scheduled_time: str  # ISO format
    actual_time: str  # ISO format
    has_schedule: bool = True

class ClockOutRequest(BaseModel):
    caregiver_name: str
    client_name: str
    phone_number: str
    location: Dict[str, float]
    scheduled_time: str
    actual_time: str

class ScenarioResponse(BaseModel):
    scenario_type: ScenarioType
    agent_script: str
    actions_required: list[str]
    priority: str  # "high", "medium", "low"

class ChatResponse(BaseModel):
    response: str
    scenario_detected: Optional[str] = None
    suggestions: list[str] = []

# In-memory storage (replace with database in production)
registered_phones = {
    "+1234567890": "John Client",
    "+0987654321": "Jane Client"
}

caregiver_schedules = {
    "Mary Caregiver": {
        "client": "John Client",
        "phone": "+1234567890",
        "schedule": "Monday-Friday 9am-5pm",
        "location": {"lat": 40.7128, "lng": -74.0060}
    }
}

@app.get("/")
async def root():
    return {"message": "Caregiver AI Agent Backend is running", "status": "online"}

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """Handle general chat messages from the frontend using Gemini AI"""
    
    try:
        print(f"📥 Received chat request from {request.user_name}")
        
        # Use AI workflows to process the message
        result = await simple_ai.process_message(
            user_info={
                'user_name': request.user_name,
                'contact_number': request.contact_number,
                'reason_for_contact': request.reason_for_contact
            },
            message=request.message
        )
        
        print(f"📤 Sending AI response: {result['response'][:100]}...")
        
        return ChatResponse(
            response=result['response'],
            scenario_detected=result['scenario_detected'],
            suggestions=result['suggestions']
        )
        
    except Exception as e:
        # Fallback to simple response if AI fails
        print(f"❌ AI Error: {e}")
        print("🔄 Using fallback response")
        
        # Determine scenario without AI
        scenario = "General Inquiry"
        if "schedule" in request.message.lower() or "schedule" in request.reason_for_contact.lower():
            scenario = "Schedule Issue"
        elif "location" in request.message.lower() or "gps" in request.message.lower():
            scenario = "Location Issue"
        elif "phone" in request.message.lower():
            scenario = "Phone Issue"
        elif "late" in request.message.lower() or "time" in request.message.lower():
            scenario = "Timing Issue"
        
        return ChatResponse(
            response=f"Hello {request.user_name}! This is Rosella from Independence Care. I understand you're contacting us about: {request.reason_for_contact}. How can I help you with this specific issue?",
            scenario_detected=scenario,
            suggestions=["Tell me more details", "What should I do next?", "Is this urgent?"]
        )

@app.post("/clock-in", response_model=ScenarioResponse)
async def handle_clock_in(request: ClockInRequest):
    """Handle clock-in events and return appropriate agent script"""
    
    # Scenario 1: No schedule on calendar
    if not request.has_schedule or request.client_name is None:
        return ScenarioResponse(
            scenario_type=ScenarioType.NO_SCHEDULE,
            agent_script="""Hello, this is Rosella, I am calling from Independence Care, how are you doing today?
            
I see you clocked in but there seems to be no schedule on your Calendar, can you confirm the client you are working with today?

[Wait for response]

No, please do not leave. Unfortunately, the app can malfunction at times and remove Caregivers from schedules. I will add you to the schedule and clock you in, if for any reason this causes an error your coordinator will reach out to you to clarify.""",
            actions_required=["Add caregiver to schedule", "Clock in caregiver", "Notify coordinator"],
            priority="high"
        )
    
    # Check if phone number is registered
    if request.phone_number not in registered_phones:
        return ScenarioResponse(
            scenario_type=ScenarioType.PHONE_NOT_FOUND,
            agent_script=f"""Hello, this is Rosella, I am calling from Independence Care, how are you doing today!

I have noticed that you have clocked in using a phone number that is not registered with us. Can you confirm whose number this is? ({request.phone_number})

[Wait for confirmation]

Okay, can your client confirm that?

[Get client on phone for verification]""",
            actions_required=["Verify phone number", "Update client profile", "Confirm with client"],
            priority="medium"
        )
    
    # Check location (GPS out of range)
    expected_location = caregiver_schedules.get(request.caregiver_name, {}).get("location")
    if expected_location:
        distance = calculate_distance(request.location, expected_location)
        if distance > 0.5:  # More than 0.5 miles away
            return ScenarioResponse(
                scenario_type=ScenarioType.GPS_OUT_OF_RANGE,
                agent_script="""Hello, this is Rosella, I am calling from Independence Care, how are you doing today!

I have noticed you have clocked in outside of the client's service area, which is not close to your client's house. Can you please clock in again once you are at your client's house, because we are not able to accept this clock in.

[Listen for explanation]

Remember it is state law that a Home Care agency cannot bill for visits that are rendered outside of the client's home.""",
                actions_required=["Request re-clock in", "Verify location", "Document exception if valid"],
                priority="high"
            )
    
    # Check timing (out of window)
    scheduled_dt = datetime.datetime.fromisoformat(request.scheduled_time.replace('Z', '+00:00'))
    actual_dt = datetime.datetime.fromisoformat(request.actual_time.replace('Z', '+00:00'))
    time_diff = abs((actual_dt - scheduled_dt).total_seconds() / 60)  # minutes
    
    if time_diff > 15:  # More than 15 minutes late/early
        return ScenarioResponse(
            scenario_type=ScenarioType.OUT_OF_WINDOW,
            agent_script="""Hello, this is Rosella, I am calling from Independence Care, how are you doing today!

I have noticed that you clocked in late for your shift today, I just wanted to confirm what was the reason for that?

[Listen for reason]

Would you be willing to make up for the hours you missed today by staying late on your shift today? Or any other day throughout the week?""",
            actions_required=["Confirm reason", "Adjust schedule if needed", "Document time change"],
            priority="medium"
        )
    
    # Default successful clock-in
    return ScenarioResponse(
        scenario_type=ScenarioType.NO_SCHEDULE,  # Will add more specific success type
        agent_script="Clock-in successful. Have a great shift!",
        actions_required=["Log successful clock-in"],
        priority="low"
    )

@app.post("/clock-out", response_model=ScenarioResponse)
async def handle_clock_out(request: ClockOutRequest):
    """Handle clock-out events and return appropriate agent script"""
    
    # Check location for clock-out
    expected_location = caregiver_schedules.get(request.caregiver_name, {}).get("location")
    if expected_location:
        distance = calculate_distance(request.location, expected_location)
        if distance > 0.5:  # More than 0.5 miles away
            return ScenarioResponse(
                scenario_type=ScenarioType.GPS_OUT_OF_RANGE,
                agent_script="""Hello, this is Rosella, I am calling from Independence Care, how are you doing today!

I have noticed your clock out is outside of the client's service area, and we are not able to accept that. Can you please go back and clock out from your client's house? Because we can't complete the visit without your clock out.

I apologize for the inconvenience this causes but we will not be able to mark your shift as completed without a clock out, so it is really important.""",
                actions_required=["Request return to client location", "Re-clock out", "Document issue"],
                priority="high"
            )
    
    return ScenarioResponse(
        scenario_type=ScenarioType.NO_SCHEDULE,  # Success type
        agent_script="Clock-out successful. Thank you for your service today!",
        actions_required=["Log successful clock-out"],
        priority="low"
    )

@app.post("/duplicate-call")
async def handle_duplicate_call():
    """Handle duplicate clock-in/out events - no call needed"""
    return {"message": "Duplicate call detected - no action required", "action": "reject"}

def analyze_message_for_scenario(message: str, reason: str) -> Optional[Dict]:
    """Analyze user message to detect caregiver scenarios"""
    combined_text = f"{message} {reason}".lower()
    
    # Clock-in/out issues
    if any(word in combined_text for word in ["clock", "schedule", "late", "early", "time"]):
        if "schedule" in combined_text or "calendar" in combined_text:
            return {
                "type": "Schedule Issue",
                "response": "It sounds like there might be a scheduling conflict. Let me help you resolve this.",
                "suggestions": ["Check your current schedule", "Contact your coordinator", "Report the issue"]
            }
        if "late" in combined_text or "early" in combined_text:
            return {
                "type": "Timing Issue", 
                "response": "I can help you with timing adjustments and make-up hours if needed.",
                "suggestions": ["Explain the reason for timing issue", "Request schedule adjustment", "Speak with client"]
            }
    
    # Location/GPS issues
    if any(word in combined_text for word in ["location", "gps", "address", "house", "outside"]):
        return {
            "type": "Location Issue",
            "response": "Location verification is important for compliance. Let me guide you through the proper procedure.",
            "suggestions": ["Verify you're at client location", "Try clocking in again", "Contact support"]
        }
    
    # Phone issues
    if any(word in combined_text for word in ["phone", "number", "call", "ivr"]):
        return {
            "type": "Phone Issue",
            "response": "Phone number verification is required. Let me help you get this sorted out.",
            "suggestions": ["Use client's house phone", "Verify phone number", "Update contact info"]
        }
    
    return None

def calculate_distance(loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
    """Calculate distance between two GPS coordinates (simplified)"""
    # Simple distance calculation (in real app, use proper geolocation library)
    lat_diff = abs(loc1["lat"] - loc2["lat"])
    lng_diff = abs(loc1["lng"] - loc2["lng"])
    return (lat_diff + lng_diff) * 69  # Rough miles conversion

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 