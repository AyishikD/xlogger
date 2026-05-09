import os
import subprocess
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

EXAMPLES_DIR = "/Users/ayishikdas/Projects/Modellogger/examples"

@router.get("/scripts")
async def list_scripts():
    """List all runnable python scripts in the examples directory."""
    scripts = []
    for file in os.listdir(EXAMPLES_DIR):
        if file.endswith(".py"):
            scripts.append({
                "name": file,
                "path": os.path.join(EXAMPLES_DIR, file),
                "description": f"Training script: {file}"
            })
    return scripts

@router.websocket("/run/{script_name}")
async def run_script(websocket: WebSocket, script_name: str):
    await websocket.accept()
    
    script_path = os.path.join(EXAMPLES_DIR, script_name)
    if not os.path.exists(script_path):
        await websocket.send_json({"type": "error", "message": "Script not found"})
        await websocket.close()
        return

    # Prepare environment
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:/Users/ayishikdas/Projects/Modellogger/sdk/python"
    env["PYTHONUNBUFFERED"] = "1"
    
    # Start process
    process = await asyncio.create_subprocess_exec(
        "/Users/ayishikdas/Projects/Modellogger/venv/bin/python",
        "-u",
        script_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    async def stream_output(stream, stream_type):
        while True:
            line = await stream.readline()
            if not line:
                break
            await websocket.send_json({
                "type": "log",
                "stream": stream_type,
                "content": line.decode().strip()
            })

    try:
        # Run stdout and stderr streaming concurrently
        await asyncio.gather(
            stream_output(process.stdout, "stdout"),
            stream_output(process.stderr, "stderr")
        )
        await process.wait()
        await websocket.send_json({"type": "status", "message": "Process finished", "exit_code": process.returncode})
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if process.returncode is None:
            process.terminate()
        await websocket.close()
