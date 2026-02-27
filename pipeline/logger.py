import json
from datetime import datetime
from pathlib import Path
from typing import Any


class RunLogger:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"run_{datetime.now().strftime('%Y%m%d')}.jsonl"

    def log(self, event: str, actor: str, data: dict[str, Any]):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "run_id": self.run_id,
            "event": event,
            "actor": actor,
            "data": data
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

def get_run_logger(run_id: str) -> RunLogger:
    return RunLogger(run_id)
