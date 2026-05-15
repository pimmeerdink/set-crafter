#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "stl-infra @ git+ssh://git@github.com/socialtechnologylab/stl-infra.git",
# ]
# ///
"""set-crafter operations CLI."""
from stl_infra import cli

if __name__ == "__main__":
    cli(name="set-crafter")
