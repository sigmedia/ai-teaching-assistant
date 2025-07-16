# AI Teaching Assistant

## About

Coming soon. 

## Deployment Instructions

### Step 1: Create and Deploy an Azure Prompt Flow

Reference Article: [https://techcommunity.microsoft.com/blog/educatordeveloperblog/create-your-own-copilot-using-azure-prompt-flow-and-streamlit/4137426](https://techcommunity.microsoft.com/blog/educatordeveloperblog/create-your-own-copilot-using-azure-prompt-flow-and-streamlit/4137426)

- Go to [Azure AI Foundry](https://ai.azure.com/)
- Follow the steps in the Reference Article to create an Azure AI Search resourse, Azure AI Hub, Project, Model Deployments and a Prompt Flow (starting from the Multi-Round Q&A on Your Data template)
- Modify the Prompt Flow as needed (see the YAML files of our customized Prompt Flow as an example here: [Prompt Flow for MPE Experiment 2025](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/azure-prompt-flow-examples/mpe-experiment-2025))
- Deploy and test the Prompt Flow as a as described in Steps 8 and 9 of the Reference Article

Notes:
- If you are using this Prompt Flow in production, consider whether to keep "Inferencing data collection" Enabled or Disabled from a data projection standpoint. Enabling it means that query and response data will be collected in Azure, may be retained for a period after the endpoint deployent is deleted, and may be used for training Azure's content safety filters)

### Step 2: Create a Database

### Step 3: Clone this Repository and Test App Locally

### Step 4: Deploy the App Online

## Third Party Licenses

This project uses KaTeX which is licensed under the MIT License. 
See [KATEX-LICENSE.txt](licenses/KATEX-LICENSE.txt) for details.
