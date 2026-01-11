# AI Agent Behavior Specification

## Document Information
- **Project**: AI-Powered Todo Chatbot (Phase III)
- **Version**: 1.0.0
- **Date**: January 3, 2026
- **Purpose**: Define AI agent conversation behavior and tool usage patterns

---

## Overview

The AI agent is a friendly task management assistant that understands natural language and uses MCP tools to help users manage their todo lists. The agent operates in a **stateless** manner, with all conversation history persisted to the database.

**Core Principles**:
- 🎯 **Intent-driven**: Understand user goals, not just keywords
- 🛠️ **Tool-first**: Use MCP tools for all task operations
- 💬 **Conversational**: Respond naturally with confirmations
- 🔄 **Resilient**: Gracefully handle errors and ambiguity
- 🚀 **Efficient**: Chain tools when needed to complete user requests

---

## Intent Detection Rules

### Intent Categories

| Intent | Trigger Patterns | Examples |
|--------|------------------|----------|
| **CREATE_TASK** | add, create, remember, remind me, need to, don't forget, make a note, task to | "Add buy groceries", "I need to call mom", "Don't forget to submit report" |
| **LIST_TASKS** | show, list, see, what, view, display, tell me | "Show all tasks", "What's on my list?", "See pending items" |
| **COMPLETE_TASK** | done, complete, finish, completed, mark as done, finished | "Mark task 3 as done", "I finished the report", "Complete buy groceries" |
| **DELETE_TASK** | delete, remove, cancel, clear, get rid of | "Delete task 2", "Remove buy groceries", "Cancel the meeting task" |
| **UPDATE_TASK** | change, update, edit, rename, modify, revise | "Change task 1 to call mom", "Update the title", "Rename buy milk" |
| **HELP** | help, how, what can you do, commands, usage | "What can you do?", "Help me", "How do I add a task?" |
| **GREETING** | hi, hello, hey, good morning, good afternoon | "Hello!", "Hey there", "Hi bot" |
| **UNCLEAR** | Ambiguous or incomplete requests | "task", "do it", "that thing" |

### Intent Detection Logic

```
┌─────────────────────────────────────────────────────────────┐
│ User Message                                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────┐
      │ Contains task creation words? │
      │ (add, create, remember, etc.)│
      └────────┬──────────────────────┘
               │ YES → CREATE_TASK
               │
               ▼ NO
      ┌──────────────────────────────┐
      │ Contains listing words?       │
      │ (show, list, what, see, etc.) │
      └────────┬──────────────────────┘
               │ YES → LIST_TASKS
               │
               ▼ NO
      ┌──────────────────────────────┐
      │ Contains completion words?    │
      │ (done, complete, finish, etc.)│
      └────────┬──────────────────────┘
               │ YES → COMPLETE_TASK
               │
               ▼ NO
      ┌──────────────────────────────┐
      │ Contains deletion words?      │
      │ (delete, remove, cancel, etc.)│
      └────────┬──────────────────────┘
               │ YES → DELETE_TASK
               │
               ▼ NO
      ┌──────────────────────────────┐
      │ Contains update words?        │
      │ (change, update, edit, etc.)  │
      └────────┬──────────────────────┘
               │ YES → UPDATE_TASK
               │
               ▼ NO
      ┌──────────────────────────────┐
      │ Contains help words?          │
      │ (help, how, what can, etc.)   │
      └────────┬──────────────────────┘
               │ YES → HELP
               │
               ▼ NO
      ┌──────────────────────────────┐
      │ Contains greeting?            │
      │ (hi, hello, hey, etc.)        │
      └────────┬──────────────────────┘
               │ YES → GREETING
               │
               ▼ NO
              UNCLEAR
```

### Contextual Intent Detection

**Rule 1: Task ID Presence**
- If message contains `task <number>` or `#<number>` → likely COMPLETE/DELETE/UPDATE
- If no task ID but action word → likely CREATE

**Rule 2: Status Keywords**
- "pending", "incomplete", "not done" → LIST_TASKS (status: pending)
- "completed", "done", "finished" → LIST_TASKS (status: completed)
- "all", "everything" → LIST_TASKS (status: all)

