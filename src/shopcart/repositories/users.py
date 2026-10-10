import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    email: str
    name: str
    role: str
    password_hash: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class UserRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def by_email(self, email: str) -> User | None:
        row = self.conn.execute(
            "SELECT id, email, name, role, password_hash FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()
        return User(**row) if row else None

    def create(self, email: str, name: str, password_hash: str, role: str, now: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO users (email, name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (email.lower(), name, password_hash, role, now),
        )
        return cur.lastrowid

    def create_session(self, token_hash: str, user_id: int, expires_at: str) -> None:
        self.conn.execute(
            "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
            (token_hash, user_id, expires_at),
        )

    def by_session(self, token_hash: str, now: str) -> User | None:
        row = self.conn.execute(
            """
            SELECT u.id, u.email, u.name, u.role, u.password_hash
            FROM sessions s JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
            """,
            (token_hash, now),
        ).fetchone()
        return User(**row) if row else None
