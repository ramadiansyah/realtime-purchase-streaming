"""
Apache Beam Dataflow Streaming Pipeline for Purchase Events.

This script reads purchase events from a Pub/Sub topic, parses them into structured
format, writes the raw data into a BigQuery table, applies a transformation (adds a
status column), and then writes the transformed data into another BigQuery table.

Modules:
    - ParseMessage: Parses raw Pub/Sub JSON messages.
    - TransformData: Adds a 'status' field based on total_price.
    - run(): Sets up and runs the Beam pipeline with DataflowRunner.

Usage:
    $ python main.py

Author: Rizki Ramadiansyah
"""

import os
import json
import apache_beam as beam
import dateutil.parser
from typing import Any, Dict, Iterable
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions
from schema import purchase_stream_raw_schema, purchase_stream_transformed_schema
from utils.config_loader import load_config

CONFIG_PATH = "config/config.yaml"
config = load_config(CONFIG_PATH)

class ParseMessage(beam.DoFn):
    """
    A DoFn that parses a Pub/Sub message (bytes) into a structured dictionary.
    It performs data type conversions and standardizes timestamp formatting.
    """

    # def process(self, element):
    def process(self, element: bytes) -> Iterable[Dict[str, Any]]:
        """
        Parse a JSON-encoded byte string into a dictionary with typed values.

        Args:
            element (bytes): Raw message from Pub/Sub in byte format.

        Yields:
            Dict[str, Any]: Parsed and validated purchase record.
        """
        try:
            row = json.loads(element.decode("utf-8"))

            # Convert fields explicitly
            row["customer_id"] = int(row["customer_id"])
            row["product_id"] = int(row["product_id"])
            row["quantity"] = int(row["quantity"])
            row["unit_price"] = float(row["unit_price"])
            row["total_price"] = float(row["total_price"])

            # Ensure created_at is in RFC3339 (ISO 8601) string
            if not row["created_at"].endswith("Z"):
                dt = dateutil.parser.parse(row["created_at"])
                row["created_at"] = dt.isoformat() + "Z"
            yield row
            
        except Exception as e:
            # Handle malformed data
            print(f"Error parsing JSON: {e}")


class TransformData(beam.DoFn):
    """
    A DoFn that adds a 'status' column to the parsed data.
    """

    # def process(self, element):
    def process(self, element: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        """
        Append a 'status' field based on total_price value.

        Args:
            element (Dict[str, Any]): A purchase record.

        Yields:
            Dict[str, Any]: Transformed record with additional status field.
        """
        # simpel tranform data
        element["status"] = "success" if element["total_price"] > 0 else "failed"
        yield element


def run() -> None:
    """
    Main function to run the Apache Beam streaming pipeline.

    Reads messages from Pub/Sub, writes raw data to BigQuery,
    applies transformation, and writes transformed data to another BigQuery table.
    """
    options = PipelineOptions(
        streaming=True,
        save_main_session=True,
    )
    
    # Load config values
    project_id = config['project_id']
    gcp_sa_email = config['gcp_sa_email']
    pubsub_topic = config['pubsub_topic']
    gcs_dataflow = config['gcs_dataflow']
    dataflow_job_name = config['dataflow_job_name']
    bq_table = config['bq_table']
    bq_table_transformed = config['bq_table_transformed']

    # Configure GCP options
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = project_id
    google_cloud_options.job_name = dataflow_job_name
    google_cloud_options.staging_location = f"gs://{gcs_dataflow}/staging"
    google_cloud_options.temp_location = f"gs://{gcs_dataflow}/temp"
    google_cloud_options.service_account_email = gcp_sa_email
    google_cloud_options.region="us-central1"
    os.environ['BEAM_WORKER_REGION'] = 'us-central1-b'
    options.view_as(StandardOptions).runner = "DataflowRunner"
    # options.view_as(StandardOptions).runner = "DirectRunner" #for local running

    # Define pipeline
    with beam.Pipeline(options=options) as pipeline:
        parsed = (
            pipeline
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=f"projects/{project_id}/topics/{pubsub_topic}")
            | "Parse JSON" >> beam.ParDo(ParseMessage())
        )

        # Write raw data to BigQuery
        parsed | "WriteToBigQueryRaw" >> beam.io.WriteToBigQuery(
            bq_table,
            schema=purchase_stream_raw_schema,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )

        # Transform and write transformed data to BigQuery
        (
            parsed
            | "Transform Data" >> beam.ParDo(TransformData())
            | "WriteToBigQueryTransformed" >> beam.io.WriteToBigQuery(
                bq_table_transformed,
                schema=purchase_stream_transformed_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == "__main__":
    run()
