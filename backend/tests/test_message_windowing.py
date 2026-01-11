"""
Test Message Windowing - Verify 50-message context window enforcement.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.models.conversation import Conversation
from app.models.message import Message
from app.agent.service import load_message_history, MAX_CONTEXT_MESSAGES


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_message_windowing_with_less_than_50_messages(session):
    """Test that all messages are returned when less than 50."""
    # Create conversation
    conv = Conversation(
        user_id="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    
    # Add 30 messages
    for i in range(30):
        msg = Message(
            conversation_id=conv.id,
            user_id="test_user",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            created_at=datetime.utcnow() + timedelta(seconds=i)
        )
        session.add(msg)
    session.commit()
    
    # Load messages
    messages = load_message_history(session, conv.id, "test_user")
    
    # Should return all 30 messages
    assert len(messages) == 30
    
    # Should be in chronological order
    assert messages[0].content == "Message 0"
    assert messages[-1].content == "Message 29"


def test_message_windowing_with_exactly_50_messages(session):
    """Test that exactly 50 messages are returned when exactly 50 exist."""
    # Create conversation
    conv = Conversation(
        user_id="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    
    # Add exactly 50 messages
    for i in range(50):
        msg = Message(
            conversation_id=conv.id,
            user_id="test_user",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            created_at=datetime.utcnow() + timedelta(seconds=i)
        )
        session.add(msg)
    session.commit()
    
    # Load messages
    messages = load_message_history(session, conv.id, "test_user")
    
    # Should return all 50 messages
    assert len(messages) == 50
    assert messages[0].content == "Message 0"
    assert messages[-1].content == "Message 49"


def test_message_windowing_with_more_than_50_messages(session):
    """Test that only last 50 messages are returned when more than 50 exist."""
    # Create conversation
    conv = Conversation(
        user_id="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    
    # Add 100 messages
    for i in range(100):
        msg = Message(
            conversation_id=conv.id,
            user_id="test_user",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            created_at=datetime.utcnow() + timedelta(seconds=i)
        )
        session.add(msg)
    session.commit()
    
    # Load messages
    messages = load_message_history(session, conv.id, "test_user")
    
    # Should return only last 50 messages
    assert len(messages) == 50
    
    # Should start from message 50 (0-indexed, so messages 50-99)
    assert messages[0].content == "Message 50"
    assert messages[-1].content == "Message 99"
    
    # Verify messages 0-49 are NOT included
    message_contents = [msg.content for msg in messages]
    assert "Message 0" not in message_contents
    assert "Message 49" not in message_contents


def test_message_windowing_chronological_order(session):
    """Test that messages are returned in chronological order (oldest to newest)."""
    # Create conversation
    conv = Conversation(
        user_id="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    
    # Add 10 messages with explicit timestamps
    base_time = datetime.utcnow()
    for i in range(10):
        msg = Message(
            conversation_id=conv.id,
            user_id="test_user",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            created_at=base_time + timedelta(minutes=i)
        )
        session.add(msg)
    session.commit()
    
    # Load messages
    messages = load_message_history(session, conv.id, "test_user")
    
    # Verify chronological order
    for i in range(len(messages) - 1):
        assert messages[i].created_at <= messages[i + 1].created_at


def test_message_windowing_user_isolation(session):
    """Test that messages are filtered by user_id for security."""
    # Create conversation
    conv = Conversation(
        user_id="user_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    
    # Add messages for user_1
    for i in range(30):
        msg = Message(
            conversation_id=conv.id,
            user_id="user_1",
            role="user",
            content=f"User1 Message {i}",
            created_at=datetime.utcnow() + timedelta(seconds=i)
        )
        session.add(msg)
    
    # Add messages for user_2 (should not appear)
    for i in range(20):
        msg = Message(
            conversation_id=conv.id,
            user_id="user_2",
            role="user",
            content=f"User2 Message {i}",
            created_at=datetime.utcnow() + timedelta(seconds=30 + i)
        )
        session.add(msg)
    session.commit()
    
    # Load messages for user_1
    messages = load_message_history(session, conv.id, "user_1")
    
    # Should only return user_1's messages
    assert len(messages) == 30
    for msg in messages:
        assert msg.user_id == "user_1"
        assert "User1" in msg.content


def test_max_context_messages_constant():
    """Test that MAX_CONTEXT_MESSAGES constant is set to 50."""
    assert MAX_CONTEXT_MESSAGES == 50


def test_message_windowing_custom_limit(session):
    """Test that custom limit parameter works."""
    # Create conversation
    conv = Conversation(
        user_id="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    
    # Add 100 messages
    for i in range(100):
        msg = Message(
            conversation_id=conv.id,
            user_id="test_user",
            role="user",
            content=f"Message {i}",
            created_at=datetime.utcnow() + timedelta(seconds=i)
        )
        session.add(msg)
    session.commit()
    
    # Load messages with custom limit of 20
    messages = load_message_history(session, conv.id, "test_user", limit=20)
    
    # Should return only last 20 messages
    assert len(messages) == 20
    assert messages[0].content == "Message 80"
    assert messages[-1].content == "Message 99"
