"""
Utilitaires de sérialisation pour les réponses JSON.
Convertit les types MySQL non sérialisables.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal


def serialize_row(row: dict) -> dict:
    """
    Convertit tous les types non JSON-sérialisables d'une ligne MySQL.
    À appeler sur chaque dict retourné par cursor.fetchone() / fetchall().
    """
    if not row:
        return row

    result = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, (date, datetime)):
            result[key] = str(value)
        elif isinstance(value, timedelta):
            # timedelta retourné pour les colonnes TIME
            total = int(value.total_seconds())
            h     = total // 3600
            m     = (total % 3600) // 60
            s     = total % 60
            result[key] = f"{h:02d}:{m:02d}:{s:02d}"
        elif isinstance(value, bytes):
            result[key] = value.decode('utf-8')
        else:
            result[key] = value

    return result


def serialize_rows(rows: list) -> list:
    """Applique serialize_row sur une liste de lignes."""
    return [serialize_row(row) for row in rows]