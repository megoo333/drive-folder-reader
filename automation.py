from __future__ import annotations

import argparse
import json
import sys
from json import JSONDecodeError
from pathlib import Path

from src.drive_folder_reader import load_drive_items, organize_drive_items, print_summary


DEFAULT_INPUT = Path(__file__).parent / "samples" / "sample_drive_items.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Google Drive風JSONを読み込み、授業フォルダ構成を整理します。"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=str(DEFAULT_INPUT),
        help="読み込むJSONファイル。省略時は samples/sample_drive_items.json を使います。",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="整理結果を書き出すJSONファイル。指定しない場合は画面に表示します。",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Summaryを出さず、JSONだけを表示します。",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    try:
        result = run(input_path)
    except FileNotFoundError:
        print_error(
            "入力ファイルが見つかりません。",
            f"指定されたパス: {input_path}",
            "ファイル名や場所を確認してください。",
        )
        return 1
    except JSONDecodeError as error:
        print_error(
            "JSONの読み込みに失敗しました。",
            f"{error.msg} at line {error.lineno}, column {error.colno}",
            "カンマ抜け、閉じ括弧抜け、引用符の不足がないか確認してください。",
        )
        return 1
    except ValueError as error:
        print_error(
            "入力データの形式が正しくありません。",
            str(error),
            "JSONは配列、または {'files': [...]} の形にしてください。",
        )
        return 1
    except KeyError as error:
        print_error(
            "必要な項目が足りません。",
            f"足りない項目: {error}",
            "各アイテムに id, title, mime_type が入っているか確認してください。",
        )
        return 1
    except Exception as error:
        print_error(
            "予期しないエラーが起きました。",
            f"{type(error).__name__}: {error}",
            "入力JSONの内容を確認してください。",
        )
        return 1

    if args.output:
        output_path = Path(args.output)
        try:
            output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as error:
            print_error(
                "出力ファイルを書き込めませんでした。",
                str(error),
                "保存先フォルダが存在するか、書き込み権限があるか確認してください。",
            )
            return 1

        print(f"整理結果を書き出しました: {output_path}")
        return 0

    if not args.json_only:
        print("=== Summary ===")
        print_summary(result)

    print("=== JSON ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def run(input_path: Path) -> dict:
    items = load_drive_items(input_path)
    return organize_drive_items(items)


def print_error(title: str, detail: str, hint: str) -> None:
    print(f"ERROR: {title}", file=sys.stderr)
    print(f"DETAIL: {detail}", file=sys.stderr)
    print(f"HINT: {hint}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
