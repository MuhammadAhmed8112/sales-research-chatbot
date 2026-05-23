---
title: AI Sales Research Agent
emoji: 🎯
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: 1.45.1
app_file: app.py
pinned: false
license: mit
---

# 🎯 AI Sales Research Agent

An agentic B2B sales qualification tool that researches prospects in real-time, scores leads, and generates personalized outreach emails — all in one conversation.

## What It Does

1. **Real-time research** — searches the web for company news, size, and context using Tavily
2. **Smart qualification** — asks targeted questions to collect lead data naturally
3. **Lead scoring** — rates prospects 1–10 with tier (Hot / Warm / Cold) and reasoning
4. **Personalized outreach** — generates a hyper-specific email referencing real company facts

## Stack

| Layer | Tool |
|-------|------|
| LLM | Groq — Llama 3.3 70B (free tier) |
| Agent | LangGraph ReAct agent |
| Web search | Tavily API (free tier) |
| UI | Streamlit |
| Deploy | HuggingFace Spaces (free) |

## Local Setup

```bash
git clone https://github.com/MuhammadAhmed8112/sales-research-chatbot
cd sales-research-chatbot
pip install -r requirements.txt
cp .env.example .env   # add your keys
streamlit run app.py
```

## Environment Variables

| Variable | Where to get it |
|----------|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) — free |

## HuggingFace Spaces Deployment

Add `GROQ_API_KEY` and `TAVILY_API_KEY` as Secrets in your Space settings — no code changes needed.
