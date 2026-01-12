# Database Validation Instructions

## Prerequisites

1. Create a `.env` file in the `backend` directory with your Neon credentials:

   ```env
   DATABASE_URL=postgresql://user:password@host-pooler.region.aws.neon.tech/neondb?sslmode=require
   OPENAI_API_KEY=your_openai_api_key_here
   ENV=development
   DEBUG=true
   ```

2. Install backend dependencies:

   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

## Run Validation

### Option 1: Run validation script

```powershell
cd backend
python validate_db.py
```

This will test:

- ✓ Database connection
- ✓ Schema creation (tables: tasks, conversations, messages)
- ✓ CRUD operations
- ✓ No credentials logged

### Option 2: Start the backend server

```powershell
cd backend
uvicorn app.main:app --reload
```

Check startup logs for:

- `✓ Database connection successful`
- `✓ Database tables initialized`
- No database passwords visible in logs

### Option 3: Test via API

1. Start backend server (see Option 2)
2. Open <http://localhost:8000/docs>
3. Test the `/api/{user_id}/chat` endpoint with:

   ```json
   {
     "message": "Add a task to test database"
   }
   ```

## Expected Results

### Successful Validation

```text
============================================================
DATABASE VALIDATION SCRIPT
============================================================

Database URL configured: postgresql://neondb_owner@***

Testing database connection...
✓ Connection successful (result: 1)

Initializing database schema...
✓ Tables created successfully

Testing CRUD operations...
  Testing CREATE...
  ✓ Created task with ID: 1
  Testing READ...
  ✓ Read task: Test Task
  Testing UPDATE...
  ✓ Updated task status
  Testing DELETE...
  ✓ Deleted task successfully
✓ All CRUD operations successful

Checking for credential leaks...
✓ Review output above - no database passwords should be visible

============================================================
VALIDATION SUMMARY
============================================================
Connection.............. ✓ PASS
Schema.................. ✓ PASS
CRUD.................... ✓ PASS
Credentials............. ✓ PASS
============================================================
✓ ALL VALIDATIONS PASSED
```

## Troubleshooting

### Connection Failed

- Verify DATABASE_URL is correct
- Check Neon database is running
- Verify SSL is enabled (`sslmode=require`)
- Check firewall/network settings

### Schema Creation Failed

- Ensure database user has CREATE TABLE permissions
- Check Neon database storage limits

### CRUD Operations Failed

- Verify database user has INSERT/UPDATE/DELETE permissions
- Check database constraints

## Files Modified for Validation

1. **backend/app/database.py**
   - Added `hide_parameters=True` to prevent parameter values in SQL logs
   - Prevents credential leaks in debug mode

2. **backend/validate_db.py** (new)
   - Standalone validation script
   - Tests connection, schema, CRUD operations
   - Sanitizes database URL in output (shows only user@***)