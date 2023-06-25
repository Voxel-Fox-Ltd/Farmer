from __future__ import annotations

from typing import TYPE_CHECKING
from typing_extensions import Self
from uuid import uuid4
import random

from .animal_type import AnimalType

if TYPE_CHECKING:
    from uuid import UUID

    import asyncpg

__all__ = (
    'Animal',
)


class Animal:
    """
    An animal owned by a user.

    Attributes
    ----------
    id : str
        The ID of the animal.
    type : AnimalType
        The type of the animal.
    plot_id : str
        The ID of the plot that the animal is in.
    """

    def __init__(
            self,
            *,
            id: str | UUID | None,
            type: AnimalType,
            plot_id: str | UUID,
            production_rate: float | None = None):
        self.id: str = str(id) if id is not None else str(uuid4())
        self.type: AnimalType = type
        self.plot_id: str = str(plot_id)
        self.production_rate = (
            production_rate
            if production_rate is not None
            else random.random()
        )

    def __str__(self) -> str:
        return self.type.value.name

    @property
    def emoji(self) -> str:
        return self.type.value.emoji

    @classmethod
    def from_row(cls, row: dict) -> Self:
        """
        Create a plot instance from a row.
        """

        return cls(
            id=row["id"],
            type=AnimalType[row["type"]],
            plot_id=row["plot_id"],
            production_rate=row["production_rate"],
        )

    async def save(self, db: asyncpg.Connection) -> Self:
        """
        Save the animal into the database.
        """

        rows = await db.fetch(
            """
            INSERT INTO
                animals
                (
                    id,
                    type,
                    plot_id,
                    production_rate
                )
            VALUES
                (
                    $1,
                    $2,
                    $3,
                    $4
                )
            ON CONFLICT (id)
            DO UPDATE
            SET
                type = excluded.type,
                plot_id = excluded.plot_id,
                production_rate = excluded.production_rate
            RETURNING *
            """,
            self.id,
            self.type.name,
            self.plot_id,
            self.production_rate,
        )
        return self.from_row(rows[0])
