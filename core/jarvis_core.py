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
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_input TEXT,
                    response TEXT,
                    context TEXT,
                    session_id TEXT
                )
            """)

    async def store_interaction(self, user_input: str, response: str, 
                              session_id: str, context: Optional[Dict] = None):
        """Store a conversation interaction"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO conversations 
                   (timestamp, user_input, response, context, session_id) 
                   VALUES (?, ?, ?, ?, ?)""",
                (datetime.now().isoformat(), user_input, response, 
                 json.dumps(context or {}), session_id)
            )

    async def get_recent_context(self, session_id: str, limit: int = 5) -> List[Dict]:
        """Retrieve recent conversations for context"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT timestamp, user_input, response, context 
                   FROM conversations 
                   WHERE session_id = ? 
                   ORDER BY timestamp DESC LIMIT ?""",
                (session_id, limit)
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