import azure.functions as func
import uuid
from createApp import create_app

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Clone base request and override only what's needed
    task_id = str(uuid.uuid4())[:8]
    app_name = f"lion-task-{task_id}"

    # Add default image and environment if not passed
    params = req.params.copy()
    params = dict(params)
    params.setdefault("appName", app_name)
    params.setdefault("appEnv", "lion-env")
    params.setdefault("resourceGroup", "rg-lion-app")
    params.setdefault("location", "westeurope")
    params.setdefault("image", "<your-base-image>")
    params.setdefault("task", req.params.get("task", "optimize-run"))

    # Wrap as a new HttpRequest with patched parameters
    class ModifiedRequest(func.HttpRequest):
        def __init__(self):
            super().__init__(req.method, req.url, params, req.headers, req.route_params, req.body)

    return create_app(ModifiedRequest())
