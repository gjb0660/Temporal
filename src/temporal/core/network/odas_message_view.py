from __future__ import annotations


def build_source_items(sst_message: dict) -> list[str]:
    src = sst_message.get("src", [])
    if not isinstance(src, list):
        return []

    items: list[str] = []
    for item in src:
        if not isinstance(item, dict):
            continue
        source_id = item.get("id")
        if not isinstance(source_id, int) or source_id == 0:
            continue
        items.append(f"Source {source_id}")
    return items


def count_potentials(ssl_message: dict) -> int:
    src = ssl_message.get("src", [])
    if not isinstance(src, list):
        return 0
    return sum(1 for item in src if isinstance(item, dict))
