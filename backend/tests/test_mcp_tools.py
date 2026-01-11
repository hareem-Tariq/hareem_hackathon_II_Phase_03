"""Tests for MCP tools."""
import pytest
from app.mcp.tools import add_task, list_tasks, update_task, complete_task, delete_task


@pytest.mark.asyncio
async def test_add_task():
    """Test adding a task."""
    result = await add_task(
        user_id="test_user",
        title="Test Task",
        description="Test Description"
    )
    
    assert result["status"] == "created"
    assert result["title"] == "Test Task"
    assert "task_id" in result


@pytest.mark.asyncio
async def test_list_tasks():
    """Test listing tasks."""
    # Add some tasks first
    await add_task(user_id="test_user", title="Task 1")
    await add_task(user_id="test_user", title="Task 2")
    
    # List all tasks
    tasks = await list_tasks(user_id="test_user", status="all")
    assert len(tasks) >= 2


@pytest.mark.asyncio
async def test_complete_task():
    """Test completing a task."""
    # Add a task
    add_result = await add_task(user_id="test_user", title="Task to Complete")
    task_id = add_result["task_id"]
    
    # Complete the task
    result = await complete_task(user_id="test_user", task_id=task_id, completed=True)
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_delete_task():
    """Test deleting a task."""
    # Add a task
    add_result = await add_task(user_id="test_user", title="Task to Delete")
    task_id = add_result["task_id"]
    
    # Delete the task
    result = await delete_task(user_id="test_user", task_id=task_id)
    assert result["status"] == "deleted"
