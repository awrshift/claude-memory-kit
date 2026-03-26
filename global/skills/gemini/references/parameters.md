# Gemini API Parameters Reference

Last updated: 2026-03-11 (web-verified from ai.google.dev, cloud.google.com, googleapis.github.io)

## GenerateContentConfig — All Parameters

### Sampling Parameters (control output quality)

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `temperature` | float | 0.0–2.0 | **1.0** | Controls randomness. Lower = deterministic, higher = creative. **Gemini 3 is optimized for 1.0 — changing it can cause looping or degraded reasoning.** |
| `top_p` | float | 0.0–1.0 | **0.95** | Nucleus sampling. Tokens selected until cumulative probability reaches top_p. Lower = less diverse. |
| `top_k` | int | 1–∞ | **40** (conventional) | Limits sampling to top K most probable tokens. top_k=1 = greedy decoding. |
| `seed` | int | any | None | Fixed seed → deterministic output (best effort). |
| `candidate_count` | int | 1+ | 1 | Number of response variations to generate. |

### Output Control

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `max_output_tokens` | int | 1–65536 | Model max (65536) | Maximum tokens in response. All Gemini 3 models support up to 64K output. |
| `stop_sequences` | list[str] | up to 5 | None | Sequences that stop generation. Case-sensitive. |
| `response_mime_type` | str | — | "text/plain" | `"application/json"` for structured JSON output. |
| `response_schema` | dict/Pydantic | — | None | Schema for structured output (requires `response_mime_type="application/json"`). |
| `response_json_schema` | dict | — | None | Alternative JSON schema format. |
| `response_modalities` | list[str] | — | ["TEXT"] | Output modalities: `["TEXT"]`, `["TEXT", "IMAGE"]`, `["AUDIO"]`. |

### Penalty Parameters (reduce repetition)

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `presence_penalty` | float | -2.0 to <2.0 | 0.0 | Positive = penalize tokens already present. Encourages diversity. |
| `frequency_penalty` | float | -2.0 to <2.0 | 0.0 | Positive = penalize frequently appearing tokens. Reduces repetition. |

### Thinking Configuration

| Parameter | Type | Values | Default | Description |
|-----------|------|--------|---------|-------------|
| `thinking_config.thinking_level` | str | MINIMAL, LOW, MEDIUM, HIGH | **HIGH** | Controls reasoning depth. Gemini 3 models only. |
| `thinking_config.thinking_budget` | int | 0–32768 | 8192 | Token budget for reasoning. Gemini 2.5 models only. **Do NOT combine with thinking_level.** |
| `thinking_config.include_thoughts` | bool | — | False | Return thought summaries in response. Not guaranteed to return thoughts. |

#### Thinking Level per Model

| Model | MINIMAL | LOW | MEDIUM | HIGH |
|-------|---------|-----|--------|------|
| `gemini-3.1-pro-preview` | NO | YES | **YES** (new in 3.1) | YES (default) |
| `gemini-3-flash-preview` | YES | YES | YES | YES (default) |
| `gemini-3.1-flash-lite-preview` | YES | YES | YES | YES (default) |

**Key facts:**
- Thinking cannot be turned off for Pro models (MINIMAL not supported).
- `MINIMAL` does not guarantee thinking is off — model may still reason.
- Gemini 3 treats levels as **relative allowances**, not strict token guarantees.
- If you used `thinking_budget=0` (Gemini 2.5), use `MINIMAL` for similar latency.

### System & Tools

| Parameter | Type | Description |
|-----------|------|-------------|
| `system_instruction` | str/Content | System-level instructions for the model. |
| `tools` | list[Tool] | Tools: `GoogleSearch`, `CodeExecution`, `FunctionDeclaration`. |
| `tool_config` | ToolConfig | Function calling mode: `AUTO`, `ANY`, `NONE`. |
| `automatic_function_calling` | AutomaticFunctionCallingConfig | Auto-invoke tool calls. |

### Safety Settings

| Parameter | Type | Description |
|-----------|------|-------------|
| `safety_settings` | list[SafetySetting] | Per-category harm thresholds. |

**Safety categories:** `HARM_CATEGORY_HARASSMENT`, `HARM_CATEGORY_HATE_SPEECH`, `HARM_CATEGORY_SEXUALLY_EXPLICIT`, `HARM_CATEGORY_DANGEROUS_CONTENT`, `HARM_CATEGORY_CIVIC_INTEGRITY`.

