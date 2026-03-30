from __future__ import annotations

import logging

SOURCE_COLOR_PALETTE: tuple[str, ...] = (
    "#4bc0c0",  # odas_web base-0
    "#c04bc0",  # odas_web base-1
    "#c0c01e",  # odas_web base-2
    "#00c828",  # odas_web base-3
    "#6a88ff",
    "#f16f7d",
    "#ff9c47",
    "#5ac97c",
    "#47b2da",
    "#e970ff",
    "#ff7cbd",
    "#76da52",
)

_LOGGER = logging.getLogger(__name__)


class SourceColorAllocator:
    def __init__(self, palette: tuple[str, ...] | None = None) -> None:
        provided_palette = tuple(palette or SOURCE_COLOR_PALETTE)
        if not provided_palette:
            provided_palette = ("#4bc0c0",)
        self._palette = provided_palette
        self._color_by_source_id: dict[int, str] = {}
        self._next_color_index = 0
        self._overflow_warned = False
        self.reset()

    def reset(self) -> None:
        self._color_by_source_id: dict[int, str] = {}
        self._next_color_index = 0
        self._overflow_warned = False

    def color_for(self, source_id: int) -> str:
        sid = int(source_id)
        if sid in self._color_by_source_id:
            return self._color_by_source_id[sid]
        color = self._next_color()
        self._color_by_source_id[sid] = color
        return color

    def _next_color(self) -> str:
        palette_size = len(self._palette)
        if self._next_color_index < palette_size:
            color = self._palette[self._next_color_index]
        else:
            color = self._palette[self._next_color_index % palette_size]
            if not self._overflow_warned:
                self._overflow_warned = True
                _LOGGER.warning(
                    "Source color palette exhausted; reusing colors from palette head (size=%d)",
                    palette_size,
                )
        self._next_color_index += 1
        return color
