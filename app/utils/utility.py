def get_keywords_as_list(keywords_text: str) -> list[str]:
    return [kw.strip() for kw in keywords_text.strip().split('\n') if kw.strip()]

def set_keywords_from_list(keywords_list: list[str]) -> str:
    return '\n'.join(keywords_list)
