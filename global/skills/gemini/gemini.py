#!/usr/bin/env python3
"""
Gemini SDK CLI — direct Google GenAI calls via Python subprocess.

Models (March 2026):
  3.1 Pro ($2/$12)       — #1 reasoning, brainstorm R1-R3
  3 Flash ($0.50/$3)     — Pro-quality coding, general tasks (default)
  3.1 Flash-Lite ($0.25/$1.50) — Fastest, research & grounding

Usage:
  python3 gemini.py ask "prompt"
  python3 gemini.py second-opinion "question" --context "context"
  python3 gemini.py ask "prompt" --grounded          # web-grounded answer
  python3 gemini.py ask "prompt" --save output.md
  python3 gemini.py ask "prompt" -m gemini-3.1-flash-lite-preview --grounded  # research mode
  python3 gemini.py second-opinion @prompt.txt --image site.png --image ref.png  # visual review

Env: GOOGLE_API_KEY (from .env or export)
"""

import argparse
import json
import os
import sys
import time

try:
  from google import genai
  from google.genai import types
except ImportError:
  print("ERROR: google-genai not installed. Run: pip install google-genai", file=sys.stderr)
  sys.exit(1)

# --- Config ---

MODELS = {
  "gemini-3.1-pro-preview",       # Flagship: $2/$12 per 1M. #1 reasoning.
  "gemini-3-flash-preview",       # Mid-tier: $0.50/$3. Pro-quality coding.
  "gemini-3.1-flash-lite-preview", # Fastest:  $0.25/$1.50. 381 tok/s. Research & grounding.
}
GEMINI_3 = MODELS  # All current models are Gemini 3 series
# Gemini 3.1 Pro: LOW, MEDIUM (new in 3.1), HIGH. No MINIMAL (thinking can't be off).
# Gemini 3 Flash / 3.1 Flash-Lite: all 4 levels (MINIMAL, LOW, MEDIUM, HIGH)
GEMINI_3_FLASH = {"gemini-3-flash-preview", "gemini-3.1-flash-lite-preview"}
THINKING_LEVELS = {"minimal", "low", "medium", "high"}
THINKING_LEVELS_PRO = {"low", "medium", "high"}

DEFAULT_MODEL = "gemini-3-flash-preview"
RESEARCH_MODEL = "gemini-3.1-flash-lite-preview"
SECOND_OPINION_MODEL = "gemini-3.1-pro-preview"


def call_gemini(
  prompt: str,
  model: str = DEFAULT_MODEL,
  system_instruction: str | None = None,
  thinking_level: str | None = None,
  grounded: bool = False,
  temperature: float | None = None,
  top_p: float | None = None,
  top_k: int | None = None,
  max_output_tokens: int | None = None,
  json_mode: bool = False,
  seed: int | None = None,
  images: list[str] | None = None,
) -> dict:
  """Call Gemini SDK and return response + usage. Supports multimodal (text + images)."""
  api_key = os.environ.get("GOOGLE_API_KEY")
  if not api_key:
    return {"error": "GOOGLE_API_KEY not set"}

  if model not in MODELS:
    return {"error": f"Invalid model: {model}. Valid: {', '.join(sorted(MODELS))}"}

  try:
    client = genai.Client(api_key=api_key)
    start = time.time()

    config_kwargs = {}
    if system_instruction:
      config_kwargs["system_instruction"] = system_instruction

    # Sampling parameters (Gemini 3 default: temp=1.0, top_p=0.95)
    if temperature is not None:
      config_kwargs["temperature"] = temperature
    if top_p is not None:
      config_kwargs["top_p"] = top_p
    if top_k is not None:
      config_kwargs["top_k"] = top_k
    if max_output_tokens is not None:
      config_kwargs["max_output_tokens"] = max_output_tokens
    if seed is not None:
      config_kwargs["seed"] = seed

    # JSON structured output
    if json_mode:
      config_kwargs["response_mime_type"] = "application/json"

    # Google Search grounding
    if grounded:
      config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    # Thinking configuration — all models are Gemini 3.x, use thinkingLevel
    is_flash = model in GEMINI_3_FLASH
    if is_flash:
      level = thinking_level or "medium"
      valid = THINKING_LEVELS
    else:
      # Pro: LOW, MEDIUM (new in 3.1), HIGH. No MINIMAL.
      level = thinking_level or "high"
      valid = THINKING_LEVELS_PRO
      if level not in valid:
        level = "high"  # fallback for Pro
    if level in valid:
      config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=level)

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    # Build multimodal contents if images provided
    contents = prompt
    if images:
      parts = [types.Part.from_text(text=prompt)]
      for img_path in images:
        if not os.path.isfile(img_path):
          return {"error": f"Image file not found: {img_path}"}
        with open(img_path, "rb") as f:
          img_data = f.read()
        ext = os.path.splitext(img_path)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
        mime = mime_map.get(ext, "image/png")
        parts.append(types.Part.from_bytes(data=img_data, mime_type=mime))
      contents = parts

    response = client.models.generate_content(
      model=model, contents=contents, config=config,
    )

    elapsed_ms = int((time.time() - start) * 1000)

    usage = {"model": model, "latency_ms": elapsed_ms}
    if response.usage_metadata:
      um = response.usage_metadata
      usage.update({
        "input_tokens": um.prompt_token_count or 0,
        "output_tokens": um.candidates_token_count or 0,
        "total_tokens": um.total_token_count or 0,
      })
      if hasattr(um, "thoughts_token_count") and um.thoughts_token_count:
        usage["thinking_tokens"] = um.thoughts_token_count

    return {"response": response.text or "", "usage": usage}

  except Exception as e:
    return {"error": f"{type(e).__name__}: {e}"}


