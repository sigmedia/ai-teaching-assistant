# Azure Prompt Flow Examples

This directory contains example Azure AI Foundry Prompt Flows. Each subdirectory is a complete, importable flow.

## Available Examples

- **mpe-experiment-2025**: This is the RAG-based prompt flow that was used for a pilot deployment of the AI Teaching Assistant for Motion Picture Engineering in 2025.

## Usage

Each example can be imported directly into Azure AI Foundry. See the README in each folder for details.

## Important: License Notice

⚠️ **These are example templates, not part of the main application.**

These prompt flows use Azure-specific runtime dependencies with **proprietary licensing**, including `promptflow-vectordb[azure]` which is licensed under Microsoft's proprietary terms.

**Important notes:**
- These files are configuration templates for Azure AI Foundry
- Dependencies run in Azure's environment, not as part of the main application
- Users who deploy or run these flows are responsible for reviewing and complying with all dependency license terms
- These dependencies are separate from the main project's GPLv3 license

For dependency details, see: https://pypi.org/project/promptflow-vectordb/