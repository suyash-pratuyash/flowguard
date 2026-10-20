# Run in a SECOND PowerShell window while the API is running on port 8000.
# Expected: health 200 | 429 | 200 | 503 | 422
$base = "http://127.0.0.1:8000"

function Call($name, $scenario, $attempt, $payload, $id) {
  $body = @{ request_id = $id; scenario = $scenario; attempt = $attempt; payload = $payload } | ConvertTo-Json -Depth 5
  try {
    $r = Invoke-WebRequest -Method POST -Uri "$base/api/target" -ContentType "application/json" -Body $body -UseBasicParsing
    Write-Host ("{0,-28} -> {1}  {2}" -f $name, $r.StatusCode, $r.Content)
  } catch {
    $resp = $_.Exception.Response
    $code = [int]$resp.StatusCode
    $retry = $resp.Headers["Retry-After"]
    Write-Host ("{0,-28} -> {1}  Retry-After={2}" -f $name, $code, $retry)
  }
}

$h = Invoke-RestMethod "$base/health"
Write-Host "health                       -> 200  $($h | ConvertTo-Json -Compress)"
Call "RATE_LIMIT_ONCE attempt 1" "RATE_LIMIT_ONCE" 1 @{ requiredField = "demo-value" } "demo-001"
Call "RATE_LIMIT_ONCE attempt 2" "RATE_LIMIT_ONCE" 2 @{ requiredField = "demo-value" } "demo-001"
Call "SERVICE_UNAVAILABLE attempt 1" "SERVICE_UNAVAILABLE" 1 @{} "demo-503"
Call "INVALID_DATA empty payload" "INVALID_DATA" 1 @{} "demo-invalid"
