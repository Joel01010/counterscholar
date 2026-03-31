# CounterScholar

> An ADK agent that finds what the scientific community disagrees with in any research paper, using ArXiv via MCP.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Google ADK](https://img.shields.io/badge/google--adk-1.28%2B-orange)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

## The Problem

When engineers or students read a research paper, they have no visibility into the scientific debate around it. A 2017 paper might have been challenged or refuted by 2022. Finding counter-arguments requires hours of manual literature review. CounterScholar finds them in **5 seconds**.

---

## Architecture

```
User ──► ADK Web UI ──► Agent (Gemini 2.5 Flash / Vertex AI)
                              │
                              ▼ stdio subprocess
                        MCP Server (FastMCP)
                              │
                              ▼ HTTPS
                        ArXiv Public API (free, no key needed)
```

> **Key design choice:** The MCP server runs as a local stdio subprocess inside the same container — no second service needed. This halves infrastructure cost.

---

## Project Structure

```
counterscholar/            ← repo root
├── counterscholar/        ← ADK agent package
│   ├── __init__.py        ← exposes root_agent
│   └── agent.py           ← Agent definition + McpToolset config
├── mcp_server.py          ← FastMCP server exposing find_counter_papers
├── requirements.txt       ← pinned dependencies
├── .env                   ← MODEL env var (git-ignored)
└── .gitignore
```

---

## How It Works

1. User enters a paper title (e.g. *"Attention Is All You Need"*)
2. The ADK agent calls the `find_counter_papers` MCP tool
3. The MCP server queries ArXiv for papers containing counter-argument signal words (`refute`, `contradict`, `challenge`, `limitation`, `critique`, etc.) combined with the paper title
4. Structured results (title, authors, abstract excerpt, URL, year) are returned to the agent
5. Gemini 2.5 Flash synthesizes them into a structured academic debate brief

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Agent Framework | Google ADK >= 1.28.0 | Agent orchestration and deployment |
| Tool Protocol | MCP (Model Context Protocol) | Standardized agent-to-tool communication |
| LLM | Gemini 2.5 Flash (Vertex AI) | Response generation and synthesis |
| Data Source | ArXiv Public API | Academic paper metadata (free, no key needed) |
| MCP Server | FastMCP (Python) | Exposes `find_counter_papers` tool |
| Deployment | Google Cloud Run | Serverless container hosting |

---

## Prerequisites

- Python 3.11+
- Google Cloud SDK (`gcloud`) installed and authenticated
- A GCP project with **Vertex AI API** enabled

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/Joel01010/counterscholar.git
cd counterscholar
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Authenticate with GCP

```bash
export GOOGLE_CLOUD_PROJECT=<your-project-id>
gcloud auth application-default login
```

### 4. Create a `.env` file

```bash
echo "MODEL=gemini-2.5-flash" > .env
```

### 5. Run the agent

```bash
adk web .
```

Open **http://localhost:8000** and select `counterscholar` from the agent dropdown.

> **Cloud Shell users** — use this instead to enable web preview:
> ```bash
> adk web --allow_origins 'regex:https://.*\.cloudshell\.dev'
> ```

---

## Deployment to Cloud Run

### 1. Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com
```

### 2. Create a service account

```bash
export PROJECT_ID=$(gcloud config get-value project)
export SA_NAME=counterscholar-sa
export SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

gcloud iam service-accounts create $SA_NAME \
  --display-name="CounterScholar Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/aiplatform.user"
```

### 3. Deploy

```bash
adk deploy cloudrun \
  --project=$PROJECT_ID \
  --region=asia-south1 \
  --service-name=counterscholar \
  --with-ui \
  --service-account=$SERVICE_ACCOUNT \
  . -- \
  --memory=512Mi \
  --min-instances=0 \
  --max-instances=3
```

### 4. Get the deployed URL

```bash
gcloud run services describe counterscholar \
  --region=asia-south1 \
  --format="value(status.url)"
```

---

## Example Queries

Try these in the web UI:

1. *"Find counter-arguments to Attention Is All You Need by Vaswani et al. 2017"*
2. *"What does the scientific community disagree with in BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding?"*
3. *"Challenge the paper Dropout: A Simple Way to Prevent Neural Networks from Overfitting"*

---

## Cost Optimization

- **Gemini 2.5 Flash** — significantly cheaper per token than Pro models
- **ArXiv API** — completely free, no API key required
- **`--min-instances=0`** — scales to zero when idle
- **`--memory=512Mi`** — minimum sufficient memory
- **Single container** — MCP runs as stdio subprocess, no second service

---

## License

MIT
