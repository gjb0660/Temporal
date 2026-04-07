from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

from PySide6.QtCore import Property, Slot

F = TypeVar("F", bound=Callable[..., Any])


def qt_property(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], Property(*args, **kwargs))


def qt_slot(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], Slot(*args, **kwargs))
