# This is very well-structured for automated app deployment. You can confidently use this in:
# Azure Functions (triggered by HTTP)
# CI/CD workflows (GitHub Actions, DevOps Pipelines)
# Internal service agents
import logging
from os import getenv
import subprocess
import azure.functions as func
from utils.get_sql_env import get_sql_env_vars


def validate_az_group(rg: str, location: str = 'westeurope', maxtries=5) -> bool:
    try:
        itr=1
        while itr < maxtries:

            check_group = subprocess.run(
                        f"az group exists --name {rg}",
                        shell=True,
                        capture_output=True,
                        text=True
                    )

            if check_group.stdout.strip().lower() == 'true':
                return True

            subprocess.run(f"az group create --name {rg} --location {location}", shell=True, check=True)
            itr += 1

    except Exception as e:
        logging.error(f'Creating az-group {rg} failed: {str(e)}')
    
    return False


def create_app(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Processing request to deploy container app.')

    # Read parameters from request
    image = req.params.get('image')
    app_env = req.params.get('appEnv')
    app_name = req.params.get('appName')
    rg = req.params.get('resourceGroup', 'rg-lion-app')
    location = req.params.get('location', 'westeurope')
    rg = rg or getenv('ResourceGroup')

    if not app_env.lower().endswith('-env'):
        app_env = f"{app_env}-env"

    try:
        check_app = subprocess.run(
            f"az containerapp show --name {app_name} --resource-group {rg} ",
            shell=True,
            capture_output=True,
            text=True
        )

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

    port = int(getenv("PORT", 80))
    sql_env = get_sql_env_vars()
    env_vars = ' '.join([f"{k}={v}" for k, v in sql_env.items()])

    #  check if it's a task container
    task_type = req.params.get('task')
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
            subprocess.run(cmd, shell=True, check=True)

        return func.HttpResponse(f"Container App '{app_name}' deployed with image '{image}'.", status_code=201)

    except subprocess.CalledProcessError as e:
        return func.HttpResponse(f"Deployment failed: {e}", status_code=500)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return create_app(req)