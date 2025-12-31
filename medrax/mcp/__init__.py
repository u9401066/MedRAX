"""
MedRAX MCP Server - Model Context Protocol Integration

This module provides MCP server implementation for MedRAX medical imaging tools.
Follows DDD (Domain-Driven Design) architecture.

Layers:
- domain/: Core entities and protocols
- application/: Service layer orchestrating tools
- infrastructure/: Tool wrappers for DL models
- presentation/: FastMCP tool definitions

Usage:
    # Run MCP server
    python -m medrax.mcp.server

    # Or use as library
    from medrax.mcp import create_mcp_app
    app = create_mcp_app()
"""

from medrax.mcp.server import create_mcp_app

__all__ = ["create_mcp_app"]
__version__ = "0.1.4-alpha"
