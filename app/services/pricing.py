MODEL_PRICES = {
    "openai/gpt-oss-120b": (0.039, 0.19),
    "openai/gpt-5-nano": (0.05, 0.40),
    "openai/gpt-5-mini": (0.25, 2.00),
}


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int, fee_pct: float = 5.5) -> float:
    in_price, out_price = MODEL_PRICES.get(model, MODEL_PRICES["openai/gpt-5-nano"])
    raw = (prompt_tokens * in_price + completion_tokens * out_price) / 1_000_000
    return raw * (1.0 + fee_pct / 100.0)

