# AI Teaching Assistant

## About

Coming soon. 

## Deployment Instructions

### Step 1: Create and Deploy an Azure Prompt Flow

Reference Article: [Create your own copilot using Azure Prompt flow and Streamlit](https://techcommunity.microsoft.com/blog/educatordeveloperblog/create-your-own-copilot-using-azure-prompt-flow-and-streamlit/4137426)

- Go to [Azure AI Foundry](https://ai.azure.com/)
- Follow the steps in the Reference Article to create an Azure AI Search resource, Azure AI Foundry Hub, Project, Model Deployments and a Prompt Flow (starting from the "Multi-Round Q&A on Your Data" template)
- Modify the Prompt Flow as needed for your use case (see the YAML files of our customized Prompt Flow as an example here: [Prompt Flow for MPE Experiment 2025](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/azure-prompt-flow-examples/mpe-experiment-2025))
- Deploy and test the Prompt Flow as described in Steps 8 and 9 of the Reference Article
- Note your deployment's Endpoint and Key (e.g. you may find this by navigating to My Assets > Models & Endpoints, then find your deployment and click "Get Endpoint")

Notes:
- If you change the default inputs to and/or outputs of your Prompt Flow, it may not continue to work with the AI Teaching Assistant application in the [app](https://github.com/sigmedia/ai-teaching-assistant/tree/main/app) folder of this repository
- When deploying your Prompt Flow, if you keep "Inferencing data collection" Enabled, this will store the inputs to and outputs from your Prompt Flow (including query and response text) in an Azure blob storage container in your Azure AI Foundry Project. You may want to consider whether this is appropirate and/or configure the data retention policy of the storage container depending on your specific data protection requirements.

### Step 2: Create a Database Server & Database for Local Testing

- Go to [Azure Portal](https://portal.azure.com/)
- Create an Azure SQL Server with a SQL Database for testing/development
- Navigate the SQL Database, and go to Settings > Connection Strings > ODBC
- Note the ODBC SQL Authentication Connection String

Notes:
- We used the DTU based purchasing model with "Locally-redundant backup storage"
- You may want to consider changing the default database collation to support specific international languages

### Step 3: Clone this Repository Locally

- Clone this repository locally for testing

### Step 4: Prepare Hashed App Password For Local Testing

- Navigate to the [tools/app-setup]([https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/app-setup) folder
- Create a virtual environment (optional, but recommended)
- Install packages in requirements.txt (e.g. pip install -r requirements.txt)
- Run prep_password.py with your desired password as the only command line argument (e.g. python3 prep_password.py MyGr8Passw0rd!)
- Note the command line output (which is your password hashed)

### Step 5: Set Up Environment Variables For Local Testing

- Navigate to the [tools/environment-variables-reference]([https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/envinronment-variables-reference) folder
- Copy the [reference.env](https://github.com/sigmedia/ai-teaching-assistant/blob/main/tools/environment-variables-reference/reference.env) file to the root of the [app](https://github.com/sigmedia/ai-teaching-assistant/tree/main/app) folder

More coming soon. 

## Third Party Licenses

This project uses KaTeX which is licensed under the MIT License. 
See [KATEX-LICENSE.txt](licenses/KATEX-LICENSE.txt) for details.