**Rule 3: Implicit Context**
- "I finished it" (after mentioning specific task) → COMPLETE_TASK
- "Delete that" (after listing tasks) → DELETE_TASK (use most recent task)
- "Actually, make it..." (after creating task) → UPDATE_TASK

**Rule 4: Multi-Intent Messages**
- "Add buy groceries and show me all tasks" → CREATE_TASK + LIST_TASKS (chain)
- "Delete task 3 and tell me what's left" → DELETE_TASK + LIST_TASKS (chain)

---

## Tool Selection Logic

### Tool Selection Decision Tree

```
Intent: CREATE_TASK
├─ Extract task title from message
├─ Extract description (if present)
└─ Tool: add_task(user_id, title, description)

Intent: LIST_TASKS
├─ Detect status filter
│  ├─ "pending"/"incomplete"/"not done" → status="pending"
│  ├─ "completed"/"done"/"finished" → status="completed"
│  └─ "all"/"everything"/no filter → status="all"
└─ Tool: list_tasks(user_id, status)

Intent: COMPLETE_TASK
├─ Extract task_id from message
│  ├─ Found task ID → use it
│  └─ No task ID → ask for clarification
└─ Tool: complete_task(user_id, task_id)

Intent: DELETE_TASK
├─ Extract task_id OR task title from message
│  ├─ Has task ID → use it
│  ├─ Has task title → list_tasks first, find ID
│  └─ Neither → ask for clarification
└─ Tool: delete_task(user_id, task_id)

Intent: UPDATE_TASK
├─ Extract task_id from message
├─ Extract new title OR description
│  ├─ Found both → update both
│  └─ Found one → update that field
└─ Tool: update_task(user_id, task_id, title?, description?)
```

### Parameter Extraction Rules

**Extract `task_id`**:
- Pattern: `task <number>`, `#<number>`, `id <number>`, `number <number>`
- Examples: "task 3" → 3, "#5" → 5, "id 12" → 12

**Extract `title`**:
- CREATE: Everything after trigger word → "Add buy groceries" → "buy groceries"
- UPDATE: Everything after "to" → "Change to call mom" → "call mom"
- DELETE by title: Everything after trigger → "Delete buy groceries" → "buy groceries"

**Extract `description`**:
- Pattern: Look for "with", ":", "—", "including"
- Example: "Add report with executive summary" → description="executive summary"

**Extract `status`**:
- "pending"/"incomplete"/"to do"/"not done" → "pending"
- "completed"/"done"/"finished" → "completed"  
- "all"/"everything"/"every" → "all"
- Default: "all"

---

## Deterministic Natural Language to Tool Mapping

### Rule 1: Natural Language Pattern Matching (Deterministic)

The agent uses **deterministic keyword-based pattern matching** to map natural language to tool invocations. No probabilistic inference is used.

**Mapping Table**:

| Natural Language Pattern | Tool Invocation | Parameters |
|-------------------------|-----------------|------------|
| "add \<title\>" / "create \<title\>" | `add_task()` | title=\<extracted\>, description=\<optional\> |
| "show \<filter?\>" / "list \<filter?\>" / "what" | `list_tasks()` | status=\<extracted or "all"\> |
| "done \<id/title\>" / "complete \<id/title\>" | `complete_task()` | task_id=\<resolved\> |
| "delete \<id/title\>" / "remove \<id/title\>" | `delete_task()` | task_id=\<resolved\> |
| "change \<id\>" / "update \<id\>" / "edit \<id\>" | `update_task()` | task_id=\<resolved\>, fields=\<extracted\> |

**Keyword Lists** (exhaustive):
- **CREATE**: add, create, remember, remind, need to, don't forget, make a note, task to
- **LIST**: show, list, see, what, view, display, tell me
- **COMPLETE**: done, complete, finish, completed, mark as done, finished
- **DELETE**: delete, remove, cancel, clear, get rid of
- **UPDATE**: change, update, edit, rename, modify, revise

**Matching Logic**:
1. Convert user message to lowercase
2. Check for keyword presence (in order: CREATE → LIST → COMPLETE → DELETE → UPDATE → HELP → GREETING)
3. First keyword match determines intent
4. Extract parameters using regex patterns
5. Map to tool with extracted parameters

### Rule 2: Ambiguous Task Handling

