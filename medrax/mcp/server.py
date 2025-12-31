"""
MedRAX MCP Server - Main server module

This module provides the FastMCP server implementation for MedRAX.
It creates and configures the MCP server with all tools, prompts, and resources.

Usage:
    # Run directly
    python -m medrax.mcp.server
    
    # Or import and create app
    from medrax.mcp.server import create_mcp_app
    app = create_mcp_app()
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from medrax.mcp.application.services import MedRAXServiceContainer
from medrax.mcp.presentation.tools import register_tools
from medrax.mcp.presentation.prompts import register_prompts
from medrax.mcp.presentation.resources import register_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_mcp_app(
    name: str = "medrax-mcp",
    device: Optional[str] = None,
    temp_dir: Optional[Path] = None,
    lazy_load: bool = True,
):
    """
    Create and configure the MedRAX MCP server application.
    
    Args:
        name: Server name for MCP protocol
        device: Device for model inference (cuda/cpu/mps)
        temp_dir: Directory for temporary files
        lazy_load: If True, models are loaded on first use
        
    Returns:
        Configured FastMCP application instance
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise ImportError(
            "FastMCP is required. Install with: pip install mcp"
        )
    
    # Create FastMCP app
    app = FastMCP(name)
    
    # Create service container
    services = MedRAXServiceContainer(
        device=device,
        temp_dir=temp_dir,
        lazy_load=lazy_load,
    )
    
    # Register all components
    register_tools(app, services)
    register_prompts(app)
    register_resources(app)
    
    logger.info(f"MedRAX MCP Server '{name}' initialized")
    logger.info(f"Device: {device or 'auto'}, Lazy load: {lazy_load}")
    
    return app


def main():
    """Main entry point for running MCP server."""
    parser = argparse.ArgumentParser(
        description="MedRAX MCP Server - Medical Imaging AI for Chest X-rays"
    )
    parser.add_argument(
        "--name",
        default="medrax-mcp",
        help="Server name for MCP protocol"
    )
    parser.add_argument(
        "--device",
        choices=["cuda", "cpu", "mps"],
        default=None,
        help="Device for model inference (auto-detected if not specified)"
    )
    parser.add_argument(
        "--temp-dir",
        type=Path,
        default=None,
        help="Directory for temporary files"
    )
    parser.add_argument(
        "--eager-load",
        action="store_true",
        help="Load all models at startup instead of on first use"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport protocol"
    )
    
    args = parser.parse_args()
    
    # Create app
    app = create_mcp_app(
        name=args.name,
        device=args.device,
        temp_dir=args.temp_dir,
        lazy_load=not args.eager_load,
    )
    
    # Run server
    logger.info(f"Starting MedRAX MCP Server with {args.transport} transport...")
    
    if args.transport == "stdio":
        app.run(transport="stdio")
    else:
        app.run(transport="sse")


if __name__ == "__main__":
    main()
