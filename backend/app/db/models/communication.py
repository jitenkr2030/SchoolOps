"""
Communication Database Models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class ChatRoomType(str, enum.Enum):
    DIRECT = "direct"
    GROUP = "group"
    ANNOUNCEMENT = "announcement"


class AnnouncementTarget(str, enum.Enum):
    ALL = "all"
    STUDENTS = "students"
    PARENTS = "parents"
    STAFF = "staff"
    TEACHERS = "teachers"
    ADMIN = "admin"


class CommunicationBase(Base):
    """Abstract base class for communication models"""
    __abstract__ = True
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatRoom(CommunicationBase):
    """Chat room model for real-time messaging"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    room_type = Column(SQLEnum(ChatRoomType), default=ChatRoomType.GROUP)
    description = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    max_participants = Column(Integer, default=100)
    last_message_at = Column(DateTime, nullable=True)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    participants = relationship("ChatParticipant", back_populates="room")
    messages = relationship("Message", back_populates="room")
    
    def __repr__(self):
        return f"<ChatRoom {self.name or self.id}>"


class ChatParticipant(CommunicationBase):
    """Chat room participants model"""
    __tablename__ = "chat_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")  # admin, member
    joined_at = Column(DateTime, server_default=func.now())
    left_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    unread_count = Column(Integer, default=0)
    last_read_message_id = Column(Integer, nullable=True)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<ChatParticipant User {self.user_id} in Room {self.room_id}>"


class Message(CommunicationBase):
    """Message model for chat messages"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    file_url = Column(String(500), nullable=True)
    file_name = Column(String(200), nullable=True)
    file_size = Column(Integer, nullable=True)
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    reply_to_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    reply_to = relationship("Message", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<Message {self.id} by User {self.sender_id}>"


class Announcement(CommunicationBase):
    """Announcement model for broadcasts"""
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    posted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_audience = Column(SQLEnum(AnnouncementTarget), default=AnnouncementTarget.ALL)
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    category = Column(String(50), nullable=True)  # academic, event, emergency, general
    is_pinned = Column(Boolean, default=False)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    published = Column(Boolean, default=True)
    published_at = Column(DateTime, nullable=True)
    views_count = Column(Integer, default=0)
    
    # Relationships
    posted_by = relationship("User", foreign_keys=[posted_by_id])
    
    def __repr__(self):
        return f"<Announcement {self.title}>"


class AnnouncementRead(CommunicationBase):
    """Announcement read receipts"""
    __tablename__ = "announcement_reads"
    
    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    announcement = relationship("Announcement")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<AnnouncementRead Announcement {self.announcement_id} by User {self.user_id}>"


class Meeting(CommunicationBase):
    """Meeting/schedule model for parent-teacher meetings"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meeting_type = Column(String(50), default="general")  # parent_teacher, staff, committee
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    location = Column(String(200), nullable=True)
    meeting_link = Column(String(500), nullable=True)  # For virtual meetings
    max_participants = Column(Integer, default=10)
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    notes = Column(Text, nullable=True)
    
    # Relationships
    organizer = relationship("User", foreign_keys=[organizer_id])
    participants = relationship("MeetingParticipant", back_populates="meeting")
    
    def __repr__(self):
        return f"<Meeting {self.title}>"


class MeetingParticipant(CommunicationBase):
    """Meeting participants model"""
    __tablename__ = "meeting_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    participant_type = Column(String(20), default="attendee")  # attendee, presenter, chair
    response_status = Column(String(20), default="pending")  # pending, accepted, declined, tentative
    responded_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="participants")
    participant = relationship("User", foreign_keys=[participant_id])
    
    def __repr__(self):
        return f"<MeetingParticipant Meeting {self.meeting_id} User {self.participant_id}>"
