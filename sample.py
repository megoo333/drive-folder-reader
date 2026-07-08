import json
from pathlib import Path

from src.drive_folder_reader import load_drive_items, organize_drive_items, print_summary


def main() -> None:
    sample_path = Path(__file__).parent / "samples" / "sample_drive_items.json"
    items = load_drive_items(sample_path)
    result = organize_drive_items(items)

    print("=== Summary ===")
    print_summary(result)

    print("=== JSON ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
