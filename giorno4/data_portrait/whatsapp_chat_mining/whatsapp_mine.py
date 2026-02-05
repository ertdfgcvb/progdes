#!/usr/bin/env python3
# whatsapp_mine.py
# Stdlib-only WhatsApp exported chat analyzer (folder of .txt files)

import os
import re
import sys
from datetime import datetime
from collections import Counter, defaultdict

# ----------------------------
# CONFIG
# ----------------------------
# Put your WhatsApp display name(s) exactly as they appear in exports.
# Example:
# MY_NAMES = {"Andreas", "Andreas R."}
MY_NAMES = {"Andreas"}

# Reaction time cutoff (seconds). Helps avoid “next day” gaps skewing averages.
# Set to None to disable cutoff.
REACTION_CUTOFF_SEC = 6 * 3600  # 6 hours

# How wide the hourly bar chart should be
HOUR_BAR_WIDTH = 40

# Top words
TOP_WORDS = 100

# Word regex (keeps letters, including accents)
WORD_RE = re.compile(r"[a-zàèéìòùäöüßçñ]+", re.IGNORECASE)

# ----------------------------
# WhatsApp line formats
# Common:
#   Android:  12/31/23, 21:05 - Name: message
#   iOS:      [12/31/23, 21:05:12] Name: message
# Also possible:
#   31.12.23, 21:05 - Name: message
# Time may include seconds; may include AM/PM
# ----------------------------

# Start-of-message patterns (capture date, time, sender, text)
# iOS-like (bracketed) patterns:
# Supports:
#   [15.04.2020, 16:20:56] Name: text
#   [15.04.2020 16:20:56]  Name: text

PATTERNS = [
    # Android-like: "dd/mm/yy, hh:mm - Name: text"
    re.compile(
        r"^(?P<date>\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}),?\s+"
        r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s+-\s+"
        r"(?P<sender>[^:]+):\s*(?P<text>.*)$"
    ),
    # iOS-like: "[dd/mm/yy, hh:mm:ss] Name: text" OR "[dd/mm/yy hh:mm:ss] Name: text"
    re.compile(
        r"^\[(?P<date>\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})(?:,\s+|\s+)"
        r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\]\s+"
        r"(?P<sender>[^:]+):\s*(?P<text>.*)$"
    ),
]

SYSTEM_PATTERNS = [
    # Android-like system: "dd/mm/yy, hh:mm - text"
    re.compile(
        r"^(?P<date>\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}),?\s+"
        r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s+-\s+"
        r"(?P<text>.*)$"
    ),
    # iOS-like system: "[dd/mm/yy, hh:mm:ss] text" OR "[dd/mm/yy hh:mm:ss] text"
    re.compile(
        r"^\[(?P<date>\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})(?:,\s+|\s+)"
        r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\]\s+"
        r"(?P<text>.*)$"
    ),
]


# Date/time parse formats to try
DT_FORMATS = [
    # day/month
    "%d/%m/%y %H:%M",
    "%d/%m/%Y %H:%M",
    "%d/%m/%y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d.%m.%y %H:%M",
    "%d.%m.%Y %H:%M",
    "%d.%m.%y %H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%d-%m-%y %H:%M",
    "%d-%m-%Y %H:%M",
    "%d-%m-%y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    # month/day
    "%m/%d/%y %H:%M",
    "%m/%d/%Y %H:%M",
    "%m/%d/%y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    # 12-hour variants
    "%d/%m/%y %I:%M %p",
    "%d/%m/%Y %I:%M %p",
    "%d/%m/%y %I:%M:%S %p",
    "%d/%m/%Y %I:%M:%S %p",
    "%m/%d/%y %I:%M %p",
    "%m/%d/%Y %I:%M %p",
    "%m/%d/%y %I:%M:%S %p",
    "%m/%d/%Y %I:%M:%S %p",
    "%d.%m.%y %I:%M %p",
    "%d.%m.%Y %I:%M %p",
    "%d.%m.%y %I:%M:%S %p",
    "%d.%m.%Y %I:%M:%S %p",
]


