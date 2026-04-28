import weaviate
from weaviate.classes.init import Auth

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="2me0s79vrzky3ota7obp6w.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials=Auth.api_key("dzhSQmdxcGluSFJLTGtnZl9tWmwvVFRwSHhGSUs2eFVibEhXUDFyWGwrY1l6Tit1dFYzMXRrRHljZDI0PV92MjAw"),
    skip_init_checks=True
)
print("Connected:", client.is_ready())
client.close()