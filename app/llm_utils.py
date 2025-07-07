# app/llm_utils.py
import json, asyncio, ollama
from typing import Tuple, List

SUMMARY_PROMPT = """
You are a helpful assistant.
Provide a concise 20–30‑word summary of the following text.

<text>
{chunk}
"""

KEYWORDS_PROMPT = """
You are a helpful assistant.
Return 3‑6 concise keywords for the text below as a **single comma‑separated line**.

<text>
{chunk}
"""

def _sync_summary(chunk: str) -> str:
    """Blocking call; returns summary string."""
    res = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": SUMMARY_PROMPT.format(chunk=chunk)}],
        stream=False,
    )
    return res["message"]["content"].strip()

def _sync_keywords(chunk: str) -> str:
    res = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": KEYWORDS_PROMPT.format(chunk=chunk)}],
        stream=False,
    )
    return res["message"]["content"].strip()

async def generate_summary(chunk: str) -> str:
    """Return summary without blocking the event loop."""
    return await asyncio.to_thread(_sync_summary, chunk)

async def generate_keywords(chunk: str) -> str:
    """Return keywords without blocking the event loop."""
    return await asyncio.to_thread(_sync_keywords, chunk)


async def extract_summary_keywords(chunk: str) -> Tuple[str, List[str]]:
    """
    Run summary & keyword extraction concurrently and
    return (summary, keywords).
    """
    # Fire both tasks simultaneously
    summary_task   = asyncio.create_task(generate_summary(chunk))
    keywords_task  = asyncio.create_task(generate_keywords(chunk))

    summary  = await summary_task
    keywords = await keywords_task
    return summary, keywords
