import os


def provider_secret(provider: str) -> str | None:
    """Read a key from the local OS keychain, with env fallback for server deployments."""
    try:
        import keyring
        value = keyring.get_password("Memento Personal Agent", f"provider-api-key:{provider}")
        if value:
            return value
    except Exception:
        pass
    return os.getenv(f"{provider.upper()}_API_KEY") or os.getenv("LLM_API_KEY")
