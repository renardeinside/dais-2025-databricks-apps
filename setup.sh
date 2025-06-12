mkdir -p ~/.streamlit

# write browser.gatherUsageStats = false into ~/.streamlit/config.toml
echo "[browser]
gatherUsageStats = false" > ~/.streamlit/config.toml

# env file 

echo "
DAIS_2025_APPS_DBSQL_HTTP_PATH=...
DAIS_2025_APPS_GENIE_SPACE_ID=...
" > ~/dais-2025-databricks-apps/.env 


echo "
[DEFAULT]
host  = https://your-databricks-workspace.com
token = paste-your-token-here
" > ~/.databrickscfg
