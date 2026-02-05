import sqlite3
import pandas as pd
from collections import Counter
import re
import numpy as np

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

# Normalize types
df["is_from_me"] = df["is_from_me"].fillna(0).astype(int)
df["contact"] = df["contact"].fillna("(unknown)")

# ==============================
# TOTAL + TIME SPAN + SENT/RECEIVED
# ==============================
total_msgs = len(df)
sent_msgs = int((df["is_from_me"] == 1).sum())
recv_msgs = int((df["is_from_me"] == 0).sum())

first_ts = df["ts"].min()
last_ts = df["ts"].max()
span = last_ts - first_ts if pd.notna(first_ts) and pd.notna(last_ts) else None

print("\n==============================")
print("TOTALE MESSAGGI")
print("==============================")
print(f"Totali:   {total_msgs}")
print(f"Inviati:  {sent_msgs}")
print(f"Ricevuti: {recv_msgs}")

print("\n==============================")
print("INTERVALLO TEMPORALE")
print("==============================")
print(f"Primo messaggio: {first_ts}")
print(f"Ultimo messaggio: {last_ts}")
if span is not None:
    print(f"Durata: {span} (circa {span.days} giorni)")
else:
    print("Durata: n/a")

# ==============================
# MESSAGES PER YEAR + SENT/RECEIVED
# ==============================
df["year"] = df["ts"].dt.year

print("\n==============================")
print("MESSAGGI PER ANNO")
print("==============================")
per_year = df.groupby("year").size().sort_index()
for y, n in per_year.items():
    print(f"{y}: {n}")

print("\n==============================")
print("MESSAGGI PER ANNO (INVIATI vs RICEVUTI)")
print("==============================")
year_dir = df.groupby(["year", "is_from_me"]).size().unstack(fill_value=0)
for year in sorted(year_dir.index):
    sent = int(year_dir.loc[year].get(1, 0))
    recv = int(year_dir.loc[year].get(0, 0))
    tot = sent + recv
    print(f"{year}: tot={tot} | inviati={sent} | ricevuti={recv}")

# ==============================
# BUSIEST DAY EVER + AVG MSGS/DAY
# ==============================
df["day"] = df["ts"].dt.date
per_day = df.groupby("day").size().sort_index()

print("\n==============================")
print("GIORNO PIÙ INTENSO + MEDIA MESSAGGI/GIORNO")
print("==============================")
if len(per_day) > 0:
    busiest_day = per_day.idxmax()
    busiest_count = int(per_day.max())
    active_days = int(per_day.size)
    # Average over active days (days with at least 1 message)
    avg_active = float(per_day.mean())
    # Average over full span (including days with 0 messages)
    if span is not None and span.days >= 0:
        full_days = span.days + 1
        avg_full = total_msgs / full_days if full_days > 0 else np.nan
    else:
        avg_full = np.nan

    print(f"Giorno più intenso: {busiest_day} ({busiest_count} messaggi)")
    print(f"Giorni attivi: {active_days}")
    print(f"Media (solo giorni attivi): {avg_active:.2f} messaggi/giorno")
    if not np.isnan(avg_full):
        print(f"Media (su tutta la durata): {avg_full:.2f} messaggi/giorno")
else:
    print("Nessun dato per giorno.")

# ==============================
# LONGEST STREAK (daily streak with >=1 msg)
# ==============================
print("\n==============================")
print("STREAK PIÙ LUNGO (ALMENO 1 MESSAGGIO AL GIORNO)")
print("==============================")

if len(per_day) > 0:
    days_idx = pd.to_datetime(per_day.index)
    diffs = days_idx.to_series().diff().dt.days.fillna(9999).astype(int)

    # A new streak starts when diff != 1
    streak_id = (diffs != 1).cumsum().values
    streak_sizes = pd.Series(1, index=days_idx).groupby(streak_id).sum()

    best_streak_len = int(streak_sizes.max())
    best_streak_group = int(streak_sizes.idxmax())

    streak_days = days_idx[streak_id == best_streak_group]
    streak_start = streak_days.min().date()
    streak_end = streak_days.max().date()

    print(f"Streak più lungo: {best_streak_len} giorni")
    print(f"Dal: {streak_start}  Al: {streak_end}")
else:
    print("Nessun dato per calcolare streak.")

# ==============================
# TOP CONTACT PER YEAR
# ==============================
print("\n==============================")
print("TOP CONTATTO PER ANNO")
print("==============================")

top_contact_year = (
    df.groupby(["year", "contact"])
      .size()
      .reset_index(name="n")
      .sort_values(["year", "n"], ascending=[True, False])
)

if len(top_contact_year) > 0:
    best_per_year = top_contact_year.groupby("year").head(1)
    for _, row in best_per_year.iterrows():
        print(f"{int(row['year'])}: {row['contact']} ({int(row['n'])} messaggi)")
else:
    print("Nessun dato per top contatto per anno.")

# ==============================
# RESPONSE TIME STATS
# ==============================
print("\n==============================")
print("TEMPI DI RISPOSTA (STATS)")
print("==============================")

df_sorted = df.sort_values(["contact", "ts"]).copy()

# Next message within same contact
df_sorted["next_ts"] = df_sorted.groupby("contact")["ts"].shift(-1)
df_sorted["next_is_from_me"] = df_sorted.groupby("contact")["is_from_me"].shift(-1)

df_sorted["delta_sec_to_next"] = (
    df_sorted["next_ts"] - df_sorted["ts"]
).dt.total_seconds()

# Your response: received -> sent
your_resp = df_sorted[
    (df_sorted["is_from_me"] == 0) &
    (df_sorted["next_is_from_me"] == 1) &
    (df_sorted["delta_sec_to_next"].notna()) &
    (df_sorted["delta_sec_to_next"] >= 0)
][["contact", "delta_sec_to_next"]].copy()

# Their response: sent -> received
their_resp = df_sorted[
    (df_sorted["is_from_me"] == 1) &
    (df_sorted["next_is_from_me"] == 0) &
    (df_sorted["delta_sec_to_next"].notna()) &
    (df_sorted["delta_sec_to_next"] >= 0)
][["contact", "delta_sec_to_next"]].copy()

import numpy as np

def fmt_seconds(s):
    if s < 60:
        return f"{s:.0f}s"
    m = s / 60
    if m < 60:
        return f"{m:.1f}m"
    h = m / 60
    if h < 48:
        return f"{h:.2f}h"
    d = h / 24
    return f"{d:.2f}d"

def print_resp_block(title, resp_df):
    print(f"\n--- {title} ---")
    if len(resp_df) == 0:
        print("Nessun dato.")
        return

    vals = resp_df["delta_sec_to_next"].values
    print(f"N campioni: {len(vals)}")
    print(f"Mediana: {fmt_seconds(np.median(vals))}")
    print(f"Media:   {fmt_seconds(np.mean(vals))}")
    print(f"P90:     {fmt_seconds(np.quantile(vals, 0.90))}")

print_resp_block("Tempo di risposta TUO (ricevuto → inviato)", your_resp)
print_resp_block("Tempo di risposta LORO (inviato → ricevuto)", their_resp)
