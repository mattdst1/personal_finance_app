def clean_text_field(description: str) -> str:
    description = (
        description.replace("description:", "")
        .replace("ref.", "ref ")
        .replace("&amp;", " ")
    ).lower()
    return description
