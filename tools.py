import os
import json
from langchain_core.tools import tool
from tavily import TavilyClient
from langchain_groq import ChatGroq


@tool
def search_company(query: str) -> str:
    """Search the web for real-time information about a company or industry. Call this whenever a company name is mentioned."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    try:
        results = client.search(query=query, max_results=3)
        chunks = []
        for r in results.get("results", []):
            chunks.append(f"Title: {r['title']}\nContent: {r['content']}\nURL: {r['url']}")
        return "\n\n---\n\n".join(chunks) if chunks else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def score_lead(
    company_name: str,
    industry: str,
    company_size: str,
    pain_points: str,
    budget_range: str,
    urgency: str,
) -> str:
    """Score a prospect lead 1-10. Call this after collecting company size, pain points, budget, and urgency signals."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    prompt = f"""You are a B2B sales qualification expert. Score this lead and return ONLY valid JSON — no markdown, no explanation.

Company: {company_name}
Industry: {industry}
Size: {company_size}
Pain Points: {pain_points}
Budget Range: {budget_range}
Urgency: {urgency}

Scoring guide:
- Hot (8-10): clear pain points, right industry, signals of urgency or budget
- Warm (5-7): good fit but missing some signals
- Cold (1-4): poor fit or very low urgency

Return exactly this structure:
{{
  "score": <integer 1-10>,
  "tier": "<Hot|Warm|Cold>",
  "reasoning": "<2-3 confident sentences explaining the score based on the data above — do NOT say 'more information needed'>",
  "recommended_next_step": "<one specific, actionable next step>"
}}"""
    return llm.invoke(prompt).content


@tool
def generate_outreach_email(
    company_name: str,
    contact_name: str,
    pain_points: str,
    company_context: str,
    our_value_proposition: str,
) -> str:
    """Generate a hyper-personalized cold outreach email. Call this after scoring the lead."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    prompt = f"""Write a B2B cold outreach email using this EXACT format — no exceptions:

Subject: [subject line here]

Dear {contact_name},

[Opening line — one specific fact about the company as a hook]

[1-2 sentences connecting their pain points to a concrete outcome we deliver]

[Single CTA: propose a 15-minute discovery call]

Best regards,
[Your Name]
AI Automation Agency

---
Rules:
- Under 150 words total
- Sound human — no buzzwords like "synergy", "leverage", or "innovative solutions"
- Each section must be on its own line with a blank line between paragraphs

Company: {company_name}
Contact: {contact_name}
Pain Points: {pain_points}
Company Context: {company_context}
Our Value Prop: {our_value_proposition}

Write ONLY the email in the exact format above."""
    return llm.invoke(prompt).content
