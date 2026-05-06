from langchain_openai import ChatOpenAI

_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Add new models here: model_id -> default inference params
_MODEL_REGISTRY: dict[str, dict] = {
    "moonshotai/kimi-k2-instruct": {
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 1024,
    },
    "google/gemma-3n-e4b-it": {
        "temperature": 0.20,
        "top_p": 0.70,
        "max_tokens": 512,
    },
}


def create_llm(model_id: str, api_key: str) -> ChatOpenAI:
    params = _MODEL_REGISTRY.get(model_id)
    if params is None:
        raise ValueError(
            f"Unknown model '{model_id}'. "
            f"Registered models: {list(_MODEL_REGISTRY)}"
        )
    return ChatOpenAI(
        model=model_id,
        api_key=api_key,
        base_url=_NVIDIA_BASE_URL,
        **params,
    )
