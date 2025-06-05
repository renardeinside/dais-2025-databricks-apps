import streamlit as st
from dais_2025_databricks_apps.config import Config
import plotly.express as px

def dbsql_basics(config: Config) -> None:
    st.header("Accessing Databricks SQL")
    st.markdown(
        """
        This page demonstrates how to access Databricks SQL using Databricks SQL Connector for Python.
        You can run SQL queries and visualize the results directly in this Streamlit app.
        """
    )
    st.subheader("Querying Sample Data")
    st.markdown(
        """
        Below is a sample query that retrieves the total number of trips by pickup ZIP code from the NYC Taxi dataset.
        You can modify this query to explore different datasets or perform various analyses.
        """
    )
    with st.spinner("Executing query...", show_time=True):
        st.dataframe(
            config.execute_query(
                """
                select pickup_zip, count(*) as total
                from samples.nyctaxi.trips
                where pickup_zip is not null
                group by pickup_zip
                order by total desc
                """
            )
        )

    st.subheader("Building charts")
    st.markdown(
        """
        You can also create visualizations based on the query results. Below is a simple bar chart showing the total number of trips by pickup ZIP code.
        """
    )

    with st.spinner("Generating chart...", show_time=True):
        df = config.execute_query(
            """
            select pickup_zip, count(*) as total
            from samples.nyctaxi.trips
            where pickup_zip is not null
            group by pickup_zip
            order by total desc
            """
        )
        fig = px.bar(
            df, x="pickup_zip", y="total", title="Total Trips by Pickup ZIP Code"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Executing Custom Queries")
    st.markdown(
        """
        You can execute any custom SQL query using the input box below. The results will be displayed in a table format.
        """
    )
    st.warning(
        """
        Note for developers: Ensure that your SQL query is valid and does not contain any harmful commands. 
        This app does not sanitize input, so be cautious with the queries you run.
        """
    )
    custom_query = st.text_area(
        "Enter your SQL query here:",
        value="SELECT * FROM samples.nyctaxi.trips LIMIT 10",
        height=150,
    )
    if st.button("Execute Query"):
        with st.spinner("Executing custom query...", show_time=True):
            try:
                result_df = config.execute_query(custom_query)
                st.dataframe(result_df)
            except Exception as e:
                st.error(f"Error executing query: {e}")
