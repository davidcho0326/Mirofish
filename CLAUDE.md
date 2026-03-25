# FnF Marketing Simulator — Project Rules

## Python Environment
- This project uses **Python 3.11** via `.venv/` (NOT the system Python 3.12)
- ALWAYS use `.venv/Scripts/python.exe` for Python commands (never bare `python`)
- ALWAYS use `.venv/Scripts/pip.exe` for pip commands (never bare `pip`)
- NEVER use `source activate`, `deactivate`, or any venv activation commands
- The `.venv/` directory is gitignored and must not be committed

## Examples
```bash
# Run server
.venv/Scripts/python.exe run.py

# Install a package
.venv/Scripts/pip.exe install package-name

# Run a script
.venv/Scripts/python.exe -c "print('hello')"

# Run tests
.venv/Scripts/python.exe -m pytest
```

## Server
- Flask runs on port **5002**
- Health check: `GET http://localhost:5002/health`

## Architecture
- `core/` — MiroFish engine (forked, do not modify unless necessary)
- `modules/m1~m5/` — F&F marketing modules (active development)
- `shared/` — Brand definitions, Korean market config
- `templates/` — JSON templates for ontology/archetypes/brands

## File I/O
- Windows에서 한국어 포함 파일 읽을 때 반드시 `encoding='utf-8'` 명시
- `open('file.json', encoding='utf-8')` — 생략 시 cp949 에러 발생

## LLM
- Uses Claude API via OpenAI SDK compatibility layer
- `response_format: {"type": "json_object"}` is IGNORED by Claude — use `chat()` with explicit JSON instructions in prompts instead of `chat_json()`

## Working Directory
- Bash 명령 실행 시 CWD가 `c:\python\venv`일 수 있음
- 반드시 `cd /c/python/venv/fnf-mkt-sim &&` 프리픽스를 붙이거나 절대 경로 사용
