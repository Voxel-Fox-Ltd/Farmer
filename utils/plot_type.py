from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import novus

__all__ = (
    'PlotBase',
    'PlotType',
)


class PlotBase:
    """
    A type of plot that animals can live in.
    """

    def __init__(self, name: str):
        self.name = name

    @property
    def style(self) -> novus.ButtonStyle:
        match self.name:
            case "farm":
                return novus.ButtonStyle.green
            case "garden":
                return novus.ButtonStyle.red
            case "lake":
                return novus.ButtonStyle.blurple
            case "sky":
                return novus.ButtonStyle.gray
            case _:
                raise ValueError("Invalid Type")


class PlotType(Enum):
    FARM = PlotBase("farm")
    GARDEN = PlotBase("garden")
    LAKE = PlotBase("lake")
    SKY = PlotBase("sky")

    if TYPE_CHECKING:
        value: PlotBase
