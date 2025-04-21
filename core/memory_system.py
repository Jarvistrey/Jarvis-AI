from pathlib import Path
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class JarvisMemory:
    """Memory system for Jarvis AI"""
    def __init__(self, base_path: Path):
        self.memory_path = base_path / "data" / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.memory_path / "jarvis_memory.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_input TEXT,
                    response TEXT,
                    context TEXT
                )
            """)

    async def store_interaction(self, user_input: str, response: str, context: Optional[Dict] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO conversations 
                   (timestamp, user_input, response, context) 
                   VALUES (?, ?, ?, ?)""",
                (datetime.now().isoformat(), user_input, response, 
                 json.dumps(context or {}))
            )

    async def get_recent_context(self, limit: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT timestamp, user_input, response, context 
                   FROM conversations 
                   ORDER BY timestamp DESC LIMIT ?""",
                (limit,)
            )
            return [
                {
                    "timestamp": row[0],
                    "user_input": row[1],
                    "response": row[2],
                    "context": json.loads(row[3])
                }
                for row in cursor.fetchall()
            ]