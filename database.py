import sqlite3
from pathlib import Path


class Database:

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.db_path = self.data_dir / "decisionlab.db"

        self.create_tables()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):

        with self.connect() as conn:

            conn.executescript("""

                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS alternatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,

                    FOREIGN KEY (decision_id)
                    REFERENCES decisions(id)
                    ON DELETE CASCADE,

                    UNIQUE(decision_id, name)
                );

                CREATE TABLE IF NOT EXISTS criteria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    weight REAL NOT NULL CHECK(weight > 0),

                    FOREIGN KEY (decision_id)
                    REFERENCES decisions(id)
                    ON DELETE CASCADE,

                    UNIQUE(decision_id, name)
                );

                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alternative_id INTEGER NOT NULL,
                    criterion_id INTEGER NOT NULL,
                    value REAL NOT NULL CHECK(value >= 0 AND value <= 10),

                    FOREIGN KEY (alternative_id)
                    REFERENCES alternatives(id)
                    ON DELETE CASCADE,

                    FOREIGN KEY (criterion_id)
                    REFERENCES criteria(id)
                    ON DELETE CASCADE,

                    UNIQUE(alternative_id, criterion_id)
                );

            """)

    # ---------------------------------
    # DECISION MANAGEMENT
    # ---------------------------------

    def add_decision(self, title, description):

        with self.connect() as conn:

            cursor = conn.execute(
                """
                INSERT INTO decisions (title, description)
                VALUES (?, ?)
                """,
                (title, description)
            )

            return cursor.lastrowid

    def get_decisions(self):

        with self.connect() as conn:

            return conn.execute(
                """
                SELECT *
                FROM decisions
                ORDER BY created_at DESC
                """
            ).fetchall()

    def delete_decision(self, decision_id):

        with self.connect() as conn:

            conn.execute(
                "DELETE FROM decisions WHERE id = ?",
                (decision_id,)
            )

    # ---------------------------------
    # ALTERNATIVE MANAGEMENT
    # ---------------------------------

    def add_alternative(self, decision_id, name, description=""):

        with self.connect() as conn:

            cursor = conn.execute(
                """
                INSERT INTO alternatives
                (decision_id, name, description)
                VALUES (?, ?, ?)
                """,
                (decision_id, name, description)
            )

            return cursor.lastrowid

    def get_alternatives(self, decision_id):

        with self.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM alternatives
                WHERE decision_id = ?
                ORDER BY id
                """,
                (decision_id,)
            ).fetchall()

    def delete_alternative(self, alternative_id):

        with self.connect() as conn:

            conn.execute(
                "DELETE FROM alternatives WHERE id = ?",
                (alternative_id,)
            )

    # ---------------------------------
    # CRITERIA MANAGEMENT
    # ---------------------------------

    def add_criterion(self, decision_id, name, weight):

        with self.connect() as conn:

            cursor = conn.execute(
                """
                INSERT INTO criteria
                (decision_id, name, weight)
                VALUES (?, ?, ?)
                """,
                (decision_id, name, weight)
            )

            return cursor.lastrowid

    def get_criteria(self, decision_id):

        with self.connect() as conn:

            return conn.execute(
                """
                SELECT *
                FROM criteria
                WHERE decision_id = ?
                ORDER BY id
                """,
                (decision_id,)
            ).fetchall()

    def delete_criterion(self, criterion_id):

        with self.connect() as conn:

            conn.execute(
                "DELETE FROM criteria WHERE id = ?",
                (criterion_id,)
            )

    # ---------------------------------
    # SCORE MANAGEMENT
    # ---------------------------------

    def save_score(self, alternative_id, criterion_id, value):

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO scores
                (alternative_id, criterion_id, value)
                VALUES (?, ?, ?)

                ON CONFLICT(alternative_id, criterion_id)
                DO UPDATE SET value = excluded.value
                """,
                (alternative_id, criterion_id, value)
            )

    def get_scores(self, decision_id):

        with self.connect() as conn:

            return conn.execute(
                """
                SELECT
                    alternatives.name AS alternative,
                    criteria.name AS criterion,
                    scores.value AS score

                FROM scores

                JOIN alternatives
                    ON scores.alternative_id = alternatives.id

                JOIN criteria
                    ON scores.criterion_id = criteria.id

                WHERE alternatives.decision_id = ?
                AND criteria.decision_id = ?

                """,
                (decision_id, decision_id)
            ).fetchall()

    # ---------------------------------
    # DECISION ANALYSIS
    # ---------------------------------

    def calculate_results(self, decision_id):

        alternatives = self.get_alternatives(decision_id)
        criteria = self.get_criteria(decision_id)

        if not alternatives or not criteria:
            return []

        total_weight = sum(
            criterion["weight"]
            for criterion in criteria
        )

        if total_weight <= 0:
            return []

        results = []

        for alternative in alternatives:

            weighted_score = 0
            completed_scores = 0

            for criterion in criteria:

                with self.connect() as conn:

                    score = conn.execute(
                        """
                        SELECT value
                        FROM scores
                        WHERE alternative_id = ?
                        AND criterion_id = ?
                        """,
                        (
                            alternative["id"],
                            criterion["id"]
                        )
                    ).fetchone()

                if score is not None:
                    weighted_score += (
                        score["value"] * criterion["weight"]
                    )

                    completed_scores += 1

            final_score = weighted_score / total_weight

            coverage = (
                completed_scores / len(criteria)
            ) * 100

            results.append({

                "id": alternative["id"],

                "name": alternative["name"],

                "score": round(final_score, 2),

                "coverage": round(coverage, 1)

            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        for rank, result in enumerate(results, start=1):
            result["rank"] = rank

        return results

    # ---------------------------------
    # DASHBOARD STATISTICS
    # ---------------------------------

    def get_statistics(self):

        with self.connect() as conn:

            decisions = conn.execute(
                "SELECT COUNT(*) FROM decisions"
            ).fetchone()[0]

            alternatives = conn.execute(
                "SELECT COUNT(*) FROM alternatives"
            ).fetchone()[0]

            criteria = conn.execute(
                "SELECT COUNT(*) FROM criteria"
            ).fetchone()[0]

            scores = conn.execute(
                "SELECT COUNT(*) FROM scores"
            ).fetchone()[0]

        return {

            "decisions": decisions,

            "alternatives": alternatives,

            "criteria": criteria,

            "scores": scores

        }