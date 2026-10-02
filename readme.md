# ResumeMatch AI 🚀

**AI-Powered Resume & Job Matching System**

ResumeMatch AI is an AI-powered career intelligence platform that analyzes a candidate's resume against a job description using **document processing, embeddings, semantic similarity, and Large Language Models (LLMs)**.

It identifies matching skills, partially matching skills, missing skills, relevant experience, and provides personalized recommendations for improving the resume.

---

## 🎯 Project Overview

Traditional resume screening systems often depend heavily on keyword matching.

For example:

**Resume:**

> Developed RESTful APIs using FastAPI.

**Job Description:**

> Experience building backend APIs.

A keyword-based system may not recognize these statements as strongly related because the exact words are different.

ResumeMatch AI uses **semantic embeddings and similarity analysis** to understand the relationship between the resume and job requirements.

---

## ✨ Key Features

### MVP

* 📄 Upload Resume PDF
* 📋 Paste Job Description
* 📑 Upload Job Description PDF
* 🔍 Extract text from documents
* 🧩 Identify resume sections
* 🎯 Extract job requirements
* 🧠 Generate embeddings
* 🔗 Calculate semantic similarity
* 📊 Generate explainable match score
* ✅ Identify strong matches
* 🟡 Identify partial matches
* ❌ Identify missing skills
* 💡 Generate improvement recommendations
* 🔎 Provide evidence for matching decisions
* 🤖 Generate structured LLM analysis

---

## 🏗️ System Architecture

```text
                    Resume PDF
                        │
                        ▼
                Text Extraction
                        │
                        ▼
                  Text Chunking
                        │
                        ▼
                Resume Sections
                        │
                        ▼
                    Embeddings
                        │
                        │
                        ▼
                  Resume Vectors
                        │
                        │
                        ├──────────────┐
                        │              │
                        │              │
                        ▼              ▼
                  Similarity       Job Description
                   Analysis             │
                        │                ▼
                        │          Requirements
                        │                │
                        │                ▼
                        │            Embeddings
                        │                │
                        └───────┬────────┘
                                ▼
                       Match Score Engine
                                │
                                ▼
                              LLM
                                │
                                ▼
                    Structured JSON Output
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
        Strong Matches      Missing Skills    Recommendations
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                            Frontend
```

---

## 🔄 How It Works

### 1. Resume Upload

The user uploads a resume in PDF format.

```text
Vamsi_Krishna_Resume.pdf
```

The system extracts the text from the document.

---

### 2. Job Description

The user can either:

* Paste a job description
* Upload a Job Description PDF

Example:

```text
Required Skills:

Python
SQL
Machine Learning
AWS
Docker

Preferred Skills:

FastAPI
React
Git
```

---

### 3. Information Extraction

The system identifies important information from the resume:

```text
Skills
Experience
Projects
Education
Certifications
Programming Languages
Frameworks
Tools
```

The job description is also processed to identify:

```text
Required Skills
Preferred Skills
Experience Requirements
Technical Requirements
```

---

### 4. Embedding Generation

Resume sections and job requirements are converted into vector representations.

For example:

```text
Resume:
"Built REST APIs using FastAPI"

                ↓

          Embedding Vector


Job Description:
"Experience developing backend APIs"

                ↓

          Embedding Vector
```

The vectors can then be compared to determine semantic similarity.

---

### 5. Semantic Similarity

Resume information is compared with job requirements using similarity metrics such as **cosine similarity**.

Example:

```text
Requirement       Similarity

Python              0.94
SQL                 0.91
FastAPI             0.88
Machine Learning    0.86
AWS                 0.31
Docker              0.25
```

The system classifies requirements into:

```text
Strong Match
Partial Match
Missing
```

---

### 6. Match Score

The numerical match score is calculated using the similarity analysis rather than asking the LLM to invent a score.

Example:

```text
Overall Match Score

82%
```

The score can consider factors such as:

```text
Skill Match
Experience Match
Project Relevance
Required Skill Coverage
Preferred Skill Coverage
```

---

### 7. LLM Analysis

The structured similarity results are provided to the LLM.

The LLM generates:

* Matching skills
* Missing skills
* Partial matches
* Relevant projects
* Evidence
* Recommendations

The model is instructed **not to invent candidate skills or experience**.

---

## 🛡️ Hallucination Control

ResumeMatch AI follows an evidence-based approach.

The LLM should never claim:

```text
❌ Candidate has AWS experience
```

unless the resume provides supporting evidence.

The analysis follows the principle:

```text
Only use information explicitly present
in the resume or clearly supported by
the semantic analysis.
```

