"""
prompt_templates.py
Advanced prompt engineering templates for K.I.N.D. fashion content generation.
Each template injects brand context + market research to ensure unique, non-generic output.
"""


SYSTEM_BASE = """You are a senior creative at K.I.N.D., an AI-first fashion content production agency.
You produce content for leading fashion and e-commerce brands. Your outputs are precise, specific,
and grounded in each brand's documented aesthetic — never generic, never interchangeable.

You have access to two knowledge bases:

PRIMARY KNOWLEDGE BASE (brand-specific):
{brand_context}

SECONDARY RESEARCH LAYER (market context):
{market_context}

CRITICAL RULES:
- Every output must be unmistakably for {client_name}, not a generic fashion brand
- Reference specific brand aesthetic details from the primary knowledge base
- Never use clichéd fashion language: "effortless", "timeless", "versatile", "chic"
- Be specific about light, silhouette, material behaviour, and brand positioning
- Write as a creative director who knows this brand deeply, not an AI completing a task
"""


TEMPLATES = {

    "shoot_direction": {
        "system": SYSTEM_BASE,
        "user": """Generate a shoot direction memo for {client_name} {category}.

Format as a professional internal document with these sections:
- Scene / location logic
- Lighting direction (be specific: quality, angle, mood)
- Pose logic (how the body should relate to the garment)
- Background direction
- Brand alignment note (what makes this distinctly {client_name})

Mood: {mood}
Keep it under 250 words. Be specific. Avoid generic fashion copy."""
    },

    "pdp_copy": {
        "system": SYSTEM_BASE,
        "user": """Write product description page (PDP) copy for a {client_name} {category} piece.

Requirements:
- 80-120 words
- Mood: {mood}
- Lead with how the garment behaves, not what it is
- Include one specific detail about fit, material, or construction
- End with a styling suggestion that reflects the brand's customer lifestyle
- Do NOT use the words: versatile, timeless, effortless, chic, perfect, luxurious

Write in {client_name}'s established brand voice as documented in the brand guidelines."""
    },

    "art_direction_brief": {
        "system": SYSTEM_BASE,
        "user": """Create an art direction brief for a {client_name} {category} campaign.

Include:
- Concept statement (1-2 sentences, declarative)
- Casting direction (type, energy, not demographics)
- Location / set design logic
- Colour palette for the shoot (3-4 references, not generic colours)
- References to avoid (what this should NOT look like)
- Brand positioning note

Mood: {mood}
This brief will be handed to a photographer and art director. Be directive and specific."""
    },

    "lookbook_brief": {
        "system": SYSTEM_BASE,
        "user": """Write a lookbook brief for {client_name}'s {category} collection.

Structure:
- Season / collection narrative (2-3 sentences)
- Key looks to feature (3-4 looks with styling notes)
- Shoot locations or set direction
- Model direction
- Typography and layout mood notes

Mood: {mood}
Ground every decision in the brand's documented aesthetic. Be opinionated."""
    },

    "social_caption": {
        "system": SYSTEM_BASE,
        "user": """Write 3 social media caption variations for {client_name} {category}.

Each caption:
- Under 40 words
- No hashtags
- No emojis
- Different angles: product-led, lifestyle-led, and brand-philosophy-led
- Mood: {mood}

Label them: [Product], [Lifestyle], [Philosophy]
Each must be unmistakably {client_name} in voice."""
    },
}


GENERIC_PROMPTS = {
    "shoot_direction": "Write a shoot direction for {category} fashion photography.",
    "pdp_copy": "Write a product description for a {category} clothing item.",
    "art_direction_brief": "Write an art direction brief for a {category} fashion campaign.",
    "lookbook_brief": "Write a lookbook brief for a {category} clothing collection.",
    "social_caption": "Write 3 social media captions for {category} fashion.",
}


def get_template(content_format: str) -> dict:
    """Return the prompt template for a given content format."""
    if content_format not in TEMPLATES:
        raise ValueError(f"Unknown format: {content_format}. Available: {list(TEMPLATES.keys())}")
    return TEMPLATES[content_format]


def get_generic_prompt(content_format: str, category: str) -> str:
    """Return a generic (non-brand-aware) prompt for comparison purposes."""
    template = GENERIC_PROMPTS.get(content_format, "Write fashion content about {category}.")
    return template.format(category=category)


def build_messages(
    content_format: str,
    client_name: str,
    category: str,
    mood: str,
    brand_context: str,
    market_context: str,
) -> list[dict]:
    """
    Build the messages array for the Anthropic API call.
    Returns [{"role": "user", "content": "..."}] with system prompt embedded.
    """
    template = get_template(content_format)

    system = template["system"].format(
        brand_context=brand_context,
        market_context=market_context,
        client_name=client_name,
    )

    user = template["user"].format(
        client_name=client_name,
        category=category,
        mood=mood,
    )

    return system, [{"role": "user", "content": user}]
