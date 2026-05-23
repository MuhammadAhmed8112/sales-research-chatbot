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

Return exactly this structure:
{{
  "score": <integer 1-10>,
  "tier": "<Hot|Warm|Cold>",
  "reasoning": "<2-3 sentences>",
  "recommended_next_step": "<one specific action>"
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
    prompt = f"""Write a B2B cold outreach email. Rules:
- Open with a specific hook referencing a real fact about the company
- Connect their pain points to a concrete outcome we deliver
- Single CTA: 15-minute discovery call
- Under 150 words
- Sound human — no buzzwords like "synergy" or "leverage"

Company: {company_name}
Contact: {contact_name}
Pain Points: {pain_points}
Company Context: {company_context}
Our Value Prop: {our_value_proposition}

Write ONLY the email. First line = Subject line. Then the body."""
    return llm.invoke(prompt).content
