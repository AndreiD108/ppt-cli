"""Tests for the guidelines command."""


def test_guidelines_no_subcommand_shows_overview(cli):
    rc, out, _ = cli("guidelines")
    assert rc == 0
    assert "ppt-cli guidelines design" in out
    assert "ppt-cli guidelines image-gen" in out
    assert "Start with 'design'" in out


def test_guidelines_design(cli):
    rc, out, _ = cli("guidelines", "design")
    assert rc == 0
    assert "Design Guidelines" in out
    assert "Color Palette" in out
    assert "Typography" in out
    assert "ppt-cli" in out


def test_guidelines_image_gen(cli):
    rc, out, _ = cli("guidelines", "image-gen")
    assert rc == 0
    assert "Image Prompting Tips" in out
    assert "Prompt Structure" in out
    assert "Style Modifiers" in out
    assert "ppt-cli" in out
