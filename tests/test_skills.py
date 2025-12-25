"""Tests for skills system."""

from __future__ import annotations

from pathlib import Path

import pytest

from workflows.skills import (
    SkillFilter,
    SkillProperties,
    build_system_prompt,
    get_skill_content,
    load_all_skills,
    read_properties,
    to_prompt,
    to_prompt_from_skills,
    validate,
)


class TestValidate:
    """Tests for skill validation."""

    def test_validate_valid_skill(self, tmp_skills_dir: Path) -> None:
        """Test validating a valid skill."""
        problems = validate(tmp_skills_dir / "web_search")
        errors = [p for p in problems if p.level == "error"]
        assert len(errors) == 0

    def test_validate_missing_skill_md(self, tmp_path: Path) -> None:
        """Test validating skill without SKILL.md."""
        skill_dir = tmp_path / "invalid_skill"
        skill_dir.mkdir()
        problems = validate(skill_dir)
        assert any("SKILL.md file not found" in p.message for p in problems)

    def test_validate_missing_name(self, tmp_path: Path) -> None:
        """Test validating skill without name field."""
        skill_dir = tmp_path / "nameless"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
description: No name here
---

Content
"""
        )
        problems = validate(skill_dir)
        assert any("Missing required field: name" in p.message for p in problems)

    def test_validate_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test validating nonexistent directory."""
        problems = validate(tmp_path / "nonexistent")
        assert any("does not exist" in p.message for p in problems)


class TestReadProperties:
    """Tests for reading skill properties."""

    def test_read_properties(self, tmp_skills_dir: Path) -> None:
        """Test reading skill properties."""
        props = read_properties(tmp_skills_dir / "web_search")
        assert props.name == "web_search"
        assert props.description == "Search the web for information"
        assert props.version == "1.0"
        assert props.author == "test"
        assert "search" in props.tags

    def test_read_properties_missing_file(self, tmp_path: Path) -> None:
        """Test reading from missing SKILL.md."""
        with pytest.raises(FileNotFoundError):
            read_properties(tmp_path / "missing")


class TestGetSkillContent:
    """Tests for getting skill content."""

    def test_get_skill_content(self, tmp_skills_dir: Path) -> None:
        """Test getting skill content."""
        content = get_skill_content(tmp_skills_dir / "web_search")
        assert "Web Search Skill" in content
        assert "Use this skill" in content


class TestLoadAllSkills:
    """Tests for loading all skills."""

    def test_load_all_skills(self, tmp_skills_dir: Path) -> None:
        """Test loading all skills from directory."""
        skills = load_all_skills(tmp_skills_dir)
        assert "web_search" in skills
        assert "summarize" in skills
        assert len(skills) == 2

    def test_load_all_skills_empty_dir(self, tmp_path: Path) -> None:
        """Test loading from empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        skills = load_all_skills(empty_dir)
        assert skills == {}


class TestSkillFilter:
    """Tests for SkillFilter."""

    def test_filter_with_denied(self) -> None:
        """Test filtering with denied skills."""
        skills = {
            "a": SkillProperties(name="a"),
            "b": SkillProperties(name="b"),
            "c": SkillProperties(name="c"),
        }
        filter = SkillFilter(denied=["b"])
        filtered = filter.filter_skills(skills)
        assert "a" in filtered
        assert "b" not in filtered
        assert "c" in filtered

    def test_filter_with_allowed(self) -> None:
        """Test filtering with allowed list."""
        skills = {
            "a": SkillProperties(name="a"),
            "b": SkillProperties(name="b"),
            "c": SkillProperties(name="c"),
        }
        filter = SkillFilter(allowed=["a", "b"])
        filtered = filter.filter_skills(skills)
        assert "a" in filtered
        assert "b" in filtered
        assert "c" not in filtered

    def test_filter_excludes_required(self) -> None:
        """Test that required skills are excluded from available."""
        skills = {
            "a": SkillProperties(name="a"),
            "b": SkillProperties(name="b"),
        }
        filter = SkillFilter(required=["a"])
        filtered = filter.filter_skills(skills)
        assert "a" not in filtered
        assert "b" in filtered

    def test_get_required_skills(self) -> None:
        """Test getting required skills."""
        skills = {
            "a": SkillProperties(name="a"),
            "b": SkillProperties(name="b"),
        }
        filter = SkillFilter(required=["a"])
        required = filter.get_required_skills(skills)
        assert "a" in required
        assert "b" not in required


class TestToPrompt:
    """Tests for prompt generation."""

    def test_to_prompt(self, tmp_skills_dir: Path) -> None:
        """Test generating XML prompt."""
        paths = [tmp_skills_dir / "web_search", tmp_skills_dir / "summarize"]
        prompt = to_prompt(paths)
        assert "<available_skills>" in prompt
        assert "<name>" in prompt
        assert "web_search" in prompt
        assert "summarize" in prompt
        assert "</available_skills>" in prompt

    def test_to_prompt_from_skills(self) -> None:
        """Test generating prompt from skill objects."""
        skills = {
            "test": SkillProperties(
                name="test",
                description="Test skill",
            )
        }
        prompt = to_prompt_from_skills(skills)
        assert "<available_skills>" in prompt
        assert "test" in prompt
        assert "Test skill" in prompt


class TestBuildSystemPrompt:
    """Tests for building complete system prompts."""

    def test_build_with_no_filter(self, tmp_skills_dir: Path) -> None:
        """Test building prompt with no filter."""
        skills = load_all_skills(tmp_skills_dir)
        prompt = build_system_prompt("Base prompt", skills)
        assert "Base prompt" in prompt
        assert "<available_skills>" in prompt
        assert "web_search" in prompt

    def test_build_with_filter(self, tmp_skills_dir: Path) -> None:
        """Test building prompt with skill filter."""
        skills = load_all_skills(tmp_skills_dir)
        filter = SkillFilter(
            required=["web_search"],
            allowed=["summarize"],
        )
        prompt = build_system_prompt("Base prompt", skills, filter)
        assert "Base prompt" in prompt
        assert "Required Skills" in prompt
        # web_search content should be included directly
        assert "Web Search Skill" in prompt
        # summarize should be in available_skills
        assert "summarize" in prompt
