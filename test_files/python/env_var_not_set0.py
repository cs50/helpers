from os import environ

if not environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
