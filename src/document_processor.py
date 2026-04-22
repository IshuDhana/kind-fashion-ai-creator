"""
document_processor.py
Ingests and parses markdown documents from the knowledge base directories.
"""

import os
import re
from pathlib import Path
from typing import Optional


class MarkdownDocument:
    """Represents a parsed markdown document with metadata."""

    def __init__(self, path: str):
        self.path = path
        self.filename = Path(path).name
        self.raw_content = ""
        self.sections = {}
        self.metadata = {}

    def __repr__(self):
        return f"<MarkdownDocument: {self.filename} ({len(self.sections)} sections)>"


class DocumentProcessor:
    """
    Ingests markdown files and parses them into structured documents.
    No RAG / embeddings — pure markdown parsing and structured retrieval.
    """

    def __init__(self):
        self.documents = []

    def load_file(self, filepath: str) -> Optional[MarkdownDocument]:
        """Load and parse a single markdown file."""
        if not os.path.exists(filepath):
            print(f"  [Warning] File not found: {filepath}")
            return None

        doc = MarkdownDocument(path=filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            doc.raw_content = f.read()

        doc.sections = self._parse_sections(doc.raw_content)
        doc.metadata = self._extract_metadata(doc.raw_content)

        return doc

    def load_directory(self, directory: str, recursive: bool = True) -> list:
        """Load all markdown files from a directory."""
        docs = []
        path = Path(directory)

        if not path.exists():
            print(f"  [Warning] Directory not found: {directory}")
            return docs

        pattern = "**/*.md" if recursive else "*.md"
        for md_file in path.glob(pattern):
            doc = self.load_file(str(md_file))
            if doc:
                docs.append(doc)

        return docs

    def _parse_sections(self, content: str) -> dict:
        """
        Parse markdown into named sections based on headers.
        Returns dict: { section_title: section_content }
        """
        sections = {}
        current_section = "intro"
        current_lines = []

        for line in content.split("\n"):
            if line.startswith("## "):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = line.replace("## ", "").strip().lower().replace(" ", "_")
                current_lines = []
            elif line.startswith("# "):
                # Top-level header becomes document title
                sections["title"] = line.replace("# ", "").strip()
            else:
                current_lines.append(line)

        # Don't forget the last section
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    def _extract_metadata(self, content: str) -> dict:
        """
        Extract key-value metadata from markdown frontmatter or tagged lines.
        Supports --- frontmatter blocks and inline tags like [client: arket]
        """
        metadata = {}

        # Frontmatter block
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    metadata[key.strip()] = value.strip()

        # Inline tags: [key: value]
        for match in re.finditer(r"\[(\w+):\s*(.+?)\]", content):
            metadata[match.group(1)] = match.group(2)

        return metadata

    def get_section(self, doc: MarkdownDocument, section_name: str, fallback: str = "") -> str:
        """Safely retrieve a named section from a document."""
        key = section_name.lower().replace(" ", "_")
        return doc.sections.get(key, fallback)

    def summarise(self, doc: MarkdownDocument, max_chars: int = 800) -> str:
        """Return a truncated summary of the document for prompt injection."""
        text = doc.raw_content
        # Strip markdown syntax for cleaner injection
        text = re.sub(r"#{1,6}\s", "", text)
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"\[.+?\]", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:max_chars].strip()
