import sqlite3
from pathlib import Path


class Database:

    def __init__(self):

        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"

        self.data_dir.mkdir(exist_ok=True)

        self.db_path = self.data_dir / "decisionlab.db"

        self.create_tables()

    # ---------------------------------
    # DATABASE CONNECTION
    # ---------------------------------

    def connect(self):

        connection = sqlite3.connect(self.db_path)

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON")

        return connection

    # ---------------------------------
    # CREATE TABLES
    # ---------------------------------

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

                    value REAL NOT NULL

                    CHECK(value >= 0 AND value <= 10),

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

    def add_decision(self, title, description=""):

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

                ORDER BY created_at DESC, id DESC
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

    def add_alternative(
        self,
        decision_id,
        name,
        description=""
    ):

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

    def add_criterion(
        self,
        decision_id,
        name,
        weight
    ):

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

    def save_score(
        self,
        alternative_id,
        criterion_id,
        value
    ):

        if not 0 <= value <= 10:

            raise ValueError(
                "Score must be between 0 and 10."
            )

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

                    scores.value AS score,

                    alternatives.id AS alternative_id,

                    criteria.id AS criterion_id

                FROM scores

                JOIN alternatives

                    ON scores.alternative_id = alternatives.id

                JOIN criteria

                    ON scores.criterion_id = criteria.id

                WHERE alternatives.decision_id = ?

                AND criteria.decision_id = ?

                ORDER BY alternatives.id, criteria.id

                """,

                (decision_id, decision_id)

            ).fetchall()

    # ---------------------------------
    # SCORE MATRIX
    # ---------------------------------

    def get_score_matrix(self, decision_id):

        alternatives = self.get_alternatives(decision_id)

        criteria = self.get_criteria(decision_id)

        scores = self.get_scores(decision_id)

        matrix = {}

        # Step 1: Create the structure for all alternatives
        for alternative in alternatives:

            matrix[alternative["id"]] = {
            "name": alternative["name"],
            "scores": {}
        }

        # Step 2: Initialize all criteria scores
            for criterion in criteria:

                matrix[alternative["id"]]["scores"][
                criterion["id"]
            ] = None

    # Step 3: Fill the matrix with saved scores
        for score in scores:

            alternative_id = score["alternative_id"]

            criterion_id = score["criterion_id"]

            if alternative_id in matrix:

                matrix[alternative_id]["scores"][
                criterion_id
            ] = score["score"]

        return matrix
    
    # ---------------------------------
    # WEIGHTED DECISION ANALYSIS
    # ---------------------------------

    def calculate_results(self, decision_id):

        alternatives = self.get_alternatives(decision_id)

        criteria = self.get_criteria(decision_id)

        matrix = self.get_score_matrix(decision_id)

        if not alternatives or not criteria:

            return []

        total_weight = sum(

            criterion["weight"]

            for criterion in criteria

        )

        results = []

        for alternative in alternatives:

            alternative_data = matrix[alternative["id"]]

            weighted_score = 0

            completed_weight = 0

            completed_scores = 0

            for criterion in criteria:

                value = alternative_data["scores"][
                    criterion["id"]
                ]

                if value is not None:

                    weighted_score += (

                        value * criterion["weight"]

                    )

                    completed_weight += criterion["weight"]

                    completed_scores += 1

            coverage = (

                completed_scores / len(criteria)

            ) * 100

            is_complete = (

                completed_scores == len(criteria)

            )

            if is_complete and total_weight > 0:

                final_score = (

                    weighted_score / total_weight

                )

            else:

                final_score = None

            results.append({

                "id": alternative["id"],

                "name": alternative["name"],

                "score": (

                    round(final_score, 2)

                    if final_score is not None

                    else None

                ),

                "coverage": round(coverage, 1),

                "completed": completed_scores,

                "total": len(criteria),

                "status": (

                    "Complete"

                    if is_complete

                    else "Incomplete"

                ),

                "rank": None

            })

        complete_results = [

            item for item in results

            if item["score"] is not None

        ]

        incomplete_results = [

            item for item in results

            if item["score"] is None

        ]

        complete_results.sort(

            key=lambda item: item["score"],

            reverse=True

        )

        for rank, item in enumerate(

            complete_results,

            start=1

        ):

            item["rank"] = rank

        return complete_results + incomplete_results

    # ---------------------------------
    # SMART INSIGHTS
    # ---------------------------------

    def get_insights(self, decision_id):

        results = self.calculate_results(decision_id)

        criteria = self.get_criteria(decision_id)

        matrix = self.get_score_matrix(decision_id)

        complete = [

            item for item in results

            if item["status"] == "Complete"

        ]

        incomplete = [

            item for item in results

            if item["status"] == "Incomplete"

        ]

        if not complete:

            return {

                "winner": None,

                "runner_up": None,

                "margin": None,

                "best_criterion": None,

                "incomplete": incomplete,

                "message": (

                    "Complete at least one alternative "

                    "to generate decision insights."

                )

            }

        winner = complete[0]

        runner_up = (

            complete[1]

            if len(complete) > 1

            else None

        )

        margin = (

            round(

                winner["score"] - runner_up["score"],

                2
                )

            if runner_up

            else None

        )

        criterion_averages = []

        for criterion in criteria:

            values = []

            for alternative in matrix.values():

                value = alternative["scores"][criterion["id"]]

                if value is not None:

                    values.append(value)

            if values:

                average = sum(values) / len(values)

                criterion_averages.append({

                    "name": criterion["name"],

                    "average": round(average, 2)

                })

        best_criterion = None

        if criterion_averages:

            best_criterion = max(

                criterion_averages,

                key=lambda item: item["average"]

            )

        return {

            "winner": winner,

            "runner_up": runner_up,

            "margin": margin,

            "best_criterion": best_criterion,

            "incomplete": incomplete,

            "message": "Analysis completed successfully."

        }

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