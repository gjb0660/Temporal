from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Qt, Signal

from temporal.qt_decorators import qt_property, qt_slot


class QmlListModel(QAbstractListModel):
    countChanged = Signal()

    def __init__(self, roles: list[str], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._roles = list(roles)
        self._role_ids = {
            Qt.ItemDataRole.UserRole + index + 1: role_name
            for index, role_name in enumerate(self._roles)
        }
        self._items: list[dict[str, Any]] = []

    @qt_property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._items)

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        if row < 0 or row >= len(self._items):
            return None

        role_name = self._role_ids.get(role)
        if role_name is None:
            return None
        return self._items[row].get(role_name)

    def roleNames(self) -> dict[int, bytes]:
        return {role_id: role_name.encode("utf-8") for role_id, role_name in self._role_ids.items()}

    @qt_slot(int, result="QVariant")
    def get(self, index: int) -> dict[str, Any]:
        if index < 0 or index >= len(self._items):
            return {}
        return dict(self._items[index])

    def replace(self, items: list[dict[str, Any]] | list[Any]) -> None:
        normalized = [self._normalize_item(item) for item in items]
        if normalized == self._items:
            return
        count_before = len(self._items)
        self.beginResetModel()
        self._items = normalized
        self.endResetModel()
        if count_before != len(self._items):
            self.countChanged.emit()

    def snapshot(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._items]

    def _normalize_item(self, item: dict[str, Any] | Any) -> dict[str, Any]:
        if len(self._roles) == 1 and self._roles[0] == "value" and not isinstance(item, dict):
            return {"value": item}

        if not isinstance(item, dict):
            return {role_name: None for role_name in self._roles}

        return {role_name: item.get(role_name) for role_name in self._roles}
