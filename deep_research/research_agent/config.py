# src/config.py

# LEVEL 1: Trivial (Formatting, Spelling, Simple Extraction)
# Provider: OpenRouter (Free/Cheap)
LEVEL_1_MODEL = "meta-llama/llama-3.2-3b-instruct:free"

# LEVEL 2: Routine (Summarization, Basic Search, Fact Retrieval)
# Provider: OpenRouter
LEVEL_2_MODEL = "mistralai/mistral-nemo"

# LEVEL 3: Intermediate (Comparative Analysis, Code Generation)
# Provider: OpenRouter
LEVEL_3_MODEL = "meta-llama/llama-3.3-70b-instruct"

# LEVEL 4: Advanced (Strategic Planning, Complex Synthesis)
# Provider: OpenRouter (High-end Open Source or Proprietary)
LEVEL_4_MODEL = "anthropic/claude-3.5-sonnet"

# LEVEL 5: Expert/Deep Thought (Novel Research, Massive Context, Reasoning)
# Provider: Google Native
LEVEL_5_MODEL = "gemini-3-pro-preview"

# --- RATE LIMITS (Requests Per Minute) ---
# Adjust these based on your actual plan limits.
MODEL_LIMITS = {
    LEVEL_1_MODEL: 200, # OpenRouter Free is usually generous
    LEVEL_2_MODEL: 200,
    LEVEL_3_MODEL: 50,  # 70B models might have stricter rate limits
    LEVEL_4_MODEL: 10,  # Claude 3.5 Sonnet (Proprietary) often strict on free proxies or paid tiers
    LEVEL_5_MODEL: 2,   # Gemini Experimental/Preview models are often VERY strict (e.g. 5-10 RPM)
    
    # Generic fallback
    "default": 10
}
