"""Chat and messaging routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List
from datetime import datetime

from app.db import get_db
from app.models import User, Conversation, Message, Patient
from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageCreate,
    MessageResponse,
    MarkAsRead
)
from app.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation."""
    
    # Determine conversation type
    conv_type = "user_to_user"
    user2_id = conversation_data.receiver_id
    patient_id = conversation_data.patient_id
    
    if patient_id:
        conv_type = "user_to_patient"
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
    
    if user2_id:
        # Verify user exists
        user2 = db.query(User).filter(User.id == user2_id).first()
        if not user2:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Check if conversation already exists
    existing_conv = db.query(Conversation).filter(
        or_(
            and_(
                Conversation.user1_id == current_user.id,
                Conversation.user2_id == user2_id,
                Conversation.patient_id == patient_id
            ),
            and_(
                Conversation.user1_id == user2_id,
                Conversation.user2_id == current_user.id,
                Conversation.patient_id == patient_id
            )
        )
    ).first()
    
    if existing_conv:
        # Return existing conversation
        return _format_conversation_response(existing_conv, current_user.id, db)
    
    # Create new conversation
    new_conversation = Conversation(
        user1_id=current_user.id,
        user2_id=user2_id,
        patient_id=patient_id,
        case_id=conversation_data.case_id,
        appointment_id=conversation_data.appointment_id,
        conversation_type=conv_type,
        title=conversation_data.title,
        status="active"
    )
    
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    # Create initial message
    initial_message = Message(
        conversation_id=new_conversation.id,
        sender_id=current_user.id,
        content=conversation_data.initial_message,
        message_type="text"
    )
    
    db.add(initial_message)
    db.commit()
    
    # Update conversation's last_message_at
    new_conversation.last_message_at = datetime.utcnow()
    db.commit()
    db.refresh(new_conversation)
    
    return _format_conversation_response(new_conversation, current_user.id, db)


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user."""
    
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        ),
        Conversation.status == "active"
    ).order_by(desc(Conversation.last_message_at)).all()
    
    return [_format_conversation_response(conv, current_user.id, db) for conv in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation_with_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a conversation with all messages."""
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify user is participant
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this conversation")
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    # Format response
    response_data = _format_conversation_response(conversation, current_user.id, db)
    message_list = [_format_message_response(msg, db) for msg in messages]
    
    return ConversationWithMessages(
        **response_data.model_dump(),
        messages=message_list
    )


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message in a conversation."""
    
    conversation_id = message_data.conversation_id
    
    # If no conversation_id, create new conversation
    if not conversation_id:
        if not message_data.receiver_id and not message_data.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Must provide either conversation_id or receiver_id/patient_id"
            )
        
        # Create new conversation
        conv_data = ConversationCreate(
            receiver_id=message_data.receiver_id,
            patient_id=message_data.patient_id,
            case_id=message_data.case_id,
            initial_message=message_data.content
        )
        
        conversation = create_conversation(conv_data, db, current_user)
        # Return the initial message already created
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(desc(Message.created_at)).first()
        return _format_message_response(messages, db)
    
    # Verify conversation exists and user is participant
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to send messages in this conversation")
    
    # Create message
    new_message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=message_data.content,
        message_type=message_data.message_type
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Update conversation's last_message_at
    conversation.last_message_at = datetime.utcnow()
    db.commit()
    
    return _format_message_response(new_message, db)


@router.post("/messages/read", status_code=status.HTTP_200_OK)
def mark_messages_as_read(
    mark_data: MarkAsRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark messages as read."""
    
    messages = db.query(Message).filter(Message.id.in_(mark_data.message_ids)).all()
    
    updated_count = 0
    for message in messages:
        # Verify user is receiver (not sender)
        conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
        if conversation and message.sender_id != current_user.id:
            if conversation.user1_id == current_user.id or conversation.user2_id == current_user.id:
                message.is_read = 1
                message.read_at = datetime.utcnow()
                updated_count += 1
    
    db.commit()
    
    return {"message": f"Marked {updated_count} messages as read"}


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
def archive_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a conversation (soft delete)."""
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify user is participant
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to archive this conversation")
    
    conversation.status = "archived"
    db.commit()
    
    return {"message": "Conversation archived"}


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total unread message count for current user."""
    
    # Get all conversations where user is participant
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        ),
        Conversation.status == "active"
    ).all()
    
    total_unread = 0
    for conv in conversations:
        # Count unread messages where user is not the sender
        unread = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.sender_id != current_user.id,
            Message.is_read == 0
        ).count()
        total_unread += unread
    
    return {"unread_count": total_unread}


# Helper functions
def _format_conversation_response(conversation: Conversation, current_user_id: int, db: Session) -> ConversationResponse:
    """Format a conversation for response."""
    
    # Determine other participant
    other_participant_name = "Unknown"
    other_participant_role = None
    other_participant_photo = None
    
    if conversation.patient_id:
        patient = db.query(Patient).filter(Patient.id == conversation.patient_id).first()
        if patient:
            other_participant_name = patient.full_name or "Patient"
            other_participant_role = "Patient"
    elif conversation.user2_id:
        other_user_id = conversation.user2_id if conversation.user1_id == current_user_id else conversation.user1_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if other_user:
            other_participant_name = other_user.full_name or other_user.username
            other_participant_role = other_user.role
            other_participant_photo = other_user.profile_photo
    
    # Get unread count
    unread_count = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.sender_id != current_user_id,
        Message.is_read == 0
    ).count()
    
    # Get last message
    last_msg = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(desc(Message.created_at)).first()
    
    last_message_text = None
    last_message_sender = None
    if last_msg:
        last_message_text = last_msg.content[:50] + "..." if len(last_msg.content) > 50 else last_msg.content
        sender = db.query(User).filter(User.id == last_msg.sender_id).first()
        last_message_sender = sender.full_name if sender else "Unknown"
    
    return ConversationResponse(
        id=conversation.id,
        user1_id=conversation.user1_id,
        user2_id=conversation.user2_id,
        patient_id=conversation.patient_id,
        case_id=conversation.case_id,
        appointment_id=conversation.appointment_id,
        conversation_type=conversation.conversation_type,
        status=conversation.status,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=conversation.last_message_at,
        other_participant_name=other_participant_name,
        other_participant_role=other_participant_role,
        other_participant_photo=other_participant_photo,
        unread_count=unread_count,
        last_message=last_message_text,
        last_message_sender=last_message_sender
    )


def _format_message_response(message: Message, db: Session) -> MessageResponse:
    """Format a message for response."""
    
    sender = db.query(User).filter(User.id == message.sender_id).first()
    sender_name = sender.full_name if sender else "Unknown"
    sender_role = sender.role if sender else None
    
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender_name=sender_name,
        sender_role=sender_role,
        content=message.content,
        message_type=message.message_type,
        attachment_url=message.attachment_url,
        is_read=bool(message.is_read),
        read_at=message.read_at,
        is_edited=bool(message.is_edited),
        edited_at=message.edited_at,
        created_at=message.created_at
    )

