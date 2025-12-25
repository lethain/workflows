"""Prompt loading from markdown files with YAML frontmatter."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .types import Prompt

# Pattern to match YAML frontmatter
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

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


def load_prompt(path: Path) -> Prompt:
    """Load a prompt from a markdown file.

    Expected format:
        ---
        name: my_prompt
        description: What this prompt does
        version: 1.0
        workflow: my_workflow
        ---

        # Prompt Content

        The actual prompt text...

    Args:
        path: Path to the markdown file

    Returns:
        Prompt object with parsed metadata and content
    """
    content = path.read_text()
    frontmatter, body = parse_frontmatter(content)

    return Prompt(
        name=frontmatter.get("name", path.stem),
        description=frontmatter.get("description", ""),
        version=str(frontmatter.get("version", "1.0")),
        workflow=frontmatter.get("workflow"),
        content=body.strip(),
        metadata={k: v for k, v in frontmatter.items() if k not in ("name", "description", "version", "workflow")},
        path=str(path),
    )


def load_prompts(directory: Path) -> dict[str, Prompt]:
    """Load all prompts from a directory.

    Args:
        directory: Directory containing markdown prompt files

    Returns:
        Dictionary mapping prompt names to Prompt objects
    """
    prompts: dict[str, Prompt] = {}

    if not directory.exists():
        return prompts

    for path in directory.glob("*.md"):
        prompt = load_prompt(path)
        prompts[prompt.name] = prompt

    return prompts


def get_prompt_for_workflow(
    workflow_name: str,
    prompts_dir: Path | None = None,
) -> Prompt | None:
    """Get the prompt associated with a workflow.

    Args:
        workflow_name: Name of the workflow
        prompts_dir: Directory containing prompts (defaults to 'prompts/')

    Returns:
        Prompt if found, None otherwise
    """
    if prompts_dir is None:
        prompts_dir = Path("prompts")

    prompts = load_prompts(prompts_dir)

    # First try to find by workflow field
    for prompt in prompts.values():
        if prompt.workflow == workflow_name:
            return prompt

    # Fall back to matching by name
    return prompts.get(workflow_name)
