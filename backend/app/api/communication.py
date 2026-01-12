"""
Communication API Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.communication_service import CommunicationService
from app.services.chat_manager import chat_manager, message_formatter
from app.schema.communication_schema import (
    ChatRoomCreate, ChatRoomUpdate, ChatRoomResponse, ChatRoomWithDetailsResponse,
    MessageCreate, MessageResponse, MessageListResponse,
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse, AnnouncementListResponse,
    MeetingCreate, MeetingUpdate, MeetingResponse, MeetingListResponse,
    MeetingResponseUpdate, AnnouncementReadCreate,
    ChatRoomListResponse, CommunicationSummaryResponse
)
from app.core.security import get_current_user, get_current_user_from_websocket
from app.db.models.models import User


router = APIRouter(prefix="/communication", tags=["Communication"])


# ==================== Chat Room Endpoints ====================

@router.post("/rooms", response_model=ChatRoomResponse)
async def create_chat_room(
    room: ChatRoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat room"""
    service = CommunicationService(db)
    return await service.create_chat_room(room, current_user.id)


@router.get("/rooms", response_model=ChatRoomListResponse)
async def get_chat_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat rooms for current user"""
    service = CommunicationService(db)
    rooms = await service.get_user_chat_rooms(current_user.id, skip, limit)
    return {"rooms": rooms, "total": len(rooms), "page": skip // limit + 1, "page_size": limit}


@router.get("/rooms/{room_id}", response_model=ChatRoomWithDetailsResponse)
async def get_chat_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat room by ID"""
    service = CommunicationService(db)
    room = await service.get_chat_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    # Get last message if exists
    last_message = None
    if room.last_message_at:
        messages = await service.get_room_messages(room_id, skip=0, limit=1)
        last_message = messages[0] if messages else None
    
    return {
        **room.__dict__,
        "participant_count": len(room.participants) if room.participants else 0,
        "participants": room.participants,
        "last_message": last_message
    }


