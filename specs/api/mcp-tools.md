# MCP Tools API Specification

## Document Information
- **Project**: AI-Powered Todo Chatbot (Phase III)
- **Version**: 1.0.0
- **Date**: January 3, 2026
- **Purpose**: MCP Tools API Reference
- **Protocol**: Model Context Protocol (MCP)

---

## Overview

This document specifies the 5 MCP tools that enable the AI agent to manage todo tasks. Each tool is a stateless function that performs database operations and returns structured results.

**Key Principles**:
- **Stateless**: No shared state between tool invocations
- **Database-backed**: All state persisted to Neon PostgreSQL
- **User-scoped**: All operations filtered by `user_id`
- **Atomic**: Each tool performs a single, well-defined operation
- **Consistent**: All tools follow the same error handling pattern

---

## Tool 1: add_task

### Purpose
Create a new task in the database.

### Parameters

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | ✅ Yes | Non-empty, max 50 chars | User identifier for task ownership |
| `title` | string | ✅ Yes | Non-empty, max 200 chars | Task title/summary |
| `description` | string | ❌ No | Max 1000 chars | Detailed task description (default: "") |

### Returns

**Success Response**:
```json
{
  "task_id": integer,
  "status": "created",
  "title": string
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | Unique identifier for the created task |
| `status` | string | Always "created" for successful operations |
| `title` | string | The task title that was created |

### Example Input/Output

**Example 1: Task with description**
```json
// Input
{
  "user_id": "ziakhan",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

// Output
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

**Example 2: Task without description**
```json
// Input
{
  "user_id": "ziakhan",
  "title": "Call mom"
}

// Output
{
  "task_id": 6,
  "status": "created",
  "title": "Call mom"
}
```

### Error Behavior

#### Error 1: Missing Title
**Condition**: `title` is empty or not provided

**Response**:
```json
{
  "error": "MISSING_TITLE",
  "message": "Task title is required"
}
```

#### Error 2: Title Too Long
**Condition**: `title` exceeds 200 characters

**Response**:
```json
{
  "error": "TITLE_TOO_LONG",
  "message": "Title must be 200 characters or less"
}
```

#### Error 3: Description Too Long
**Condition**: `description` exceeds 1000 characters

**Response**:
```json
{
  "error": "DESCRIPTION_TOO_LONG",
  "message": "Description must be 1000 characters or less"
}
```

#### Error 4: Database Error
**Condition**: Database connection failure or write error

**Response**:
```json
{
  "error": "DATABASE_ERROR",
  "message": "Unable to create task. Please try again."
}
```

### Implementation Notes
- Task `completed` field defaults to `false`
- Timestamps `created_at` and `updated_at` auto-populate with current UTC time
- Task is immediately persisted to database (no caching)
- User isolation enforced: task associated with provided `user_id`

---

## Tool 2: list_tasks

### Purpose
Retrieve tasks from the database with optional status filtering.

### Parameters

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | ✅ Yes | Non-empty, max 50 chars | User identifier |
| `status` | string | ❌ No | "all", "pending", or "completed" | Filter tasks by completion status |

### Returns

**Success Response**:
```json
[
  {
    "id": integer,
    "title": string,
    "completed": boolean
  },
  ...
]
```

Returns an **array** of task objects (not wrapped in an object).

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Task identifier |
| `title` | string | Task title |
| `completed` | boolean | Completion status (true/false) |

### Filtering Logic

| Status Value | Returns |
|--------------|---------|
| `"all"` or `null` | All tasks for the user |
| `"pending"` | Tasks where `completed = false` |
| `"completed"` | Tasks where `completed = true` |

### Example Input/Output

**Example 1: List all tasks**
```json
// Input
{
  "user_id": "ziakhan",
  "status": "all"
}

// Output
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false
  },
  {
    "id": 2,
    "title": "Call mom",
    "completed": true
  },
  {
    "id": 3,
    "title": "Finish project report",
    "completed": false
  }
]
```

**Example 2: List pending tasks**
```json
// Input
{
  "user_id": "ziakhan",
  "status": "pending"
}

// Output
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false
  },
  {
    "id": 3,
    "title": "Finish project report",
    "completed": false
  }
]
```

**Example 3: List completed tasks**
```json
// Input
{
  "user_id": "ziakhan",
  "status": "completed"
}

// Output
[
  {
    "id": 2,
    "title": "Call mom",
    "completed": true
  }
]
```

**Example 4: Empty task list**
```json
// Input
{
  "user_id": "newuser",
  "status": "all"
}

// Output
[]
```

### Error Behavior

#### Error 1: Invalid Status
**Condition**: `status` is not "all", "pending", "completed", or null

**Response**:
```json
{
  "error": "INVALID_STATUS",
  "message": "Status must be 'all', 'pending', or 'completed'"
}
```

#### Error 2: Database Error
**Condition**: Database connection failure or query error

**Response**:
```json
{
  "error": "DATABASE_ERROR",
  "message": "Unable to retrieve tasks. Please try again."
}
```

### Implementation Notes
- Only returns tasks belonging to `user_id` (user isolation enforced)
- Tasks ordered by `created_at DESC` (newest first)
- Empty array returned when no tasks match (not an error)
- Query optimized with indexes on `user_id` and `completed`

---

## Tool 3: complete_task

### Purpose
Mark a task as completed by setting `completed` field to `true`.

### Parameters

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | ✅ Yes | Non-empty, max 50 chars | User identifier |
| `task_id` | integer | ✅ Yes | Positive integer | Task identifier to complete |

### Returns

**Success Response**:
```json
{
  "task_id": integer,
  "status": "completed",
  "title": string
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | The task identifier that was completed |
| `status` | string | Always "completed" for successful operations |
| `title` | string | The title of the completed task |

### Example Input/Output

**Example 1: Complete a pending task**
```json
// Input
{
  "user_id": "ziakhan",
  "task_id": 3
}

// Output
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

**Example 2: Complete an already completed task (idempotent)**
```json
// Input
{
  "user_id": "ziakhan",
  "task_id": 3
}

// Output
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

### Error Behavior

#### Error 1: Task Not Found
**Condition**: No task with `task_id` exists for `user_id`

**Response**:
```json
{
  "error": "TASK_NOT_FOUND",
  "message": "Task not found"
}
```

**Security Note**: Same error returned whether task doesn't exist OR belongs to different user (prevents information disclosure).

#### Error 2: Invalid Task ID
**Condition**: `task_id` is not a positive integer

**Response**:
```json
{
  "error": "INVALID_TASK_ID",
  "message": "Task ID must be a positive integer"
}
```

#### Error 3: Database Error
**Condition**: Database connection failure or update error

**Response**:
```json
{
  "error": "DATABASE_ERROR",
  "message": "Unable to complete task. Please try again."
}
```

### Implementation Notes
- Sets `completed = true` in database
- Updates `updated_at` timestamp to current UTC time
- **Idempotent**: Completing already-completed task succeeds (not an error)
- User isolation enforced: Query filters by both `task_id` AND `user_id`
- Returns task title for confirmation message

---

## Tool 4: delete_task

### Purpose
Permanently delete a task from the database.

### Parameters

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | ✅ Yes | Non-empty, max 50 chars | User identifier |
| `task_id` | integer | ✅ Yes | Positive integer | Task identifier to delete |

### Returns

**Success Response**:
```json
{
  "task_id": integer,
  "status": "deleted",
  "title": string
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | The task identifier that was deleted |
| `status` | string | Always "deleted" for successful operations |
| `title` | string | The title of the deleted task (for confirmation) |

### Example Input/Output

**Example 1: Delete a task**
```json
// Input
{
  "user_id": "ziakhan",
  "task_id": 2
}

// Output
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

### Error Behavior

#### Error 1: Task Not Found
**Condition**: No task with `task_id` exists for `user_id`

**Response**:
```json
{
  "error": "TASK_NOT_FOUND",
  "message": "Task not found"
}
```

**Security Note**: Same error returned whether task doesn't exist OR belongs to different user.

#### Error 2: Invalid Task ID
**Condition**: `task_id` is not a positive integer

**Response**:
```json
{
  "error": "INVALID_TASK_ID",
  "message": "Task ID must be a positive integer"
}
```

#### Error 3: Database Error
**Condition**: Database connection failure or delete error

**Response**:
```json
{
  "error": "DATABASE_ERROR",
  "message": "Unable to delete task. Please try again."
}
```

### Implementation Notes
- **Hard delete**: Task permanently removed from database (not soft delete)
- Task title captured before deletion for response
- User isolation enforced: Query filters by both `task_id` AND `user_id`
- **Not idempotent**: Deleting non-existent task returns error
- Operation is atomic and immediate

---

## Tool 5: update_task

### Purpose
Modify task title and/or description.

### Parameters

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | ✅ Yes | Non-empty, max 50 chars | User identifier |
| `task_id` | integer | ✅ Yes | Positive integer | Task identifier to update |
| `title` | string | ❌ No | Non-empty if provided, max 200 chars | New task title |
| `description` | string | ❌ No | Max 1000 chars | New task description |

**Note**: At least one of `title` or `description` must be provided.

### Returns

**Success Response**:
```json
{
  "task_id": integer,
  "status": "updated",
  "title": string
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | The task identifier that was updated |
| `status` | string | Always "updated" for successful operations |
| `title` | string | The updated task title (or original if not changed) |

### Example Input/Output

**Example 1: Update title only**
```json
// Input
{
  "user_id": "ziakhan",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}

// Output
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

**Example 2: Update description only**
```json
// Input
{
  "user_id": "ziakhan",
  "task_id": 1,
  "description": "Milk, eggs, bread, apples, oranges"
}

// Output
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

**Example 3: Update both title and description**
```json
// Input
{
  "user_id": "ziakhan",
  "task_id": 1,
  "title": "Weekly grocery shopping",
  "description": "Milk, eggs, bread, fruits, vegetables"
}

// Output
{
  "task_id": 1,
  "status": "updated",
  "title": "Weekly grocery shopping"
}
```

### Error Behavior

#### Error 1: Task Not Found
**Condition**: No task with `task_id` exists for `user_id`

**Response**:
```json
{
  "error": "TASK_NOT_FOUND",
  "message": "Task not found"
}
```

#### Error 2: No Updates Provided
**Condition**: Neither `title` nor `description` provided

**Response**:
```json
{
  "error": "NO_UPDATES",
  "message": "No fields to update. Provide title or description."
}
```

#### Error 3: Invalid Task ID
**Condition**: `task_id` is not a positive integer

**Response**:
```json
{
  "error": "INVALID_TASK_ID",
  "message": "Task ID must be a positive integer"
}
```

#### Error 4: Title Too Long
**Condition**: `title` exceeds 200 characters

**Response**:
```json
{
  "error": "TITLE_TOO_LONG",
  "message": "Title must be 200 characters or less"
}
```

#### Error 5: Description Too Long
**Condition**: `description` exceeds 1000 characters

**Response**:
```json
{
  "error": "DESCRIPTION_TOO_LONG",
  "message": "Description must be 1000 characters or less"
}
```

#### Error 6: Empty Title
**Condition**: `title` provided but is empty string

**Response**:
```json
{
  "error": "INVALID_TITLE",
  "message": "Title cannot be empty"
}
```

#### Error 7: Database Error
**Condition**: Database connection failure or update error

**Response**:
```json
{
  "error": "DATABASE_ERROR",
  "message": "Unable to update task. Please try again."
}
```

### Implementation Notes
- **Partial updates**: Only provided fields are updated
- Unchanged fields remain as-is in database
- Updates `updated_at` timestamp to current UTC time
- User isolation enforced: Query filters by both `task_id` AND `user_id`
- Returns current title in response (updated or original)
- Validates all provided fields before update

---

## Cross-Tool Specifications

### User Isolation

**All tools MUST**:
- Filter database queries by `user_id`
- Prevent cross-user data access
- Return identical errors for "not found" vs "belongs to other user"

**Example**: User A attempts to complete User B's task
```python
# User A trying to complete task belonging to User B
complete_task(user_id="userA", task_id=999)

# Response (same as if task doesn't exist)
{
  "error": "TASK_NOT_FOUND",
  "message": "Task not found"
}
```

### Error Response Format

All tools follow consistent error format:

```json
{
  "error": "ERROR_CODE",
  "message": "User-friendly error message"
}
```

**Standard Error Codes**:
- `TASK_NOT_FOUND`: Task doesn't exist or doesn't belong to user
- `INVALID_TASK_ID`: Task ID format invalid
- `MISSING_TITLE`: Required title not provided
- `TITLE_TOO_LONG`: Title exceeds max length
- `DESCRIPTION_TOO_LONG`: Description exceeds max length
- `INVALID_TITLE`: Title is empty when provided
- `INVALID_STATUS`: Status value not recognized
- `NO_UPDATES`: No fields provided for update
- `DATABASE_ERROR`: Database operation failed

### Stateless Operation

**All tools**:
- Have NO shared state between invocations
- Read/write exclusively through database
- Return consistent results for same inputs
- Complete in single atomic operation

### Performance Expectations

| Tool | Expected Latency | Database Operations |
|------|------------------|---------------------|
| `add_task` | < 100ms | 1 INSERT |
| `list_tasks` | < 150ms | 1 SELECT (with index) |
| `complete_task` | < 100ms | 1 SELECT + 1 UPDATE |
| `delete_task` | < 100ms | 1 SELECT + 1 DELETE |
| `update_task` | < 100ms | 1 SELECT + 1 UPDATE |

### Transaction Handling

All tools use atomic transactions:
```python
# Conceptual transaction pattern
async with db.begin():
    # 1. Validate
    # 2. Execute operation
    # 3. Commit
# If any step fails, transaction rolls back
```

---

## Integration with OpenAI Agent

### Tool Registration

Tools are registered with OpenAI Agent using MCP protocol:

```python
# Tool registration (conceptual)
mcp_server.register_tool(
    name="add_task",
    description="Create a new task",
    parameters={
        "user_id": {"type": "string", "required": True},
        "title": {"type": "string", "required": True},
        "description": {"type": "string", "required": False}
    },
    handler=add_task
)
```

### Agent Tool Selection

Agent selects tools based on user intent:

| User Intent | Tool Called |
|-------------|-------------|
| Create task | `add_task` |
| View tasks | `list_tasks` |
| Complete task | `complete_task` |
| Remove task | `delete_task` |
| Modify task | `update_task` |

### Agent Response Generation

Agent uses tool results to generate natural language responses:

**Example Flow**:
```
User: "Add buy groceries to my list"
  ↓
Agent Intent: CREATE_TASK
  ↓
Tool Call: add_task(user_id="ziakhan", title="Buy groceries")
  ↓
Tool Result: {"task_id": 5, "status": "created", "title": "Buy groceries"}
  ↓
Agent Response: "I've added 'Buy groceries' to your task list."
```

---

## Testing Requirements

### Unit Tests (per tool)

Each tool must have tests for:
1. ✅ Successful operation with valid inputs
2. ✅ All error conditions
3. ✅ User isolation (cross-user access blocked)
4. ✅ Input validation (boundaries, edge cases)
5. ✅ Database transaction rollback on error

### Integration Tests

1. ✅ Agent invokes tool correctly
2. ✅ Tool results returned to agent
3. ✅ Multi-tool chaining (e.g., list_tasks → delete_task)
4. ✅ Concurrent tool invocations

### Performance Tests

1. ✅ Latency under load
2. ✅ Database connection pool behavior
3. ✅ 100 concurrent tool invocations

---

## Security Considerations

### Input Sanitization
- All string inputs trimmed of leading/trailing whitespace
- SQL injection prevented (using parameterized queries via SQLModel)
- No user input executed as code

### Data Isolation
- `user_id` filter on ALL database queries
- No shared data between users
- Task IDs not sequential/guessable across users

### Error Messages
- Don't reveal existence of other users' tasks
- Don't expose internal system details
- Generic messages for security errors

### Logging
- Log all tool invocations with user_id
- Log errors with context for debugging
- Don't log sensitive user data in plain text

---

## Changelog

### Version 1.0.0 (2026-01-03)
- Initial specification
- 5 core MCP tools defined
- Complete API reference with examples
- Error handling specification
- Security and testing requirements

---

## Appendix: Complete Examples

### Scenario 1: Creating and Completing a Task

```json
// 1. Create task
add_task({
  "user_id": "ziakhan",
  "title": "Submit tax documents"
})
→ {
  "task_id": 10,
  "status": "created",
  "title": "Submit tax documents"
}

// 2. List tasks to verify
list_tasks({
  "user_id": "ziakhan",
  "status": "pending"
})
→ [
  {
    "id": 10,
    "title": "Submit tax documents",
    "completed": false
  }
]

// 3. Complete the task
complete_task({
  "user_id": "ziakhan",
  "task_id": 10
})
→ {
  "task_id": 10,
  "status": "completed",
  "title": "Submit tax documents"
}

// 4. Verify completion
list_tasks({
  "user_id": "ziakhan",
  "status": "completed"
})
→ [
  {
    "id": 10,
    "title": "Submit tax documents",
    "completed": true
  }
]
```

### Scenario 2: Updating and Deleting a Task

```json
// 1. Create task with description
add_task({
  "user_id": "ziakhan",
  "title": "Buy milk",
  "description": "2% milk from organic section"
})
→ {
  "task_id": 11,
  "status": "created",
  "title": "Buy milk"
}

// 2. Update title to be more specific
update_task({
  "user_id": "ziakhan",
  "task_id": 11,
  "title": "Buy organic 2% milk"
})
→ {
  "task_id": 11,
  "status": "updated",
  "title": "Buy organic 2% milk"
}

// 3. Update description
update_task({
  "user_id": "ziakhan",
  "task_id": 11,
  "description": "2% milk from organic section, 1 gallon"
})
→ {
  "task_id": 11,
  "status": "updated",
  "title": "Buy organic 2% milk"
}

// 4. Delete the task
delete_task({
  "user_id": "ziakhan",
  "task_id": 11
})
→ {
  "task_id": 11,
  "status": "deleted",
  "title": "Buy organic 2% milk"
}
```

### Scenario 3: Error Handling

```json
// 1. Attempt to complete non-existent task
complete_task({
  "user_id": "ziakhan",
  "task_id": 9999
})
→ {
  "error": "TASK_NOT_FOUND",
  "message": "Task not found"
}

// 2. Attempt to create task without title
add_task({
  "user_id": "ziakhan"
})
→ {
  "error": "MISSING_TITLE",
  "message": "Task title is required"
}

// 3. Attempt to update with no fields
update_task({
  "user_id": "ziakhan",
  "task_id": 1
})
→ {
  "error": "NO_UPDATES",
  "message": "No fields to update. Provide title or description."
}

// 4. Invalid status filter
list_tasks({
  "user_id": "ziakhan",
  "status": "invalid"
})
→ {
  "error": "INVALID_STATUS",
  "message": "Status must be 'all', 'pending', or 'completed'"
}
```

---

**Document Status**: ✅ APPROVED  
**Last Updated**: January 3, 2026  
**Maintained By**: Phase III Development Team