**Threshold levels:** `BLOCK_NONE`, `BLOCK_LOW_AND_ABOVE`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_HIGH_AND_ABOVE` (most permissive → most restrictive).

### Other Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cached_content` | str | Reference to context cache (reduces cost for repeated large contexts). |
| `image_config` | ImageConfig | Image generation config (for image-capable models only). |
| `speech_config` | SpeechConfig | Speech/audio generation config. |
| `media_resolution` | MediaResolution | Resolution for media processing. |
| `audio_timestamp` | bool | Include timestamps for audio. |
| `logprobs` | int (1-20) | Number of top token log probabilities to return. |
| `response_logprobs` | bool | Include log probabilities in response. |
| `enable_enhanced_civic_answers` | bool | Enhanced civic information. |

### Vertex AI Only (not available in Gemini Developer API)

| Parameter | Description |
|-----------|-------------|
| `routing_config` | Request routing (raises ValueError in Developer API). |
| `model_selection_config` | Model selection strategy. |
| `model_armor_config` | Security configuration. |
| `labels` | User-defined metadata for billing breakdown. |

## Model Specifications (March 2026)

| Spec | 3.1 Pro | 3 Flash | 3.1 Flash-Lite |
|------|---------|---------|----------------|
| Input tokens | 1,048,576 (1M) | 1,048,576 (1M) | 1,048,576 (1M) |
| Output tokens | 65,536 (64K) | 65,536 (64K) | 65,536 (64K) |
| Default temperature | 1.0 | 1.0 | 1.0 |
| Default top_p | 0.95 | 0.95 | 0.95 |
| Default thinking | HIGH | HIGH | HIGH |
| Knowledge cutoff | Jan 2025 | Jan 2025 | Jan 2025 |
| Google Search grounding | YES | YES | YES |
| Code execution | YES | YES | YES |
| Function calling | YES | YES | YES |
| Structured output (JSON) | YES | YES | YES |
| Caching | YES | YES | YES |
| URL context | YES | YES | YES |
| File search | YES (AI Studio) | YES (AI Studio) | YES (AI Studio) |
| Image generation | NO | NO | NO |
| Audio generation | NO | NO | NO |
| Live API | NO | NO | NO |

## Thought Signatures (Gemini 3 specific)

Gemini 3 uses **Thought Signatures** — encrypted representations of internal reasoning. In multi-turn conversations, signatures must be returned exactly as received. Missing signatures → 400 error. This is handled automatically by the SDK in single-turn calls.

## Optimal Parameter Presets for Our Skills

### Research (Phase 0.5, 3.5 — Flash-Lite grounded)
```python
config = types.GenerateContentConfig(
    temperature=1.0,       # Keep default — Gemini 3 optimized for 1.0
    thinking_config=types.ThinkingConfig(thinking_level="low"),  # Fast, minimal reasoning needed
    tools=[types.Tool(google_search=types.GoogleSearch())],      # Web grounding
)
```

### Brainstorm Reasoning (R1-R3 — Pro ungrounded)
```python
config = types.GenerateContentConfig(
    temperature=1.0,       # Keep default — best reasoning quality
    thinking_config=types.ThinkingConfig(thinking_level="high"),  # Deep reasoning
    # NO grounding — pre-verified facts only
)
```

### Quick Question (ask — Flash)
```python
config = types.GenerateContentConfig(
    temperature=1.0,       # Keep default
    thinking_config=types.ThinkingConfig(thinking_level="medium"),  # Balance speed/quality
)
```

### Data Extraction (extract — Flash-Lite)
```python
config = types.GenerateContentConfig(
    temperature=0.2,       # Low randomness for structured output
    thinking_config=types.ThinkingConfig(thinking_level="minimal"),  # Speed priority
    response_mime_type="application/json",
)
```

### Code Review (review — Flash)
```python
config = types.GenerateContentConfig(
    temperature=1.0,       # Keep default
    thinking_config=types.ThinkingConfig(thinking_level="high"),  # Thorough analysis
)
```

## Key Rules

1. **Temperature 1.0 for Gemini 3** — Google strongly recommends keeping default. Lower values cause looping/degradation in reasoning tasks.
2. **thinking_level replaces thinking_budget** — Do NOT combine both in same request (→ error).
3. **Structured JSON** — Set `response_mime_type="application/json"` + `response_schema` for guaranteed valid JSON.
4. **Grounding = Tool** — Google Search is a tool, not a parameter: `tools=[types.Tool(google_search=types.GoogleSearch())]`.
5. **Seed for reproducibility** — Same seed + same prompt = same output (best effort, not guaranteed).
6. **Penalties for long-form** — Use `presence_penalty` (0.1–0.5) and `frequency_penalty` (0.1–0.5) to reduce repetition in long outputs.

## Sources

- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Gemini 3.1 Pro Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview)
- [Gemini Thinking Docs](https://ai.google.dev/gemini-api/docs/thinking)
- [Content Generation Parameters](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/content-generation-parameters)
- [Python GenAI SDK](https://googleapis.github.io/python-genai/)
- [Thought Signatures](https://ai.google.dev/gemini-api/docs/thought-signatures)
