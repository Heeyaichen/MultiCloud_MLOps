from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import os

def rollback_model():
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
        resource_group_name="rg-guardian-ai-prod",
        workspace_name="guardian-ml-workspace"
    )
    
    endpoint_name = "nsfw-endpoint"
    endpoint = ml_client.online_endpoints.get(endpoint_name)
    
    endpoint.traffic = {"champion": 0, "previous-champion": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    print("✅ Model rolled back to previous version!")

if __name__ == "__main__":
    rollback_model()