When multiple tasks match a user's query (e.g., delete/complete by partial title), the agent **MUST** ask for clarification.

**Detection**:
- User provides partial title or description
- Fuzzy match returns >1 result from `list_tasks()`

**Response Template**:
```
"I found multiple tasks matching '[QUERY]':
1. [TASK_TITLE_1] (ID: [ID])
2. [TASK_TITLE_2] (ID: [ID])
...
Which task would you like to [ACTION]? Please specify by number."
```

**Resolution**:
- Wait for user to provide task ID or position ("the first one", "task 1", "number 2")
- Use provided ID to execute original tool
- If user provides another ambiguous response, repeat clarification

**Example**:
```
User: "Delete the report"
[Matches: "Finish Q4 Report" (ID: 3), "Review Report Draft" (ID: 7)]
Agent: "I found multiple tasks matching 'report':
1. Finish Q4 Report (ID: 3)
2. Review Report Draft (ID: 7)
Which task would you like to delete? Please specify by number."
User: "The first one"
Agent: [Executes delete_task(task_id=3)]
```

### Rule 3: Pronoun and Contextual Reference Handling

The agent resolves pronouns by tracking the **last mentioned task_id** in the conversation history.

**Pronouns**: "it", "that", "that task", "that one", "the task"

**Resolution Logic**:
1. Search conversation history (within context window) for last task_id mention
2. Last task_id can come from:
   - User explicitly stating task ID ("task 3")
   - Agent response mentioning task ID ("I've added task 5")
   - Agent listing tasks (most recent task in list)
3. If found, use that task_id
4. If not found, ask for clarification

**Tracking Rules**:
- After `add_task()`: Track newly created task_id
- After `list_tasks()`: Track first task in returned list
- After `complete_task()`/`delete_task()`/`update_task()`: Track the task_id used
- User mentions task ID: Track that ID

**Example**:
```
User: "Add buy groceries"
Agent: "I've added 'Buy groceries' to your list." [tracks task_id=5]
User: "Actually, mark it as done"
Agent: [Resolves "it" → task_id=5] "Great job! I've marked 'Buy groceries' as complete."
```

**Ambiguity**:
```
User: "Delete it"
[No task_id in context window]
Agent: "Which task would you like to delete? You can say the task number or title."
```

### Rule 4: Context Window Limitations

The agent only considers the **last 50 messages** (25 user + 25 assistant) for contextual understanding.

**Context Window Rules**:
- **Size**: Last 50 messages (25 pairs)
- **Usage**: Pronoun resolution, implicit references, conversation continuity
- **Exclusion**: Messages beyond 50 are not loaded from database
- **Reset**: Context resets if conversation_id changes or is absent

**Behavior Beyond Window**:
- Task references older than 50 messages are not resolvable via pronouns
- User must provide explicit task ID or title
- Agent does not "remember" tasks mentioned 50+ messages ago

**Example**:
```
[Message 1] User: "Add task A" → task_id=1
[Messages 2-51] ... other conversation ...
[Message 52] User: "Delete it"
Agent: [Cannot resolve "it" because task_id=1 is beyond context window]
"Which task would you like to delete? You can say the task number or title."
```

### Rule 5: Tool Invocation Priority (Task Resolution)

When a user references a task (for complete/delete/update), resolve task_id using this **strict priority order**:

**Priority Order**:
1. **Explicit ID** (highest priority)
   - Pattern: `task <number>`, `#<number>`, `id <number>`
   - Example: "delete task 5" → task_id=5
   - **Action**: Use ID directly

2. **Exact Title Match**
   - User provides exact task title (case-insensitive)
   - Example: "delete buy groceries" where task exists with title "Buy Groceries"
   - **Action**: Call `list_tasks()`, find exact match, use task_id

3. **Fuzzy Match** (lowest priority)
   - User provides partial/similar title
   - Example: "delete groceries" matches "Buy groceries from store"
   - **Action**: Call `list_tasks()`, perform substring/fuzzy match
   - **If 1 match**: Use task_id
   - **If >1 match**: Ask for clarification (Rule 2)
   - **If 0 matches**: Inform user task not found

**Fuzzy Matching Algorithm**:
- Convert both strings to lowercase
- Check if user query is substring of task title
- Calculate similarity score (optional: Levenshtein distance)
- Threshold: Accept matches with >60% similarity

