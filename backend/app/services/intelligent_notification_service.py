"""
Intelligent Notification Service
AI-powered message generation for parent/student communications
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.provider import AIProvider, get_ai_service
from app.schema.ai_schema import (
    RecipientType,
    NotificationContextType,
    MessageGenerationRequest,
    GeneratedMessage,
    BulkMessageRequest,
)

logger = logging.getLogger(__name__)


class IntelligentNotificationService:
    """
    Service for generating AI-powered notification messages
    
    Creates personalized, context-aware messages for parents and students
    based on the specific situation and available data.
    """
    
    # Message templates with placeholders for context injection
    TEMPLATES = {
        (RecipientType.PARENT, NotificationContextType.ATTENDANCE_WARNING): {
            "tone": "formal",
            "template": """Dear Parent/Guardian,

We are writing to inform you that {student_name} has accumulated {absences} absence(s) during the current term. This is concerning as regular attendance is crucial for academic success.

We kindly request that you ensure {student_name} attends school regularly from now on. If there are extenuating circumstances, please contact us at your earliest convenience.

Thank you for your cooperation in supporting {student_name}'s education.

Best regards,
School Administration"""
        },
        (RecipientType.PARENT, NotificationContextType.ATTENDANCE_CELEBRATION): {
            "tone": "friendly",
            "template": """Dear Parent/Guardian,

We are pleased to inform you that {student_name} has maintained excellent attendance this term with {present_days} days present out of {total_days} total school days. This demonstrates {student_name}'s commitment to learning.

Keep up the great work! We appreciate your support in ensuring regular attendance.

Warm regards,
School Administration"""
        },
        (RecipientType.PARENT, NotificationContextType.GRADE_WARNING): {
            "tone": "formal",
            "template": """Dear Parent/Guardian,

We wanted to bring to your attention that {student_name}'s recent academic performance in {subject} requires attention. The current grade is {grade}%, which is below the expected standard.

We recommend the following steps:
1. Review {student_name}'s study habits and schedule
2. Consider additional support or tutoring
3. Set up a meeting with the subject teacher

Please feel free to contact us to discuss how we can work together to support {student_name}'s improvement.

Best regards,
School Administration"""
        },
        (RecipientType.PARENT, NotificationContextType.GRADE_CELEBRATION): {
            "tone": "friendly",
            "template": """Dear Parent/Guardian,

Great news! {student_name} has achieved excellent results in {subject} with a score of {grade}%. This is a testament to {student_name}'s hard work and your support at home.

We encourage {student_name} to continue this positive momentum. Congratulations on this achievement!

Warm regards,
School Administration"""
        },
        (RecipientType.STUDENT, NotificationContextType.ATTENDANCE_WARNING): {
            "tone": "encouraging",
            "template": """Dear {student_name},

Your attendance has been tracked, and we noticed you have missed {absences} days recently. Attending school regularly helps you keep up with your studies and connect with friends.

We believe in you and want to see you succeed. Try to be present every day from now on. If there's anything preventing you from attending, please let us know so we can help.

Best wishes,
School Administration"""
        },
        (RecipientType.STUDENT, NotificationContextType.GRADE_WARNING): {
            "tone": "supportive",
            "template": """Dear {student_name},

We noticed that your recent score in {subject} was {grade}%. Don't worry - this is just one step in your learning journey! Many students face challenges, and the important thing is to keep trying.

Here are some suggestions:
- Talk to your teacher about areas you find difficult
- Set aside regular study time
- Ask for help when you need it

You have the potential to improve. We're here to support you!

