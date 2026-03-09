# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Internet of Agents (IoA) is a platform for heterogeneous AI agent collaboration. See `README.md` for architecture and usage.

### Services

| Service | Port | Description |
|---|---|---|
| Milvus stack (etcd + MinIO + Milvus) | 19530 (internal) | Vector DB for agent registration/discovery. Runs in Docker via `dockerfiles/compose/milvus.yaml` |
| IoA Server (`im_server/app.py`) | 7788 | FastAPI server — agent registry, session/team management, WebSocket message routing |
| IoA Client (`im_client/main.py`) | 5050 | FastAPI client wrapping a tool agent with communication layer |
| React Frontend (`im_server/frontend/`) | 3000 (dev) / 80 (prod) | Dashboard for monitoring agent conversations |

### Running locally (outside Docker)

The code hardcodes the Milvus host as `standalone`. To run the server/client locally against the Dockerized Milvus:

1. Start Docker daemon: `sudo bash -c 'dockerd &>/var/log/dockerd.log &'`
2. Create network: `sudo docker network create agent_network 2>/dev/null || true`
3. Start Milvus: `cd dockerfiles/compose && sudo docker compose -f milvus.yaml up -d`
4. Map hostname: find the Milvus container IP with `sudo docker inspect milvus-standalone --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'` and add it to `/etc/hosts` as `standalone`
5. Server: `cd im_server && PYTHONPATH=/workspace OPENAI_BASE_URL="https://openrouter.ai/api/v1" .venv/bin/python app.py`
   - Requires symlink: `ln -sf /workspace/configs/server_configs /workspace/im_server/configs`
   - Creates `database/server/` directory automatically
6. Frontend: `cd im_server/frontend && npm start`
7. Client: `cd im_client && PYTHONPATH=/workspace OPENAI_BASE_URL="https://openrouter.ai/api/v1" .venv/bin/python main.py` (requires `CUSTOM_CONFIG` env var for agent config)

### Gotchas

- `pymilvus==2.3.0` (pinned in requirements) does not build on Python 3.12 due to grpcio build issues. Install latest `pymilvus` instead — it is API-compatible.
- The `OPENAI_API_KEY` provided in this environment is an OpenRouter key. Set `OPENAI_BASE_URL=https://openrouter.ai/api/v1` when starting the server/client so the OpenAI SDK routes to OpenRouter.
- The server config path `configs/agent_registry.yaml` is relative to CWD. In Docker, configs are mounted at `/app/configs`. For local dev, symlink `configs/server_configs` into `im_server/configs`.
- The `common/` package is shared between server and client. Set `PYTHONPATH=/workspace` when running either locally.

### Lint / format

- Python: `ruff check .` and `ruff format --check .` from the repo root.
- Frontend: ESLint is configured via `react-app` preset in `package.json`.

### Tests

- Frontend: `cd im_server/frontend && CI=true npx react-scripts test --watchAll=false --passWithNoTests`
- No Python test suite is included; the `scripts/` directory contains benchmark test scripts that require the full stack + OpenAI.

### Build

- Frontend: `cd im_server/frontend && npm run build`
- Docker images: see `README.md` (Step 3) for build commands.
