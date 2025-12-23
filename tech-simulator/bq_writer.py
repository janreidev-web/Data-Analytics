from google.cloud import bigquery

def append_df_bq(df, table_id, write_disposition="WRITE_APPEND"):
    """
    Append a pandas DataFrame to BigQuery
    """
    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=True
    )

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config
    )

    job.result()
    print(f"✓ Loaded {len(df):,} rows into {table_id}")
