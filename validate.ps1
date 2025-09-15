# ===============================
# AI-Dev-Federation-Dashboard
# Stage 3 Phase 5 Full End-to-End Validation (Approved User)
# ===============================

$baseUrl = "http://localhost:8080"
$email = "admin@example.com"
$password = "adminpass"

# -------------------------------------------------
# Phase 1: Health checks
# -------------------------------------------------
Write-Host "`n[Step 1] Health checks" -ForegroundColor Cyan
try {
    Invoke-RestMethod "$baseUrl/health/ping"
    Invoke-RestMethod "$baseUrl/healthz"
    Write-Host "[OK] Health endpoints working" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Health checks failed" -ForegroundColor Red
    exit 1
}

# -------------------------------------------------
# Phase 2: Login as approved non-admin user
# -------------------------------------------------
Write-Host "`n[Step 2] Login as approved user ($email)" -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" `
      -Method POST -ContentType "application/json" `
      -Body (@{ email = $email; password = $password } | ConvertTo-Json)

    $jwt = $loginResponse.access_token
    Write-Host "[OK] Got JWT for $email" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Login failed for $email" -ForegroundColor Red
    $_ | Out-String | Write-Host
    exit 1
}


# -------------------------------------------------
# Phase 3: Repo context (direct fetch)
# -------------------------------------------------
Write-Host "`n[Step 3] Repo context fetch (direct)" -ForegroundColor Cyan
try {
    $treeResponse = Invoke-RestMethod -Uri "$baseUrl/repo/tree?repo_id=AlexSeisler/AI-Dev-Federation-Dashboard&branch=main" `
        -Method GET -Headers @{ Authorization = "Bearer $jwt" }

    if ($treeResponse) {
        Write-Host "[OK] Repo tree fetch succeeded" -ForegroundColor Green
        Write-Host "Found $($treeResponse.Count) files in tree."
    } else {
        Write-Host "[ERROR] Repo tree fetch returned empty" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Repo tree fetch failed." -ForegroundColor Red
    $_ | Out-String | Write-Host
    exit 1
}
# -------------------------------------------------
# Phase 4: Hugging Face Task Runner (preset tests)
# -------------------------------------------------
Write-Host "`n[Step 4] Hugging Face task runner" -ForegroundColor Cyan
try {
    # Alignment/Plan
    $alignBody = @{
        context = '{
            "user_prompt": "Draft an alignment plan for repo improvements"
        }'
    } | ConvertTo-Json
    $alignTask = Invoke-RestMethod -Uri "$baseUrl/tasks/run/align" `
        -Method POST -ContentType "application/json" -Body $alignBody `
        -Headers @{ Authorization = "Bearer $jwt" }
    $alignTaskId = $alignTask.task_id
    Write-Host "[OK] Alignment/Plan task started (ID: $alignTaskId)" -ForegroundColor Green
    $alignStream = Invoke-WebRequest -Uri "$baseUrl/tasks/$alignTaskId/stream" -Headers @{ Authorization = "Bearer $jwt" } -UseBasicParsing
    $alignStream.Content | Write-Host

    # Structure Analysis (injects /repo/tree context)
    $structBody = @{
        context = '{
            "repo_id": "AlexSeisler/AI-Dev-Federation-Dashboard",
            "user_prompt": "Summarize the repository structure and suggest improvements"
        }'
    } | ConvertTo-Json
    $structTask = Invoke-RestMethod -Uri "$baseUrl/tasks/run/structure" `
        -Method POST -ContentType "application/json" -Body $structBody `
        -Headers @{ Authorization = "Bearer $jwt" }
    $structTaskId = $structTask.task_id
    Write-Host "[OK] Structure Analysis task started (ID: $structTaskId)" -ForegroundColor Green
    $structStream = Invoke-WebRequest -Uri "$baseUrl/tasks/$structTaskId/stream" -Headers @{ Authorization = "Bearer $jwt" } -UseBasicParsing
    $structStream.Content | Write-Host

    # File Analysis (injects /repo/file context)
    $fileBody = @{
        context = '{
            "repo_id": "AlexSeisler/AI-Dev-Federation-Dashboard",
            "file_path": "server/main.py",
            "user_prompt": "Review this file for purpose, risks, and possible improvements"
        }'
    } | ConvertTo-Json
    $fileTask = Invoke-RestMethod -Uri "$baseUrl/tasks/run/file" `
        -Method POST -ContentType "application/json" -Body $fileBody `
        -Headers @{ Authorization = "Bearer $jwt" }
    $fileTaskId = $fileTask.task_id
    Write-Host "[OK] File Analysis task started (ID: $fileTaskId)" -ForegroundColor Green
    $fileStream = Invoke-WebRequest -Uri "$baseUrl/tasks/$fileTaskId/stream" -Headers @{ Authorization = "Bearer $jwt" } -UseBasicParsing
    $fileStream.Content | Write-Host
}
catch {
    Write-Host "[ERROR] HF task runner test failed." -ForegroundColor Red
    $_ | Out-String | Write-Host
    exit 1
}