This improves the reliability and explainability of the system.

---

## 📊 Explainable Match Score

Instead of displaying only:

```text
82%
```

ResumeMatch AI provides an explanation.

Example:

```text
Python
Match: 95%

Evidence:
"Developed machine learning models using Python..."
```

```text
AWS
Match: 20%

Evidence:
"No direct AWS experience found."
```

This makes the score easier for candidates to understand and trust.

---

## 📤 Example Output

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        RESUME MATCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Match

82%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strong Matches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Python
✓ SQL
✓ Machine Learning
✓ FastAPI
✓ Git

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Partial Matches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◐ Cloud
◐ React

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Missing Skills
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✗ AWS
✗ Docker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Relevant Experience
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SmartSeat Project

• Python
• FastAPI
• REST APIs
• Database

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Add Docker experience
2. Learn basic AWS services
3. Highlight FastAPI experience
```

---

## 🧱 Structured JSON

The LLM output is designed to follow a structured format.

```json
{
  "match_score": 82,
  "strong_matches": [
    "Python",
    "SQL",
    "Machine Learning",
    "FastAPI"
  ],
  "partial_matches": [
    "Cloud",
    "React"
  ],
  "missing_skills": [
    "AWS",
    "Docker"
  ],
  "relevant_projects": [
    "SmartSeat"
  ],
  "recommendations": [
    "Add Docker experience",
    "Learn basic AWS services",
    "Highlight FastAPI experience"
  ]
}
```

Structured output makes it easier for the backend to validate the response and allows the frontend to display the information consistently.

---

## 🖥️ User Interface

```text
┌──────────────────────────────────────────────┐
│              ResumeMatch AI                  │
│       AI-Powered Career Intelligence         │
├──────────────────────────────────────────────┤
│                                              │
│ Resume                 Job Description       │
│                                              │
│ ┌───────────────┐      ┌───────────────┐     │
│ │ Upload Resume │      │ Paste / Upload│     │
│ └───────────────┘      └───────────────┘     │
│                                              │
│              [ Analyze Resume ]              │
│                                              │
├──────────────────────────────────────────────┤
│                                              │
│             MATCH SCORE: 82%                 │
│                                              │
│ ✓ Strong Matches                             │
│ Python • SQL • ML • FastAPI                  │
│                                              │
│ ◐ Partial Matches                            │
│ Cloud • React                                │
│                                              │
│ ✗ Missing                                    │
│ AWS • Docker                                 │
│                                              │
│ Recommendations                              │
│ ...                                          │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

* React.js
* JavaScript
* HTML
* CSS

### Backend

* Python
* FastAPI
* Pydantic

### AI / ML

* Embeddings
* Semantic Similarity
* Cosine Similarity
* Large Language Models (LLMs)

### Document Processing

* PDF text extraction
* Text chunking
* Resume section extraction

### Database

* PostgreSQL
* SQLAlchemy

### Development Tools

* Git
* GitHub
* VS Code

---

## 📁 Planned Project Structure

```text
resume-match-ai/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── embeddings/
│   │   ├── scoring/
│   │   └── llm/
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   │
│   └── package.json
│
├── data/
│
├── README.md
├── .gitignore
└── LICENSE
```

---

## 🚀 Development Roadmap

### Phase 1 — Foundation

* [ ] Create FastAPI backend
* [ ] Create React frontend
* [ ] Implement PDF upload
* [ ] Implement text extraction
* [ ] Create basic API structure

### Phase 2 — Resume & JD Processing

* [ ] Resume section extraction
* [ ] Job requirement extraction
* [ ] Skill identification
* [ ] Text chunking

### Phase 3 — Semantic Matching

* [ ] Integrate embedding model
* [ ] Generate resume embeddings
* [ ] Generate JD requirement embeddings
* [ ] Implement cosine similarity
* [ ] Build match classification

### Phase 4 — AI Analysis

* [ ] Integrate LLM
* [ ] Design analysis prompt
* [ ] Implement structured JSON output
* [ ] Add hallucination protection
* [ ] Generate recommendations

### Phase 5 — Explainability

* [ ] Add evidence snippets
* [ ] Explain match score
* [ ] Show requirement-level scores
* [ ] Add skill-gap visualization

### Phase 6 — Production

* [ ] PostgreSQL integration
* [ ] Authentication
* [ ] Analysis history
* [ ] Error handling
* [ ] API validation
* [ ] Deployment

---

## 🔮 Future Features

### Version 2

* Multiple job descriptions
* Resume comparison
* Skill-gap visualization
* Section-level scoring
* Evidence snippets
* Analysis history

### Version 3

