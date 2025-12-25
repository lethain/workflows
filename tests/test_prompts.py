"""Tests for prompt loading."""

from __future__ import annotations

from pathlib import Path

from workflows.prompts import (
    Prompt,
    get_prompt_for_workflow,
    load_prompt,
    load_prompts,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Tests for frontmatter parsing."""

    def test_parse_valid_frontmatter(self) -> None:
        """Test parsing valid YAML frontmatter."""
        content = """---
name: test
description: A test prompt
version: "1.0"
---

# Content here
"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "test"
        assert frontmatter["description"] == "A test prompt"
        assert body.strip() == "# Content here"

    def test_parse_no_frontmatter(self) -> None:
        """Test parsing content without frontmatter."""
        content = "# Just markdown content"
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}
        assert body == content

    def test_parse_empty_frontmatter(self) -> None:
        """Test parsing empty frontmatter."""
        content = """---
---

Content
"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}


class TestLoadPrompt:
    """Tests for loading individual prompts."""

    def test_load_prompt(self, tmp_prompts_dir: Path) -> None:
        """Test loading a prompt from a file."""
        prompt = load_prompt(tmp_prompts_dir / "test_prompt.md")
        assert prompt.name == "test_prompt"
        assert prompt.description == "A test prompt"
        assert prompt.version == "1.0"
        assert prompt.workflow == "test_workflow"
        assert "Test Prompt" in prompt.content

    def test_load_prompt_without_name(self, tmp_path: Path) -> None:
        """Test loading a prompt that uses filename as name."""
        prompt_file = tmp_path / "my_prompt.md"
        prompt_file.write_text(
            """---
description: No name field
---

Content
"""
        )
        prompt = load_prompt(prompt_file)
        assert prompt.name == "my_prompt"


class TestLoadPrompts:
    """Tests for loading multiple prompts."""

    def test_load_prompts(self, tmp_prompts_dir: Path) -> None:
        """Test loading all prompts from a directory."""
        prompts = load_prompts(tmp_prompts_dir)
        assert "test_prompt" in prompts
        assert isinstance(prompts["test_prompt"], Prompt)

    def test_load_prompts_empty_dir(self, tmp_path: Path) -> None:
        """Test loading from empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        prompts = load_prompts(empty_dir)
        assert prompts == {}

    def test_load_prompts_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test loading from nonexistent directory."""
        prompts = load_prompts(tmp_path / "nonexistent")
        assert prompts == {}


class TestGetPromptForWorkflow:
    """Tests for getting prompts by workflow name."""

    def test_get_prompt_by_workflow_field(self, tmp_prompts_dir: Path) -> None:
        """Test finding prompt by workflow field."""
        prompt = get_prompt_for_workflow("test_workflow", tmp_prompts_dir)
        assert prompt is not None
        assert prompt.name == "test_prompt"

    def test_get_prompt_by_name_fallback(self, tmp_prompts_dir: Path) -> None:
        """Test fallback to matching by prompt name."""
        prompt = get_prompt_for_workflow("test_prompt", tmp_prompts_dir)
        assert prompt is not None

    def test_get_prompt_not_found(self, tmp_prompts_dir: Path) -> None:
        """Test when no matching prompt is found."""
        prompt = get_prompt_for_workflow("nonexistent", tmp_prompts_dir)
        assert prompt is None
