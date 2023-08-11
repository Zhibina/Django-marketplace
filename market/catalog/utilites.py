from transliterate import detect_language, translit


def get_slug(name: str) -> str:
    """Возвращает строку slug."""

    slug: str = name if " " not in name else "-".join(name.split())
    if detect_language(slug) == "ru":
        slug = translit(slug, reversed=True)
    return slug
