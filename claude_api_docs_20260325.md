# Claude API 최신 문서 정보

## 개요
Anthropic의 Claude는 코딩, 추론, 멀티모달(텍스트+이미지) 입력을 지원하는 LLM 패밀리입니다.
OpenAI SDK 호환 레이어를 제공하여 `openai` 패키지로 Claude를 호출할 수 있습니다.

---

## 사용 가능한 모델 (최신)

| 모델 | API Model ID | 컨텍스트 | Max Output | 학습 데이터 | 특징 |
|------|-------------|----------|------------|------------|------|
| **Claude Opus 4.6** | `claude-opus-4-6` | 1M tokens | 128k tokens | ~Aug 2025 | 최고 지능, 에이전트/코딩 최적 |
| **Claude Sonnet 4.6** | `claude-sonnet-4-6` | 1M tokens | 64k tokens | ~Jan 2026 | 속도+지능 최적 밸런스 |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001` | 200k tokens | 64k tokens | ~Jul 2025 | 최고 속도, 준프론티어 지능 |

### 레거시 모델

| 모델 | API Model ID | 컨텍스트 | Max Output | 학습 데이터 |
|------|-------------|----------|------------|------------|
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | 1M (200k default) | 64k | Jul 2025 |
| Claude Opus 4.5 | `claude-opus-4-5-20251101` | 200k | 64k | Aug 2025 |
| Claude Opus 4.1 | `claude-opus-4-1-20250805` | 200k | 32k | Mar 2025 |
| Claude Sonnet 4 | `claude-sonnet-4-20250514` | 1M (200k default) | 64k | Mar 2025 |
| Claude Opus 4 | `claude-opus-4-20250514` | 200k | 32k | Mar 2025 |
| Claude Haiku 3 | `claude-3-haiku-20240307` | 200k | 4k | Aug 2023 |

> Claude Haiku 3은 **deprecated** — 2026-04-19 이후 서비스 종료 예정

---

## 가격 정책 (100만 토큰당, USD)

| 모델 | Input | Output | 비고 |
|------|-------|--------|------|
| **Claude Opus 4.6** | $5 | $25 | 최고 성능 |
| **Claude Sonnet 4.6** | $3 | $15 | **추천 (비용 대비 성능)** |
| **Claude Haiku 4.5** | $1 | $5 | 대량 처리/빠른 응답 |
| Claude Opus 4.5 | $5 | $25 | |
| Claude Opus 4.1 | $15 | $75 | |
| Claude Opus 4 | $15 | $75 | |
| Claude Sonnet 4.5 | $3 | $15 | |
| Claude Sonnet 4 | $3 | $15 | |
| Claude Haiku 3 | $0.25 | $1.25 | deprecated |

---

## OpenAI SDK 호환 설정

### Python 설정
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-ant-api03-YOUR_KEY",      # Anthropic API Key
    base_url="https://api.anthropic.com/v1/",  # Claude 엔드포인트
)

response = client.chat.completions.create(
    model="claude-sonnet-4-6",   # Claude 모델 ID
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    max_tokens=4096,
    temperature=0.7,
)
print(response.choices[0].message.content)
```

### .env 설정
```env
LLM_API_KEY=sk-ant-api03-여기에_키
LLM_BASE_URL=https://api.anthropic.com/v1/
LLM_MODEL_NAME=claude-sonnet-4-6
```

---

## 지원 기능 (OpenAI 호환 레이어)

| 기능 | 지원 상태 |
|------|----------|
| `model` | Claude 모델명 사용 |
| `messages` (text) | 완전 지원 |
| `messages` (image_url) | 완전 지원 |
| `max_tokens` | 완전 지원 |
| `temperature` | 0~1 (1 초과시 1로 cap) |
| `top_p` | 완전 지원 |
| `stream` | 완전 지원 |
| `tools` / function calling | 완전 지원 |
| `tool_choice` | 완전 지원 |
| `stop` sequences | 공백 아닌 시퀀스 지원 |
| Extended Thinking | `extra_body={"thinking": {...}}` |

### 미지원/무시 기능

| 기능 | 상태 |
|------|------|
| `response_format` (json_object) | **무시됨** — 네이티브 API의 Structured Outputs 사용 |
| `strict` (tool schema) | 무시됨 |
| Prompt caching | 네이티브 API에서만 지원 |
| Audio input | 무시됨 |
| `logprobs` | 무시됨 |
| `seed` | 무시됨 |
| `n` | 반드시 1 |

### 주의사항
- `response_format: {"type": "json_object"}`가 **무시**됩니다
- system/developer 메시지는 대화 시작 부분으로 자동 합쳐집니다
- 프로덕션에서는 네이티브 Anthropic SDK 권장
- Rate limit은 Anthropic 표준 `/v1/messages` 제한 적용

---

## 공식 리소스

- **API 키 발급**: https://platform.claude.com/settings/keys
- **OpenAI 호환 문서**: https://platform.claude.com/docs/en/api/openai-sdk
- **모델 목록**: https://platform.claude.com/docs/en/docs/about-claude/models/all-models
- **네이티브 SDK**: https://platform.claude.com/docs/en/api/client-sdks

---

*문서 수집일: 2026-03-25 | 출처: Anthropic 공식 문서*
