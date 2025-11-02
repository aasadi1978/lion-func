# Serverless container orchestration
---

## 🎯 **Your Goal Recap**

> From a running container app (`lion-capp`), you want to **spin off a temporary container instance** using the same Docker image — to handle a **background-heavy task** — triggered by a **user action (button click)**.

This pattern is **serverless container orchestration** — highly efficient and scalable.

---

## ✅ **Target Architecture**

1. **Main App (`lion-capp`)**

   * Runs continuously
   * Exposes a user-facing UI or API
   * On trigger (button click), it invokes a backend function or automation

2. **Background App (temporary)**

   * Same Docker image
   * Created dynamically with env vars / payload
   * Runs the heavy task
   * Scales to zero or is deleted afterward

3. **Automation Layer**

   * Azure Function or Logic App
   * Accepts trigger + parameters
   * Executes `az containerapp create` with custom name and lifetime

---

## 🛠️ Step-by-Step Implementation

### **Step 1: Confirm Your Container App Image**

Get the image used in `lion-capp`:

```bash
az containerapp show \
  --name lion-capp \
  --resource-group <your-rg> \
  --query "properties.template.containers[0].image" \
  --output tsv
```

Save it as `BASE_IMAGE`.

---

### **Step 2: Create an Azure Function (HTTP Trigger)**

Use the same setup you already built, add a new function:

#### 🔧 `spawnTaskApp/__init__.py`

```python
import azure.functions as func
import subprocess
import uuid
from os import getenv

def main(req: func.HttpRequest) -> func.HttpResponse:
    base_image = req.params.get("image") or getenv("DEFAULT_IMAGE")
    rg = req.params.get("resourceGroup", "rg-lion-app")
    app_env = req.params.get("appEnv", "lion-env")
    location = req.params.get("location", "westeurope")

    # Generate unique name for this job
    task_id = str(uuid.uuid4())[:8]
    task_app_name = f"lion-task-{task_id}"

    port = int(getenv("PORT", "80"))

    # Optional task-specific env vars
    task_type = req.params.get("task", "heavy-job")

    try:
        cmd = (
            f"az containerapp create --name {task_app_name} "
            f"--resource-group {rg} --environment {app_env} "
            f"--image {base_image} --target-port {port} --ingress internal "
            f"--env-vars TASK_TYPE={task_type}"
        )

        subprocess.run(cmd, shell=True, check=True)

        return func.HttpResponse(
            f"Task container '{task_app_name}' started for task: {task_type}",
            status_code=201
        )

    except subprocess.CalledProcessError as e:
        return func.HttpResponse(
            f"Failed to spawn task container: {e}",
            status_code=500
        )
```

---

### **Step 3: Call the Function From Your Main App**

From `lion-capp`, make a POST request on button click:

```js
fetch("/api/spawn-task", {
  method: "POST",
  body: JSON.stringify({ task: "optimize-run" })
});
```

Or from Python (if server-side):

```python
requests.post(
    "https://your-func-url/api/spawn-task",
    params={"task": "optimize-run"}
)
```

---

### **Step 4: In Your Docker Container Code**

Check if it's a **task container** via env var `TASK_TYPE` and run the background process directly:

```python
if os.getenv("TASK_TYPE"):
    run_my_heavy_job(os.getenv("TASK_TYPE"))
    exit(0)
```

---

### 🔄 Optional Enhancements

* Auto-delete container app after it completes
* Use **Azure Service Bus** to queue jobs
* Use **KEDA** for scale-to-zero workers

---

Would you like me to scaffold this new `spawn-task` function and container logic for you?
