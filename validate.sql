-- ===============================
-- AI-Dev-Federation-Dashboard
-- Stage 3 Phase 3 Validation SQL
-- ===============================

-- 🔎 Check Users
\echo '--- USERS ---'
SELECT id, email, role, status, created_at
FROM users
ORDER BY created_at DESC
LIMIT 5;

-- 🔎 Check Audit Logs
\echo '--- AUDIT LOGS ---'
SELECT id, user_id, action, timestamp
FROM audit_logs
ORDER BY timestamp DESC
LIMIT 10;

-- 🔎 Check Tasks
\echo '--- TASKS ---'
SELECT id, user_id, type, status, created_at
FROM tasks
ORDER BY created_at DESC
LIMIT 5;

-- 🔎 Check Task Logs
\echo '--- TASK LOGS ---'
SELECT id, task_id, message, timestamp
FROM logs
ORDER BY timestamp DESC
LIMIT 10;

-- 🔎 Check Memory (if applicable)
\echo '--- MEMORY ---'
SELECT id, user_id, content, created_at
FROM memory
ORDER BY created_at DESC
LIMIT 5;

-- Done
\echo '✅ Validation SQL complete!'
