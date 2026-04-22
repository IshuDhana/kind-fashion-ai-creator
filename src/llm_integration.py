"""
llm_integration.py
Handles all Anthropic Claude API calls.
"""

import os
from typing import Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wrapper around the Anthropic API."""

    MODEL = "claude-opus-4-5"
    MAX_TOKENS = 1024

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not found. "
                "Create a .env file with ANTHROPIC_API_KEY=your_key"
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = MAX_TOKENS,
        temperature: float = 0.7,
    ) -> str:
        """
        Call the Anthropic API and return the text response.
        """
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            return response.content[0].text

        except anthropic.AuthenticationError:
            raise EnvironmentError("Invalid ANTHROPIC_API_KEY. Check your .env file.")
        except anthropic.RateLimitError:
            raise RuntimeError("Anthropic rate limit hit. Wait a moment and retry.")
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    def generate_simple(self, prompt: str) -> str:
        """
        Simple single-prompt generation — used for generic comparison outputs.
        No system prompt, no brand context.
        """
        return self.generate(
            system="You are a helpful fashion content writer.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
