import secrets
from config import settings
from .logger import logger
from database.models import Session, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy import func, text

MAX_MESSAGES_HISTORY = int(settings.MAX_INTERACTIONS_HISTORY)*2 
MAX_INACTIVE_TIME_MINS = int(settings.MAX_INACTIVE_TIME_MINS)

async def create_session(agreement_part_1: bool, agreement_part_2: bool, db: AsyncSession):

    if not (agreement_part_1 and agreement_part_2):
        logger.error(f"Session {session_id} has not agreed to both agreements. Not creating session.", event_type="aita")
        return False

    session_id = secrets.token_urlsafe()
    new_session = Session(
        SessionID=session_id,
        Active=1, 
        HasAgreedToPart1=agreement_part_1, 
        AgreementPart1Version=settings.AGREEMENT_PART_1_VERSION, 
        HasAgreedToPart2=agreement_part_2, 
        AgreementPart2Version=settings.AGREEMENT_PART_2_VERSION, 
    )

    try:
        # Add session to database
        db.add(new_session)
        await db.commit()
        logger.info(f"Session id {session_id} created successfully", event_type="aita")
        return session_id

    except Exception as e:
        logger.error(f"Error creating session {session_id} in database. Rolling back. Error: {str(e)}", event_type="aita")
        await db.rollback()
        # Handle unique constraint violations
        if "unique constraint" in str(e).lower():
            logger.error(f"Session with id {session_id} already exists", event_type="aita")
        return False

async def get_session(session: Session, db: AsyncSession):

    if "anon_session" not in session:
        logger.error("Session not in expected format", event_type="aita")
        return False
    
    session_id = session["anon_session"]

    try:
        query = select(Session).where(Session.SessionID == session_id)
        result = await db.execute(query)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            logger.error(f"Session {session_id} not found in database", event_type="aita")
            return False
            
        if not db_session.Active:
            logger.error(f"Session {session_id} has expired", event_type="aita")
            return False
        
        if not (db_session.HasAgreedToPart1 and db_session.HasAgreedToPart2):
            logger.error(f"Session {session_id} has not agreed to both agreements. Invalidating session.", event_type="aita")
            return False
        
        logger.info(f"Session {session_id} retrieved successfully", event_type="aita")
        return db_session
        
    except Exception as e:
        logger.error(f"Error retrieving session {session_id} in database: {str(e)}", event_type="aita")
        return False

async def expire_session(session: Session, db: AsyncSession):

    if "anon_session" not in session:
        logger.error("Session not in expected format", event_type="aita")
        return False
    
    session_id = session["anon_session"]

    try:
        # Find the session
        query = select(Session).where(Session.SessionID == session_id)
        result = await db.execute(query)
        db_session = result.scalar_one_or_none()
        
        if db_session:
            # Update the Active status to False
            db_session.Active = 0
            await db.commit()
            session.clear()
            logger.info(f"Session {session_id} was deactivated successfully", event_type="aita")
            return True
        else:
            logger.error(f"Session {session_id} not found in database. Could not expire.", event_type="aita")
            return False
            
    except Exception as e:
        logger.error(f"Error deactivating session {session_id}: {str(e)}", event_type="aita")
        await db.rollback()
        return False

async def save_message(session_id: str, is_bot: bool, message: str, db: AsyncSession):

    try:
        # Save message
        new_message = Message(SessionID=session_id, IsBot=is_bot, MessageText=message)
        db.add(new_message)
        await db.commit()
        logger.info(f"Message saved in session {session_id}, bot {is_bot}", event_type="aita") 
        return True
    except Exception as e:
        logger.error(f"Error saving message in session {session_id}, bot {is_bot}: {str(e)}", event_type="aita")
        await db.rollback()
        return False
    
async def format_message_history(session_id: str, db: AsyncSession):

    # Retrieve the most recent chunk of messages
    message_history = (await db.execute(
        select(Message)
        .filter(Message.SessionID == session_id)  
        .order_by(Message.DateCreated.desc())
        .limit(MAX_MESSAGES_HISTORY)
    )).scalars().all()

    # Reverse the list to chronological order
    message_history.reverse()  

    chat_history = []
    for i in range(len(message_history)-1):
        curr, next_msg = message_history[i], message_history[i+1]
        chat_history.append({
            "inputs": {"chat_input": curr.MessageText} if not curr.IsBot else {},
            "outputs": {"chat_output": next_msg.MessageText} if next_msg.IsBot else {}
        })

    return chat_history

# Session cleanup task
async def expire_sessions(db: AsyncSession):
    
    try:
        logger.info(f"Scheduled session cleanup", event_type="aita")  
    
        query = update(Session).where(
        Session.DateUpdated < func.DATEADD(
            text('MINUTE'), 
            -MAX_INACTIVE_TIME_MINS, 
            func.GETUTCDATE()
            )
        ).filter(Session.Active==True).values(
            Active=False,
            DateUpdated=func.GETUTCDATE()  
        )

        result = await db.execute(query)
        num_updated = result.rowcount
        await db.commit()

        logger.info(f"Session cleanup complete. Expired {num_updated} sessions", event_type="aita")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during session cleanup: {e}", event_type="aita")