from bs4 import BeautifulSoup
import json
import re

def _flatten_json(data, parent_key="", result=None):
    """
    Helper to flatten JSON data (dicts/lists) into a string by extracting textual/numeric values.
    """
    if result is None:
        result = []
    if isinstance(data, dict):
        for key, value in data.items():
            # Skip keys that are not content (e.g., metadata keys starting with '@')
            if str(key).startswith("@"):
                continue
            _flatten_json(value, key, result)
    elif isinstance(data, list):
        for item in data:
            _flatten_json(item, parent_key, result)
    else:
        # If it's a primitive type (str, int, float), add it
        if isinstance(data, (str, int, float)):
            text = str(data)
            # Filter out very short or non-informative strings (like empty or just special chars)
            if len(text.strip()) > 0:
                result.append(text.strip())
    return result

def extract_content(html: str, query: str = None):
    soup = BeautifulSoup(html, "lxml")
    content = {}

    title_tag = soup.find('title')
    content["title"] = title_tag.get_text().strip() if title_tag else ""

    desc_tag = soup.find('meta', attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        content["meta_description"] = desc_tag["content"].strip()
    else:
        content["meta_description"] = ""

    hidden_text_parts = []
    for script in soup.find_all("script"):
        script_type = script.get("type", "")
        script_text = script.string

        if script_text:
            script_text = script_text.strip()
        else:
            script_text = ""

        if script_type.lower().endswith("json") or script_text.startswith("{"):
            try:
                data = json.loads(script_text)
            except Exception:
                data = None
            if data:
                flat_values = _flatten_json(data)
                if flat_values:
                    hidden_text_parts.append(" ".join(flat_values))

    content["hidden_text"] = " ".join(hidden_text_parts)

    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.decompose()

    visible_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in visible_text.splitlines()]
    lines = [line for line in lines if line and not re.match(r'^[A-Za-z0-9\W]{1,15}$', line)]
    main_text = "\n".join(lines)

    content["text"] = main_text.strip()
    return content
