import pytest

from app.tools.privacy_filter import (
    assert_public_output_is_safe,
    find_public_output_safety_flags,
)


def test_privacy_filter_allows_synthetic_ids() -> None:
    assert find_public_output_safety_flags("Learner L-1001 from TEAM-A uses EMP-001.") == []


def test_privacy_filter_flags_email_and_secret_terms() -> None:
    flags = find_public_output_safety_flags("Contact test@example.com with api_key value.")

    assert "email-like value" in flags
    assert "secret-like label" in flags


def test_assert_public_output_is_safe_raises_for_public_output_risk() -> None:
    with pytest.raises(ValueError, match="disallowed"):
        assert_public_output_is_safe("password should not appear in public output")
