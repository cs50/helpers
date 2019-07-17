from os import environ

if not environ.get("API_SECRET"):
    raise RuntimeError("API_SECRET not set")
