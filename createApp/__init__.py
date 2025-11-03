import logging
from os import getenv
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.appcontainers import ContainerAppsAPIClient
from azure.mgmt.appcontainers.models import (
    ContainerApp,
    Configuration,
    Template,
    Container,
    EnvironmentVar,
    Ingress
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request to deploy container app via SDK.')

    # Get parameters or fallbacks
    app_name = req.params.get('app_name')
    task_type = req.params.get('task_type')
    port = req.params.get('port')

    if not app_name:
        return func.HttpResponse("Missing required parameter: app_name", status_code=400)

    subscription_id = getenv("AZURE_SUBSCRIPTION_ID")
    rg = getenv("AZURE_RESOURCE_GROUP")
    location = getenv("LOCATION", "westeurope")
    app_env = getenv("APP_ENV")
    image = getenv("DOCKER_IMAGE")
    port = port or getenv("PORT", "8000")

    env_vars = {
        "AZURE_SQL_USER": getenv("AZURE_SQL_USER"),
        "AZURE_SQL_PASS": getenv("AZURE_SQL_PASS"),
        "AZURE_SQL_SERVER": getenv("AZURE_SQL_SERVER"),
        "AZURE_SQL_DB": getenv("AZURE_SQL_DB"),
        "TASK_TYPE": task_type or ""
    }

    try:
        credential = DefaultAzureCredential()

        # Ensure resource group exists
        resource_client = ResourceManagementClient(credential, subscription_id)
        if not resource_client.resource_groups.check_existence(rg):
            resource_client.resource_groups.create_or_update(rg, {"location": location})

        # Create Container App
        container_client = ContainerAppsAPIClient(credential, subscription_id)

        env_id = f"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.App/managedEnvironments/{app_env}"
        if not env_id:
            raise Exception(f"{app_env} does not exist. Create: az containerapp env create --name lion-containerapp-env --resource-group rg-lion-app --location westeurope")

        container_def = Container(name=app_name, image=image, env=[EnvironmentVar(name=k, value=v) for k, v in env_vars.items() if v])

        container_app = ContainerApp(
            location=location,
            configuration=Configuration(
                ingress=Ingress(external=True, target_port=int(port))
            ),
            template=Template(
                containers=[Container(name=app_name, image=image, env=[
                    EnvironmentVar(name=k, value=v) for k, v in env_vars.items() if v
                ])]
            ),
            environment_id=env_id
        )

        container_client.container_apps.begin_create_or_update(rg, app_name, container_app).result()

        return func.HttpResponse(f"Container App '{app_name}' deployed with image '{image}'.", status_code=201)

    except Exception as e:
        logging.error(f"Deployment failed: {str(e)}")
        return func.HttpResponse(f"Deployment failed: {str(e)}", status_code=500)