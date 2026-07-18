from app.application.schemas.assistant import TokenUsageDTO


class TokenCounter:
    """Token counting and estimation engine across different model tokenizers."""

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Estimate token count (approx 1 token = 4 characters or 0.75 words)."""
        if not text:
            return 0
        words = text.split()
        return max(1, int(len(words) * 1.3))


class CostTracker:
    """Tracks token consumption costs per model provider."""

    # Approximate pricing in USD per 1,000 tokens
    RATES = {
        "gemini-1.5-pro": {"prompt": 0.00125, "completion": 0.00375},
        "gpt-4o": {"prompt": 0.00500, "completion": 0.01500},
    }

    @classmethod
    def calculate_cost(cls, prompt_tokens: int, completion_tokens: int, model: str = "gemini-1.5-pro") -> float:
        rate = cls.RATES.get(model, cls.RATES["gemini-1.5-pro"])
        cost = (prompt_tokens / 1000.0 * rate["prompt"]) + (completion_tokens / 1000.0 * rate["completion"])
        return round(cost, 6)

    @classmethod
    def create_usage_dto(cls, prompt_text: str, completion_text: str, model: str = "gemini-1.5-pro") -> TokenUsageDTO:
        prompt_tokens = TokenCounter.estimate_tokens(prompt_text)
        completion_tokens = TokenCounter.estimate_tokens(completion_text)
        total = prompt_tokens + completion_tokens
        cost = cls.calculate_cost(prompt_tokens, completion_tokens, model)
        return TokenUsageDTO(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            estimated_cost_usd=cost,
        )