* Advanced RAG-based resume analysis
* LangChain integration
* Better structured outputs
* Resume improvement assistant
* Downloadable analysis reports
* Job recommendation system

---

## 🎓 Learning Objectives

This project provides practical experience with:

* Document processing
* Embeddings
* Vector representations
* Semantic similarity
* Cosine similarity
* Prompt engineering
* Structured LLM outputs
* Hallucination control
* Explainable AI
* FastAPI
* React
* PostgreSQL
* AI application architecture

---

## 📌 Resume Description

> **ResumeMatch AI — AI-Powered Resume & Job Matching System**
> Developed an AI-powered resume analysis platform that uses embeddings and semantic similarity to compare resumes with job descriptions and an LLM to generate structured skill-gap analysis, match scores, evidence, and personalized recommendations.

**Only include technologies and features in the resume that are actually implemented in the final project.**

---

## 👨‍💻 Author

**Vamsi Krishna**

Computer Science & Mathematics — AI/ML

---

## ⭐ Project Goal

ResumeMatch AI aims to make resume screening more **semantic, explainable, and useful for candidates** by combining traditional document processing with modern AI techniques.

```text
Resume + Job Description
          ↓
    Document Analysis
          ↓
      Embeddings
          ↓
 Semantic Similarity
          ↓
   Explainable Score
          ↓
       LLM Analysis
          ↓
   Career Insights
```

---

## 📄 License

This project is intended for educational and portfolio purposes.

### Phase 6: deterministic match score engine

Phase 6 calculates an explainable overall score directly from the Phase 5 similarity response. It is deterministic and does not call an LLM, regenerate embeddings, recalculate similarity, or inspect PDFs.

The group scores are the averages of the clamped requirement-level similarities, expressed as percentages:

```text
overall = required_score * required_weight
        + preferred_score * preferred_weight
```

The configurable default weights are `0.80` for required requirements and `0.20` for preferred requirements. If only one group exists, that group is normalized to 100% of the score; an absent preferred section therefore does not reduce the score. An input with no requirements returns a clear error.

The score is returned on a `0-100` scale, with the overall value rounded to one decimal place. Initial interpretation bands are: `90-100 Excellent Match`, `75-89.9 Strong Match`, `60-74.9 Moderate Match`, `40-59.9 Weak Match`, and `0-39.9 Low Match`. These are product interpretation bands, not scientifically validated hiring thresholds.

Endpoint: `POST /api/score/analyze`. It accepts the Phase 5 `SimilarityResponse` and returns the overall, required, and preferred scores; configured weights; requirement totals; and strong, partial, and missing counts. The result represents semantic alignment between the supplied resume and job description. It is not hiring probability, an ATS guarantee, a candidate quality score, or an employment prediction.

### Phase 7: LLM analysis and structured JSON

Phase 7 adds an optional backend-only LLM analysis layer. The LLM explains strong and partial matches, identifies missing requirements, selects supplied resume projects, and produces grounded recommendations and a concise summary. It does not calculate similarity or the numerical match score.

`POST /api/analysis/generate` accepts the typed Phase 3 resume and job-description data, Phase 5 similarity results, and the Phase 6 deterministic score. The response separates the authoritative `score` object from the validated `analysis` object. Any score returned by an LLM is ignored.

The provider is isolated behind `llm_service.py` and uses an OpenAI-compatible chat-completions API. Configure it through `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`, and optionally `LLM_BASE_URL`. The API key is never sent to the frontend or committed to the repository.

Prompts delimit resume, job-description, and match-result data as untrusted document content. Pydantic validation and business rules reject malformed output, changed similarity values, unsupported skills, and invented projects. Tests use deterministic provider mocks and never call a real LLM.

The LLM provides career analysis only; the deterministic score represents semantic alignment and is not hiring probability, an ATS guarantee, or an employment prediction.

### Phase 8: evidence verification and hallucination control

Phase 8 verifies Phase 7 output against authoritative Phase 3 resume/JD data, Phase 5 similarity results, and the Phase 6 deterministic score. The LLM generates analysis, but deterministic application data remains authoritative.

Endpoint: `POST /api/analysis/verify`. It returns verified evidence with source type, page number when available, confidence, and an explicit `verified`, `corrected`, or `rejected` status. Similarity values, categories, missing skills, projects, recommendations, and summaries are checked independently. A validation summary reports total, verified, corrected, and rejected claims.

Evidence matching normalizes whitespace, capitalization, punctuation, and harmless wording differences. Unsupported facts, invented skills/projects, fake page references, and recommendations that assert unsupported experience are rejected or corrected using authoritative data. Resume and JD content remains untrusted data and never changes validation rules.

