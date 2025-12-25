"""Skill loading and management."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .types import SkillFilter, SkillProperties, ValidationProblem

# Pattern to match YAML frontmatter
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Required fields for a valid skill
REQUIRED_FIELDS = ["name", "description"]


def parse_skill_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from skill markdown content.

    Args:
        content: Full SKILL.md file content

    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    remaining_content = content[match.end() :]

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, remaining_content


def validate(path: Path) -> list[ValidationProblem]:
    """Validate a skill directory structure.

    Checks for:
    - SKILL.md file exists
    - Required frontmatter fields present
    - Valid YAML frontmatter

    Args:
        path: Path to the skill directory

    Returns:
        List of validation problems (empty if valid)
    """
    problems: list[ValidationProblem] = []

    # Check directory exists
    if not path.exists():
        problems.append(ValidationProblem("error", "Skill directory does not exist", str(path)))
        return problems

    if not path.is_dir():
        problems.append(ValidationProblem("error", "Path is not a directory", str(path)))
        return problems

    # Check SKILL.md exists
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        problems.append(ValidationProblem("error", "SKILL.md file not found", str(skill_md)))
        return problems

    # Parse and validate content
    content = skill_md.read_text()
    frontmatter, body = parse_skill_frontmatter(content)

    if not frontmatter:
        problems.append(ValidationProblem("error", "No YAML frontmatter found", str(skill_md)))
        return problems

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            problems.append(
                ValidationProblem("error", f"Missing required field: {field}", str(skill_md))
            )

    # Warnings for recommended fields
    if not frontmatter.get("version"):
        problems.append(
            ValidationProblem("warning", "Missing recommended field: version", str(skill_md))
        )

    if not body.strip():
        problems.append(
            ValidationProblem("warning", "Skill has no content/instructions", str(skill_md))
        )

    return problems


def read_properties(path: Path) -> SkillProperties:
    """Read skill properties from a skill directory.

    Args:
        path: Path to the skill directory

    Returns:
        SkillProperties with parsed metadata

    Raises:
        FileNotFoundError: If SKILL.md doesn't exist
        ValueError: If required fields are missing
    """
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {path}")

    content = skill_md.read_text()
    frontmatter, _ = parse_skill_frontmatter(content)

    if "name" not in frontmatter:
        raise ValueError(f"Skill missing required 'name' field: {path}")

    return SkillProperties(
        name=frontmatter["name"],
        description=frontmatter.get("description", ""),
        version=str(frontmatter.get("version", "1.0")),
        author=frontmatter.get("author", ""),
        tags=frontmatter.get("tags", []),
        parameters=frontmatter.get("parameters", []),
        metadata={
            k: v
            for k, v in frontmatter.items()
            if k not in ("name", "description", "version", "author", "tags", "parameters")
        },
        path=path,
    )


def get_skill_content(path: Path) -> str:
    """Get the full content (instructions) of a skill.

    Args:
        path: Path to the skill directory

    Returns:
        The markdown content after frontmatter
    """
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {path}")

    content = skill_md.read_text()
    _, body = parse_skill_frontmatter(content)
    return body.strip()


def load_all_skills(skills_dir: Path) -> dict[str, SkillProperties]:
    """Load all skills from a directory.

    Each subdirectory containing a SKILL.md file is treated as a skill.

    Args:
        skills_dir: Directory containing skill directories

    Returns:
        Dictionary mapping skill names to SkillProperties
    """
    skills: dict[str, SkillProperties] = {}

    if not skills_dir.exists():
        return skills

    for subdir in skills_dir.iterdir():
        if not subdir.is_dir():
            continue

        skill_md = subdir / "SKILL.md"
        if not skill_md.exists():
            continue

        try:
            props = read_properties(subdir)
            skills[props.name] = props
        except (ValueError, FileNotFoundError):
            # Skip invalid skills
            continue

    return skills


def to_prompt(
    paths: list[Path],
    include_content: bool = False,
) -> str:
    """Generate <available_skills> XML block for agent prompts.

    Args:
        paths: List of paths to skill directories
        include_content: If True, include full skill content

    Returns:
        XML formatted string for agent system prompt
    """
    lines = ["<available_skills>"]

    for path in paths:
        try:
            props = read_properties(path)
            lines.append("<skill>")
            lines.append("<name>")
            lines.append(props.name)
            lines.append("</name>")
            lines.append("<description>")
            lines.append(props.description)
            lines.append("</description>")
            lines.append("<location>")
            lines.append(str(path / "SKILL.md"))
            lines.append("</location>")

            if include_content:
                content = get_skill_content(path)
                lines.append("<instructions>")
                lines.append(content)
                lines.append("</instructions>")

            lines.append("</skill>")
        except (ValueError, FileNotFoundError):
            continue

    lines.append("</available_skills>")
    return "\n".join(lines)


def to_prompt_from_skills(
    skills: dict[str, SkillProperties],
    include_content: bool = False,
) -> str:
    """Generate <available_skills> XML from loaded skills.

    Args:
        skills: Dictionary of skill name to SkillProperties
        include_content: If True, include full skill content

    Returns:
        XML formatted string for agent system prompt
    """
    lines = ["<available_skills>"]

    for props in skills.values():
        lines.append("<skill>")
        lines.append("<name>")
        lines.append(props.name)
        lines.append("</name>")
        lines.append("<description>")
        lines.append(props.description)
        lines.append("</description>")

        if props.path:
            lines.append("<location>")
            lines.append(str(props.path / "SKILL.md"))
            lines.append("</location>")

            if include_content:
                try:
                    content = get_skill_content(props.path)
                    lines.append("<instructions>")
                    lines.append(content)
                    lines.append("</instructions>")
                except FileNotFoundError:
                    pass

        lines.append("</skill>")

    lines.append("</available_skills>")
    return "\n".join(lines)


def build_system_prompt(
    base_prompt: str,
    all_skills: dict[str, SkillProperties],
    skill_filter: SkillFilter | None = None,
) -> str:
    """Build a system prompt with skills.

    Required skills are included directly in the prompt.
    Available skills are listed in <available_skills> block.

    Args:
        base_prompt: The base system prompt content
        all_skills: All loaded skills
        skill_filter: Filter for required/allowed/denied skills

    Returns:
        Complete system prompt with skills
    """
    if skill_filter is None:
        # No filter means all skills are available
        available_xml = to_prompt_from_skills(all_skills)
        return f"{base_prompt}\n\n{available_xml}"

    # Get required skills and include their content
    required_skills = skill_filter.get_required_skills(all_skills)
    required_content = ""
    if required_skills:
        required_parts = []
        for props in required_skills.values():
            if props.path:
                try:
                    content = get_skill_content(props.path)
                    required_parts.append(f"## {props.name}\n\n{content}")
                except FileNotFoundError:
                    pass
        if required_parts:
            required_content = "\n\n".join(required_parts)

    # Get available skills (filtered)
    available_skills = skill_filter.filter_skills(all_skills)
    available_xml = to_prompt_from_skills(available_skills)

    # Build final prompt
    parts = [base_prompt]
    if required_content:
        parts.append(f"\n\n# Required Skills\n\n{required_content}")
    if available_skills:
        parts.append(f"\n\n{available_xml}")

    return "".join(parts)
