
# 📦 Azure Function App: `lion-func`

## 🧭 Overview

`lion-func` is an Azure Function App designed to provide **automated deployment, control, and execution of Azure Container Apps** in a dynamic and scalable way. It enables a main application (like `lion-capp`) to **spin off containerized jobs**, run them on demand, and cleanly manage the lifecycle of temporary compute resources.

---

## 🚀 Features

- 🔨 **Create new container apps** dynamically using `createApp`
- ⚙️ **Start and stop** existing container apps with `startApp` and `stopApp`
- 🧠 **Run background tasks** by spawning temporary container apps via `spawn_task.py`
- 🛠️ Includes helper scripts and reusable utility functions

---

## 📁 Project Structure

```
lion-func/
├── __init__.py
├── bash/
│   └── *.sh              # Deployment and configuration scripts
├── createApp/
│   ├── __init__.py       # Logic for creating new container apps
│   ├── function.json
│   └── spawn_task.py     # Spawns task-specific container apps
├── startApp/
│   ├── __init__.py       # Starts existing container apps
│   └── function.json
├── stopApp/
│   ├── __init__.py       # Stops existing container apps
│   └── function.json
├── utils/
│   └── get_sql_env.py    # Secure environment variable injection
├── host.json
├── local.settings.json
├── requirements.txt
├── scaffold-lion-deploy.txt
├── orchestration.md      # Process documentation
```

---

## 🔁 Workflow Integration

The module is fully integrated into a **GitHub Actions CI/CD pipeline**, which:

1. **Builds** the function app
2. **Zips and uploads** the package
3. **Configures application settings** using secrets
4. **Deploys** to Azure via `azure/functions-action@v1`

---

## 🔐 App Settings (Environment Variables)

These are securely configured using Azure CLI or GitHub Secrets:

- `AZURE_SQL_USER`, `AZURE_SQL_PASS`
- `AZURE_SQL_SERVER`, `AZURE_SQL_DB`
- `DOCKER_IMAGE`, `APP_ENV`, `APP_NAME`
- `AZURE_STORAGE_CONNECTION_STRING`

---

## 🧪 Usage Scenarios

| Function      | Description                                | Trigger                      |
|---------------|--------------------------------------------|------------------------------|
| `createApp`   | Deploy a container app with given image     | HTTP POST `/api/create-app` |
| `startApp`    | Start an existing container app             | HTTP POST `/api/start-app`  |
| `stopApp`     | Stop an existing container app              | HTTP POST `/api/stop-app`   |
| `spawn_task`  | Create a short-lived container for a task   | POST `/api/create-app?task=...` |

---

## 🔄 Future Enhancements

- ⏱ Auto-delete expired task containers
- 📊 Monitoring for active job containers
- 🔐 Key Vault-based secrets injection

---

## 📬 Maintained by

Azure Function App + GitHub Actions + Container Apps integration for dynamic cloud-native scheduling and job execution.
