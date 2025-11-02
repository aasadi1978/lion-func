# This is very well-structured for automated app deployment. You can confidently use this in:
# Azure Functions (triggered by HTTP)
# CI/CD workflows (GitHub Actions, DevOps Pipelines)
# Internal service agents
import logging
from os import getenv
import subprocess
import azure.functions as func

def get_app_settings():
    return {
        "AZURE_SQL_USER": getenv("AZURE_SQL_USER", "lion2025"),
        "AZURE_SQL_PASS": getenv("AZURE_SQL_PASS"),
        "AZURE_SQL_SERVER": getenv("AZURE_SQL_SERVER"),
        "AZURE_SQL_DB": getenv("AZURE_SQL_DB"),
        "AZURE_STORAGE_CONNECTION_STRING": getenv("AZURE_STORAGE_CONNECTION_STRING"),
        "DOCKER_IMAGE" : getenv("DOCKER_IMAGE"),
        "APP_NAME" : getenv("APP_NAME"),
        "APP_ENV" : getenv("APP_ENV"),
        "AZURE_RESOURCE_GROUP" : getenv("AZURE_RESOURCE_GROUP"),
        "LOCATION": getenv("LOCATION")
    }


def validate_az_group(rg: str=getenv("AZURE_RESOURCE_GROUP", "rg-lion-app"), location: str = 'westeurope', maxtries=5) -> bool:
    try:
        itr=1
        while itr < maxtries:

            check_group = subprocess.run(
                        f"az group exists --name {rg}",
                        shell=True,
                        capture_output=True,
                        text=True
                    )

            logging.debug(f"CLI stdout: {check_group.stdout}")
            logging.error(f"CLI stderr: {check_group.stderr}")

            if check_group.stdout.strip().lower() == 'true':
                return True

            subprocess.run(f"az group create --name {rg} --location {location}", shell=True, check=True)
            itr += 1

    except Exception as e:
        logging.error(f'Creating az-group {rg} failed: {str(e)}')
    
    return False


def create_app(req: func.HttpRequest) -> func.HttpResponse:

    """
    This is function to re-create a new isntance of an existing container app to be used for parallel computing 
    or background task
    """

    logging.info('Processing request to deploy container app.')

    image = req.params.get('image')
    app_env = req.params.get('app_env')
    rg = req.params.get('rg')
    location = req.params.get('location')
    port = req.params.get('port')
    app_name = req.params.get('app_name')
    task_type = req.params.get('task_type')

    image = image or getenv('DOCKER_IMAGE')
    app_env = app_env or getenv('APP_ENV')
    app_name = app_name or getenv("APP_NAME")
    rg = rg or getenv('AZURE_RESOURCE_GROUP')
    location = location or getenv('LOCATION')
    port = port or int(getenv("PORT", 80))


    if not app_env.lower().endswith('-env'):
        app_env = f"{app_env}-env"

    try:
        check_app = subprocess.run(
            f"az containerapp show --name {app_name} --resource-group {rg} ",
            shell=True,
            capture_output=True,
            text=True
        )

        logging.debug(f"CLI stdout: {check_app.stdout}")
        logging.error(f"CLI stderr: {check_app.stderr}")

        if check_app.returncode == 0:
            return func.HttpResponse(f"App '{app_name}' already exist.", status_code=409)
        
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Failed to validate '{app_name}'.", status_code=404)

    if not validate_az_group():
        return func.HttpResponse(
            "Resource group could not be validated. Please create it manually through portal.",
            status_code=400
        )

    sql_env = get_app_settings()
    env_vars = ' '.join([f"{k}={v}" for k, v in sql_env.items()])

    if task_type:
        env_vars += f" TASK_TYPE={task_type}"

    ingress = 'external' if not task_type else 'internal'

    if not image or not app_name:
        return func.HttpResponse(
            "Please pass both 'image' and 'appName' in the query string.",
            status_code=400
        )

    try:
        cmds = [
            f"az containerapp env create --name {app_env} --resource-group {rg} --location {location} ",
            f"az containerapp create --name {app_name} --resource-group {rg} --environment {app_env} --image {image} --target-port {port} --ingress {ingress} "
            f"--env-vars {env_vars}"
        ]

        for cmd in cmds:
            create_status = subprocess.run(cmd, shell=True, check=True)

            logging.debug(f"CLI stdout: {create_status.stdout}")
            logging.error(f"CLI stderr: {create_status.stderr}")

        return func.HttpResponse(f"Container App '{app_name}' deployed with image '{image}'.", status_code=201)

    except subprocess.CalledProcessError as e:
        return func.HttpResponse(f"Deployment failed: {e}", status_code=500)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return create_app(req)