def format_output(result: dict) -> str:
  """Format response with usage footer."""
  if "error" in result:
    return f"ERROR: {result['error']}"

  usage = result.get("usage", {})
  model = usage.get("model", "?")
  tokens = usage.get("total_tokens", "?")
  latency = usage.get("latency_ms", "?")
  thinking = f" | {usage['thinking_tokens']} thinking" if usage.get("thinking_tokens") else ""

  return f"{result['response']}\n\n---\n*[Gemini {model} | {tokens} tokens{thinking} | {latency}ms]*"


# --- Commands ---

COMMANDS = {
  "ask": {
    "system": None,
    "model": DEFAULT_MODEL,
    "thinking": None,
  },
  "second-opinion": {
    "system": "Provide a critical second opinion. Identify blind spots, errors, unconsidered alternatives, and missing context. Challenge assumptions. Be thorough but structured.",
    "model": SECOND_OPINION_MODEL,
    "thinking": "high",
  },
  "analyze": {
    "system": "You are a data analyst. Analyze the provided data precisely. Structure findings clearly.",
    "model": DEFAULT_MODEL,
    "thinking": None,
  },
  "review": {
    "system": "You are an expert code reviewer. Be precise and actionable. Bullet points, max 10 items.",
    "model": DEFAULT_MODEL,
    "thinking": None,
  },
  "extract": {
    "system": "Extract structured data. Return ONLY valid JSON.",
    "model": RESEARCH_MODEL,
    "thinking": "minimal",
  },
  "think": {
    "system": None,
    "model": SECOND_OPINION_MODEL,
    "thinking": "high",
  },
}


def main():
  parser = argparse.ArgumentParser(
    description="Gemini SDK CLI",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument("command", choices=COMMANDS.keys(), help="Command to run")
  parser.add_argument("prompt", help="Prompt text (or @file to read from file)")
  parser.add_argument("--context", "-c", help="Additional context (for second-opinion)")
  parser.add_argument("--model", "-m", help="Override model")
  parser.add_argument("--thinking", "-t", help="Thinking level: minimal/low/medium/high")
  parser.add_argument("--system", "-s", help="Override system instruction")
  parser.add_argument("--save", help="Save response to file")
  parser.add_argument("--json", action="store_true", help="Output raw JSON (for piping)")
  parser.add_argument("--grounded", "-g", action="store_true", help="Enable Google Search grounding (Gemini searches web before answering)")
  parser.add_argument("--temp", type=float, help="Temperature: 0.0-2.0 (default 1.0, keep default for Gemini 3)")
  parser.add_argument("--top-p", type=float, help="Top-p nucleus sampling: 0.0-1.0 (default 0.95)")
  parser.add_argument("--top-k", type=int, help="Top-k sampling (default ~40)")
  parser.add_argument("--max-tokens", type=int, help="Max output tokens: 1-65536 (default model max)")
  parser.add_argument("--json-mode", action="store_true", help="Force JSON output (sets response_mime_type=application/json)")
  parser.add_argument("--seed", type=int, help="Seed for reproducible output")
  parser.add_argument("--focus", help="Focus area for review command")
  parser.add_argument("--image", "-i", action="append", dest="images", help="Image file path (repeatable, for multimodal input)")

  args = parser.parse_args()
  cmd = COMMANDS[args.command]

  # Read prompt from file if @file syntax
  prompt = args.prompt
  if prompt.startswith("@"):
    filepath = prompt[1:]
    try:
      with open(filepath, "r") as f:
        prompt = f.read()
    except FileNotFoundError:
      print(f"ERROR: File not found: {filepath}", file=sys.stderr)
      sys.exit(1)

  # Build final prompt
  if args.command == "second-opinion" and args.context:
    prompt = f"{prompt}\n\nContext:\n{args.context}"
  elif args.command == "review":
    focus = args.focus or "bugs, security, improvements"
    prompt = f"Review this code. Focus on: {focus}.\n\n```\n{prompt}\n```"
  elif args.command == "analyze" and args.context:
    prompt = f"{prompt}\n\n---\nData:\n{args.context}"

  # Call Gemini
  result = call_gemini(
    prompt=prompt,
    model=args.model or cmd["model"],
    system_instruction=args.system or cmd["system"],
    thinking_level=args.thinking or cmd["thinking"],
    grounded=args.grounded,
    temperature=args.temp,
    top_p=args.top_p,
    top_k=args.top_k,
    max_output_tokens=args.max_tokens,
    json_mode=args.json_mode,
    seed=args.seed,
    images=args.images,
  )

  # Output
  if args.json:
    print(json.dumps(result, ensure_ascii=False, indent=2))
  else:
    output = format_output(result)
    print(output)

  # Save to file
  if args.save and "error" not in result:
    output = format_output(result)
    os.makedirs(os.path.dirname(args.save) or ".", exist_ok=True)
    with open(args.save, "w") as f:
      f.write(output)
    print(f"\n>> Saved to {args.save}", file=sys.stderr)

  sys.exit(1 if "error" in result else 0)


if __name__ == "__main__":
  main()