**Example Decision Tree**:
```
User: "Delete buy groceries"

Check Priority 1: Contains task ID?
→ No

Check Priority 2: Exact title match?
→ Call list_tasks()
→ Check for exact match "buy groceries" (case-insensitive)
→ Found: task_id=3 with title "Buy Groceries"
→ Use task_id=3

User: "Delete groceries"

Check Priority 1: Contains task ID?
→ No

Check Priority 2: Exact title match?
→ Call list_tasks()
→ No exact match for "groceries"

Check Priority 3: Fuzzy match?
→ Found 2 matches:
   - task_id=3: "Buy Groceries"
   - task_id=7: "Return Groceries"
→ Multiple matches → Ask clarification (Rule 2)
```

**Disambiguation**:
- If user says "the first one" after clarification, use first listed task_id
- If user says "task 3", use task_id=3
- If user provides position ("number 2"), use task_id at that position

---

## Multi-Step Tool Chaining

### Chaining Scenarios

#### Scenario 1: Delete by Title
**User**: "Delete the groceries task"

**Chain**:
1. Tool: `list_tasks(user_id, status="all")`
2. Find task with title matching "groceries" (fuzzy match)
3. Tool: `delete_task(user_id, task_id=<found_id>)`
4. Response: "I've deleted 'Buy groceries' from your list."

**Error Handling**:
- No match found → "I couldn't find a task matching 'groceries'. Here's your current list: [show tasks]"
- Multiple matches → "I found multiple tasks with 'groceries': [list matches]. Which one would you like to delete?"

#### Scenario 2: Complete by Title
**User**: "I finished the report"

**Chain**:
1. Tool: `list_tasks(user_id, status="pending")`
2. Find task with title containing "report"
3. Tool: `complete_task(user_id, task_id=<found_id>)`
4. Response: "Great job! I've marked 'Finish project report' as complete."

#### Scenario 3: Add and List
**User**: "Add buy milk and show me all my tasks"

**Chain**:
1. Tool: `add_task(user_id, title="buy milk")`
2. Tool: `list_tasks(user_id, status="all")`
3. Response: "I've added 'Buy milk' to your list. Here are all your tasks: [task list]"

#### Scenario 4: Update Multiple Fields
**User**: "Change task 3 title to 'Call mom tonight' and add description 'Ask about weekend plans'"

**Chain**:
1. Tool: `update_task(user_id, task_id=3, title="Call mom tonight", description="Ask about weekend plans")`
2. Response: "I've updated task 3 with the new title and description."

### Chaining Rules

**Rule 1: Order Matters**
- Always execute tools in logical dependency order
- Example: list_tasks BEFORE delete_task (when deleting by title)

**Rule 2: Stop on Error**
- If first tool fails, don't execute subsequent tools
- Inform user of the failure

**Rule 3: Batch When Possible**
- If tools are independent, execute in parallel (if agent supports)
- Example: add_task + list_tasks can be batched

**Rule 4: Context Passing**
- Pass results from first tool to second when needed
- Example: task_id from list_tasks → delete_task

---

## Confirmation Response Rules

### Response Templates

#### Task Created
```
Template: "I've added '[TITLE]' to your list."
Variations:
- "Added '[TITLE]' to your tasks."
- "Got it! '[TITLE]' is now on your list."
- "✓ Created: [TITLE]"
```

**Examples**:
- User: "Add buy groceries" → "I've added 'Buy groceries' to your list."
- User: "Remember to call mom" → "Got it! 'Call mom' is now on your list."

#### Tasks Listed
```
Template (with tasks):
"Here are your [STATUS] tasks:
1. [TASK_TITLE] [✓ if completed]
2. [TASK_TITLE]
..."

Template (no tasks):
"You don't have any [STATUS] tasks."
```

**Examples**:
- Pending tasks: "Here are your pending tasks:\n1. Buy groceries\n2. Call mom"
- No tasks: "You don't have any pending tasks. Great work!"
- All tasks: "Here are all your tasks:\n1. ✓ Submit report\n2. Buy groceries"

#### Task Completed
```
Template: "[ENCOURAGEMENT] I've marked '[TITLE]' as complete."
Encouragements: Great job! | Awesome! | Well done! | Nice work! | Excellent!
```

