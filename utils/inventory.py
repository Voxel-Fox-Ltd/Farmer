from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, NoReturn
from typing_extensions import Self

from .animal import AnimalType

if TYPE_CHECKING:
    from uuid import UUID

    import asyncpg


__all__ = (
    'Item',
    'ItemInventory',
    'UserItems',
    'PlotItems',
    'Inventory',
)


class Item:
    """
    An item contained within an inventory.
    """

    def __init__(self, animal: AnimalType, amount: int = 0):
        self.animal = animal
        self.amount = amount

    def __str__(self) -> str:
        # return f"{self.amount} {self.animal.value.name} {self.get_name()}"
        return f"{self.amount:,} {self.get_name()}"

    @property
    def product(self) -> tuple[str, str]:
        return self.animal.value.product

    def get_name(self) -> str:
        if self.amount == 1:
            return self.animal.value.product[0]
        return self.animal.value.product[1]


class ItemInventory:
    """
    Abstract base class for a user and a plot's inventory.
    """

    items: list[Item]

    @classmethod
    def from_rows(cls, data) -> NoReturn:
        raise NotImplementedError()


class UserItems(ItemInventory):
    """
    Items that a user has.
    """

    def __init__(
            self,
            guild_id: int,
            user_id: int,
            items: list[Item] | None = None):
        self.guild_id = guild_id
        self.user_id = user_id
        self.items = items or []

    @classmethod
    def from_rows(cls, rows: list[dict]) -> Self:
        items = [
            Item(AnimalType[r["item"]], r["amount"])
            for r in rows
            if r["amount"] > 0
        ]
        return cls(
            guild_id=rows[0]["guild_id"],
            user_id=rows[0]["owner_id"],
            items=items,
        )

    @classmethod
    async def fetch(cls, conn: asyncpg.Connection, guild_id: int, user_id: int) -> Self:
        """
        Get a user's inventory from the database.
        """

        rows = await conn.fetch(
            """
            SELECT
                *
            FROM
                user_items
            WHERE
                guild_id = $1
                AND owner_id = $2
            """,
            guild_id, user_id,
        )
        if not rows:
            return cls(guild_id, user_id)
        return cls.from_rows(rows)


class PlotItems(ItemInventory):
    """
    Items that a plot has.
    """

    def __init__(
            self,
            plot_id: str | UUID,
            items: list[Item] | None = None):
        self.plot_id = str(plot_id)
        self.items = items or []

    @classmethod
    def from_rows(cls, rows: list[dict]) -> Self:
        items = [
            Item(AnimalType[r["item"]], r["amount"])
            for r in rows
        ]
        return cls(rows[0]["plot_id"], items)

    @classmethod
    async def fetch(cls, conn: asyncpg.Connection, plot_id: str | UUID) -> Self:
        """
        Get a plot's inventory from the database.
        """

        rows = await conn.fetch(
            """
            SELECT
                *
            FROM
                plot_items
            WHERE
                plot_id = $1
            """,
            plot_id,
        )
        if not rows:
            return cls(plot_id)
        return cls.from_rows(rows)


class Inventory:
    """
    A class for all of the items that a user has.
    """

    def __init__(
            self,
            *,
            guild_id: int,
            user_id: int,
            money: int = 0):
        self.guild_id = guild_id
        self.user_id = user_id
        self.money = money

    @classmethod
    def from_row(cls, data) -> Self:
        return cls(
            user_id=data["owner_id"],
            guild_id=data["guild_id"],
            money=data["money"],
        )

    @classmethod
    async def fetch(
            cls,
            conn: asyncpg.Connection,
            guild_id: int,
            user_id: int) -> Self:
        """
        Fetch an inventory instance from the databse.
        """

        row = await conn.fetch(
            """
            SELECT
                *
            FROM
                inventory
            WHERE
                guild_id = $1
                AND owner_id = $2
            """,
            guild_id, user_id,
        )
        if not row:
            return cls(
                guild_id=guild_id,
                user_id=user_id,
            )
        return cls.from_row(row[0])
