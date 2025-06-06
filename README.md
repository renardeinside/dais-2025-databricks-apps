# DAIS 2025 - Databricks Apps Training session

## Local setup

1. Make sure you have `uv` installed
2. Clone this repository
3. Navigate to the cloned repository
4. Run `uv sync` to install the required dependencies
5. Setup the VSCode to use the virtual environment created by `uv`
6. Create a new `.env` file in the project directory and add the following variables:
   - `DAIS_2025_APPS_DBSQL_HTTP_PATH`: the HTTP path for your Databricks SQL endpoint, copy it from the Workspace UI
   - `DAIS_2025_APPS_GENIE_SPACE_ID`: create a Genie space in your Databricks workspace and copy the space ID here

## Run the app locally
1. Make sure you have the `.env` file created with the required variables
2. Run `make run-app` to start the app locally
3. Open your browser and navigate to `http://localhost:8051`
4. You should see the app running, and you can interact with it


## Deploy the app to Databricks
1. Make sure you have Databricks CLI installed and configured
2. Deploy the app:
   ```databricks bundle deploy```
3. Configure the app permissions in the workspace:
   - provide access to the Genie space you created earlier
   - provide access to the SQL endpoint you are using (`CAN_USE` permission is required)
4. Run the app:
   ```databricks bundle run dais2025-app```

