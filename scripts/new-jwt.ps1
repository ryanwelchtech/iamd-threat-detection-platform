param(
  [Parameter(Mandatory = $true)]
  [string]$Subject,

  [Parameter(Mandatory = $true)]
  [ValidateSet("sensor", "operator", "system")]
  [string]$Role
)

# Demo secret (matches docker-compose defaults)
$secret = "dev_super_secret_change_me"

# Requires: python + pip install pyjwt
$pythonCode = @"
import time, jwt
payload = {
  "sub": "$Subject",
  "role": "$Role",
  "iat": int(time.time()),
  "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "$secret", algorithm="HS256")
print(token)
"@

python -c $pythonCode
