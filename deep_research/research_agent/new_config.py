
# RE-ORCHESTRATION CONFIGURATION

# PLANNER & META-JUDGE AGENT: The "Brain"
# Uses Llama 3.1 405B for high-level planning and synthesizing the ensemble results.
PLANNER_MODEL_ID = "meta-llama/llama-3.1-405b-instruct"

# ENSEMBLE MODELS (The "Workers")
# Three distinct, high-performance open models for diverse perspectives.
ENSEMBLE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct",   # Llama 3.3 (Generalist)
    "qwen/qwen-2.5-72b-instruct",          # Qwen 2.5 (Math/Logic Strong)
    "mistralai/mixtral-8x22b-instruct",    # Mixtral (MoE Architecture)
]

# RATE LIMITS (RPM)
PLANNER_RATE_LIMIT = 50 
EXECUTOR_RATE_LIMIT = 50
