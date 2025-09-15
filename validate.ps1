# ===============================
# AI-Dev-Federation-Dashboard
# Stage 3 Phase 3 Validation Script (Runner-Focused)
# ===============================

$baseUrl = "http://localhost:8080"
$email = "testuser@example.com"
$password = "securepass"

Write-Host "🔎 Step 1: Health checks" -ForegroundColor Cyan
Invoke-RestMethod "$baseUrl/health/ping"
Invoke-RestMethod "$baseUrl/healthz"

Write-Host "`n🔎 Step 2: Login as approved user" -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" `
      -Method POST -ContentType "application/json" `
      -Body (@{ email = $email; password = $password } | ConvertTo-Json)
    $jwt = $loginResponse.access_token
    Write-Host "✅ Got JWT: $jwt" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed. Make sure testuser@example.com is approved." -ForegroundColor Red
    exit 1
}

Write-Host "`n🔎 Step 3: Run a structure analysis task" -ForegroundColor Cyan
try {
    $taskResponse = Invoke-RestMethod -Uri "$baseUrl/tasks/run/structure" `
      -Method POST -ContentType "application/json" `
      -Headers @{ Authorization = "Bearer $jwt" } `
      -Body (@{ context = "" } | ConvertTo-Json)
    $taskResponse
    $taskId = $taskResponse.task_id
} catch {
    Write-Host "❌ Task creation failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n🔎 Step 4: Stream task logs (event stream)" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$baseUrl/tasks/$taskId/stream" `
      -Headers @{ Authorization = "Bearer $jwt" } `
      -UseBasicParsing | Select-Object -Expand Content
} catch {
    Write-Host "⚠️ SSE stream failed (may need manual check)." -ForegroundColor Yellow
}

Write-Host "`n🔎 Step 5: Fetch task details" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "$baseUrl/tasks/$taskId" `
      -Method GET -Headers @{ Authorization = "Bearer $jwt" }
} catch {
    Write-Host "⚠️ Could not fetch task details." -ForegroundColor Yellow
}

Write-Host "`n✅ Runner validation flow complete!" -ForegroundColor Green
