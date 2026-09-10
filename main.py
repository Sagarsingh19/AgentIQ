"""Development entry point. Use an ASGI process manager in production."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("agentiq.api:app", host="127.0.0.1", port=8000, reload=True)
