# Bring your own Data Chat QnA

⚠️ **Important**: This prompt flow uses proprietary dependencies. See the License Notice section below.

This is the RAG-based prompt flow that was used for a pilot deployment of the AI Teaching Assistant for Motion Picture Engineering in 2025


## Prerequisites

- Connection: Azure OpenAI or OpenAI connection, with the availability of chat and embedding models/deployments.

## Tools used in this flow

* LLM tool
* Embedding tool
* Vector Index Lookup tool
* Python tool

## How to Use This Flow

### Deploy to Azure AI Foundry

1. Go to [Azure AI Foundry](https://ai.azure.com/)
2. Navigate to your project
3. Select **Prompt Flow** → **Create** → **Upload from local**
4. Choose this folder to import the complete flow
5. Configure your connections:
   - Azure OpenAI connection for chat and embeddings
   - Azure Cognitive Search connection for vector index
6. Test the flow with sample questions
7. Deploy as an endpoint when ready

## License Notice

⚠️ **This is an example template, not part of the main application.**

This prompt flow requires `promptflow_vectordb[azure]` (specified in `requirements.txt`) which is licensed under **Microsoft's proprietary terms**, not open source.

**Important notes:**
- This flow is a configuration template for Azure AI Foundry
- Users who deploy or run this flow are responsible for reviewing and complying with all dependency license terms
- These dependencies are separate from the main project's GPLv3 license
- By using this flow, you accept the terms of the proprietary dependencies

For dependency license details, see: https://pypi.org/project/promptflow-vectordb/