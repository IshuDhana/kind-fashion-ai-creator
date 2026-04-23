"""
K.I.N.D. AI Fashion Content Creator
Main entry point — run CLI or API server.
"""

import argparse
import os
import sys

def run_cli():
    parser = argparse.ArgumentParser(description="K.I.N.D. AI Fashion Content Creator")
    parser.add_argument("--client", choices=["arket", "cos", "mango"], default="arket")
    parser.add_argument("--format", dest="content_format", choices=[
        "shoot_direction", "pdp_copy", "art_direction_brief", "lookbook_brief", "social_caption"
    ], default="shoot_direction")
    parser.add_argument("--category", choices=[
        "outerwear", "knitwear", "tailoring", "denim", "accessories"
    ], default="outerwear")
    parser.add_argument("--mood", choices=["minimal", "editorial", "campaign", "ecom_clean"], default="minimal")
    parser.add_argument("--compare", action="store_true", help="Show comparison vs generic ChatGPT")
    parser.add_argument("--server", action="store_true", help="Start FastAPI server")
    args = parser.parse_args()

    if args.server:
        import uvicorn
        from api import app
        print("Starting K.I.N.D. API server at http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return

    from knowledge_base import KnowledgeBase
    from content_pipeline import ContentPipeline

    print("\n" + "="*60)
    print("  K.I.N.D. AI Fashion Content Creator")
    print("="*60)

    print(f"\n[1/5] Loading knowledge bases for: {args.client.upper()}")
    kb = KnowledgeBase(client=args.client)
    kb.load()
    print(f"  Primary KB:   {len(kb.primary_docs)} documents")
    print(f"  Secondary KB: {len(kb.secondary_docs)} documents")

    print(f"\n[2/5] Monitoring market signals...")
    print(f"\n[3/5] Generating {args.content_format} for {args.category} [{args.mood}]...")

    pipeline = ContentPipeline(knowledge_base=kb)
    result = pipeline.run(
        content_format=args.content_format,
        category=args.category,
        mood=args.mood
    )

    print(f"\n[4/5] Applying brand voice filter...")
    print(f"\n[5/5] Output ready\n")
    print("-"*60)
    print(f"CLIENT: {args.client.upper()} | {args.content_format} | {args.category} | {args.mood}")
    print("-"*60)
    print(result["content"])
    print("-"*60)

    os.makedirs("outputs", exist_ok=True)
    out_path = f"outputs/{args.client}_{args.content_format}_{args.category}.txt"
    with open(out_path, "w") as f:
        f.write(result["content"])
    print(f"\nSaved to: {out_path}")

    if args.compare:
        print("\n" + "="*60)
        print("  UNIQUENESS: K.I.N.D. vs Generic ChatGPT")
        print("="*60)
        comp = pipeline.generate_comparison(args.content_format, args.category)
        print("\n[Generic ChatGPT]")
        print(comp["generic"])
        print("\n[K.I.N.D. brand-aligned]")
        print(comp["kind"])
        print("\n[Differentiation]")
        for r in comp["differentiation_reasons"]:
            print(f"  • {r}")

if __name__ == "__main__":
    run_cli()