@router.put("/rooms/{room_id}", response_model=ChatRoomResponse)
async def update_chat_room(
    room_id: int,
    room_update: ChatRoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update chat room"""
    service = CommunicationService(db)
    room = await service.update_chat_room(room_id, room_update)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return room


@router.delete("/rooms/{room_id}")
async def delete_chat_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat room"""
    service = CommunicationService(db)
    success = await service.delete_chat_room(room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return {"message": "Chat room deleted successfully"}


@router.post("/rooms/{room_id}/participants/{user_id}")
async def add_participant(
    room_id: int,
    user_id: int,
    role: str = "member",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add participant to chat room"""
    service = CommunicationService(db)
    try:
        participant = await service.add_participant_to_room(room_id, user_id, role)
        return {"message": "Participant added successfully", "participant": participant}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/rooms/{room_id}/participants/{user_id}")
async def remove_participant(
    room_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove participant from chat room"""
    service = CommunicationService(db)
    success = await service.remove_participant_from_room(room_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    return {"message": "Participant removed successfully"}


# ==================== Message Endpoints ====================

@router.post("/messages", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to a chat room"""
    service = CommunicationService(db)
    try:
        msg = await service.send_message(message, current_user.id)
        
        # Broadcast to room via WebSocket
        await chat_manager.broadcast_to_room_json(
            message.room_id,
            message_formatter.format_chat_message(
                message_id=msg.id,
                room_id=message.room_id,
                sender_id=current_user.id,
                content=message.content,
                sender_name=current_user.email
            )
        )
        
        return msg
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rooms/{room_id}/messages", response_model=MessageListResponse)
async def get_room_messages(
    room_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages from a chat room"""
    service = CommunicationService(db)
    messages = await service.get_room_messages(room_id, skip, limit)
    return {"messages": messages, "total": len(messages), "page": skip // limit + 1, "page_size": limit}


@router.post("/rooms/{room_id}/read")
async def mark_messages_as_read(
    room_id: int,
    last_read_message_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all messages in room as read"""
    service = CommunicationService(db)
    success = await service.mark_messages_as_read(room_id, current_user.id, last_read_message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return {"message": "Messages marked as read"}


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a message"""
    service = CommunicationService(db)
    success = await service.delete_message(message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}


# ==================== WebSocket Endpoint ====================

@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: int,
    token: str
):
    """
    WebSocket endpoint for real-time chat
    """
    # Authenticate user from token
    try:
        user = await get_current_user_from_websocket(websocket, token)
        user_id = user.id
    except Exception as e:
        await websocket.close(code=4001)
        return
    
    # Connect to chat manager
    await chat_manager.connect(websocket, user_id, room_id)
    
    try:
        # Join room
        await chat_manager.join_room(user_id, room_id, websocket)
        
        while True:
            data = await websocket.receive_text()
            
            # Parse incoming message
            try:
                import json
                message_data = json.loads(data)
                message_type = message_data.get("type", "chat")
                
                if message_type == "chat":
                    # Create and broadcast message
                    service = CommunicationService(websocket.state.db)
                    msg = await service.send_message(
                        MessageCreate(
                            room_id=room_id,
                            content=message_data.get("content"),
                            message_type=message_data.get("message_type", "text")
                        ),
                        user_id
                    )
                    
                    # Broadcast to room
                    await chat_manager.broadcast_to_room_json(
                        room_id,
                        message_formatter.format_chat_message(
                            message_id=msg.id,
                            room_id=room_id,
                            sender_id=user_id,
                            content=msg.content,
                            sender_name=user.email
                        )
                    )
                
                elif message_type == "typing":
                    # Broadcast typing indicator
                    await chat_manager.broadcast_to_room_json(
                        room_id,
                        message_formatter.format_typing_indicator(
                            user_id=user_id,
                            room_id=room_id,
                            is_typing=message_data.get("is_typing", True)
                        ),
                        exclude_user_id=user_id
                    )
                    
            except Exception as e:
                await chat_manager.send_personal_json(
                    message_formatter.format_error_message(str(e)),
                    websocket
                )
                
    except WebSocketDisconnect:
        pass
    finally:
        await chat_manager.leave_room(user_id, room_id, websocket)
        chat_manager.disconnect(websocket, user_id)


# ==================== Announcement Endpoints ====================

@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new announcement"""
    service = CommunicationService(db)
    return await service.create_announcement(announcement, current_user.id)


@router.get("/announcements", response_model=AnnouncementListResponse)
async def get_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    target_audience: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get announcements"""
    service = CommunicationService(db)
    from app.schema.communication_schema import AnnouncementTargetEnum
    target = AnnouncementTargetEnum(target_audience) if target_audience else None
    announcements = await service.get_announcements(skip, limit, target, category)
    return {"announcements": announcements, "total": len(announcements), "page": skip // limit + 1, "page_size": limit}


@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get announcement by ID"""
    service = CommunicationService(db)
    announcement = await service.get_announcement(announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: int,
    announcement_update: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update announcement"""
    service = CommunicationService(db)
    announcement = await service.update_announcement(announcement_id, announcement_update)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an announcement"""
    service = CommunicationService(db)
    success = await service.delete_announcement(announcement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted successfully"}


@router.post("/announcements/{announcement_id}/read")
async def mark_announcement_as_read(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark announcement as read"""
    service = CommunicationService(db)
    read = await service.mark_announcement_as_read(announcement_id, current_user.id)
    return {"message": "Announcement marked as read", "read_at": read.read_at}


@router.get("/announcements/unread/count")
async def get_unread_announcement_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread announcements"""
    service = CommunicationService(db)
    count = await service.get_unread_announcement_count(current_user.id)
    return {"unread_count": count}


# ==================== Meeting Endpoints ====================

@router.post("/meetings", response_model=MeetingResponse)
async def create_meeting(
    meeting: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new meeting"""
    service = CommunicationService(db)
    return await service.create_meeting(meeting, current_user.id)


@router.get("/meetings", response_model=MeetingListResponse)
async def get_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    upcoming_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meetings for current user"""
    service = CommunicationService(db)
    meetings = await service.get_user_meetings(current_user.id, skip, limit, upcoming_only)
    return {"meetings": meetings, "total": len(meetings), "page": skip // limit + 1, "page_size": limit}


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meeting by ID"""
    service = CommunicationService(db)
    meeting = await service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.put("/meetings/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update meeting"""
    service = CommunicationService(db)
    meeting = await service.update_meeting(meeting_id, meeting_update)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("/meetings/{meeting_id}/respond")
async def update_meeting_response(
    meeting_id: int,
    response: MeetingResponseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's meeting response"""
    service = CommunicationService(db)
    participant = await service.update_meeting_response(meeting_id, current_user.id, response)
    if not participant:
        raise HTTPException(status_code=404, detail="Meeting participant not found")
    return {"message": "Response updated", "participant": participant}


@router.post("/meetings/{meeting_id}/cancel")
async def cancel_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a meeting"""
    service = CommunicationService(db)
    meeting = await service.cancel_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"message": "Meeting cancelled", "meeting": meeting}


# ==================== Summary Endpoint ====================

@router.get("/summary", response_model=CommunicationSummaryResponse)
async def get_communication_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get communication summary for current user"""
    service = CommunicationService(db)
    return await service.get_communication_summary(current_user.id)