**Examples**:
- User: "Done with task 3" → "Great job! I've marked 'Buy groceries' as complete."
- User: "I finished the report" → "Excellent! I've marked 'Finish project report' as complete."

#### Task Deleted
```
Template: "I've deleted '[TITLE]' from your list."
Variations:
- "Removed '[TITLE]'."
- "'[TITLE]' has been deleted."
```

**Examples**:
- User: "Delete task 2" → "I've deleted 'Old meeting notes' from your list."

#### Task Updated
```
Template: "I've updated '[TITLE]'."
With details: "I've updated task [ID] with the new [FIELDS_CHANGED]."
```

**Examples**:
- User: "Change task 1 to call mom" → "I've updated 'Call mom'."
- User: "Update description for task 3" → "I've updated task 3 with the new description."

#### Greeting
```
Template: "Hi! I'm your task assistant. I can help you add, view, complete, update, and delete tasks. What would you like to do?"
```

#### Help
```
Template: "I can help you manage your tasks! Here's what you can say:
• 'Add [task]' - Create a new task
• 'Show my tasks' - View all tasks
• 'What's pending?' - View incomplete tasks
• 'Mark task [#] as done' - Complete a task
• 'Delete task [#]' - Remove a task
• 'Change task [#] to [new title]' - Update a task

Just talk naturally, and I'll understand!"
```

### Response Tone Guidelines

**✅ DO**:
- Use first person ("I've added")
- Be conversational ("Got it!", "Great job!")
- Confirm what was done ("I've marked 'X' as complete")
- Keep it brief (1-2 sentences)
- Use task titles in quotes for clarity
- Add light encouragement for completions

**❌ DON'T**:
- Be robotic ("Task successfully created in database")
- Over-explain ("I have successfully executed the add_task function...")
- Use technical jargon ("Tool invocation complete")
- Be verbose (3+ sentences)
- Show internal errors to user

---

## Error Recovery Behavior

### Error Types and Responses

#### Error 1: Task Not Found
**Situation**: User references non-existent task ID

**Agent Response**:
```
"I couldn't find task [ID]. Would you like to see your current tasks?"
```

**Recovery**:
1. Offer to list tasks
2. If user confirms, call `list_tasks`

**Example**:
- User: "Complete task 99"
- Agent: "I couldn't find task 99. Would you like to see your current tasks?"
- User: "Yes"
- Agent: [calls list_tasks] "Here are your pending tasks: ..."

#### Error 2: Ambiguous Request
**Situation**: Can't determine what user wants

**Agent Response**:
```
"I'm not sure what you'd like me to do. Could you rephrase that?"
```

**Recovery**:
1. Ask for clarification
2. Provide examples

**Example**:
- User: "Do the thing"
- Agent: "I'm not sure what you'd like me to do. Could you rephrase that? For example, you can say 'Add buy groceries' or 'Show my tasks'."

#### Error 3: Missing Parameters
**Situation**: User intent clear, but missing required info (e.g., task ID for completion)

**Agent Response**:
```
"Which task would you like to [ACTION]? You can say the task number or title."
```

**Recovery**:
1. Ask for missing parameter
2. Wait for user response with required info

**Example**:
- User: "Mark it as done"
- Agent: "Which task would you like to complete? You can say the task number or title."
- User: "Task 3"
- Agent: [calls complete_task] "Great job! I've marked 'Buy groceries' as complete."

#### Error 4: Multiple Matches
**Situation**: User deletes/completes by title, but multiple tasks match

**Agent Response**:
```
"I found multiple tasks with '[QUERY]':
1. [TASK_TITLE_1]
2. [TASK_TITLE_2]
Which one would you like to [ACTION]?"
```

**Recovery**:
1. Show all matches with IDs
2. Wait for user to specify which one

**Example**:
- User: "Delete the report task"
- Agent: "I found multiple tasks with 'report':\n1. Finish project report\n2. Review report draft\nWhich one would you like to delete?"
- User: "The first one"
- Agent: [calls delete_task with id=1] "I've deleted 'Finish project report' from your list."

#### Error 5: Database/System Error
**Situation**: MCP tool returns error (e.g., database connection failure)

**Agent Response**:
```
"Sorry, I encountered an issue. Please try again in a moment."
```

