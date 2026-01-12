"""
Communication Pydantic Schemas
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MessageTypeEnum(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class ChatRoomTypeEnum(str, Enum):
    DIRECT = "direct"
    GROUP = "group"
    ANNOUNCEMENT = "announcement"


class AnnouncementTargetEnum(str, Enum):
    ALL = "all"
    STUDENTS = "students"
    PARENTS = "parents"
    STAFF = "staff"
    TEACHERS = "teachers"
    ADMIN = "admin"


# ==================== Chat Room Schemas ====================

class ChatRoomBase(BaseModel):
    """Base schema for chat room"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    room_type: ChatRoomTypeEnum = ChatRoomTypeEnum.GROUP
    max_participants: int = Field(default=100, ge=2)


class ChatRoomCreate(ChatRoomBase):
    """Schema for creating chat room"""
    participant_ids: List[int] = []


class ChatRoomUpdate(BaseModel):
    """Schema for updating chat room"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    max_participants: Optional[int] = Field(None, ge=2)
    is_active: Optional[bool] = None


class ChatRoomResponse(ChatRoomBase):
    """Schema for chat room response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_by_id: int
    is_active: bool
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ChatRoomWithDetailsResponse(ChatRoomResponse):
    """Schema for room with participant details"""
    created_by_name: Optional[str] = None
    participant_count: int = 0
    participants: List[ChatParticipantResponse] = []
    last_message: Optional[MessageResponse] = None


class ChatRoomListResponse(BaseModel):
    """Schema for room list response"""
    rooms: List[ChatRoomResponse]
    total: int
    page: int
    page_size: int


# ==================== Chat Participant Schemas ====================

class ChatParticipantBase(BaseModel):
    """Base schema for chat participant"""
    role: str = Field(default="member")


class ChatParticipantResponse(ChatParticipantBase):
    """Schema for chat participant response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    user_id: int
    joined_at: datetime
    is_active: bool
    unread_count: int


class ChatParticipantWithUserResponse(ChatParticipantResponse):
    """Schema for participant with user details"""
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None


# ==================== Message Schemas ====================

class MessageBase(BaseModel):
    """Base schema for message"""
    content: Optional[str] = None
    message_type: MessageTypeEnum = MessageTypeEnum.TEXT


class MessageCreate(MessageBase):
    """Schema for creating message"""
    room_id: int
    reply_to_id: Optional[int] = None


class MessageUpdate(BaseModel):
    """Schema for updating message"""
    content: Optional[str] = None
    is_deleted: Optional[bool] = None


class MessageResponse(MessageBase):
    """Schema for message response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    sender_id: int
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_edited: bool
    is_deleted: bool
    reply_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class MessageWithSenderResponse(MessageResponse):
    """Schema for message with sender details"""
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    reply_to_message: Optional[MessageResponse] = None


class MessageListResponse(BaseModel):
    """Schema for message list response"""
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int


# ==================== WebSocket Message Schema ====================

class WebSocketMessage(BaseModel):
    """Schema for WebSocket message"""
    type: str = Field(..., description="Message type: chat, read, typing, join, leave")
    room_id: int
    sender_id: int
    content: Optional[str] = None
    message_id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketMessageResponse(BaseModel):
    """Response for WebSocket message"""
    success: bool
    message: str


# ==================== Announcement Schemas ====================

class AnnouncementBase(BaseModel):
    """Base schema for announcement"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    target_audience: AnnouncementTargetEnum = AnnouncementTargetEnum.ALL
    priority: str = Field(default="normal")
    category: Optional[str] = Field(None, max_length=50)


class AnnouncementCreate(AnnouncementBase):
    """Schema for creating announcement"""
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    published: bool = True


class AnnouncementUpdate(BaseModel):
    """Schema for updating announcement"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    target_audience: Optional[AnnouncementTargetEnum] = None
    priority: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_pinned: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    published: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    """Schema for announcement response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    posted_by_id: int
    is_pinned: bool
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    published: bool
    published_at: Optional[datetime] = None
    views_count: int
    created_at: datetime
    updated_at: datetime


class AnnouncementWithDetailsResponse(AnnouncementResponse):
    """Schema for announcement with poster details"""
    posted_by_name: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None


class AnnouncementListResponse(BaseModel):
    """Schema for announcement list response"""
    announcements: List[AnnouncementResponse]
    total: int
    page: int
    page_size: int


# ==================== Announcement Read Receipt Schemas ====================

class AnnouncementReadCreate(BaseModel):
    """Schema for marking announcement as read"""
    pass


class AnnouncementReadResponse(BaseModel):
    """Schema for announcement read response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    announcement_id: int
    user_id: int
    read_at: datetime


# ==================== Meeting Schemas ====================

class MeetingBase(BaseModel):
    """Base schema for meeting"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    meeting_type: str = Field(default="general")
    scheduled_date: datetime
    duration_minutes: int = Field(default=30, ge=5, le=480)
    location: Optional[str] = Field(None, max_length=200)
    meeting_link: Optional[str] = Field(None, max_length=500)
    max_participants: int = Field(default=10, ge=2)
    notes: Optional[str] = None


class MeetingCreate(MeetingBase):
    """Schema for creating meeting"""
    participant_ids: List[int] = []


class MeetingUpdate(BaseModel):
    """Schema for updating meeting"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    meeting_type: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    location: Optional[str] = Field(None, max_length=200)
    meeting_link: Optional[str] = Field(None, max_length=500)
    max_participants: Optional[int] = Field(None, ge=2)
    status: Optional[str] = None
    notes: Optional[str] = None


class MeetingResponse(MeetingBase):
    """Schema for meeting response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organizer_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class MeetingWithDetailsResponse(MeetingResponse):
    """Schema for meeting with participant details"""
    organizer_name: Optional[str] = None
    participants: List[MeetingParticipantResponse] = []
    participant_count: int = 0


class MeetingListResponse(BaseModel):
    """Schema for meeting list response"""
    meetings: List[MeetingResponse]
    total: int
    page: int
    page_size: int


# ==================== Meeting Participant Schemas ====================

class MeetingParticipantBase(BaseModel):
    """Base schema for meeting participant"""
    participant_type: str = Field(default="attendee")


class MeetingParticipantResponse(MeetingParticipantBase):
    """Schema for meeting participant response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    meeting_id: int
    participant_id: int
    response_status: str
    responded_at: Optional[datetime] = None


class MeetingParticipantWithUserResponse(MeetingParticipantResponse):
    """Schema for participant with user details"""
    participant_name: Optional[str] = None
    participant_email: Optional[str] = None


class MeetingResponseUpdate(BaseModel):
    """Schema for updating meeting response"""
    response_status: str  # accepted, declined, tentative


# ==================== Communication Summary Schema ====================

class CommunicationSummaryResponse(BaseModel):
    """Schema for communication summary"""
    total_rooms: int
    total_messages: int
    total_announcements: int
    unread_announcements: int
    total_meetings: int
    upcoming_meetings: int
    total_participations: int
