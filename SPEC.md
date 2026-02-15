# Synthetic Respondents Bot - MVP Specification

## 1. Product Goal
Give clients a Telegram-first tool to simulate synthetic respondents and score purchase intent via SSR, returning familiar survey metrics and PDF reports.

## 2. Primary Use Cases
- Concept screening (product ideas)
- A/B message testing
- Packaging pre-tests
- Fast pre-research before human panel spend

## 3. Study Unit
- 1 question (purchase intent)
- 5-10 stimuli
- 200-300 / 500 / 1000+ synthetic respondents per stimulus
- Total typical volume: 1,500-5,000 responses

## 4. Modes
- `pilot`: 200-300 respondents/stimulus
- `standard`: 500 respondents/stimulus
- `validation`: 1000+ respondents/stimulus

## 5. Input
- Telegram text messages + file upload (`txt`, `csv`)
- CSV schema:
  - `stimulus_id` (required, unique)
  - `stimulus_text` (required)
  - `category` (optional: `product|packaging|message|other`)
  - `language` (optional: `ru|en`)

## 6. Language Behavior
- Detect input language (`ru` or `en`)
- Bot responses in same language
- Prompt templates for both languages

## 7. Segmentation (MVP)
- Adoption: `early_adopters`, `early_majority`, `late_majority`, `laggards`
- Engagement: `power_users`, `regular`, `occasional`, `new_users`
- Activity: `active`, `passive`, `dormant`

## 8. Mandatory Metrics
- Mean
- Median
- Standard Deviation
- Distribution % (1..5)
- Top-2-Box (4+5)
- Bottom-2-Box (1+2)
- Top-Box (5)

## 9. Optional Metrics
- Mode
- Net Score (`Top-Box - Bottom-Box`)
- Variance
- Confidence Intervals (mean, T2B)
- KS similarity (beta in MVP, if no human baseline)
- Test-retest reliability (post-MVP)

## 10. Telegram Commands
- `/start`
- `/new_study`
- `/upload_stimuli`
- `/set_mode`
- `/set_segments`
- `/run`
- `/status`
- `/report`
- `/history`
- `/rerun <study_id>`

## 11. Processing Pipeline
1. Parse stimuli and validate
2. Build respondent profiles from selected segments
3. Generate free-text answers via OpenRouter
4. Convert text to Likert PMFs with SSR
5. Aggregate metrics by stimulus/segment/study
6. Generate PDF
7. Save history + artifacts

## 12. Tech Stack
- Bot: `aiogram`
- API: `FastAPI`
- DB: `PostgreSQL`
- Queue: `Celery + Redis`
- Storage: local path in MVP (S3-compatible planned)
- LLM Provider: OpenRouter
- Analytics: `polars`, `numpy`, `semantic_similarity_rating`

## 13. Cost Control
- Hard cap on `max_output_tokens`
- Batch queue throttling
- Hash-based cache for repeated generation requests
- Cheap model in pilot; selective rerun with stronger model for finalists

## 14. Quality Guardrails
- Every report tagged: `Synthetic Research - Uncalibrated Beta` until calibrated
- Version all model/prompt settings in each run
- Track token usage and cost per study

