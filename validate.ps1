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

Write-Host "`n[Step 3] Dry-run repo context assembly (no HF call)" -ForegroundColor Cyan
try {
    # ✅ Public repo — no JWT required
    $treeResponse = Invoke-RestMethod -Uri "$baseUrl/repo/tree?repo_id=AlexSeisler/AI-Dev-Federation-Dashboard&branch=main" -Method GET
    if ($treeResponse) {
        Write-Host "[OK] Repo tree fetch succeeded" -ForegroundColor Green
        Write-Host "Found $($treeResponse.Count) files in tree."
    } else {
        Write-Host "[ERROR] Repo tree fetch returned empty" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Dry-run repo tree fetch failed." -ForegroundColor Red
    $_ | Out-String | Write-Host
    exit 1
}

Write-Host "`n[Step 4] Hugging Face streaming integration" -ForegroundColor Cyan
try {
    $hfBody = @{ prompt = "Hello Federation" } | ConvertTo-Json
    $hfResponse = Invoke-RestMethod -Uri "$baseUrl/hf/stream" -Method POST -Body $hfBody -ContentType "application/json"
    Write-Host "[OK] HF streaming call succeeded" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] HF streaming test failed." -ForegroundColor Red
    $_ | Out-String | Write-Host
    exit 1
}


<#
Write-Host "`n[Step 5] End-to-end recruiter validation" -ForegroundColor Cyan
try {
    $validateBody = @{ candidate = "John Doe" } | ConvertTo-Json
    $validateResponse = Invoke-RestMethod -Uri "$baseUrl/recruiter/validate" -Method POST -Body $validateBody -ContentType "application/json"
    Write-Host "[OK] Recruiter validation succeeded" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Recruiter validation failed." -ForegroundColor Red
    $_ | Out-String | Write-Host
    exit 1
}
#>