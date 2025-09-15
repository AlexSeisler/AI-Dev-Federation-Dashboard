# ===============================
# AI-Dev-Federation-Dashboard
# Stage 3 Phase 3 Validation Script (Runner-Focused)
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
# Phase 2: Login
# -------------------------------------------------
Write-Host "`n[Step 2] Login as approved user" -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" `
      -Method POST -ContentType "application/json" `
      -Body (@{ email = $email; password = $password } | ConvertTo-Json)

    $jwt = $loginResponse.access_token
    Write-Host "[OK] Got JWT: $jwt" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Login failed. Make sure $email is approved." -ForegroundColor Red
    exit 1
}

# -------------------------------------------------
# Phase 3: Dry Run (repo tree context only)
# -------------------------------------------------
Write-Host "`n[Step 3] Dry-run repo context assembly (no HF call)" -ForegroundColor Cyan
try {
    $treeResponse = Invoke-RestMethod -Uri "$baseUrl/repo/tree?repo_id=AlexSeisler/AI-Dev-Federation-Dashboard`&branch=main" `
      -Method GET `
      -Headers @{ Authorization = "Bearer $jwt" }

    Write-Host "[OK] Repo tree retrieved (showing first 10 entries):" -ForegroundColor Green
    $treeResponse | Select-Object -First 10 | ConvertTo-Json -Depth 3
}
catch {
    Write-Host "[ERROR] Dry-run repo tree fetch failed." -ForegroundColor Red
    exit 1
}

# -------------------------------------------------
# Extra phases (commented for now)
# -------------------------------------------------
<#
# Phase 4: HF Integration Test (with streaming)
# Phase 5: Full End-to-End Fetch
#>
