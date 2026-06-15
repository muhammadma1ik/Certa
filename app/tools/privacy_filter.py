import re


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b")
SECRET_HINT_PATTERN = re.compile(
    r"\b(api[_-]?key|client[_-]?secret|connection[_-]?string|password|token)\b",
    re.IGNORECASE,
)


def find_public_output_safety_flags(text: str) -> list[str]:
    """
    Return lightweight safety flags for content that should not appear in public outputs.
    """
    flags: list[str] = []

    if EMAIL_PATTERN.search(text):
        flags.append("email-like value")

    if PHONE_PATTERN.search(text):
        flags.append("phone-like value")

    if SECRET_HINT_PATTERN.search(text):
        flags.append("secret-like label")

    return flags


def assert_public_output_is_safe(text: str) -> None:
    flags = find_public_output_safety_flags(text)

    if flags:
        raise ValueError(f"Public output contains disallowed patterns: {', '.join(flags)}")
