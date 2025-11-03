from datetime import datetime
import logging
from os import getenv

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.appcontainers import ContainerAppsAPIClient

def stop_app(app_name: str, resource_group: str = getenv("AZURE_RESOURCE_GROUP", "rg-lion-app")) -> func.HttpResponse:
    try:
        credential = DefaultAzureCredential()
        subscription_id = getenv("AZURE_SUBSCRIPTION_ID")
        client = ContainerAppsAPIClient(credential, subscription_id)

        app = client.container_apps.get(resource_group, app_name)
        state = app.provisioning_state.lower()

        if state == "running":
            poller = client.container_apps.begin_stop(resource_group, app_name)
            poller.result()  # Wait for completion

            logging.info(f"{app_name} stopped on {datetime.now()}")
            return func.HttpResponse(f"App '{app_name}' stopped successfully.", status_code=200)
        else:
            return func.HttpResponse(f"App '{app_name}' is already stopped or provisioning: {state}", status_code=200)

    except Exception as e:
        logging.error(f"Error while stopping app '{app_name}': {str(e)}")
        return func.HttpResponse(f"Error while stopping app '{app_name}': {str(e)}", status_code=500)

def main(req: func.HttpRequest) -> func.HttpResponse:
    app_name = req.params.get("app_name")
    if not app_name:
        return func.HttpResponse("Missing required parameter: app_name", status_code=400)
    
    return stop_app(app_name)
