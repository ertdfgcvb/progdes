import sqlite3
import pandas as pd
from collections import Counter
import re

DB = "/Users/andreas/iphone_decrypted/sms.db"

conn = sqlite3.connect(DB)

df = pd.read_sql("""
SELECT
 datetime(date/1000000000 + 978307200,'unixepoch') AS ts,
 is_from_me,
 text,
 handle.id as contact
FROM message
LEFT JOIN handle ON message.handle_id = handle.ROWID
WHERE text IS NOT NULL
""", conn)

df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
df = df.dropna(subset=["ts"])

print("\n==============================")
print("TOP 10 contatti per numero messaggi")
print("==============================")

top_users = df["contact"].value_counts().head(10)
print(top_users)

print("\n==============================")
print("TOP 10 parole più usate")
print("==============================")

all_text = " ".join(df["text"].astype(str)).lower()
words = re.findall(r"\b[a-zàèéìòù]+\b", all_text)
common = Counter(words).most_common(10)

for word, count in common:
    print(f"{word}: {count}")

print("\n==============================")
print("Media messaggi per ora del giorno")
print("==============================")

df["hour"] = df["ts"].dt.hour
hourly = df.groupby("hour").size().reindex(range(24), fill_value=0)

max_val = hourly.max()

for h, val in hourly.items():
    bar = "█" * int((val / max_val) * 40) if max_val > 0 else ""
    print(f"{h:02d}: {val:5d} {bar}")