def try_parse_dt(date_str, time_str):
    s = f"{date_str} {time_str}".strip()
    # Normalize multiple spaces
    s = re.sub(r"\s+", " ", s)
    for fmt in DT_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def open_text_file(path):
    # Try common encodings
    for enc in ("utf-8-sig", "utf-8", "utf-16"):
        try:
            with open(path, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except Exception:
            pass
    # Fallback: replace errors
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_chat_text(content):
    """
    Returns list of messages:
      dict(ts=datetime, sender=str|None, text=str, is_system=bool)
    Handles multiline messages by appending lines that don't start a new message.
    """
    messages = []
    current = None

    for raw_line in content.splitlines():
        line = raw_line.rstrip("\n")

        matched = None
        is_system = False

        for pat in PATTERNS:
            m = pat.match(line)
            if m:
                matched = m
                is_system = False
                break

        if matched is None:
            for pat in SYSTEM_PATTERNS:
                m = pat.match(line)
                if m:
                    matched = m
                    is_system = True
                    break

        if matched:
            # Flush previous
            if current is not None:
                messages.append(current)

            gd = matched.groupdict()
            ts = try_parse_dt(gd.get("date", ""), gd.get("time", ""))
            sender = gd.get("sender") if not is_system else None
            text = gd.get("text", "")

            current = {
                "ts": ts,
                "sender": sender.strip() if sender else None,
                "text": text if text is not None else "",
                "is_system": is_system,
            }
        else:
            # continuation line (multiline message)
            if current is not None:
                current["text"] += "\n" + line
            else:
                # junk/header before first parsable line -> ignore
                pass

    if current is not None:
        messages.append(current)

    # Drop messages with unparsed timestamps
    messages = [m for m in messages if m["ts"] is not None]
    return messages


def ascii_hourly_bar(hour_counts):
    max_val = max(hour_counts) if hour_counts else 0
    lines = []
    for h in range(24):
        val = hour_counts[h]
        bar_len = int((val / max_val) * HOUR_BAR_WIDTH) if max_val > 0 else 0
        bar = "█" * bar_len
        lines.append(f"{h:02d}: {val:6d} {bar}")
    return "\n".join(lines)


def fmt_td(seconds):
    # human readable duration
    if seconds is None:
        return "n/a"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    if h < 48:
        return f"{h}h {m}m"
    d, h = divmod(h, 24)
    return f"{d}d {h}h"


def stats_for_messages(messages, my_names, label="TOTAL"):
    """
    Compute stats for a set of messages.
    Only counts non-system messages for most metrics (words, sent/received, reaction).
    """
    non_system = [m for m in messages if not m["is_system"] and m["sender"]]
    all_ts = [m["ts"] for m in non_system] or [m["ts"] for m in messages if m["ts"]]

    first_ts = min(all_ts) if all_ts else None
    last_ts = max(all_ts) if all_ts else None
    span_sec = (last_ts - first_ts).total_seconds() if first_ts and last_ts else None

    total_msgs = len(non_system)

    # Determine "me"
    sender_counts = Counter(m["sender"] for m in non_system)
    guessed_me = None
    if not my_names:
        if sender_counts:
            guessed_me = sender_counts.most_common(1)[0][0]
            my_names = {guessed_me}
        else:
            my_names = set()

    sent = sum(1 for m in non_system if m["sender"] in my_names)
    received = total_msgs - sent
    ratio = (sent / received) if received > 0 else None

    # Words
    all_text = " ".join(m["text"] for m in non_system).lower()
    words = WORD_RE.findall(all_text)
    top_words = Counter(words).most_common(TOP_WORDS)

    # Hourly counts
    hour_counts = [0] * 24
    for m in non_system:
        hour_counts[m["ts"].hour] += 1

    # Reaction times: within chat, when sender switches
    # me reaction: them -> me
    # them reaction: me -> them
    non_system_sorted = sorted(non_system, key=lambda x: x["ts"])
    me_react = []
    them_react = []

    def within_cutoff(dt_sec):
        return True if REACTION_CUTOFF_SEC is None else (dt_sec <= REACTION_CUTOFF_SEC)

    for prev, cur in zip(non_system_sorted, non_system_sorted[1:]):
        dt_sec = (cur["ts"] - prev["ts"]).total_seconds()
        if dt_sec < 0:
            continue
        if not within_cutoff(dt_sec):
            continue

        prev_me = prev["sender"] in my_names
        cur_me = cur["sender"] in my_names

        if (not prev_me) and cur_me:
            me_react.append(dt_sec)
        elif prev_me and (not cur_me):
            them_react.append(dt_sec)

    def avg(xs):
        return (sum(xs) / len(xs)) if xs else None

    def median(xs):
        if not xs:
            return None
        xs2 = sorted(xs)
        n = len(xs2)
        mid = n // 2
        if n % 2 == 1:
            return xs2[mid]
        return 0.5 * (xs2[mid - 1] + xs2[mid])

    return {
        "label": label,
        "guessed_me": guessed_me,
        "my_names": my_names,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "span_sec": span_sec,
        "total_msgs": total_msgs,
        "sent": sent,
        "received": received,
        "ratio": ratio,
        "top_words": top_words,
        "hour_counts": hour_counts,
        "me_react_avg": avg(me_react),
        "me_react_med": median(me_react),
        "me_react_n": len(me_react),
        "them_react_avg": avg(them_react),
        "them_react_med": median(them_react),
        "them_react_n": len(them_react),
        "top_senders": sender_counts.most_common(10),
    }


def print_report(stats):
    print("\n==============================")
    print(stats["label"])
    print("==============================")

    if stats["guessed_me"]:
        print(f"NOTE: MY_NAMES not set -> guessed 'me' as: {stats['guessed_me']!r}")
    if stats["my_names"]:
        print(f"Me names: {', '.join(sorted(stats['my_names']))}")

    print(f"First message: {stats['first_ts']}")
    print(f"Last message:  {stats['last_ts']}")
    print(f"Time span:     {fmt_td(stats['span_sec'])}")

    print("\n--- Counts ---")
    print(f"Total messages: {stats['total_msgs']}")
    print(f"Sent (me):      {stats['sent']}")
    print(f"Received:       {stats['received']}")
    if stats["ratio"] is None:
        print("Sent/Received:  n/a (no received messages)")
    else:
        print(f"Sent/Received:  {stats['ratio']:.3f}")

    print("\n--- Top senders (debug/helpful) ---")
    for name, n in stats["top_senders"]:
        print(f"{name}: {n}")

    print("\n--- Messages per hour ---")
    print(ascii_hourly_bar(stats["hour_counts"]))

    print("\n--- Reaction times (sender switch, within cutoff) ---")
    cutoff_label = "no cutoff" if REACTION_CUTOFF_SEC is None else f"<= {fmt_td(REACTION_CUTOFF_SEC)}"
    print(f"Cutoff: {cutoff_label}")
    print(f"Me reaction:   avg={fmt_td(stats['me_react_avg'])}  med={fmt_td(stats['me_react_med'])}  n={stats['me_react_n']}")
    print(f"Them reaction: avg={fmt_td(stats['them_react_avg'])}  med={fmt_td(stats['them_react_med'])}  n={stats['them_react_n']}")

    print(f"\n--- Top {TOP_WORDS} words ---")
    for w, c in stats["top_words"]:
        print(f"{w}: {c}")


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    folder = os.path.abspath(folder)

    if not os.path.isdir(folder):
        print(f"ERROR: Not a folder: {folder}")
        sys.exit(1)

    txt_files = sorted(
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".txt") and os.path.isfile(os.path.join(folder, f))
    )

    if not txt_files:
        print(f"No .txt files found in: {folder}")
        sys.exit(0)

    print(f"Folder: {folder}")
    print(f"Found {len(txt_files)} txt files.\n")

    all_messages = []
    per_file_stats = []

    for path in txt_files:
        content = open_text_file(path)
        msgs = parse_chat_text(content)
        all_messages.extend(msgs)

        label = f"FILE: {os.path.basename(path)}"
        st = stats_for_messages(msgs, set(MY_NAMES), label=label)
        per_file_stats.append(st)

    # Print per-file
    for st in per_file_stats:
        print_report(st)

    # Print total
    total_stats = stats_for_messages(all_messages, set(MY_NAMES), label="TOTAL (ALL FILES)")
    print_report(total_stats)


if __name__ == "__main__":
    main()
