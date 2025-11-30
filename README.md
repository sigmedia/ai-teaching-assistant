# AI Teaching Assistant

## About

A custom, responsive web application for deploying an online AI Teaching Assistant (AI-TA) that leverages Microsoft Azure services including Azure AI Foundry, Prompt Flow and Azure SQL Database.  

This software was developed at Trinity College Dublin for educational research purposes.

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Motion Picture Engineering (MPE) Deployment 2025

- Prompt Flow: [tools/azure-prompt-flow-examples/mpe-experiment-2025](https://github.com/sigmedia/ai-teaching-assistant/tree/4e1c4f6935a680b7c7c2de8d09521f560c4b7be5/tools/azure-prompt-flow-examples/mpe-experiment-2025)
- Prompt: [tools/azure-prompt-flow-examples/mpe-experiment-2025/chat_with_context.jinja2](https://github.com/sigmedia/ai-teaching-assistant/blob/4e1c4f6935a680b7c7c2de8d09521f560c4b7be5/tools/azure-prompt-flow-examples/mpe-experiment-2025/chat_with_context.jinja2)
- Course exit survey questions & data: [tools/evaluation/exit-survey/mpe-experiment-2025](https://github.com/sigmedia/ai-teaching-assistant/tree/4e1c4f6935a680b7c7c2de8d09521f560c4b7be5/tools/evaluation/exit-survey/mpe-experiment-2025)

#### AI-TA Specifications ####

- Web application release version: [v1.0.0](https://github.com/sigmedia/ai-teaching-assistant/releases/tag/v1.0.0)

Azure service specifications & deployment regions:

- Azure AI Hub & Project: Sweden Central
- Azure OpenAI Models: gpt-4o-mini & text-embedding-ada-002, Sweden Central 
- Azure AI Search: Basic, North Europe
- Azure Virtual Machine: Standard_E8s_v3 (likely over-provisioned), Sweden Central
- Azure SQL Database: Standard S0 (10 DTUs), North Europe
- Azure Web App Plan: B3, North Europe

## License
This project is licensed under GPLv3. See LICENSE for details.

## Cookie Usage
This application uses an anonymous session cookie for functionality.

## Important Notice for Deployers
This software is provided "as is" under GPLv3. If you deploy this application, you are responsible for compliance with applicable data protection and privacy laws in your jurisdiction, including:

- Providing appropriate privacy policies
- Obtaining necessary user consents
- Complying with GDPR, ePrivacy Directive, CCPA, HIPAA, or other relevant regulations

Please conduct appropriate due diligence before deploying it.

The original developers and institution are not liable for how you deploy or use this software.

## Deployment Instructions

### Step 1: Create and Deploy an Azure Prompt Flow

Reference Article: [Create your own copilot using Azure Prompt flow and Streamlit](https://techcommunity.microsoft.com/blog/educatordeveloperblog/create-your-own-copilot-using-azure-prompt-flow-and-streamlit/4137426)

- Go to [Azure AI Foundry](https://ai.azure.com/)
- Follow the steps in the Reference Article to create an Azure AI Search resource, Azure AI Foundry Hub, Project, Model Deployments and a Prompt Flow (starting from the "Multi-Round Q&A on Your Data" template)
- Modify the Prompt Flow as needed for your use case (see the YAML files of our customized Prompt Flow as an example here: [Prompt Flow for MPE Experiment 2025](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/azure-prompt-flow-examples/mpe-experiment-2025))
- Deploy and test the Prompt Flow as described in Steps 8 and 9 of the Reference Article
- Note your deployment's Endpoint and Key (e.g. you may find this by navigating to My Assets > Models & Endpoints, then find your deployment and click "Get Endpoint")

Notes:
- If you change the default inputs to and/or outputs of your Prompt Flow, it may not continue to work with the AI Teaching Assistant web application (which is in the [app](https://github.com/sigmedia/ai-teaching-assistant/tree/main/app) folder of this repository)
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

### Step 3: Fork and Clone this Repository Locally

- Fork this repository in GitHub, and navigate to your fork
- Clone the fork to your local machine

### Step 4: Prepare a Hashed Password for Logging in to the App Locally

- Navigate to the [tools/app-setup](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/app-setup) folder locally
- Create a new virtual environment and activate it (optional, but recommended)
- Install the packages in requirements.txt (e.g. `pip install -r requirements.txt`)
- Run prep_password.py with your desired password as the only command line argument (e.g. `python3 prep_password.py MyGr8Passw0rd!`)
- Take note of the command line output (this is your password hashed)

### Step 5: Set Up Environment Variables for Local Testing

- Navigate to the [tools/environment-variables-reference](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/environment-variables-reference) folder locally
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
- Install the packages in requirements.txt (e.g. `pip install -r requirements.txt`)
- You may need to install [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server?view=sql-server-ver17) locally if you don't already have it installed. The process for this will vary depending on your local operating system. 
- Start the app with the following command: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- Go to http://127.0.0.1:8000 in your browser
- Log in to the app, and test it by chatting with the AI-TA. You should see a new session and new message entries appearing in the tables of your test/development database when you refresh it.

### Step 7: Deploy the App as a Web App Online

- If you want to use a separate Prompt Flow for production, copy the one you created in Step 1, deploy it as a new endpoint, and take note of its Endpoint and Key (see Reference Article)
- If you want to use a separate database for production, create a new SQL Database, and take note of it's ODBC SQL Authentication Connection String (like in Step 2 above)
- Fork this repository on if you haven't already, and clone the fork locally
- Go to [Azure Portal](https://portal.azure.com/)
- Create a new Web App. This is a multi-step process.
- In the "Basics" step, choose "Code" for the Publish setting and "Python 3.10" for Runtime Environment
- Skip the "Database" step
- In the "Deployment" step, set Continuous Deployment to "Enable". Then, under GitHub Settings link your GitHub account, choose your Organization, set Repository to your fork, and set Branch to "main".
- Skip the rest by clicking "Review & Create" and then "Create" to finish creating the Web App. This deployment will likely fail, since Azure's default GitHub workflow expects the app's entry point to be at the root of the GitHub repo. The following few steps will fix this.
- If you're using [GitHub](https://github.com), go to your forked repository there and navigate to its Actions tab. You will see a warning that starts with "Workflows aren’t being run on this forked repository. Because this repository contained workflow files when it was forked, we have disabled them from running on this fork..." This is happening because there are some .yaml files in the [Prompt Flow for MPE Experiment 2025](https://github.com/sigmedia/ai-teaching-assistant/tree/main/tools/azure-prompt-flow-examples/mpe-experiment-2025)) folder. To fix this, click the green button that says "I understand my workflows, go ahead and enable them"
- Go back to [Azure Portal](https://portal.azure.com/), open up your Web App, navigate to Deployment > Deployment Center and click the "Sync" button.
- Go back to your local repository and do a `git pull`. You will see that a new file has been automatically been created in the folder [.github/workflows](https://github.com/sigmedia/ai-teaching-assistant/tree/851c65bcf23b77c118b842f0a5c19e0aa4f193ad/.github/workflows) at the root of the cloned repository. This file will be called something like main_yourwebappname.yml. This is the github workflow configuration.
- Open this file locally for editing
- Edit the file, making the same changes as the first three changes in this commit: [https://github.com/sigmedia/ai-teaching-assistant/commit/f92a6afb10f2dc6c1a5aaf4a09eef9c32ab0a9a7](https://github.com/sigmedia/ai-teaching-assistant/commit/3851a01bb762a0b7ac6ecac658180ceeebd0b357)
- Commit and push these changes
- Go to [Azure Portal](https://portal.azure.com/)
- Open up your Web App
- Navigate to Deployment > Deployment Center > Logs. You should see the Web App being automatically re-deployed. Once it's finished, the result should be Success.
- Navigate to Settings > Environment Variables > App settings, and add/edit the following Environment variables:
  
| Envronment Variable      | What It Does                                                                                                                                                                           | Some Example Value(s)         |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| ENVIRONMENT              | Set to **prod** for production. Prod forces HTTPS transmission of session data and should be set for production environments.                                                          | prod                          |
| AZURE                    | Including this tells the app that it's operating in the Azure environment (and hence not to load environment variables using dotenv). Doesn't need to have a value.                    |                               |
| BOT_NAME                 | Name of your AI Teaching Assistant (AI-TA). Displayed in various places in the app (e.g. on the login page and in the app header)                                                      | MPE AI-TA                     |
| COURSE_NAME              | Name of the course supported by your AI Teaching Assistant. Displayed in various places in the app (e.g. on the login page).                                                           | Motion Picture Engineering    |
| GLOBAL_USERNAME          | Universal username for logging into the app online. Choose it yourself.                                                                                                                | MPE_student                   |  
| GLOBAL_PASSWORD          | Universal password for logging into the app online, hashed using bcrypt. Hash your production password using the same technique as per Step 4, although it's advised to choose a different password for production versus development/testing | |
| AGREEMENT_PART_1_VERSION | A place to store the name and version of the document/clause that your users will agree to in User Agreement Part 1 on the login page                                                  | PIL.pdf version 2.1           |  
| AGREEMENT_PART_1_VERSION | A place to store the name and version of the document/clause that your users will agree to in User Agreement Part 2 on the login page=                                                 | Data_Protection_Policy.pdf v3 |
| MIDDLEWARE_SECRET        | Secret key that keeps the anonymous session cookie from being tampered with. Generate this using a cryptographically secure random generator according to security best practises.     |                               |      
| CHAT_API_ENDPOINT        | Put your production Prompt Flow deployment's endpoint URL here (i.e. the Endpoint you took note of earlier)                                                                            |                               |  
| CHAT_API_KEY             | Put your production Prompt Flow deployment's key here (i.e. the Key you took note of earlier)                                                                                          |                               |
| DB_CONN_STR              | Put your production database's ODBC SQL Authentication Connection String here (i.e. what you took note of earlier)                                                                     |                               |  
| MAX_INTERACTIONS_HISTORY | Determines how many of the (most recent) query/response pairs from the current session that will be remembered by the AI-TA as conversation history                                    | 10                            |
| MAX_INACTIVE_TIME_MINS   | Determines how long (in minutes) the AI-TA can be left without activity before the session is deemed inactive                                                                          | 240                           |  
| SCHEDULER_FREQ_MINS      | Determines the run frequency (in minutes) of an automated job that formally marks sessions older than MAX_INACTIVE_TIME_MINS as inactive (and a new session will be created if the user logs into the AI-TA again) |120|  
| SCM_DO_BUILD_DURING_DEPLOYMENT | Leave this equal to 1 if you want the app's build process to run during deployment                                                                                               | 1                             |
| WEBSITE_HTTPLOGGING_RETENTION_DAYS | Determines the number of days that app logs will be retained for. There is nothing sensitive in this app's logs. There is info that may be useful for debugging production issues | 7                        |
| WEBSITES_CONTAINER_START_TIME_LIMIT | Number of seconds before the Web App will stop the container startup process. Increase this if the app isn't starting up quickly enough.                                    | 600                           |

- On Save, confirm to restart the Web App
- Navigate to Settings > Configuration > General Settings
- Add the following to the "Startup Command" field: `gunicorn -c gunicorn.conf.py --bind 0.0.0.0:8000 main:app`
- On Save, confirm to restart the Web App
- After it has restarted, click on "Default Domain"
- Log in to the app, and test it by chatting with the AI-TA. You should see a new session and new message entries appearing in the tables of your production database when you refresh it.

Note:
- If you need to manually re-start your Web App at any point, you do so by navigating to Overview and clicking "Restart"
- You can manually trigger re-deployment of your Web App's code by navigating to Deployment Center > Settings and clicking "Sync"

## Third Party Licenses

This project includes third-party components distributed under open-source licenses.  
See [THIRD_PARTY_LICENSES.txt](./THIRD_PARTY_LICENSES.txt) for a full list.

The project also bundles **KaTeX** (by Khan Academy) for mathematical typesetting, licensed under the MIT License.  
See [licenses/KATEX-LICENSE.txt](./licenses/KATEX-LICENSE.txt) for details.