Best regards,
School Administration"""
        },
    }
    
    def __init__(self, db: AsyncSession, ai_provider: Optional[AIProvider] = None):
        self.db = db
        self.ai = ai_provider or None
    
    async def _get_ai(self) -> AIProvider:
        """Get AI provider lazily"""
        if self.ai is None:
            self.ai = await get_ai_service()
        return self.ai
    
    async def generate_message(
        self, 
        request: MessageGenerationRequest
    ) -> GeneratedMessage:
        """
        Generate a notification message based on the request
        
        Args:
            request: Message generation configuration
            
        Returns:
            GeneratedMessage with content and metadata
        """
        # Check if we have a template for this context
        template_key = (request.recipient_type, request.context_type)
        
        if template_key in self.TEMPLATES:
            # Use template-based generation with AI enhancement
            message = await self._generate_from_template(request)
        else:
            # Use pure AI generation for custom contexts
            message = await self._generate_from_scratch(request)
        
        # Ensure message doesn't exceed max length
        message.content = message.content[:request.max_length]
        message.character_count = len(message.content)
        message.sms_segments = (message.character_count // 160) + 1
        
        return message
    
    async def generate_bulk_messages(
        self,
        request: BulkMessageRequest
    ) -> List[GeneratedMessage]:
        """
        Generate messages for multiple recipients
        
        Args:
            request: Bulk message configuration
            
        Returns:
            List of GeneratedMessage objects
        """
        messages = []
        
        for recipient_id in request.recipient_ids:
            msg_request = request.base_request.model_copy()
            msg_request.student_id = recipient_id
            
            message = await self.generate_message(msg_request)
            messages.append(message)
        
        return messages
    
    async def _generate_from_template(
        self,
        request: MessageGenerationRequest
    ) -> GeneratedMessage:
        """
        Generate message using a template with AI enhancement
        
        Fills in template placeholders and uses AI to personalize
        the message based on the context data.
        """
        template_key = (request.recipient_type, request.context_type)
        template_info = self.TEMPLATES[template_key]
        template = template_info["template"]
        base_tone = template_info["tone"]
        
        # Fill in placeholders from key_data
        placeholders_used = []
        content = template
        
        for key, value in request.key_data.items():
            placeholder = "{" + key + "}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))
                placeholders_used.append(key)
        
        # Use AI to enhance the message if custom instructions provided
        if request.custom_instructions:
            ai = await self._get_ai()
            
            enhancement_prompt = f"""Enhance the following message while keeping the same meaning:

ORIGINAL MESSAGE:
{content}

INSTRUCTIONS:
- Tone: {base_tone}
- Custom request: {request.custom_instructions}
- Maximum length: {request.max_length} characters

Please rewrite this message to better match the requested tone while preserving all key information. Output only the enhanced message."""
            
            response = await ai.generate_text(
                prompt=enhancement_prompt,
                system_prompt="You are a professional school communication assistant. Rewrite messages to be clear, appropriate, and effective.",
                temperature=0.5
            )
            
            if response.success and response.content:
                content = response.content.strip()
        
        # Determine final tone
        tone = base_tone
        if request.custom_instructions:
            if "urgent" in request.custom_instructions.lower():
                tone = "urgent"
            elif "friendly" in request.custom_instructions.lower():
                tone = "friendly"
        
        return GeneratedMessage(
            content=content.strip(),
            tone=tone,
            language=request.language,
            placeholders_used=placeholders_used,
            character_count=len(content),
            sms_segments=1,
            confidence_score=0.85,
            alternatives=[]
        )
    
    async def _generate_from_scratch(
        self,
        request: MessageGenerationRequest
    ) -> GeneratedMessage:
        """
        Generate message using pure AI for custom contexts
        
        Uses the AI model to generate an appropriate message based
        on the context type and available data.
        """
        ai = await self._get_ai()
        
        # Build context description
        context_desc = self._build_context_description(request)
        
        # Determine tone based on context type
        tone = self._get_tone_for_context(request.context_type)
        
        prompt = f"""Generate a {tone} notification message for a {request.recipient_type.lower()}.

CONTEXT TYPE: {request.context_type}

CONTEXT DATA:
{context_desc}

REQUIREMENTS:
1. Message must be clear and professional
2. Maximum {request.max_length} characters
3. Include relevant details from the context data
4. Be appropriate for the recipient type
5. Include appropriate greeting and closing

