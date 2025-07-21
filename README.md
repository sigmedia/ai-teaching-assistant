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

### Step 2: Create a Database Server and Database for Local Testing/Development

- Go to [Azure Portal](https://portal.azure.com/)
- Create an Azure SQL Server containing an SQL Database for testing/development
- Navigate the SQL Database, and go to Settings > Connection Strings > ODBC
- Take note of the ODBC SQL Authentication Connection String

Notes:
- We used the DTU based purchasing model with "Locally-redundant backup storage"
- If you chose to give your Azure SQL Server "Public network access" (i.e. the default setting), it will be protected with Firewall rules. You will need to add your local client's IP address to these to be able to run the app locally. This can be done via Security > Networking > Firewall rules > "+ Add your client IPv4 address" and then Save.
- You may want to consider changing the default database collation to support specific international languages

### Step 3: Clone this Repository Locally

- Clone this repository on your local machine.

### Step 4: Prepare a Hashed Password for Logging in to the App Locally

- Navigate to the [tools/app-setup]([https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/app-setup) folder locally
- Create a new virtual environment and activate it (optional, but recommended)
- Install the packages in requirements.txt (e.g. pip install -r requirements.txt)
- Run prep_password.py with your desired password as the only command line argument (e.g. python3 prep_password.py MyGr8Passw0rd!)
- Take note of the command line output (this is your password hashed)

### Step 5: Set Up Environment Variables for Local Testing

- Navigate to the [tools/environment-variables-reference]([https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/envinronment-variables-reference) folder locally
- Copy the [reference.env](https://github.com/sigmedia/ai-teaching-assistant/blob/main/tools/environment-variables-reference/reference.env) file to the root of the [app](https://github.com/sigmedia/ai-teaching-assistant/tree/main/app) folder locally
- Change the name from reference.env to .env
- Open the .env file and add values for all environment variables. Here is a guide to what they all are:

| Envronment Variable      | What It Does                                                                                                                                                                                                       | Some Example Value(s)         |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| ENVIRONMENT              | Set to **dev** for local testing/devlopement, and **prod** for production. Prod forces HTTPS transmission of session data and should be set for production environments                                            | dev/prod                      |
| BOT_NAME                 | Name of your AI Teaching Assistant (AI-TA). Displayed in various places in the app (e.g. on the login page and in the app header)                                                                                  | Test MPE AI-TA                |
| COURSE_NAME              | Name of the course supported by your AI Teaching Assistant. Displayed in various places in the app e.g. on the login page.                                                                                         | Motion Picture Engineering    |
| GLOBAL_USERNAME          | Universal username for logging into the app. Choose it yourself.                                                                                                                                                   | Test_student                  |  
| GLOBAL_PASSWORD          | Universal password for logging into the app, hashed using bcrypt (i.e. the hashed password you took note of in Step 4)                                                                                             |                               |
| AGREEMENT_PART_1_VERSION | A place to store the name and version of the document/clause that your users will agree to in User Agreement Part 1 on the login page                                                                              | PIL.pdf version 2.1           |  
| AGREEMENT_PART_1_VERSION | A place to store the name and version of the document/clause that your users will agree to in User Agreement Part 2 on the login page                                                                              | Data_Protection_Policy.pdf v3 |
| MIDDLEWARE_SECRET        | Secret key that keeps the anonymous session cookie from being tampered with. Generate this using a cryptographically secure random generator according to security best practises.                                 |                               |             
| CHAT_API_ENDPOINT        | Put your Prompt Flow deployment's endpoint URL here (i.e. the Endpoint you took note of in Step 1)                                                                                                                 |                               |  
| CHAT_API_KEY             | Put your Prompt Flow deployment's key here (i.e. the Key you took note of in Step 1)                                                                                                                               |                               |
| DB_CONN_STR              | Put our database's ODBC SQL Authentication Connection String here (i.e. what you took note of in Step 2)                                                                                                           |                               |  
| MAX_INTERACTIONS_HISTORY | Determines how many of the (most recent) query/response pairs from the current session that will be remembered by the AI-TA as conversation history                                                                | 10                            |
| MAX_INACTIVE_TIME_MINS   | Determines how long (in minutes) the AI-TA can be left without activity before the session is deemed inactive                                                                                                      | 15                            |  
| SCHEDULER_FREQ_MINS      | Determines the run frequency (in minutes) of an automated job that formally marks sessions older than MAX_INACTIVE_TIME_MINS as inactive (and a new session will be created if the user logs into the AI-TA again) | 30                            | 

### Step 6: Run and Test the App Locally

- Navigate to the [app](https://github.com/sigmedia/ai-teaching-assistant/tree/main/app) folder locally
- Create a new virtual environment and activate it (optional, but recommended)
- Install the packages in requirements.txt (e.g. pip install -r requirements.txt)
- Start the app with the following command: uvicorn main:app --reload --host 127.0.0.1 --port 8000
- Go to http://127.0.0.1:8000 in your browser
- Log in to the app, and test it by chatting with the AI-TA. You should see a new session and new message entries appearing in the tables of your test/development database when you refresh it.

### Step 7: Deploy the App in Production Online

Coming soon.

## Third Party Licenses

This project uses KaTeX which is licensed under the MIT License. 
See [KATEX-LICENSE.txt](licenses/KATEX-LICENSE.txt) for details.