**Recovery**:
1. Log error for debugging
2. Don't expose technical details to user
3. Suggest retry

**Example**:
- User: "Add buy groceries"
- [Database error occurs]
- Agent: "Sorry, I encountered an issue. Please try again in a moment."

#### Error 6: Empty Task List
**Situation**: User asks to list tasks but has none

**Agent Response** (NOT an error, but handled specially):
```
"You don't have any [STATUS] tasks. [ENCOURAGEMENT]"
```

**Encouragement Variations**:
- "You're all caught up!" (for pending tasks)
- "Great work!" (for all tasks empty)
- "Nothing completed yet." (for completed tasks)

**Example**:
- User: "Show my pending tasks"
- [list_tasks returns empty array]
- Agent: "You don't have any pending tasks. You're all caught up!"

#### Error 7: Invalid Update (No Fields)
**Situation**: User says "update task 3" but doesn't specify what to update

**Agent Response**:
```
"What would you like to change about task [ID]? You can update the title or description."
```

**Recovery**:
1. Ask what to update
2. Wait for user to provide new title/description

**Example**:
- User: "Update task 3"
- Agent: "What would you like to change about task 3? You can update the title or description."
- User: "Change title to call mom"
- Agent: [calls update_task] "I've updated 'Call mom'."

### Error Recovery Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ Tool Returns Error                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────┐
      │ Error Type?                   │
      └────────┬──────────────────────┘
               │
      ┌────────┴────────┬────────────────┬──────────────┐
      │                 │                │              │
      ▼                 ▼                ▼              ▼
TASK_NOT_FOUND    MISSING_PARAM    DATABASE_ERROR   OTHER
      │                 │                │              │
      ▼                 ▼                ▼              ▼
Offer to list     Ask for info    Suggest retry   Show generic
     tasks          Wait for                        error msg
                   response
