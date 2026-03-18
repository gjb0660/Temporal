from __future__ import annotations


def build_source_items(sst_message: dict, enabled: bool = True) -> list[str]:
    if not enabled:
        return []

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


def _read_energy(potential: dict) -> float | None:
    for key in ("E", "energy"):
        value = potential.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def count_potentials(
    ssl_message: dict,
    min_energy: float = 0.0,
    max_energy: float = 1.0,
    enabled: bool = True,
) -> int:
    if not enabled:
        return 0

    low = min(min_energy, max_energy)
    high = max(min_energy, max_energy)

    src = ssl_message.get("src", [])
    if not isinstance(src, list):
        return 0

    count = 0
    for item in src:
        if not isinstance(item, dict):
            continue
        energy = _read_energy(item)
        if energy is None:
            continue
        if low <= energy <= high:
            count += 1
    return count
