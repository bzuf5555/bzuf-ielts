# BZUF IELTS Bot - Claude Code Rules

## Project Overview
IELTS Writing & Speaking assistant Telegram bot. Users send English essays or voice messages; the bot analyzes them against official IELTS band descriptors and returns detailed feedback in Uzbek.

## Strict Rules

### Language Rules
- Bot responses: ALWAYS in Uzbek language
- Error corrections: Show original English text + corrected English text
- Technical comments in code: English
- Variable/function names: English (snake_case)
- User-facing strings: Uzbek only

### Scope Rules
- ONLY IELTS — never mention CEFR, TOEFL, Cambridge, Duolingo, or any other certification
- ONLY Writing (Task 1 & Task 2) and Speaking — no Reading, Listening, or other modules
- Band scores ALWAYS on 0-9 scale in 0.5 increments (0, 0.5, 1.0, ..., 9.0)
- Writing criteria: Task Achievement/Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy
- Speaking criteria: Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation

### Cost Rules
- ZERO paid services — everything must use free tiers
- Groq API: free tier (no payment required) — console.groq.com
- MongoDB Atlas: free tier M0 (512MB)
- Render: free tier
- No OpenAI, no paid Anthropic API calls in production bot

### Code Quality Rules
- All async functions use `async/await`
- All database operations are async (motor)
- Pydantic v2 models for all data structures
- Structured JSON output from LLM (response_format=json_object) for reliable parsing
- Comprehensive error handling — bot never crashes on bad input
- All sensitive data in environment variables (never hardcode)
- tenacity for retry logic on Groq API calls

### Architecture Rules
- RouterAgent decides which Groq model to use based on task complexity (token-saving):
  - Simple (text < 200 words, short speaking): `llama3-8b-8192` (fastest)
  - Medium (200-400 words): `llama-3.1-70b-versatile`
  - Complex (400+ words or Task 2 essay): `llama-3.3-70b-versatile` (best quality)
- WritingAgent handles Task 1 and Task 2 with different prompts and criteria
- SpeakingAgent processes transcripts from Groq Whisper
- MongoDB stores all submissions for history/stats tracking

### File Organization
- task.md: ALL planned tasks go here first
- done.md: Move tasks here ONLY after fully complete and tested
- Never mix IELTS-only logic with general English learning features
- Never add Reading or Listening analysis

### Deployment Rules
- Webhook mode on Render (not polling)
- Health check endpoint at /health for UptimeRobot keep-alive
- Environment variables set in Render dashboard
- render.yaml defines service configuration
- Development: polling mode (ENVIRONMENT=development)

### Testing Rules
- Test with real IELTS sample essays before declaring complete
- Verify band scores are realistic (not all 9.0 or all 1.0)
- Test voice message processing end-to-end
- Test with 50-word, 150-word, and 350-word essays
- Verify all bot responses are in Uzbek
