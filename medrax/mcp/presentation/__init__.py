"""
Presentation Layer - MCP Tools

This layer contains FastMCP tool definitions that expose
application services via MCP protocol.
"""

from medrax.mcp.presentation.tools import register_tools
from medrax.mcp.presentation.prompts import register_prompts
from medrax.mcp.presentation.resources import register_resources

__all__ = [
    "register_tools",
    "register_prompts",
    "register_resources",
]
