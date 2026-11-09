from datetime import date
import pandas as pd


def test_pandas_normalizes_dates_and_removes_duplicate_emails():
    source = pd.DataFrame([
        {"nombre": "Ana", "apellido": "Pérez", "email": " ANA@GYM.COM ", "fecha_alta": "2026-01-02"},
        {"nombre": "Luis", "apellido": "Díaz", "email": "ana@gym.com", "fecha_alta": "2026-01-03"},
        {"nombre": "Eva", "apellido": "López", "email": "eva@gym.com", "fecha_alta": "2026-01-04"},
    ])
    source["email_normalizado"] = source["email"].astype(str).str.strip().str.lower()
    source["fecha_alta_normalizada"] = pd.to_datetime(source["fecha_alta"], errors="coerce").dt.date
    valid = source.dropna(subset=["fecha_alta_normalizada"]).drop_duplicates("email_normalizado", keep="first")
    assert len(valid) == 2
    assert valid.iloc[0]["email_normalizado"] == "ana@gym.com"
    assert valid.iloc[0]["fecha_alta_normalizada"] == date(2026, 1, 2)


def test_pandas_daily_series_fills_missing_days():
    source = pd.DataFrame({"fecha": ["2026-01-01", "2026-01-03"], "cantidad": [2, 4]})
    source["fecha"] = pd.to_datetime(source["fecha"])
    daily = source.set_index("fecha").asfreq("D", fill_value=0).reset_index()
    assert daily["cantidad"].tolist() == [2, 0, 4]
