# chat_prompt.py

from typing import Callable


def get_keyword_prompt(data: str) -> str:
    """
    Generates a prompt for extracting keywords in comma-separated format.
    """
    return f"""Extract the most relevant keywords from the following text.
Avoid stopwords and focus on nouns, proper nouns, and key phrases that represent the core ideas.
Return the keywords as a comma-separated list only (no bullets, no numbering).

Text:
\"\"\"{data}\"\"\"

Keywords (comma-separated):"""



def get_summary_prompt(data: str) -> str:
    """
    Generates a prompt for summarizing the given text.
    """
    return f"""Summarize the following text in a concise and clear manner. 
Preserve the main ideas and key points without copying exact sentences.

Text:
\"\"\"{data}\"\"\"

Summary:"""


def get_prompt(task_type: str) -> Callable[[str], str]:
    """
    Factory function that returns the appropriate prompt-generating function 
    based on the task type.

    Args:
        task_type (str): Task identifier ("keyword" for keywords, "summary" for summary)

    Returns:
        Callable[[str], str]: A function that takes a string and returns a prompt.

    Raises:
        ValueError: If the task type is unknown.
    """
    task_map = {
        "keyword": get_keyword_prompt,
        "summary": get_summary_prompt,
    }

    if task_type not in task_map:
        raise ValueError(f"Unknown task type '{task_type}'. Supported types: {list(task_map.keys())}")

    return task_map[task_type]
