# DAIS 2025 - Databricks Apps Training session

## Local setup


1. Step into the project directory:
   ```bash
   cd ~/dais-2025-databricks-apps
   ```

1. Run `uv sync` to install the required dependencies
3. Create a new `.env` file in the project directory and add the following variables:
   - `DAIS_2025_APPS_DBSQL_HTTP_PATH`: the HTTP path for Databricks SQL endpoint, copy it from the Workspace UI
   - `DAIS_2025_APPS_GENIE_SPACE_ID`: create a Genie space in your Databricks workspace and copy the space ID here
4. Authenticate with Databricks CLI:
   ```bash
   databricks configure --host=<workspace-url>
   ```

**Please make sure that you have the latest version of Databricks CLI and it's configured correctly**.

To check validity of configuration, please run:

```
databricks auth describe
```

## Run the app locally
1. Make sure you have the `.env` file created with the required variables
2. Make sure you're in the project directory:
   ```bash
   cd ~/dais-2025-databricks-apps
   ```
3. Run the app:
   ```bash
   uv run streamlit run src/dais_2025_databricks_apps/app.py
   ```


## Deploy the app to Databricks
1. Make sure you have Databricks CLI installed and configured
2. Deploy the app:
   ```
   databricks bundle deploy \
      --var='dbsql_http_path=XXXX' \
      --var='genie_space_id=YYYY' 
   ```
3. Configure the app permissions in the workspace:
   - provide the App SP with access to the Genie space you created earlier (`CAN_RUN` )
4. Run the app:
   ```
   databricks bundle run dais2025-app \
      --var='dbsql_http_path=XXXX' \
      --var='genie_space_id=YYYY' 
   ```

