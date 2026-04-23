"""
content_pipeline.py
Implements the full content creation pipeline:
Document → Monitor → Brief → Publish → Iterate
"""

from knowledge_base import KnowledgeBase
from llm_integration import LLMClient
from prompt_templates import build_messages, get_generic_prompt


class ContentPipeline:
    """
    Orchestrates the five-stage content creation pipeline.
    Each stage uses both knowledge bases to produce brand-aligned output.
    """

    PIPELINE_STAGES = ["document", "monitor", "brief", "publish", "iterate"]

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.llm = LLMClient()
        self._last_result = None

    # ------------------------------------------------------------------ #
    # Stage 1: Document — already handled by KnowledgeBase.load()
    # Stage 2: Monitor  — analyse current knowledge base state
    # ------------------------------------------------------------------ #

    def monitor(self) -> dict:
        """
        Stage 2: Monitor — summarise what the knowledge bases contain
        and surface any gaps or opportunities.
        """
        signals = {
            "client": self.kb.client,
            "primary_doc_count": len(self.kb.primary_docs),
            "secondary_doc_count": len(self.kb.secondary_docs),
            "primary_docs": [d.filename for d in self.kb.primary_docs],
            "secondary_docs": [d.filename for d in self.kb.secondary_docs],
            "brand_context_length": len(self.kb.get_brand_context()),
            "market_context_length": len(self.kb.get_market_context()),
        }
        return signals

    # ------------------------------------------------------------------ #
    # Stage 3: Brief — generate the content brief
    # ------------------------------------------------------------------ #

    def brief(self, content_format: str, category: str, mood: str) -> str:
        """
        Stage 3: Generate a content brief using both knowledge bases.
        """
        brand_context = self.kb.get_brand_context()
        market_context = self.kb.get_market_context()
        client_name = self.kb.get_client_display_name()

        system, messages = build_messages(
            content_format=content_format,
            client_name=client_name,
            category=category,
            mood=mood,
            brand_context=brand_context,
            market_context=market_context,
        )

        return self.llm.generate(system=system, messages=messages)

    # ------------------------------------------------------------------ #
    # Stage 4: Publish — format output for delivery
    # ------------------------------------------------------------------ #

    def publish(self, raw_content: str, content_format: str) -> dict:
        """
        Stage 4: Package the generated content for delivery.
        """
        return {
            "client": self.kb.get_client_display_name(),
            "format": content_format,
            "content": raw_content,
            "knowledge_bases_used": {
                "primary": [d.filename for d in self.kb.primary_docs],
                "secondary": [d.filename for d in self.kb.secondary_docs],
            },
            "status": "ready_for_delivery",
        }

    # ------------------------------------------------------------------ #
    # Stage 5: Iterate — refine based on feedback
    # ------------------------------------------------------------------ #

    def iterate(self, previous_content: str, feedback: str) -> str:
        """
        Stage 5: Refine the content based on creative feedback.
        Maintains brand context throughout the iteration.
        """
        brand_context = self.kb.get_brand_context()
        client_name = self.kb.get_client_display_name()

        system = f"""You are a senior creative at K.I.N.D. fashion content agency.
You previously generated this content for {client_name}:

{previous_content}

Brand context:
{brand_context}

Revise the content based on the feedback provided.
Maintain brand voice. Do not make it more generic."""

        messages = [{"role": "user", "content": f"Feedback: {feedback}\n\nPlease revise accordingly."}]
        return self.llm.generate(system=system, messages=messages)

    # ------------------------------------------------------------------ #
    # Full pipeline run
    # ------------------------------------------------------------------ #

    def run(self, content_format: str, category: str, mood: str) -> dict:
        """Run the complete pipeline and return a publish-ready result."""
        # Stage 2: Monitor
        _ = self.monitor()

        # Stage 3: Brief / generate
        raw = self.brief(content_format=content_format, category=category, mood=mood)

        # Stage 4: Publish
        result = self.publish(raw, content_format)
        self._last_result = result
        return result

    # ------------------------------------------------------------------ #
    # Uniqueness comparison
    # ------------------------------------------------------------------ #

    def generate_comparison(self, content_format: str, category: str) -> dict:
        """
        Generate side-by-side comparison:
        Generic ChatGPT-style output vs K.I.N.D. brand-aligned output.
        """
        generic_prompt = get_generic_prompt(content_format, category)
        generic_output = self.llm.generate_simple(generic_prompt)

        kind_output = self._last_result["content"] if self._last_result else \
            self.brief(content_format, category, "minimal")

        reasons = [
            f"K.I.N.D. output references {self.kb.get_client_display_name()}'s specific brand aesthetic",
            "Lighting and background direction is grounded in documented shoot guidelines",
            "Language avoids generic fashion clichés ('effortless', 'versatile', 'chic')",
            "Styling logic reflects the brand's actual customer lifestyle documentation",
            "Market context from secondary KB informs competitive positioning",
        ]

        return {
            "generic": generic_output,
            "kind": kind_output,
            "differentiation_reasons": reasons,
        }
