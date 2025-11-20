# Dev helper commands for PHANTOM
param(
  [ValidateSet('backend-test','frontend-test','compose-up','compose-down','alembic-up','alembic-downgrade')]
  [string]$Task = 'compose-up'
)

switch ($Task) {
  'backend-test' {
    Push-Location ..\backend
    if (!(Test-Path '.venv')) { py -3.11 -m venv .venv }
    . .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    pytest -q
    Pop-Location
  }
  'frontend-test' {
    Push-Location ..\frontend
    npm ci
    npm test -- --watchAll=false
    Pop-Location
  }
  'compose-up' {
    Push-Location ..
    if (!(Test-Path '.\infra\.env')) { Copy-Item '.\infra\.env.example' '.\infra\.env' }
    docker compose -f .\infra\docker-compose.yml up --build
    Pop-Location
  }
  'compose-down' {
    Push-Location ..
    docker compose -f .\infra\docker-compose.yml down -v
    Pop-Location
  }
  'alembic-up' {
    Push-Location ..\backend
    . .\.venv\Scripts\Activate.ps1
    alembic upgrade head
    Pop-Location
  }
  'alembic-downgrade' {
    Push-Location ..\backend
    . .\.venv\Scripts\Activate.ps1
    alembic downgrade -1
    Pop-Location
  }
}
