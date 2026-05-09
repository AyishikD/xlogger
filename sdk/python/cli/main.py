import typer
from modellogger import ModelLogger
import json
import httpx
import asyncio

app = typer.Typer()

@app.command()
def init(api_key: str = typer.Option(None, help="API Key for ModelLogger")):
    """Initialize local ModelLogger configuration"""
    config = {"api_key": api_key}
    with open(".modellogger.json", "w") as f:
        json.dump(config, f)
    typer.echo("ModelLogger initialized successfully.")

@app.command()
def analyze(event_id: str):
    """Analyze a specific failure event"""
    async def run():
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            res = await client.post("/api/v1/memory/analyze_failure", json={"event_id": event_id})
            typer.echo(json.dumps(res.json(), indent=2))
    asyncio.run(run())

@app.command()
def postmortem(experiment_id: str):
    """View automated postmortem for an experiment"""
    async def run():
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            res = await client.get(f"/api/v1/monitor/postmortem/{experiment_id}")
            typer.echo(json.dumps(res.json(), indent=2))
    asyncio.run(run())

if __name__ == "__main__":
    app()
