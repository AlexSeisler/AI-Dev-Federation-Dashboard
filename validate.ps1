# ===============================
# AI-Dev-Federation-Dashboard
# Stage 3 Phase 3 Validation Script
# ===============================

$baseUrl = "http://localhost:8080"

Write-Host "🔎 Step 1: Health checks" -ForegroundColor Cyan
Invoke-RestMethod "$baseUrl/health/ping"
Invoke-RestMethod "$baseUrl/healthz"

Write-Host "`n🔎 Step 2: Signup a new user" -ForegroundColor Cyan
$signupResponse = Invoke-RestMethod -Uri "$baseUrl/auth/signup" `
  -Method POST -ContentType "application/json" `
  -Body '{"email": "testuser@example.com", "password": "securepass"}'
$signupResponse

Write-Host "`n⚠️ Action Required: Approve the user via Admin JWT" -ForegroundColor Yellow
Write-Host "Example:" -ForegroundColor Yellow
Write-Host "Invoke-RestMethod -Uri `"$baseUrl/auth/approve/2`" -Method POST -Headers @{ Authorization = 'Bearer ADMIN_JWT' }" -ForegroundColor Yellow
Pause

Write-Host "`n🔎 Step 3: Login as the new user" -ForegroundColor Cyan
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" `
  -Method POST -ContentType "application/json" `
  -Body '{"email": "testuser@example.com", "password": "securepass"}'
$loginResponse
$jwt = $loginResponse.access_token
Write-Host "✅ Got JWT: $jwt" -ForegroundColor Green

Write-Host "`n🔎 Step 4: Run a structure analysis task" -ForegroundColor Cyan
$taskResponse = Invoke-RestMethod -Uri "$baseUrl/tasks/run/structure" `
  -Method POST -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer $jwt" } `
  -Body '{"context": ""}'
$taskResponse
$taskId = $taskResponse.task_id

Write-Host "`n🔎 Step 5: Stream task logs (SSE)" -ForegroundColor Cyan
# Note: WebRequest is used instead of RestMethod for streaming output
Invoke-WebRequest -Uri "$baseUrl/tasks/$taskId/stream" `
  -Headers @{ Authorization = "Bearer $jwt" } `
  -UseBasicParsing | Select-Object -Expand Content

Write-Host "`n🔎 Step 6: Fetch task details from DB" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/tasks/$taskId" `
  -Method GET -Headers @{ Authorization = "Bearer $jwt" }

Write-Host "`n✅ Validation flow complete!" -ForegroundColor Green
