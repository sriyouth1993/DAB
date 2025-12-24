# Databricks notebook source

from pyspark.sql import SparkSession
from pyspark.sql.functions import monotonically_increasing_id, row_number
from pyspark.sql.window import Window
from azure.identity import ClientSecretCredential
from azure.cosmos import CosmosClient
import logging
import random

# Spark session
spark = SparkSession.builder.appName("CosmosDBIntegration").getOrCreate()

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Read secrets from Azure Key Vault (Databricks Secret Scope)
SCOPE_NAME = "cosmos-kv-scope"

tenant_id = dbutils.secrets.get(scope=SCOPE_NAME, key="tenant-id")
client_id = dbutils.secrets.get(scope=SCOPE_NAME, key="sp-client-id")
client_secret = dbutils.secrets.get(scope=SCOPE_NAME, key="sp-client-secret")
subscription_id = dbutils.secrets.get(scope=SCOPE_NAME, key="subscription-id")

# Cosmos DB details
cosmos_endpoint = "https://sri-cus-dev-cosmos-acct.documents.azure.com:443/"
cosmos_database_name = "Sri_Finance_Products"
cosmos_container_name = "test"

# Authenticate using Service Principal
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

client = CosmosClient(cosmos_endpoint, credential)
logging.info("Authenticated to Cosmos DB")

# Cosmos Spark Connector config
config = {
    "spark.cosmos.accountEndpoint": cosmos_endpoint,
    "spark.cosmos.auth.type": "ServicePrincipal",
    "spark.cosmos.account.subscriptionId": subscription_id,
    "spark.cosmos.account.resourceGroupName": "sri-cus-dev-cosmos-rg",
    "spark.cosmos.account.tenantId": tenant_id,
    "spark.cosmos.auth.aad.clientId": client_id,
    "spark.cosmos.auth.aad.clientSecret": client_secret,
    "spark.cosmos.database": cosmos_database_name,
    "spark.cosmos.container": cosmos_container_name
}

# ADLS OAuth config
spark.conf.set(
    "fs.azure.account.auth.type.sridevcusd001.dfs.core.windows.net",
    "OAuth"
)

spark.conf.set(
    "fs.azure.account.oauth.provider.type.sridevcusd001.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
)

spark.conf.set(
    "fs.azure.account.oauth2.client.id.sridevcusd001.dfs.core.windows.net",
    client_id
)

spark.conf.set(
    "fs.azure.account.oauth2.client.secret.sridevcusd001.dfs.core.windows.net",
    client_secret
)

spark.conf.set(
    "fs.azure.account.oauth2.client.endpoint.sridevcusd001.dfs.core.windows.net",
    f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
)

# -----------------------------
# Create sample data
# -----------------------------
data_schema = ["id_data", "name", "age", "city", "salary"]

data = [
    (
        i,
        f"Name {i}",
        random.randint(20, 60),
        random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
        random.randint(50000, 150000)
    )
    for i in range(1, 10)
]

df = spark.createDataFrame(data, schema=data_schema)

logging.info("Source data created")

# -----------------------------
# Add Cosmos-compatible string id
# -----------------------------
window_spec = Window.orderBy(monotonically_increasing_id())
df = df.withColumn("id", row_number().over(window_spec).cast("string"))

df.show()
logging.info(f"Record count: {df.count()}")

# -----------------------------
# Write to Cosmos DB
# -----------------------------
logging.info("Writing data to Cosmos DB")

df.coalesce(1) \
  .write \
  .format("cosmos.oltp") \
  .mode("append") \
  .options(**config) \
  .save()

logging.info("Data successfully written to Cosmos DB")