This is deterministic validation, not a complete natural-language fact checker. It may reject nuanced but valid paraphrases and does not prove that extracted source data itself is correct.

### Phase 9: React analysis dashboard

Phase 9 adds the responsive React/Vite dashboard for the complete analysis flow. It provides PDF upload cards, client-side validation, truthful loading and error states, deterministic score presentation, strong/partial/missing skill sections, verified evidence, relevant projects, grounded recommendations, and the evidence validation summary.

The frontend keeps API calls in `frontend/src/services/api.ts` and uses typed contracts in `frontend/src/types/analysis.ts`. A sample preview is available from the navigation so the UI can be reviewed without a backend or real documents. The real workflow calls extraction, embeddings, similarity, scoring, LLM analysis, and evidence verification in sequence; business logic remains in the backend.

Environment variable:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run the application:

```bash
# Backend
cd backend
python -m venv .venv
# Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend, in a second terminal
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend never receives or stores `LLM_API_KEY`; it communicates only with the backend. The current PDF workflow requires both a resume PDF and a job-description PDF.

Screenshots: to be added after deployment or a local browser capture.

### Phase 10: end-to-end integration

The production workflow is exposed through one multipart endpoint:

```http
POST /api/analyze
Form fields: resume, job_description
```

The pipeline processes each uploaded PDF in memory exactly once:

```text
React dashboard
    ↓
POST /api/analyze
    ↓
Document extraction
    ↓
Embeddings
    ↓
Similarity
    ↓
Deterministic score
    ↓
LLM analysis
    ↓
Evidence verification
    ↓
Verified result
    ↓
React dashboard
```

The frontend calls only `/api/analyze` for a real analysis. The orchestration service reuses the Phase 3–8 services and does not persist uploaded files. Configure `FRONTEND_ORIGIN` in the backend environment for local CORS and `VITE_API_BASE_URL` in the frontend environment for the API base URL. The frontend applies a two-minute request timeout and displays a safe user-facing error.

### Phase 12: production deployment

The deployment target is:

```text
Vercel React frontend
        ↓ HTTPS
Render FastAPI backend
        ↓
Embedding model + OpenAI-compatible LLM provider
```

Render configuration is provided in `render.yaml`. The backend uses:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Render health checks use `GET /health`. Uploaded PDFs remain in memory and are not persisted. The embedding model is loaded lazily and cached for the backend process; the first analysis after a cold start may take longer while model files are obtained.

Required Render environment variables:

```text
LLM_API_KEY=<provider secret; Render only>
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
LLM_TIMEOUT_SECONDS=30
FRONTEND_ORIGIN=https://<your-vercel-domain>
MAX_PDF_SIZE_MB=10
```

For Vercel, set `VITE_API_BASE_URL` to the deployed Render HTTPS URL. Do not add `LLM_API_KEY` to Vercel or any `VITE_*` variable. The Vercel build uses `npm run build` and publishes `dist`; `frontend/vercel.json` contains the SPA configuration.

Local development continues to use `FRONTEND_ORIGIN=http://localhost:5173` and `VITE_API_BASE_URL=http://127.0.0.1:8000`. Copy the example environment files rather than committing `.env` files.

Deployment limitations include Render cold starts, CPU/RAM constraints during sentence-transformers model loading, LLM provider cost and rate limits, request timeouts, and large-PDF processing time. A real production deployment and real-document LLM test require access to the Render/Vercel accounts and a configured provider key; no external deployment was performed in this workspace.

### Phase 11: testing and hardening

Phase 11 adds regression coverage for upload validation, safe API errors, CORS restrictions, path-traversal filenames, HTML document content, pipeline stage failures, deterministic score authority, and malformed backend responses. Uploaded files are read and processed in memory; filenames are never used as filesystem paths.

Run the backend tests with:

```bash
cd backend
pytest tests -p no:cacheprovider
```

Build the frontend with:

```bash
cd frontend
npm run build
```

For a local end-to-end check, configure `LLM_API_KEY`, start the backend with `uvicorn app.main:app --reload`, start the frontend with `npm run dev`, upload a resume PDF and job-description PDF, and confirm the verified score, matches, evidence, projects, recommendations, and validation summary. If no LLM provider is configured, the API fails safely rather than substituting fake production analysis.

Security notes: `.env` files are ignored, only `.env.example` files are tracked, CORS is restricted to `FRONTEND_ORIGIN`, LLM credentials remain backend-only, provider errors do not expose credentials, and document text is treated as untrusted data. Swagger documentation is available at `/docs`, including `POST /api/analyze`.

