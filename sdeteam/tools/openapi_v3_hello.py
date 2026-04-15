#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import connexion


# openapi implement
async def post_greeting(name: str) -> str:
    return f"Hello {name}\n"


if __name__ == "__main__":
    specification_dir = Path(__file__).parent.parent.parent / "docs/.well-known"
    app = connexion.AsyncApp(__name__, specification_dir=str(specification_dir))
    app.add_api("openapi.yaml", arguments={"title": "Hello World Example"})
    app.run(port=8082)
