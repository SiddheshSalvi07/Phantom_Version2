# Smoke test script for PHANTOM backend
param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$WorkerToken = "devworkertoken"
)

Write-Host "Running smoke test against $BaseUrl"

$email = "smoke_$([Guid]::NewGuid().ToString('N').Substring(0,8))@example.com"
$pwd = "Pass123!"

$regBody = @{ email = $email; password = $pwd } | ConvertTo-Json
$reg = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/register" -ContentType "application/json" -Body $regBody
$loginBody = $regBody
$login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -ContentType "application/json" -Body $loginBody
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }

$goalBody = @{ title = "Smoke Goal"; description = "MVP" } | ConvertTo-Json
$goal = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/goal" -ContentType "application/json" -Headers $h -Body $goalBody
$tid = $goal.task_uuid

$status1 = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/status/$tid" -Headers $h
Write-Host "Status after create:" $status1.status

try { Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/execute/$tid" -Headers $h -ErrorAction Stop } catch { Write-Host "Execute before approve -> expected fail" }

Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/approve/$tid" -Headers $h | Out-Null
$queued = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/execute/$tid" -Headers $h
Write-Host "Execute after approve:" $queued.status

$logBody = @{ task_uuid = $tid; status = "done"; payload = @{ note = "smoke" } } | ConvertTo-Json
$logResp = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/worker/log" -ContentType "application/json" -Headers @{"X-Worker-Token"=$WorkerToken} -Body $logBody
Write-Host "Worker log ok:" $logResp.ok

Write-Host "Smoke test completed." -ForegroundColor Green
