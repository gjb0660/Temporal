from __future__ import annotations


def extract_source_ids(sst_message: dict) -> list[int]:
    src = sst_message.get("src", [])
    if not isinstance(src, list):
        return []

    source_ids: list[int] = []
    seen: set[int] = set()
    for item in src:
        if not isinstance(item, dict):
            continue
        source_id = item.get("id")
        if not isinstance(source_id, int) or source_id == 0:
            continue
        if source_id in seen:
            continue
        seen.add(source_id)
        source_ids.append(source_id)
    return source_ids


def extract_source_positions(
    sst_message: dict,
    selected_ids: set[int] | None = None,
    enabled: bool = True,
) -> list[dict[str, float | int]]:
    if not enabled:
        return []

    src = sst_message.get("src", [])
    if not isinstance(src, list):
        return []

    points: list[dict[str, float | int]] = []
    seen: set[int] = set()
    for item in src:
        if not isinstance(item, dict):
            continue

        source_id = item.get("id")
        x = item.get("x")
        y = item.get("y")
        z = item.get("z")
        if not isinstance(source_id, int) or source_id == 0:
            continue
        if source_id in seen:
            continue
        if selected_ids is not None and source_id not in selected_ids:
            continue
        if not isinstance(x, (int, float)):
            continue
        if not isinstance(y, (int, float)):
            continue
        if not isinstance(z, (int, float)):
            continue

        seen.add(source_id)
        points.append(
            {
                "id": source_id,
                "x": float(x),
                "y": float(y),
                "z": float(z),
            }
        )
    return points


def build_source_items(
    sst_message: dict,
    enabled: bool = True,
    selected_ids: set[int] | None = None,
) -> list[str]:
    if not enabled:
        return []

    source_ids = extract_source_ids(sst_message)
    if selected_ids is not None:
        source_ids = [source_id for source_id in source_ids if source_id in selected_ids]
    return [f"Source {source_id}" for source_id in source_ids]


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