OUTPUT:
Generate only the message content, no explanations."""
        
        if request.custom_instructions:
            prompt += f"\n\nADDITIONAL INSTRUCTIONS: {request.custom_instructions}"
        
        response = await ai.generate_text(
            prompt=prompt,
            system_prompt=f"""You are a school communication assistant. Generate clear, appropriate messages for parents and students.
- For PARENTS: Be formal, respectful, and professional
- For STUDENTS: Be encouraging, supportive, and age-appropriate
- Always maintain a helpful, constructive tone""",
            temperature=0.7,
            max_tokens=256
        )
        
        if not response.success:
            # Fallback to basic message
            return self._create_fallback_message(request, tone)
        
        content = response.content.strip()
        
        # Generate alternatives
        alternatives = []
        if request.context_type not in [NotificationContextType.GENERAL_ANNOUNCEMENT]:
            alt_prompt = f"""Generate an alternative version of this message with a different tone.

ORIGINAL: {content}
ORIGINAL TONE: {tone}
NEW TONE: {'more formal' if tone == 'friendly' else 'more friendly'}

Generate only the alternative message."""
            
            alt_response = await ai.generate_text(
                prompt=alt_prompt,
                temperature=0.8
            )
            
            if alt_response.success and alt_response.content:
                alternatives.append(alt_response.content.strip())
        
        return GeneratedMessage(
            content=content,
            tone=tone,
            language=request.language,
            placeholders_used=list(request.key_data.keys()),
            character_count=len(content),
            sms_segments=1,
            confidence_score=0.8,
            alternatives=alternatives
        )
    
    def _build_context_description(self, request: MessageGenerationRequest) -> str:
        """Build a human-readable context description from key data"""
        parts = []
        
        if request.student_name:
            parts.append(f"Student Name: {request.student_name}")
        
        for key, value in request.key_data.items():
            parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(parts)
    
    def _get_tone_for_context(self, context_type: NotificationContextType) -> str:
        """Determine appropriate tone for the context type"""
        tone_map = {
            NotificationContextType.ATTENDANCE_WARNING: "formal",
            NotificationContextType.ATTENDANCE_CELEBRATION: "friendly",
            NotificationContextType.GRADE_WARNING: "formal",
            NotificationContextType.GRADE_CELEBRATION: "friendly",
            NotificationContextType.BEHAVIOR_CONCERN: "formal",
            NotificationContextType.EVENT_REMINDER: "friendly",
            NotificationContextType.FEE_REMINDER: "formal",
            NotificationContextType.GENERAL_ANNOUNCEMENT: "neutral",
            NotificationContextType.CUSTOM: "neutral",
        }
        return tone_map.get(context_type, "neutral")
    
    def _create_fallback_message(
        self,
        request: MessageGenerationRequest,
        tone: str
    ) -> GeneratedMessage:
        """Create a basic message when AI is unavailable"""
        student_name = request.student_name or "the student"
        context_type = request.context_type.value.replace("_", " ").title()
        
        if "WARNING" in request.context_type.value:
            content = f"Dear Parent/Guardian, regarding {student_name}: {context_type}. Please contact the school for more information."
        elif "CELEBRATION" in request.context_type.value:
            content = f"Dear Parent/Guardian, great news regarding {student_name}: {context_type}. We wanted to share this positive update with you."
        else:
            content = f"School notification regarding {student_name}: {context_type}."
        
        return GeneratedMessage(
            content=content,
            tone=tone,
            language=request.language,
            placeholders_used=["student_name"],
            character_count=len(content),
            sms_segments=1,
            confidence_score=0.5,
            alternatives=[]
        )
    
    def get_available_contexts(self) -> List[Dict[str, str]]:
        """Get list of available notification context types"""
        return [
            {
                "type": ctx.value,
                "recipient": recipient.value,
                "tone": self.TEMPLATES.get((recipient, ctx), {}).get("tone", "AI-generated")
            }
            for ctx in NotificationContextType
            for recipient in RecipientType
        ]
