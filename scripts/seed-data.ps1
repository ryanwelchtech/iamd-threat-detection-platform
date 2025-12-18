param(
  [ValidateSet("benign","airborne_fast_closing","sea_surface_no_ais")]
  [string]$Scenario = "benign"
)

$ErrorActionPreference = "Stop"

# Demo secret (must match docker-compose)
$secret = "dev_super_secret_change_me"

# Requires: python + pip install pyjwt
$token = python -c "import time,jwt; print(jwt.encode({'sub':'sensor@demo.local','role':'sensor','iat':int(time.time()),'exp':int(time.time())+3600}, '$secret', algorithm='HS256'))"

$headers = @{ Authorization = "Bearer $token" }

function Post-Obs($obs) {
  Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8001/observations" `
    -Headers $headers `
    -Body ($obs | ConvertTo-Json -Depth 10) `
    -ContentType "application/json" | Out-Null
}

# Base timestamp (string is fine for demo)
$ts0 = "2025-01-01T12:00:00Z"

if ($Scenario -eq "benign") {
  # Benign: slower air track, AIS present, should trend LOW
  $obs1 = @{
    observation_id="rad-ben-0001"; sensor_type="RADAR"; sensor_id="RADAR-01"; ts_utc=$ts0
    position=@{lat=29.7604; lon=-95.3698; alt_m=9000}
    velocity=@{vx_mps=120; vy_mps=5; vz_mps=0}
    signature=@{rcs=0.2; ir=0.05}
    quality=@{snr_db=18.0; confidence=0.90}
  }
  $obs2 = @{
    observation_id="ais-ben-0001"; sensor_type="AIS"; sensor_id="AIS-EDGE-01"; ts_utc=$ts0
    position=@{lat=29.7600; lon=-95.3702; alt_m=0}
    velocity=@{vx_mps=6; vy_mps=1; vz_mps=0}
    signature=@{rcs=0.0; ir=0.0}
    quality=@{snr_db=0.0; confidence=0.99}
  }
  Post-Obs $obs1
  Post-Obs $obs2
}

elseif ($Scenario -eq "airborne_fast_closing") {
  # Airborne fast closing: high speed + no AIS -> should go MEDIUM/HIGH depending on your rules
  $obs1 = @{
    observation_id="rad-afc-0001"; sensor_type="RADAR"; sensor_id="RADAR-01"; ts_utc=$ts0
    position=@{lat=29.7604; lon=-95.3698; alt_m=12000}
    velocity=@{vx_mps=290; vy_mps=-20; vz_mps=0}
    signature=@{rcs=0.9; ir=0.2}
    quality=@{snr_db=20.0; confidence=0.90}
  }
  $obs2 = @{
    observation_id="eoir-afc-0001"; sensor_type="EOIR"; sensor_id="EOIR-02"; ts_utc="2025-01-01T12:00:02Z"
    position=@{lat=29.7610; lon=-95.3690; alt_m=12100}
    velocity=@{vx_mps=285; vy_mps=-18; vz_mps=0}
    signature=@{rcs=0.7; ir=0.4}
    quality=@{snr_db=15.0; confidence=0.82}
  }
  Post-Obs $obs1
  Post-Obs $obs2
}

elseif ($Scenario -eq "sea_surface_no_ais") {
  # Sea surface contact, no AIS -> should typically land MEDIUM (no_ais_match) but low closing rate
  $obs1 = @{
    observation_id="rad-ssn-0001"; sensor_type="RADAR"; sensor_id="RADAR-01"; ts_utc=$ts0
    position=@{lat=29.7512; lon=-95.3987; alt_m=0}
    velocity=@{vx_mps=18; vy_mps=2; vz_mps=0}
    signature=@{rcs=0.6; ir=0.05}
    quality=@{snr_db=16.5; confidence=0.88}
  }
  Post-Obs $obs1
}

Write-Host "Seed complete (scenario: $Scenario)."
Write-Host "COP:   http://localhost:8080"
Write-Host "Audit: http://localhost:8004/events"
Write-Host "Fusion stats:  http://localhost:8002/stats"
Write-Host "Scoring stats: http://localhost:8003/stats"
