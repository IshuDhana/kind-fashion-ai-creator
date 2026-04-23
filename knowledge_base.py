"""
knowledge_base.py
Manages the two-tier knowledge base:
  Primary   — client brand docs (brand guidelines, product specs, shoot direction)
  Secondary — market research (trends, competitors, benchmarks)
"""

import os
from pathlib import Path
from document_processor import DocumentProcessor, MarkdownDocument


BASE_DIR = Path(__file__).parent.parent / "knowledge_base"


class KnowledgeBase:
    """
    Loads and organises markdown documents from both knowledge base tiers.
    Exposes clean context strings ready for prompt injection.
    """

    def __init__(self, client: str = "arket"):
        self.client = client.lower()
        self.processor = DocumentProcessor()
        self.primary_docs: list[MarkdownDocument] = []
        self.secondary_docs: list[MarkdownDocument] = []

    def load(self):
        """Load all documents for both knowledge base tiers."""
        self._load_primary()
        self._load_secondary()

    def _load_primary(self):
        """Load client-specific + shared brand documents."""
        client_dir = BASE_DIR / "primary" / self.client
        shared_dir = BASE_DIR / "primary" / "shared"

        client_docs = self.processor.load_directory(str(client_dir))
        shared_docs = self.processor.load_directory(str(shared_dir))

        self.primary_docs = client_docs + shared_docs
        if not self.primary_docs:
            print(f"  [Warning] No primary KB documents found for client '{self.client}'")

    def _load_secondary(self):
        """Load market research and competitor documents."""
        secondary_dir = BASE_DIR / "secondary"
        self.secondary_docs = self.processor.load_directory(str(secondary_dir))

    def get_brand_context(self, max_chars: int = 1200) -> str:
        """
        Build a brand context string from primary KB documents.
        Used for system prompt injection.
        """
        if not self.primary_docs:
            return f"Client: {self.client.upper()}. No brand documents loaded."

        parts = []
        for doc in self.primary_docs:
            summary = self.processor.summarise(doc, max_chars=400)
            parts.append(f"[{doc.filename}]\n{summary}")

        combined = "\n\n---\n\n".join(parts)
        return combined[:max_chars]

    def get_market_context(self, max_chars: int = 800) -> str:
        """
        Build a market context string from secondary KB documents.
        Used for trend-aware content generation.
        """
        if not self.secondary_docs:
            return "No secondary market research documents loaded."

        parts = []
        for doc in self.secondary_docs:
            summary = self.processor.summarise(doc, max_chars=300)
            parts.append(f"[{doc.filename}]\n{summary}")

        combined = "\n\n---\n\n".join(parts)
        return combined[:max_chars]

    def get_client_display_name(self) -> str:
        names = {"arket": "Arket", "cos": "COS", "mango": "Mango"}
        return names.get(self.client, self.client.upper())

    def status(self) -> dict:
        return {
            "client": self.client,
            "primary_docs": [d.filename for d in self.primary_docs],
            "secondary_docs": [d.filename for d in self.secondary_docs],
        }
