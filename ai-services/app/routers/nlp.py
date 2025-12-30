"""
NLP & Conversational UX Router
Multilingual chatbot, voice assistant, automated replies, sentiment analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class ChatbotMessage(BaseModel):
    message: str
    language: str = "en"
    context: Optional[Dict] = None


class ChatbotResponse(BaseModel):
    response: str
    intent: str
    entities: List[dict]
    suggested_actions: List[str]
    confidence: float
    language: str


class VoiceQuery(BaseModel):
    audio_text: str
    language: str = "en"
    user_id: int


class VoiceQueryResponse(BaseModel):
    understood_query: str
    intent: str
    response: str
    confidence: float
    spoken_response_url: Optional[str] = None


class DraftReplyRequest(BaseModel):
    original_message: str
    message_type: str  # parent_inquiry, complaint, feedback
    tone: str  # formal, friendly, empathetic
    context: Optional[Dict] = None


class DraftReplyResponse(BaseModel):
    draft_reply: str
    alternative_tones: List[dict]
    key_points_addressed: List[str]


class SentimentRequest(BaseModel):
    text: str
    context_type: str  # feedback, complaint, parent_message


class SentimentResponse(BaseModel):
    sentiment: str  # positive, negative, neutral
    score: float  # -1 to 1
    emotions: Dict[str, float]
    urgency_level: str
    suggested_response_tone: str


class MultilingualTranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


class MultilingualTranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float


# Knowledge base for chatbot
KNOWLEDGE_BASE = {
    "attendance": {
        "patterns": ["attendance", "absent", "present", "missing", "attendance report"],
        "responses": {
            "check": "To check your child's attendance, please go to the Parent Portal > Attendance section.",
            "report": "You can download the attendance report from the Reports section.",
            "mark": "Teachers can mark attendance through the Teacher Portal > Attendance."
        }
    },
    "fees": {
        "patterns": ["fee", "payment", "due", "receipt", "balance", "concession"],
        "responses": {
            "check": "You can check your fee balance in the Finance section.",
            "pay": "Online payments are available through the payment gateway.",
            "receipt": "Receipts are automatically sent via email after payment.",
            "concession": "Fee concession applications can be submitted through the Admin office."
        }
    },
    "homework": {
        "patterns": ["homework", "assignment", "due", "submit", "deadline"],
        "responses": {
            "view": "You can view homework assignments in the Academics section.",
            "submit": "Students can submit assignments through their portal.",
            "check": "Teachers can check submission status in their dashboard."
        }
    },
    "exam": {
        "patterns": ["exam", "test", "result", "grade", "marks", "score"],
        "responses": {
            "schedule": "Exam schedules are available in the Timetable section.",
            "result": "Results are published after faculty review.",
            "prepare": "Review your notes and practice problems for exam preparation."
        }
    },
    "transport": {
        "patterns": ["bus", "transport", "route", "pickup", "drop", "driver"],
        "responses": {
            "track": "You can track the school bus in real-time through the Transport section.",
            "route": "Bus routes and timings are available in the Transport section.",
            "contact": "For transport issues, contact the transport manager."
        }
    }
}


# Endpoints
@router.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_query(request: ChatbotMessage):
    """
    Multilingual chatbot for parents and students
    Handles queries about attendance, fees, homework, exams, transport
    """
    try:
        logger.info(f"Processing chatbot query: {request.message[:50]}...")
        
        message_lower = request.message.lower()
        
        # Detect intent
        intent = "general"
        entities = []
        
        for category, data in KNOWLEDGE_BASE.items():
            for pattern in data["patterns"]:
                if pattern in message_lower:
                    intent = category
                    entities.append({"type": category, "confidence": 0.9})
                    break
        
        # Handle common queries
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            response = "Hello! How can I help you today? You can ask about attendance, fees, homework, exams, or transport."
            intent = "greeting"
        elif any(word in message_lower for word in ["thank", "thanks"]):
            response = "You're welcome! Is there anything else I can help you with?"
            intent = "appreciation"
        elif any(word in message_lower for word in ["bye", "goodbye"]):
            response = "Goodbye! Feel free to reach out if you need any assistance."
            intent = "farewell"
        elif intent in KNOWLEDGE_BASE:
            # Generate contextual response
            response_data = KNOWLEDGE_BASE[intent]["responses"]
            if "how" in message_lower or "check" in message_lower:
                response = response_data.get("check", response_data.get(list(response_data.keys())[0], "I can help with that."))
            elif "pay" in message_lower or "payment" in message_lower:
                response = response_data.get("pay", "Please check the payment section.")
            else:
                response = response_data.get(list(response_data.keys())[0], "I can help with that.")
        else:
            response = "I'm not sure about that. You can ask about attendance, fees, homework, exams, or transport. For specific issues, please contact the school office."
        
        # Detect language (simplified)
        detected_language = "en"
        
        # Generate suggested actions
        suggested_actions = []
        if intent in ["attendance", "fees", "homework", "exam", "transport"]:
            suggested_actions = [
                f"View {intent} details",
                f"Download {intent} report",
                f"Contact {intent} department"
            ]
        else:
            suggested_actions = [
                "Speak with administrator",
                "Send email to school",
                "Schedule appointment"
            ]
        
        return ChatbotResponse(
            response=response,
            intent=intent,
            entities=entities,
            suggested_actions=suggested_actions,
            confidence=0.85,
            language=detected_language
        )
        
    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def process_voice_query(request: VoiceQuery):
    """
    Process voice queries from parents/students
    Converts speech to text and generates response
    """
    try:
        logger.info(f"Processing voice query from user {request.user_id}")
        
        # Mock voice processing (in production: use Whisper or similar)
        understood_query = request.audio_text
        
        # Get intent and response
        chat_request = ChatbotMessage(
            message=understood_query,
            language=request.language
        )
        chatbot_response = await chatbot_query(chat_request)
        
        return VoiceQueryResponse(
            understood_query=understood_query,
            intent=chatbot_response.intent,
            response=chatbot_response.response,
            confidence=chatbot_response.confidence,
            spoken_response_url=None  # In production: TTS output
        )
        
    except Exception as e:
        logger.error(f"Error in voice query processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft-reply", response_model=DraftReplyResponse)
async def generate_draft_reply(request: DraftReplyRequest):
    """
    Auto-generate reply drafts for common teacher/parent queries
    """
    try:
        logger.info(f"Generating draft reply for: {request.message_type}")
        
        # Mock draft generation
        draft_templates = {
            "parent_inquiry": {
                "formal": "Dear Parent,\n\nThank you for your inquiry regarding [topic]. We have reviewed your concern and [action].\n\nPlease feel free to contact us if you have any further questions.\n\nBest regards,\n[Teacher Name]",
                "friendly": "Hi there!\n\nThanks for reaching out! I've looked into [topic] and [action].\n\nLet me know if you need anything else!\nBest,\n[Teacher Name]",
                "empathetic": "Dear Parent,\n\nI understand your concern about [topic]. I want to assure you that [action].\n\nYour child's well-being and progress are our top priority.\n\nWarm regards,\n[Teacher Name]"
            },
            "complaint": {
                "formal": "Dear [Name],\n\nWe have received your complaint regarding [issue]. We take this matter seriously and are [action].\n\nWe will keep you updated on the progress.\n\nSincerely,\nSchool Administration",
                "friendly": "Hi,\n\nThanks for bringing this to our attention. We're looking into [issue] and [action].\n\nWe appreciate your patience!\nBest,\nSchool Team",
                "empathetic": "Dear [Name],\n\nI sincerely apologize for the inconvenience caused by [issue]. We are [action] to resolve this.\n\nYour satisfaction is important to us.\n\nWith apologies,\nSchool Administration"
            },
            "feedback": {
                "formal": "Dear [Name],\n\nThank you for your valuable feedback regarding [topic]. We appreciate [specific feedback] and will [action].\n\nBest regards,\nSchool Management",
                "friendly": "Thanks so much for your feedback! We're thrilled that [positive feedback]. We're always looking to improve, so [action].\n\nCheers,\nSchool Team",
                "empathetic": "Dear [Name],\n\nYour feedback is deeply appreciated. We understand [concern] and want to [action].\n\nThank you for helping us improve.\nWarm regards,\nSchool Management"
            }
        }
        
        templates = draft_templates.get(request.message_type, draft_templates["parent_inquiry"])
        draft_reply = templates.get(request.tone, templates["formal"])
        
        # Alternative tones
        alternative_tones = [
            {"tone": tone, "preview": content[:100] + "..."}
            for tone, content in templates.items()
            if tone != request.tone
        ]
        
        return DraftReplyResponse(
            draft_reply=draft_reply,
            alternative_tones=alternative_tones,
            key_points_addressed=["Inquiry received", "Action being taken", "Open communication"]
        )
        
    except Exception as e:
        logger.error(f"Error generating draft reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of parent/teacher messages
    """
    try:
        logger.info("Analyzing sentiment")
        
        text_lower = request.text.lower()
        
        # Simple sentiment analysis (in production: use VADER or transformer model)
        positive_words = ["great", "excellent", "good", "happy", "satisfied", "thank", "appreciate", "love", "best"]
        negative_words = ["bad", "poor", "terrible", "angry", "upset", "disappointed", "unhappy", "complaint", "issue", "problem"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total > 0:
            score = (positive_count - negative_count) / total
        else:
            score = 0
        
        # Determine sentiment
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Detect emotions
        emotions = {}
        emotion_keywords = {
            "happy": ["happy", "great", "excellent", "love", "wonderful"],
            "frustrated": ["frustrated", "annoyed", "tired", "fed up"],
            "angry": ["angry", "furious", "outraged", "unacceptable"],
            "concerned": ["worried", "concerned", "afraid", "nervous"],
            "grateful": ["thank", "appreciate", "grateful", "thanks"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            emotions[emotion] = min(count / len(keywords), 1.0)
        
        # Determine urgency
        urgency_keywords = ["urgent", "immediately", "asap", "emergency", "important"]
        urgency_count = sum(1 for kw in urgency_keywords if kw in text_lower)
        
        if urgency_count > 0:
            urgency_level = "urgent"
        elif request.context_type == "complaint":
            urgency_level = "high"
        elif sentiment == "negative":
            urgency_level = "medium"
        else:
            urgency_level = "low"
        
        # Suggested response tone
        if sentiment == "negative":
            response_tone = "empathetic"
        elif urgency_level == "urgent":
            response_tone = "formal"
        else:
            response_tone = "friendly"
        
        return SentimentResponse(
            sentiment=sentiment,
            score=round(score, 3),
            emotions=emotions,
            urgency_level=urgency_level,
            suggested_response_tone=response_tone
        )
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=MultilingualTranslationResponse)
async def translate_text(request: MultilingualTranslationRequest):
    """
    Translate text between languages
    Supports Hindi, English, and regional languages
    """
    try:
        logger.info(f"Translating from {request.source_language} to {request.target_language}")
        
        # Mock translation (in production: use Google Translate or HuggingFace)
        translation_map = {
            ("en", "hi"): {
                "Hello": "नमस्ते",
                "How are you?": "आप कैसे हैं?",
                "Thank you": "धन्यवाद",
                "Attendance": "उपस्थिति",
                "Fees": "शुल्क",
                "Homework": "होमवर्क"
            },
            ("hi", "en"): {
                "नमस्ते": "Hello",
                "आप कैसे हैं?": "How are you?",
                "धन्यवाद": "Thank you",
                "उपस्थिति": "Attendance",
                "शुल्क": "Fees",
                "होमवर्क": "Homework"
            }
        }
        
        # Simple word-by-word translation
        source_words = request.text.split()
        translated_words = []
        
        key = (request.source_language, request.target_language)
        translation_dict = translation_map.get(key, {})
        
        for word in source_words:
            translated_words.append(translation_dict.get(word, f"[{word}]"))
        
        translated_text = " ".join(translated_words)
        
        return MultilingualTranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            confidence=0.85 if translated_text != request.text else 0.5
        )
        
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
