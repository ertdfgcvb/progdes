import sys
from pathlib import Path

from iphone_backup_decrypt import EncryptedBackup

TARGETS = [
    ("sms.db", "Library/SMS/sms.db"),                              # Messages
    ("addressbook.sqlitedb", "Library/AddressBook/AddressBook.sqlitedb"),  # Contacts
    ("call_history.storedata", "Library/CallHistoryDB/CallHistory.storedata"),  # Calls
    ("knowledgeC.db", "Library/CoreDuet/Knowledge/knowledgeC.db"),  # App usage (often present)
]

def try_extract(backup, relpath: str, out_file: Path) -> bool:
    # Try the common API: extract by relative_path string
    try:
        backup.extract_file(relative_path=relpath, output_filename=str(out_file))
        return True
    except TypeError:
        # Some versions use different argument names
        try:
            backup.extract_file(relpath, str(out_file))
            return True
        except Exception:
            return False
    except Exception:
        return False

def main():
    if len(sys.argv) != 4:
        print("Usage: python extract_iphone.py <BACKUP_DIR> <OUTPUT_DIR> <PASSWORD>")
        sys.exit(2)

    backup_dir = Path(sys.argv[1]).expanduser()
    out_dir = Path(sys.argv[2]).expanduser()
    password = sys.argv[3]
    out_dir.mkdir(parents=True, exist_ok=True)

    backup = EncryptedBackup(backup_directory=str(backup_dir), passphrase=password)

    # Save a decrypted manifest for hunting other files later
    manifest_path = out_dir / "Manifest.decrypted.db"
    try:
        backup.save_manifest_file(str(manifest_path))
        print(f"OK  manifest -> {manifest_path}")
    except Exception as e:
        print(f"WARN could not save manifest: {e}")

    for name, rel in TARGETS:
        out_file = out_dir / name
        ok = try_extract(backup, rel, out_file)
        if ok and out_file.exists():
            print(f"OK  {rel} -> {out_file}")
        else:
            print(f"SKIP {rel} (not found or API mismatch)")

if __name__ == "__main__":
    main()
    