from datetime import datetime
import json
import logging
from os import getenv
import subprocess
import azure.functions as func

def stop_app(app_name: str, resource_group: str =  getenv("AZURE_RESOURCE_GROUP", "rg-lion-app")) -> func.HttpResponse:
    try:
        check_app = subprocess.run(
            f"az containerapp show --name {app_name} --resource-group {resource_group}",
            shell=True,
            capture_output=True,
            text=True
        )

        if check_app.returncode != 0:
            return func.HttpResponse(f"App '{app_name}' does not exist.", status_code=404)

        logging.debug(f"CLI stdout: {check_app.stdout}")
        logging.error(f"CLI stderr: {check_app.stderr}")

        app_info = json.loads(check_app.stdout)
        state = app_info.get("properties", {}).get("provisioningState", "")

        if state.lower() in ["running", "succeeded"]:

            stop_result = subprocess.run(
                f"az containerapp stop --name {app_name} --resource-group {resource_group}",
                shell=True,
                capture_output=True,
                text=True
            )

            logging.debug(f"CLI stdout: {stop_result.stdout}")
            logging.error(f"CLI stderr: {stop_result.stderr}")

            if stop_result.returncode == 0:
                logging.info(f"{app_name} stopped on {datetime.now()}")
                return func.HttpResponse(f"App '{app_name}' stopped successfully.", status_code=200)
            else:
                return func.HttpResponse(f"Failed to stop app: {stop_result.stderr}", status_code=500)
        else:
            return func.HttpResponse(f"App '{app_name}' is already stopped or provisioning.", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error while stopping app '{app_name}': {str(e)}", status_code=500)

def main(req: func.HttpRequest) -> func.HttpResponse:
    app_name = req.params.get("app_name")
    if not app_name:
        return func.HttpResponse("Missing required parameter: app_name", status_code=400)
    
    return stop_app(app_name)