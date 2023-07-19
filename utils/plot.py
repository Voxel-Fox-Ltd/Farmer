from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, overload
from typing_extensions import Self
from uuid import uuid4
import random

from .animal import Animal
from .plot_type import PlotType

if TYPE_CHECKING:
    from uuid import UUID

    import asyncpg


__all__ = (
    'Plot',
)


class Plot:
    """
    A plot of land that contains animals.

    Attributes
    ----------
    id : str
        The ID of the plot of land.
    owner_id : int
        The ID of the user that owns the plot of land.
    guild_id : int
        The ID of the guild that the plot of land exists in.
    position : Iterable[int]
        A two-item iterable of the XY coordinate for the plot.
    type : str
        The type of the plot of land.
    """

    def __init__(
            self,
            *,
            id: str | UUID | None,
            guild_id: int,
            owner_id: int,
            position: Iterable[int],
            type: PlotType) -> None:
        self.id: str = str(id) if id is not None else str(uuid4())
        self.guild_id: int = guild_id
        self.owner_id: int = owner_id
        self.position: tuple[int, int] = tuple(position)
        self.type = type

    @classmethod
    def from_row(cls, row: dict) -> Self:
        """
        Create a plot instance from a row.
        """

        return cls(
            id=row["id"],
            owner_id=row["owner_id"],
            guild_id=row["guild_id"],
            position=row["position"],
            type=PlotType[row["type"]],
        )

    @overload
    @classmethod
    async def fetch_for_user(
            cls,
            db: asyncpg.Connection,
            guild_id: int,
            user_id: int,
            position: None = None) -> list[Self]:
        ...

    @overload
    @classmethod
    async def fetch_for_user(
            cls,
            db: asyncpg.Connection,
            guild_id: int,
            user_id: int,
            position: tuple[int, int] = ...) -> Self | None:
        ...

    @classmethod
    async def fetch_for_user(
            cls,
            db: asyncpg.Connection,
            guild_id: int,
            user_id: int,
            position: tuple[int, int] | None = None) -> list[Self] | Self | None:
        """
        Get all of the plots that a user owns.
        """

        if position is None:
            rows = await db.fetch(
                """
                SELECT
                    *
                FROM
                    plots
                WHERE
                    owner_id = $1
                    AND guild_id = $2
                """,
                user_id, guild_id,
            )
            return [cls.from_row(i) for i in rows]

        rows = await db.fetch(
            """
            SELECT
                *
            FROM
                plots
            WHERE
                owner_id = $1
                AND guild_id = $2
                AND position = $3
            """,
            user_id, guild_id, position,
        )
        if rows:
            return cls.from_row(rows[0])
        return None

    async def save(self, db: asyncpg.Connection) -> Self:
        """
        Save the plot into the database.
        """

        rows = await db.fetch(
            """
            INSERT INTO 
                plots
                (
                    id,
                    owner_id,
                    guild_id,
                    position,
                    type
                )
            VALUES
                (
                    $1,
                    $2,
                    $3,
                    $4,
                    $5
                )
            ON CONFLICT (id)
            DO UPDATE
            SET
                owner_id = excluded.owner_id,
                guild_id = excluded.guild_id,
                position = excluded.position,
                type = excluded.type
            RETURNING *
            """,
            self.id,
            self.owner_id,
            self.guild_id,
            self.position,
            self.type.name,
        )
        return self.from_row(rows[0])

    async def fetch_animals(self, db: asyncpg.Connection) -> PlotWithAnimals:
        """
        Fetch the animals for the plot, storing them in an ``animals`` attr.
        """

        rows = await db.fetch(
            """
            SELECT
                *
            FROM
                animals
            WHERE
                plot_id = $1
            """,
            self.id,
        )
        animals = [Animal.from_row(i) for i in rows]
        return PlotWithAnimals.from_plot(self, animals=animals)


class PlotWithAnimals(Plot):
    """
    A plot of land that has animals inside of it.
    """

    animals: list[Animal]

    def __init__(self, *args, animals: list[Animal], **kwargs):
        super().__init__(*args, **kwargs)
        self.animals = animals

    @classmethod
    def from_plot(cls, plot: Plot, **kwargs) -> Self:
        return cls(
            id=plot.id,
            guild_id=plot.guild_id,
            owner_id=plot.owner_id,
            position=plot.position,
            type=plot.type,
            **kwargs,
        )

    def __str__(self) -> str:
        r = random.Random(self.id)
        def make_row(r: random.Random, k: int = 5) -> list[str]:
            return [
                r.choice([
                    "<:grass2:1058306471395328030>",
                    "<:grass3:1058307717124595792>",
                ])
                for _ in range(k)
            ]
        rows = [
            ["<:fence:1058304105644294154>"] * 5,
            make_row(r),
            make_row(r),
            make_row(r),
            make_row(r),
            make_row(r),
        ]
        assigned_plots: set[tuple[int, int]] = set()
        to_add = self.animals.copy()
        while to_add:
            position = tuple(random.choices(range(0, 5), k=2))
            if position in assigned_plots:
                continue
            animal = to_add.pop()
            rows[position[0] + 1][position[1]] = animal.emoji
            assigned_plots.add(position)
        return "\n".join(["".join([c for c in r]) for r in rows])
