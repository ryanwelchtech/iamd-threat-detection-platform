# Simple policy validation placeholder

$policyPath = ".\policy\policy.json"

if (!(Test-Path $policyPath)) {
  Write-Error "policy.json not found"
  exit 1
}

$policy = Get-Content $policyPath | ConvertFrom-Json

Write-Host "Policy Name: $($policy.policy_name)"
Write-Host "Version:     $($policy.version)"
Write-Host ""
Write-Host "Release Gates:"
Write-Host "  Max Critical: $($policy.gates.maxCritical)"
Write-Host "  Max High:     $($policy.gates.maxHigh)"
Write-Host ""
Write-Host "Enforcement:"
Write-Host "  On Violation: $($policy.enforcement.onViolation)"
Write-Host "  On Pass:      $($policy.enforcement.onPass)"
