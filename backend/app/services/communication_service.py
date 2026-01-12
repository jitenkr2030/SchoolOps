"""
Communication Service - Business Logic
"""
from typing import Optional, List, Dict
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from collections import defaultdict

from app.db.models.communication import (
    ChatRoom, ChatParticipant, Message, Announcement,
    AnnouncementRead, Meeting, MeetingParticipant,
    ChatRoomType, MessageType, AnnouncementTarget
)
from app.schema.communication_schema import (
    ChatRoomCreate, ChatRoomUpdate, MessageCreate,
    AnnouncementCreate, AnnouncementUpdate, MeetingCreate,
    MeetingUpdate, MeetingResponseUpdate
)


class CommunicationService:
    """Service class for communication operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # ==================== Chat Room Operations ====================
    
    async def create_chat_room(
        self,
        room_data: ChatRoomCreate,
        created_by_id: int
    ) -> ChatRoom:
        """Create a new chat room"""
        room = ChatRoom(
            **room_data.model_dump(exclude={'participant_ids'}),
            created_by_id=created_by_id
        )
        self.session.add(room)
        await self.session.flush()
        
        # Add creator as participant
        creator_participant = ChatParticipant(
            room_id=room.id,
            user_id=created_by_id,
            role="admin",
            is_active=True
        )
        self.session.add(creator_participant)
        
        # Add other participants
        for participant_id in room_data.participant_ids:
            if participant_id != created_by_id:
                participant = ChatParticipant(
                    room_id=room.id,
                    user_id=participant_id,
                    is_active=True
                )
                self.session.add(participant)
        
        await self.session.commit()
        await self.session.refresh(room)
        return room
    
    async def get_chat_room(self, room_id: int) -> Optional[ChatRoom]:
        """Get chat room by ID"""
        result = await self.session.execute(
            select(ChatRoom)
            .options(selectinload(ChatRoom.participants))
            .where(ChatRoom.id == room_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_chat_rooms(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatRoom]:
        """Get all chat rooms for a user"""
        result = await self.session.execute(
            select(ChatRoom)
            .join(ChatParticipant, ChatParticipant.room_id == ChatRoom.id)
            .where(
                and_(
                    ChatParticipant.user_id == user_id,
                    ChatParticipant.is_active == True
                )
            )
            .options(selectinload(ChatRoom.participants))
            .order_by(ChatRoom.last_message_at.desc().nullsfirst())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_chat_room(
        self,
        room_id: int,
        room_data: ChatRoomUpdate
    ) -> Optional[ChatRoom]:
        """Update chat room"""
        room = await self.get_chat_room(room_id)
        if not room:
            return None
        
        update_data = room_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)
        
        await self.session.commit()
        await self.session.refresh(room)
        return room
    
    async def delete_chat_room(self, room_id: int) -> bool:
        """Delete a chat room"""
        room = await self.get_chat_room(room_id)
        if not room:
            return False
        
        await self.session.delete(room)
        await self.session.commit()
        return True
    
    async def add_participant_to_room(
        self,
        room_id: int,
        user_id: int,
        role: str = "member"
    ) -> Optional[ChatParticipant]:
        """Add a participant to chat room"""
        room = await self.get_chat_room(room_id)
        if not room:
            return None
        
        # Check if already a participant
        result = await self.session.execute(
            select(ChatParticipant).where(
                and_(
                    ChatParticipant.room_id == room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.joined_at = datetime.utcnow()
                await self.session.commit()
                await self.session.refresh(existing)
            return existing
        
        # Check room capacity
        count_result = await self.session.execute(
            select(func.count(ChatParticipant.id)).where(
                and_(
                    ChatParticipant.room_id == room_id,
                    ChatParticipant.is_active == True
                )
            )
        )
        participant_count = count_result.scalar() or 0
        if participant_count >= room.max_participants:
            raise ValueError("Chat room has reached maximum capacity")
        
        participant = ChatParticipant(
            room_id=room_id,
            user_id=user_id,
            role=role,
            is_active=True
        )
        self.session.add(participant)
        await self.session.commit()
        await self.session.refresh(participant)
        return participant
    
    async def remove_participant_from_room(
        self,
        room_id: int,
        user_id: int
    ) -> bool:
        """Remove a participant from chat room"""
        result = await self.session.execute(
            select(ChatParticipant).where(
                and_(
                    ChatParticipant.room_id == room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        participant = result.scalar_one_or_none()
        if not participant:
            return False
        
        participant.is_active = False
        participant.left_at = datetime.utcnow()
        await self.session.commit()
        return True
    
    # ==================== Message Operations ====================
    
    async def send_message(
        self,
        message_data: MessageCreate,
        sender_id: int
    ) -> Message:
        """Send a message to a chat room"""
        # Verify user is participant
        result = await self.session.execute(
            select(ChatParticipant).where(
                and_(
                    ChatParticipant.room_id == message_data.room_id,
                    ChatParticipant.user_id == sender_id,
                    ChatParticipant.is_active == True
                )
            )
        )
        participant = result.scalar_one_or_none()
        if not participant:
            raise ValueError("User is not a participant of this chat room")
        
        message = Message(
            **message_data.model_dump(),
            sender_id=sender_id
        )
        self.session.add(message)
        
        # Update room's last_message_at
        room = await self.get_chat_room(message_data.room_id)
        if room:
            room.last_message_at = datetime.utcnow()
        
        # Update unread counts for other participants
        participants_result = await self.session.execute(
            select(ChatParticipant).where(
                and_(
                    ChatParticipant.room_id == message_data.room_id,
                    ChatParticipant.user_id != sender_id,
                    ChatParticipant.is_active == True
                )
            )
        )
        for p in participants_result.scalars().all():
            p.unread_count += 1
        
        await self.session.commit()
        await self.session.refresh(message)
        return message
    
    async def get_message(self, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        result = await self.session.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def get_room_messages(
        self,
        room_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages from a chat room"""
        result = await self.session.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.room_id == room_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return in chronological order
    
    async def mark_messages_as_read(
        self,
        room_id: int,
        user_id: int,
        last_read_message_id: Optional[int] = None
    ) -> bool:
        """Mark all messages in room as read"""
        result = await self.session.execute(
            select(ChatParticipant).where(
                and_(
                    ChatParticipant.room_id == room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        participant = result.scalar_one_or_none()
        if not participant:
            return False
        
        participant.unread_count = 0
        if last_read_message_id:
            participant.last_read_message_id = last_read_message_id
        
        await self.session.commit()
        return True
    
    async def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message (soft delete)"""
        message = await self.get_message(message_id)
        if not message:
            return False
        
        if message.sender_id != user_id:
            raise ValueError("User can only delete their own messages")
        
        message.is_deleted = True
        await self.session.commit()
        return True
    
    # ==================== Announcement Operations ====================
    
    async def create_announcement(
        self,
        announcement_data: AnnouncementCreate,
        posted_by_id: int
    ) -> Announcement:
        """Create a new announcement"""
        announcement = Announcement(
            **announcement_data.model_dump(),
            posted_by_id=posted_by_id,
            published_at=datetime.utcnow() if announcement_data.published else None
        )
        self.session.add(announcement)
        await self.session.commit()
        await self.session.refresh(announcement)
        return announcement
    
    async def get_announcement(self, announcement_id: int) -> Optional[Announcement]:
        """Get announcement by ID"""
        result = await self.session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
        )
        return result.scalar_one_or_none()
    
    async def get_announcements(
        self,
        skip: int = 0,
        limit: int = 100,
        target_audience: Optional[AnnouncementTarget] = None,
        category: Optional[str] = None,
        published_only: bool = True
    ) -> List[Announcement]:
        """Get announcements with filtering"""
        query = select(Announcement)
        
        if published_only:
            query = query.where(Announcement.published == True)
        if target_audience:
            query = query.where(Announcement.target_audience == target_audience)
        if category:
            query = query.where(Announcement.category == category)
        
        query = query.order_by(
            Announcement.is_pinned.desc(),
            Announcement.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_announcement(
        self,
        announcement_id: int,
        announcement_data: AnnouncementUpdate
    ) -> Optional[Announcement]:
        """Update announcement"""
        announcement = await self.get_announcement(announcement_id)
        if not announcement:
            return None
        
        update_data = announcement_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(announcement, field, value)
        
        await self.session.commit()
        await self.session.refresh(announcement)
        return announcement
    
    async def delete_announcement(self, announcement_id: int) -> bool:
        """Delete an announcement"""
        announcement = await self.get_announcement(announcement_id)
        if not announcement:
            return False
        
        await self.session.delete(announcement)
        await self.session.commit()
        return True
    
    async def mark_announcement_as_read(
        self,
        announcement_id: int,
        user_id: int
    ) -> AnnouncementRead:
        """Mark announcement as read"""
        # Check if already read
        result = await self.session.execute(
            select(AnnouncementRead).where(
                and_(
                    AnnouncementRead.announcement_id == announcement_id,
                    AnnouncementRead.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        
        read_receipt = AnnouncementRead(
            announcement_id=announcement_id,
            user_id=user_id
        )
        self.session.add(read_receipt)
        
        # Increment views count
        announcement = await self.get_announcement(announcement_id)
        if announcement:
            announcement.views_count += 1
        
        await self.session.commit()
        await self.session.refresh(read_receipt)
        return read_receipt
    
    async def get_user_announcements(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Announcement]:
        """Get announcements visible to a user"""
        # Get announcements
        announcements = await self.get_announcements(
            skip=skip,
            limit=limit,
            published_only=True
        )
        return announcements
    
    async def get_unread_announcement_count(self, user_id: int) -> int:
        """Get count of unread announcements for user"""
        # This would require checking which announcements have been read
        result = await self.session.execute(
            select(func.count(Announcement.id)).where(
                and_(
                    Announcement.published == True,
                    Announcement.valid_from.is_(None) or Announcement.valid_from <= datetime.utcnow(),
                    Announcement.valid_until.is_(None) or Announcement.valid_until >= datetime.utcnow()
                )
            )
        )
        total = result.scalar() or 0
        
        # Subtract read announcements
        read_result = await self.session.execute(
            select(func.count(AnnouncementRead.id))
            .where(AnnouncementRead.user_id == user_id)
        )
        read_count = read_result.scalar() or 0
        
        return total - read_count
    
    # ==================== Meeting Operations ====================
    
    async def create_meeting(
        self,
        meeting_data: MeetingCreate,
        organizer_id: int
    ) -> Meeting:
        """Create a new meeting"""
        meeting = Meeting(
            **meeting_data.model_dump(exclude={'participant_ids'}),
            organizer_id=organizer_id
        )
        self.session.add(meeting)
        await self.session.flush()
        
        # Add participants
        for participant_id in meeting_data.participant_ids:
            participant = MeetingParticipant(
                meeting_id=meeting.id,
                participant_id=participant_id
            )
            self.session.add(participant)
        
        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting
    
    async def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID"""
        result = await self.session.execute(
            select(Meeting)
            .options(selectinload(Meeting.participants))
            .where(Meeting.id == meeting_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_meetings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        upcoming_only: bool = False
    ) -> List[Meeting]:
        """Get meetings for a user"""
        query = select(Meeting).join(
            MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id
        ).where(
            and_(
                MeetingParticipant.participant_id == user_id,
                Meeting.status.in_(["scheduled", "in_progress"])
            )
        )
        
        if upcoming_only:
            query = query.where(Meeting.scheduled_date > datetime.utcnow())
        
        query = query.order_by(Meeting.scheduled_date.asc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_meeting(
        self,
        meeting_id: int,
        meeting_data: MeetingUpdate
    ) -> Optional[Meeting]:
        """Update meeting"""
        meeting = await self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        update_data = meeting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        
        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting
    
    async def update_meeting_response(
        self,
        meeting_id: int,
        user_id: int,
        response_data: MeetingResponseUpdate
    ) -> Optional[MeetingParticipant]:
        """Update user's meeting response"""
        result = await self.session.execute(
            select(MeetingParticipant).where(
                and_(
                    MeetingParticipant.meeting_id == meeting_id,
                    MeetingParticipant.participant_id == user_id
                )
            )
        )
        participant = result.scalar_one_or_none()
        if not participant:
            return None
        
        participant.response_status = response_data.response_status
        participant.responded_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(participant)
        return participant
    
    async def cancel_meeting(self, meeting_id: int) -> Optional[Meeting]:
        """Cancel a meeting"""
        meeting = await self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        meeting.status = "cancelled"
        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting
    
    async def get_upcoming_meetings_count(self, user_id: int) -> int:
        """Get count of upcoming meetings"""
        result = await self.session.execute(
            select(func.count(Meeting.id)).join(
                MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id
            ).where(
                and_(
                    MeetingParticipant.participant_id == user_id,
                    Meeting.scheduled_date > datetime.utcnow(),
                    Meeting.status == "scheduled"
                )
            )
        )
        return result.scalar() or 0
    
    # ==================== Analytics Operations ====================
    
    async def get_communication_summary(self, user_id: int) -> dict:
        """Get communication summary for a user"""
        # Chat statistics
        rooms_result = await self.session.execute(
            select(func.count(ChatRoom.id)).join(
                ChatParticipant, ChatParticipant.room_id == ChatRoom.id
            ).where(
                and_(
                    ChatParticipant.user_id == user_id,
                    ChatParticipant.is_active == True
                )
            )
        )
        total_rooms = rooms_result.scalar() or 0
        
        messages_result = await self.session.execute(
            select(func.count(Message.id)).where(Message.sender_id == user_id)
        )
        total_messages = messages_result.scalar() or 0
        
        # Announcement statistics
        announcements_result = await self.session.execute(
            select(func.count(Announcement.id)).where(Announcement.published == True)
        )
        total_announcements = announcements_result.scalar() or 0
        
        unread_announcements = await self.get_unread_announcement_count(user_id)
        
        # Meeting statistics
        upcoming_meetings = await self.get_upcoming_meetings_count(user_id)
        
        meetings_result = await self.session.execute(
            select(func.count(Meeting.id)).join(
                MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id
            ).where(MeetingParticipant.participant_id == user_id)
        )
        total_meetings = meetings_result.scalar() or 0
        
        # Total participations
        participations_result = await self.session.execute(
            select(func.count(MeetingParticipant.id))
            .where(MeetingParticipant.participant_id == user_id)
        )
        total_participations = participations_result.scalar() or 0
        
        return {
            'total_rooms': total_rooms,
            'total_messages': total_messages,
            'total_announcements': total_announcements,
            'unread_announcements': unread_announcements,
            'total_meetings': total_meetings,
            'upcoming_meetings': upcoming_meetings,
            'total_participations': total_participations
        }