Known limitations remain: OCR is not implemented, the local embedding model must be available, the LLM provider is required for real analysis, and deterministic evidence checks are conservative rather than a complete fact checker.

## Phase 1 setup

The current Phase 1 implementation includes a minimal FastAPI backend and React frontend.

### Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health` and returns `{"status":"ok"}`.

### Phase 2: PDF extraction

The backend accepts a PDF in memory, validates it with PyMuPDF, extracts text page by page, cleans excessive whitespace, and returns both complete text and numbered page text. Image-only/scanned PDFs return a clear error because OCR is not implemented yet. The default maximum upload size is 10 MB and can be changed with `MAX_PDF_SIZE_MB`.

Endpoint: `POST /api/documents/extract` (multipart field: `file`).

```bash
curl -X POST http://127.0.0.1:8000/api/documents/extract -F "file=@resume.pdf"
```

Example response:

```json
{
  "filename": "resume.pdf",
  "page_count": 2,
  "text": "Jane Doe\nPython Developer\n\nExperience...",
  "pages": [
    {"page_number": 1, "text": "Jane Doe\nPython Developer"},
    {"page_number": 2, "text": "Experience..."}
  ]
}
```

Run backend tests with:

```bash
cd backend
pytest
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` requests to the backend. PDF processing, embeddings, similarity, LLM integration, authentication, and persistence are intentionally deferred.

### Phase 3: structured extraction

Phase 3 adds deterministic, rule-based extraction from PDF text. It detects common section headings, normalizes a controlled set of skills, removes duplicates, and preserves source page/text for resume entries. Phase 3 uses deterministic extraction and does not use an LLM.

Endpoints:

```text
POST /api/resume/extract
POST /api/job-description/extract
```

Both accept one PDF in the multipart `file` field:

```bash
curl -X POST http://127.0.0.1:8000/api/resume/extract -F "file=@resume.pdf"
curl -X POST http://127.0.0.1:8000/api/job-description/extract -F "file=@job-description.pdf"
```

Example resume response:

```json
{
  "text": "Skills\nPython\nExperience\nBackend Developer",
  "skills": ["Python"],
  "programming_languages": ["Python"],
  "frameworks": [],
  "libraries": [],
  "tools": [],
  "databases": [],
  "cloud": [],
  "experience": [{"text": "Backend Developer", "page_number": 1, "source_text": "...", "role": null, "company": null, "duration": null}],
  "projects": [],
  "education": [],
  "certifications": []
}
```

Limitations: extraction is conservative and supports common headings plus a fixed skill vocabulary. It does not perform OCR, semantic inference, embeddings, matching, or LLM analysis. Plain-text JD input is not enabled yet; PDF input is supported.

### Phase 4: embeddings

Phase 4 converts meaningful Phase 3 resume and job-description units into local semantic embeddings using `all-MiniLM-L6-v2`. The model produces normalized vectors with dimension 384 and is loaded lazily once per application process. Resume skills, experience, and projects are represented separately; JD required/preferred skills, responsibilities, and experience requirements are also separate units.

Endpoint:

```http
POST /api/embeddings/generate
```

Example request:

```json
{
  "resume": {
    "skills": ["Python", "FastAPI"],
    "experience": [{"text": "Built REST APIs using FastAPI"}],
    "projects": []
  }
}
```

Example response structure:

```json
{
  "model": "all-MiniLM-L6-v2",
  "dimension": 384,
  "items": [
    {"source_type": "resume_skill", "text": "Python", "embedding": [0.01, 0.02]}
  ]
}
```

The actual embedding array contains 384 values. Phase 4 generates semantic embeddings. Similarity calculation is implemented in Phase 5. No API key is required, but the model package and model files must be available locally. Empty or duplicate units are removed, and empty documents are rejected.

### Phase 5: similarity engine

The similarity engine compares each required and preferred JD embedding against all resume embedding units using cosine similarity, retaining only the best resume match for each requirement. It preserves requirement type, matched text, source type, and page number.

Endpoint:

```http
POST /api/similarity/analyze
```

The request contains already-generated embedding units and does not regenerate embeddings:

```json
{
  "resume_items": [{"text": "Python", "source_type": "resume_skill", "embedding": [1, 0]}],
  "required_items": [{"text": "Python", "source_type": "jd_required", "embedding": [1, 0]}],
  "preferred_items": []
}
```

Categories use configurable initial thresholds: strong `>= 0.80`, partial `0.55–<0.80`, and missing `< 0.55`. These are engineering defaults, not scientifically validated thresholds. Phase 5 calculates requirement-level semantic similarity. Overall resume match scoring is implemented in Phase 6.