```

---

## Conversation Context Management

### Stateless Conversation Flow

**Request Cycle**:
1. **Receive**: User sends message + conversation_id (optional)
2. **Load**: Fetch conversation history from database
3. **Context**: Build context from history (last 10 messages)
4. **Process**: Detect intent, select tools, execute
5. **Store**: Save user message + assistant response to database
6. **Respond**: Return response + conversation_id

### Context Window

**Size**: Last 50 messages (25 user + 25 assistant pairs)

**Purpose**: Enable pronoun resolution, contextual references, and conversation continuity

**Example**:
```json
[
  {"role": "user", "content": "Add buy groceries"},
  {"role": "assistant", "content": "I've added 'Buy groceries' to your list."},
  {"role": "user", "content": "Show my tasks"},
  {"role": "assistant", "content": "Here are your pending tasks:\n1. Buy groceries"},
  {"role": "user", "content": "Mark task 1 as done"}
  // ... up to 50 total messages
]
```

### Contextual References

The agent resolves contextual references using the rules defined in **Rule 3: Pronoun and Contextual Reference Handling** (see above).

**Pronoun Resolution**:
- "Delete it" → Refers to last mentioned task_id in context window (last 50 messages)
- "What about that one?" → Refers to last tracked task_id

**Implicit Continuation**:
- After listing tasks, "Delete the first one" → Delete task at position 1 in list
- After creating task, "Actually, change it to..." → Update just-created task (tracked task_id)

**Example (Full Flow)**:
```
User: "Show my tasks"
Agent: [lists tasks including "#3: Buy groceries"] [tracks task_id=3 as first in list]
User: "Delete that one"
Agent: [resolves "that one" → task_id=3] "I've deleted 'Buy groceries' from your list."
```

**Resolution Failure**:
```
User: "Delete it"
[No task_id in context window]
Agent: "Which task would you like to delete? You can say the task number or title."
```

**See Also**: Rule 3 (Pronoun Handling), Rule 4 (Context Window Limits)

---

## Special Behaviors

### Behavior 1: Proactive Suggestions

When user has completed all pending tasks:
```
Agent: "You don't have any pending tasks. You're all caught up! 🎉"
```

When user creates similar tasks:
```
User: "Add buy milk"
[Previous task: "Buy groceries" exists]
Agent: "I've added 'Buy milk' to your list. (You also have 'Buy groceries' pending.)"
```

### Behavior 2: Smart Defaults

**Default status filter**: "all"
- User: "Show tasks" → list_tasks(status="all")

**Infer status from context**:
- User: "What's left to do?" → list_tasks(status="pending")
- User: "What did I finish?" → list_tasks(status="completed")

### Behavior 3: Friendly Nudges

After several creates without completions:
```
Agent: "I've added '[TASK]'. You now have [X] pending tasks. Ready to tackle one?"
```

### Behavior 4: Natural Language Flexibility

Accept variations:
- "Buy groceries" = "I need to buy groceries" = "Add a task to buy groceries"
- "Show tasks" = "What's on my list?" = "Tell me my todos"
- "Done with task 3" = "Finished task 3" = "Mark 3 as complete"

---

## Agent Personality

### Voice Characteristics

**Tone**: Friendly, helpful, encouraging
**Style**: Conversational, not robotic
**Attitude**: Positive, supportive

### Example Responses (Good vs Bad)

#### Creating Tasks

❌ **Bad (Robotic)**:
```
"Task created successfully. ID: 5. Title: Buy groceries."
```

✅ **Good (Friendly)**:
```
"I've added 'Buy groceries' to your list."
```

#### Completing Tasks

❌ **Bad (Dry)**:
```
"Task 3 status updated to completed."
```

✅ **Good (Encouraging)**:
```
"Great job! I've marked 'Buy groceries' as complete."
```

#### Listing Tasks

❌ **Bad (Technical)**:
```
"Query returned 3 records. Displaying results."
```

✅ **Good (Conversational)**:
```
"Here are your 3 pending tasks:"
```

#### Errors

❌ **Bad (Exposing Internals)**:
```
"DatabaseException: Connection timeout on query execution."
```

✅ **Good (User-Friendly)**:
```
"Sorry, I encountered an issue. Please try again in a moment."
```

---

## Testing Scenarios

### Happy Path Scenarios

1. **Create and Complete**:
   - User: "Add buy groceries"
   - Agent: "I've added 'Buy groceries' to your list."
   - User: "Mark it as done"
   - Agent: "Great job! I've marked 'Buy groceries' as complete."

2. **List Filtered**:
   - User: "Show my pending tasks"
   - Agent: "Here are your pending tasks:\n1. Call mom\n2. Submit report"

3. **Delete by Title**:
   - User: "Delete the groceries task"
   - Agent: "I've deleted 'Buy groceries' from your list."

### Edge Case Scenarios

1. **Empty List**:
   - User: "Show my tasks"
   - Agent: "You don't have any tasks. You're all caught up!"

2. **Ambiguous Request**:
   - User: "Do that thing"
   - Agent: "I'm not sure what you'd like me to do. Could you rephrase that?"

3. **Task Not Found**:
   - User: "Complete task 999"
   - Agent: "I couldn't find task 999. Would you like to see your current tasks?"

4. **Multiple Matches**:
   - User: "Delete the report"
   - [2 tasks contain "report"]
   - Agent: "I found multiple tasks with 'report':\n1. Finish report\n2. Review report\nWhich one would you like to delete?"

### Multi-Turn Scenarios

1. **Clarification Flow**:
   - User: "Delete it"
   - Agent: "Which task would you like to delete? You can say the task number or title."
   - User: "Task 3"
   - Agent: "I've deleted 'Buy groceries' from your list."

2. **Chained Actions**:
   - User: "Add buy milk and show me all tasks"
   - Agent: "I've added 'Buy milk' to your list. Here are all your tasks:\n1. Buy milk\n2. Call mom"

---

## Implementation Checklist

### Intent Detection
- [ ] Pattern matching for all 8 intent types
- [ ] Contextual intent detection (task ID presence, status keywords)
- [ ] Multi-intent message parsing
- [ ] **Deterministic keyword matching (Rule 1)**

### Tool Selection
- [ ] Correct tool mapping for each intent
- [ ] Parameter extraction (task_id, title, description, status)
- [ ] Default parameter handling
- [ ] **Tool invocation priority: ID > exact title > fuzzy match (Rule 5)**

### Task Resolution
- [ ] **Explicit ID resolution (highest priority)**
- [ ] **Exact title matching (case-insensitive)**
- [ ] **Fuzzy matching with >60% similarity threshold**
- [ ] **Multiple match disambiguation (Rule 2)**

### Contextual Understanding
- [ ] **Pronoun resolution ("it", "that task") via last mentioned task_id (Rule 3)**
- [ ] **Context window: last 50 messages (Rule 4)**
- [ ] **Task ID tracking across conversation**
- [ ] **Graceful degradation when context is unavailable**

### Multi-Step Chaining
- [ ] Delete/complete by title (list → delete/complete)
- [ ] Add and list (add → list)
- [ ] Update multiple fields
- [ ] Stop on error in chain

### Confirmation Responses
- [ ] Friendly templates for all 5 tools
- [ ] Encouragement for completions
- [ ] Concise formatting (1-2 sentences)

### Error Recovery
- [ ] Task not found handling
- [ ] Ambiguous request clarification
- [ ] Missing parameter prompts
- [ ] Multiple matches disambiguation
- [ ] Generic error messages (no technical details)

### Tone & Personality
- [ ] Conversational language
- [ ] First person ("I've added")
- [ ] Positive attitude
- [ ] No robotic phrasing

---

## Acceptance Criteria

### AC-CB1: Intent Detection Accuracy
**Given** a user message with clear intent  
**When** the agent processes the message  
**Then** the agent correctly identifies the intent with >95% accuracy using deterministic keyword matching (Rule 1)

### AC-CB2: Tool Selection Correctness
**Given** a detected intent  
**When** the agent selects an MCP tool  
**Then** the correct tool is chosen with correct parameters following priority rules (Rule 5)

### AC-CB3: Multi-Step Execution
**Given** a message requiring multiple tools (e.g., "delete groceries task")  
**When** the agent processes the request  
**Then** tools are executed in correct order and results combined

### AC-CB4: Confirmation Quality
**Given** a successful tool execution  
**When** the agent responds  
**Then** response is friendly, concise (1-2 sentences), and confirms action

### AC-CB5: Error Handling
**Given** an error (task not found, missing param, etc.)  
**When** the agent responds  
**Then** response is user-friendly, offers recovery, no technical details

### AC-CB6: Contextual Understanding
**Given** a pronoun reference ("delete it", "mark that as done")  
**When** the agent processes the message  
**Then** agent correctly resolves reference from conversation history using last mentioned task_id (Rule 3)

### AC-CB7: Natural Language Flexibility
**Given** variations of the same request ("add buy milk", "I need to buy milk", "remind me to buy milk")  
**When** the agent processes each variation  
**Then** all result in the same tool call (add_task with title="buy milk")

### AC-CB8: Ambiguous Task Handling
**Given** a user request that matches multiple tasks (e.g., "delete report")  
**When** fuzzy matching returns >1 result  
**Then** agent asks for clarification with numbered list of matches (Rule 2)

### AC-CB9: Task Resolution Priority
**Given** a task reference with both ID and title ("delete task 3 groceries")  
**When** the agent resolves the task  
**Then** explicit ID takes priority over title (Rule 5: Priority Order)

### AC-CB10: Context Window Limitation
**Given** a pronoun reference to a task mentioned >50 messages ago  
**When** the agent attempts to resolve the pronoun  
**Then** agent asks for clarification due to context window limitation (Rule 4)

---

## Version History

### v1.1.0 (2026-01-03)
- **Added Rule 1**: Deterministic natural language to tool mapping
- **Added Rule 2**: Ambiguous task handling with clarification flow
- **Added Rule 3**: Pronoun handling with last mentioned task_id tracking
- **Added Rule 4**: Context window limitations (50 messages)
- **Added Rule 5**: Tool invocation priority (ID > exact title > fuzzy match)
- Updated context window from 10 to 50 messages
- Added 3 new acceptance criteria (AC-CB8, AC-CB9, AC-CB10)
- Enhanced implementation checklist with rule references

### v1.0.0 (2026-01-03)
- Initial specification
- 8 intent types defined
- Tool selection logic documented
- Multi-step chaining scenarios
- Confirmation templates
- Error recovery behaviors
- Tone guidelines
- Testing scenarios

---

**Document Status**: ✅ APPROVED  
**Last Updated**: January 3, 2026  
**Maintained By**: Phase III Development Team
