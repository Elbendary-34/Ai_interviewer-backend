import os

#1. Folders
folders = [
    "app",
    "app/core",
    "app/db",
    "app/db/models",
    "app/api",
    "app/api/v1",
    "app/api/v1/endpoints",
    "app/services",
    "app/workers",
    "app/schemas",
]

#2. Files
files = {
    "app/__init__.py": "",
    "app/main.py": "# FastAPI Entry Point\n",
    "app/core/__init__.py": "",
    "app/core/config.py": "# Configurations & Env Settings\n",
    "app/core/database.py": "# PostgreSQL Async Setup\n",
    "app/core/security.py": "# JWT & Security Helpers\n",
    "app/db/__init__.py": "",
    "app/db/base.py": "# Base model registry for Alembic\n",
    "app/db/models/__init__.py": "",
    "app/db/models/user.py": "# User Database Model\n",
    "app/db/models/session.py": "# Interview Session Model\n",
    "app/db/models/report.py": "# Report & Analytics Model\n",
    "app/api/__init__.py": "",
    "app/api/v1/__init__.py": "",
    "app/api/v1/router.py": "# API Router Aggregator\n",
    "app/api/v1/endpoints/__init__.py": "",
    "app/api/v1/endpoints/livekit.py": "# LiveKit Room & Token Endpoints\n",
    "app/api/v1/endpoints/ws_analytics.py": "# Real-time WebSocket Endpoint\n",
    "app/api/v1/endpoints/session.py": "# Interview Session Endpoints\n",
    "app/api/v1/endpoints/auth.py": "# Authentication Endpoints\n",
    "app/api/v1/endpoints/candidate.py": "# Candidate Management Endpoints\n",
    "app/services/__init__.py": "",
    "app/services/redis_service.py": "# Async Redis Service\n",
    "app/services/livekit_service.py": "# LiveKit Server Integration\n",
    "app/services/alert_engine.py": "# Real-time Alert & Threshold Rules\n",
    "app/services/cv_parser.py": "# CV Parser Service\n",
    "app/workers/__init__.py": "",
    "app/workers/celery_app.py": "# Celery Application Instance\n",
    "app/workers/tasks.py": "# Background Processing Tasks\n",
    "app/schemas/__init__.py": "",
    "app/schemas/metadata.py": "# Pydantic Schemas for Metadata\n",
    "app/schemas/report.py": "# Pydantic Schemas for Reports\n",
    
    # Docker & Environment
    "docker-compose.yml": (
        "services:\n"
        "  redis:\n"
        "    image: redis:7-alpine\n"
        "    container_name: intervyou_redis\n"
        "    restart: always\n"
        "    ports:\n"
        "      - \"6379:6379\"\n"
        "    volumes:\n"
        "      - redis_data:/data\n\n"
        "  livekit:\n"
        "    image: livekit/livekit-server:v1.6\n"
        "    container_name: intervyou_livekit\n"
        "    restart: always\n"
        "    command: --config /etc/livekit.yaml\n"
        "    ports:\n"
        "      - \"7880:7880\"\n"
        "      - \"7881:7881\"\n"
        "      - \"7882:7882/udp\"\n"
        "      - \"50000-50010:50000-50010/udp\"\n"
        "    environment:\n"
        "      LIVEKIT_KEYS: \"devkey: secretsecretsecretsecretsecretsecretsecret\"\n"
        "    volumes:\n"
        "      - ./livekit.yaml:/etc/livekit.yaml\n\n"
        "volumes:\n"
        "  redis_data:\n"
    ),
    "livekit.yaml": (
        "port: 7880\n"
        "bind_addresses:\n"
        "  - \"\"\n"
        "rtc:\n"
        "  tcp_port: 7881\n"
        "  port_range_start: 50000\n"
        "  port_range_end: 50010\n"
        "  use_external_ip: false\n\n"
        "keys:\n"
        "  devkey: secretsecretsecretsecretsecretsecretsecret\n"
    ),
    ".env": (
        "REDIS_URL=redis://localhost:6379\n"
        "POSTGRES_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intervyou_db\n"
        "LIVEKIT_API_KEY=devkey\n"
        "LIVEKIT_API_SECRET=secretsecretsecretsecretsecretsecretsecret\n"
        "LIVEKIT_URL=ws://localhost:7880\n"
    ),
    "requirements.txt": (
        "fastapi\n"
        "uvicorn[standard]\n"
        "redis\n"
        "pydantic\n"
        "livekit-api\n"
        "sqlalchemy[asyncio]\n"
        "asyncpg\n"
        "celery\n"
        "python-dotenv\n"
    ),
    "README.md": "",
}

def generate_project():
    print("--- Starting Full Project Generation ---")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"[+] Folder: {folder}")

    for file_path, default_content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(default_content)
            print(f"[+] File:   {file_path}")

    print("\nProject Structure Created Successfully!")

if __name__ == "__main__":
    generate_project()