# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4-alpha] - 2025-12-31

### Added
- **MCP Server** - Model Context Protocol integration for VS Code Copilot
  - DDD architecture with 4 layers (Domain, Infrastructure, Application, Presentation)
  - 9 MCP tools: `register_image`, `process_dicom`, `get_dicom_metadata`, `classify_cxr`, `segment_anatomy`, `ask_cxr_expert`, `get_supported_pathologies`, `get_supported_organs`, `list_registered_images`
  - Support for stdio and SSE transports
  - Lazy loading for heavy ML model dependencies
- **VS Code Integration**
  - `.vscode/mcp.json` - MCP server configuration
  - `.vscode/settings.json` - Python development settings
- **Unit Tests** - 14 tests for MCP server components

### Changed
- **pyproject.toml** modernization
  - Updated to Python 3.12
  - Reorganized dependencies by category (HTTP, Data, ML, Medical Imaging, etc.)
  - MCP dependency moved from optional to required
- **medrax/mcp/__init__.py** - Lazy import pattern to avoid loading heavy dependencies on module import

### Fixed
- Import error when `mcp` package not installed

## [0.1.0] - 2025-06-01

### Added
- Initial MedRAX Plus fork from bowang-lab/MedRAX
- Constitutional AI Framework (CONSTITUTION.md + Bylaws + Skills)
- Memory Bank for cross-session project knowledge
- 13 Claude Skills for AI-assisted development
- DDD architecture foundation

---

[Unreleased]: https://github.com/u9401066/MedRAX/compare/v0.1.4-alpha...HEAD
[0.1.4-alpha]: https://github.com/u9401066/MedRAX/compare/v0.1.0...v0.1.4-alpha
[0.1.0]: https://github.com/u9401066/MedRAX/releases/tag/v0.1.0
