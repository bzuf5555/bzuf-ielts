# BZUF IELTS Bot - Task Tracker

## Status Legend
- [ ] Planned
- [~] In Progress
- [x] Done (move to done.md)

---

## Phase 1: Project Setup
- [ ] Create project directory structure
- [ ] Setup requirements.txt with all dependencies
- [ ] Create .env.example with all required env vars
- [ ] Create render.yaml for Render deployment
- [ ] Setup .gitignore
- [ ] Create CLAUDE.md with project rules

## Phase 2: Data Models (Pydantic v2)
- [ ] UserModel (telegram_id, username, created_at, submission_count, averages)
- [ ] SubmissionModel (user_id, type, text, feedback, band_score, timestamp)
- [ ] WritingFeedbackModel (4 criteria scores, errors list, corrected text, suggestions)
- [ ] SpeakingFeedbackModel (4 criteria scores, errors list, transcript, corrected transcript)
- [ ] ErrorItemModel (original, corrected, error_type, explanation_uz)

## Phase 3: Services
- [ ] MongoDBService: async CRUD for users and submissions, rate limiting
- [ ] GroqService: LLM completions with JSON output + retry logic
- [ ] STTService: Voice message download + Groq Whisper transcription

## Phase 4: AI Agents
- [ ] BaseAgent: shared validation, error parsing, safe string helpers
- [ ] RouterAgent: complexity assessment → model selection (token-saving)
- [ ] WritingAgent: Task 1 / Task 2 IELTS analysis with band scoring
- [ ] SpeakingAgent: Speaking analysis from Whisper transcript

## Phase 5: IELTS Prompts
- [ ] Writing Task 1 analysis prompt (graph/chart/process/map/letter)
- [ ] Writing Task 2 analysis prompt (opinion/argument/discussion essay)
- [ ] Speaking analysis prompt (fluency/lexical/grammar/pronunciation)
- [ ] System role prompts with official IELTS band descriptors

## Phase 6: Telegram Handlers
- [ ] StartHandler: welcome message + inline keyboard in Uzbek
- [ ] WritingHandler: text + document (.txt/.docx) processing
- [ ] SpeakingHandler: voice message download, STT, analysis
- [ ] HistoryHandler: last 5 submissions with scores
- [ ] StatsHandler: user statistics (total submissions, avg scores)
- [ ] HelpHandler: detailed usage guide in Uzbek
- [ ] ErrorHandler: graceful error messages in Uzbek

## Phase 7: Response Formatters
- [ ] Writing feedback formatter (Markdown with band scores, visual bars, errors)
- [ ] Speaking feedback formatter (transcript preview + analysis)
- [ ] History formatter (compact list of past submissions)
- [ ] Stats formatter (progress visualization)

## Phase 8: Main Application
- [ ] Bot application setup with all handlers registered
- [ ] Webhook mode (production) + polling mode (development)
- [ ] Health check endpoint /health (aiohttp)
- [ ] Graceful startup and shutdown

## Phase 9: Deployment
- [ ] render.yaml configuration
- [ ] Test locally with polling (ENVIRONMENT=development)
- [ ] Push to GitHub
- [ ] Deploy to Render
- [ ] Set ENVIRONMENT=production + all env vars in Render dashboard
- [ ] Register webhook URL
- [ ] Set up UptimeRobot for /health keep-alive pinging

## Phase 10: Quality Assurance
- [ ] Test Writing Task 1 with sample academic essay (150 words)
- [ ] Test Writing Task 2 with sample essay (280 words)
- [ ] Test Speaking with sample voice message
- [ ] Test /history and /stats commands
- [ ] Test error handling (empty text, non-English, too short)
- [ ] Verify all responses are in Uzbek
- [ ] Verify band scores are accurate and realistic
- [ ] Test rate limiting (10/hour per user)
