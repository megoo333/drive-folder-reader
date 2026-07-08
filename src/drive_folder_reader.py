from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


FILE_TYPE_BY_MIME = {
    "application/vnd.google-apps.presentation": "presentation",
    "application/vnd.google-apps.document": "document",
    "application/vnd.google-apps.spreadsheet": "spreadsheet",
    "application/vnd.google-apps.form": "form",
    "application/pdf": "pdf",
    "image/png": "image",
    "image/jpeg": "image",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
}


@dataclass
class Material:
    id: str
    title: str
    mime_type: str
    type: str
    url: str | None = None


@dataclass
class LessonFolder:
    id: str
    title: str
    lesson_number: int
    url: str | None = None
    materials: list[Material] = field(default_factory=list)


@dataclass
class SubjectFolder:
    id: str
    title: str
    url: str | None = None
    lessons: list[LessonFolder] = field(default_factory=list)
    shared_materials: list[Material] = field(default_factory=list)


def load_drive_items(json_path: str | Path) -> list[dict[str, Any]]:
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and isinstance(data.get("files"), list):
        return data["files"]

    raise ValueError("JSON must be a list of items or an object with a 'files' list.")


def organize_drive_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    item_by_id = {item["id"]: item for item in items}
    children_by_parent = _group_children_by_parent(items)
    subject_folders = _find_subject_folders(items, item_by_id)

    subjects = []
    for subject_item in subject_folders:
        subject = SubjectFolder(
            id=subject_item["id"],
            title=subject_item["title"],
            url=subject_item.get("url"),
        )

        for child in children_by_parent.get(subject.id, []):
            if _is_folder(child):
                lesson_number = parse_lesson_number(child["title"])
                if lesson_number is not None:
                    lesson = LessonFolder(
                        id=child["id"],
                        title=child["title"],
                        lesson_number=lesson_number,
                        url=child.get("url"),
                    )
                    lesson.materials = [
                        _to_material(grandchild)
                        for grandchild in children_by_parent.get(child["id"], [])
                        if not _is_folder(grandchild)
                    ]
                    subject.lessons.append(lesson)
            else:
                subject.shared_materials.append(_to_material(child))

        subject.lessons.sort(key=lambda lesson: lesson.lesson_number)
        subjects.append(subject)

    return {"subjects": [asdict(subject) for subject in subjects]}


def parse_lesson_number(title: str) -> int | None:
    normalized = title.strip().translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    if normalized.isdigit():
        return int(normalized)

    match = re.search(r"(?:第|回\s*)?(\d{1,2})\s*回?", normalized)
    if match:
        return int(match.group(1))

    return None


def print_summary(result: dict[str, Any]) -> None:
    for subject in result["subjects"]:
        print(f"科目: {subject['title']}")

        if subject["shared_materials"]:
            print("  共通資料:")
            for material in subject["shared_materials"]:
                print(f"    - [{material['type']}] {material['title']}")

        if subject["lessons"]:
            print("  授業回:")
            for lesson in subject["lessons"]:
                print(f"    - 第{lesson['lesson_number']}回: {lesson['title']}")
                for material in lesson["materials"]:
                    print(f"      - [{material['type']}] {material['title']}")

        print()


def _group_children_by_parent(items: list[dict[str, Any]]) -> dict[str | None, list[dict[str, Any]]]:
    children_by_parent: dict[str | None, list[dict[str, Any]]] = {}
    for item in items:
        parent_id = item.get("parent_id")
        children_by_parent.setdefault(parent_id, []).append(item)
    return children_by_parent


def _find_subject_folders(
    items: list[dict[str, Any]],
    item_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    folders = [item for item in items if _is_folder(item)]
    lesson_folder_ids = {
        item["id"]
        for item in folders
        if parse_lesson_number(item["title"]) is not None
    }

    subjects = []
    for folder in folders:
        parent_id = folder.get("parent_id")
        parent = item_by_id.get(parent_id) if parent_id else None
        is_child_of_lesson = parent is not None and parent["id"] in lesson_folder_ids
        has_lesson_children = any(
            child.get("parent_id") == folder["id"] and parse_lesson_number(child["title"]) is not None
            for child in folders
        )

        if folder["id"] not in lesson_folder_ids and not is_child_of_lesson and has_lesson_children:
            subjects.append(folder)

    return subjects


def _is_folder(item: dict[str, Any]) -> bool:
    return item.get("mime_type") == FOLDER_MIME_TYPE


def _to_material(item: dict[str, Any]) -> Material:
    mime_type = item.get("mime_type", "")
    return Material(
        id=item["id"],
        title=item["title"],
        mime_type=mime_type,
        type=FILE_TYPE_BY_MIME.get(mime_type, "file"),
        url=item.get("url"),
    )
