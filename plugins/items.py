from __future__ import annotations

from typing import TYPE_CHECKING
from difflib import SequenceMatcher

import novus as n
from novus import types as t
from novus.utils import Localization as LC
from novus.ext import client, database as db

from utils import AnimalType, UserItems

if TYPE_CHECKING:
    import asyncpg


def get_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


class Items(client.Plugin):

    async def get_sell_price(
            self,
            conn: asyncpg.Connection,
            guild: n.types.Snowflake,
            animal: AnimalType) -> int:
        """
        Get the sell price of an item for a particular guild.
        """

        return 50

    @client.command(
        name_localizations=LC._("sell"),
        description_localizations=LC._("Sell an item on the market."),
        options=[
            n.ApplicationCommandOption(
                name="item",
                type=n.ApplicationOptionType.string,
                description="The item that you want to sell.",
                autocomplete=True,
            ),
            n.ApplicationCommandOption(
                name="amount",
                type=n.ApplicationOptionType.integer,
                description="The amount of the item that you want to sell.",
                min_value=1,
                required=False,
            ),
        ],
        dm_permission=False,
    )
    async def sell(self, ctx: t.CommandI, item: str, amount: int = -1):
        """
        Sell an item on the market.
        """

        # Check that the item they want to sell is valid.
        if item not in [i.name for i in AnimalType]:
            return await ctx.send("That item is not valid :/")
        animal = AnimalType[item]

        # Check that they have enough of that item
        assert ctx.guild
        async with db.Database.acquire() as conn:
            current_amount = await conn.fetchval(
                """
                SELECT
                    amount
                FROM
                    user_items
                WHERE
                    owner_id = $1
                    AND guild_id = $2
                    AND item = $3
                """,
                ctx.user.id, ctx.guild.id, animal.name,
            )
            sell_price = await self.get_sell_price(conn, ctx.guild, animal.name)
        amount_adjusted = False
        if current_amount is None or current_amount <= 0:
            return await ctx.send(
                (
                    ctx._("You don't have any **{item}** items!")
                    .format(item=animal.value.name)
                )
            )
        elif amount == -1:
            amount = current_amount
        elif current_amount < amount:
            amount_adjusted = True
            amount = current_amount

        # Spawn the "are you sure" buttons
        content = ""
        if amount_adjusted:
            content = (
                ctx._("You only have {amount} of that item, so your request has been lowered.")
                .format(amount=amount)
            )
        content += "\n"
        content += (
            ctx._("Sell **{amount:,}x {item}** @ **{sell_price:,} gold each**?")
            .format(
                amount=amount,
                item=animal.value.product[0 if amount == 1 else 1],
                sell_price=sell_price,
            )
        )
        await ctx.send(
            content,
            components=[
                n.ActionRow([
                    n.Button(
                        ctx._("Sell"),
                        custom_id=f"SELL {animal.name} {amount} {sell_price}",
                        style=n.ButtonStyle.green,
                    ),
                    n.Button(
                        ctx._("Cancel"),
                        custom_id=f"SELL CANCEL",
                        style=n.ButtonStyle.red,
                    ),
                ]),
            ],
            ephemeral=True,
        )

    @sell.autocomplete
    async def sell_autocomplete(
            self,
            ctx: t.CommandI,
            options: dict[str, n.InteractionOption]) -> list[n.ApplicationCommandChoice]:
        assert ctx.guild
        async with db.Database.acquire() as conn:
            user_items = await UserItems.fetch(conn, ctx.guild.id, ctx.user.id)
        current_string: str = options["item"].value  # pyright: ignore
        return sorted(
            [
                n.ApplicationCommandChoice(f"{i.amount}x {i.animal.value.product[-1].title()}", i.animal.name)
                for i in user_items.items
            ],
            key=lambda acc: get_similarity(str(acc.value).lower(), current_string.lower()),
            reverse=True,
        )[:25]

    @client.event.filtered_component(r"^SELL .*$")
    async def sell_button_pressed(self, ctx: t.ComponentI):
        """
        A sell button has been pressed.
        """

        _, actions = ctx.data.custom_id.split(" ", 1)

        # See if they want to cancel
        if actions == "CANCEL":
            await ctx.update(content=ctx._("Cancelled sale."), components=None)

        # Work out what they want to sell
        item, amount_str, sell_price_str = actions.split(" ")
        amount, sell_price = int(amount_str), int(sell_price_str)
        animal = AnimalType[item]

        # Sell their items
        assert ctx.guild
        async with db.Database.acquire() as conn:
            async with conn.transaction():
                new_amount = await conn.fetchval(
                    """
                    UPDATE
                        user_items
                    SET
                        amount = amount - $4
                    WHERE
                        owner_id = $1
                        AND guild_id = $2
                        AND item = $3
                    RETURNING
                        amount
                    """,
                    ctx.user.id, ctx.guild.id, animal.name, amount,
                )
                if (new_amount or 0) < 0:
                    return await ctx.update(
                        content=ctx._("You don't have enough of that item to make this sale!"),
                        components=None,
                    )
                new_money = await conn.fetchval(
                    """
                    INSERT INTO
                        inventory
                        (
                            owner_id,
                            guild_id,
                            money
                        )
                    VALUES
                        ($1, $2, $3)
                    ON CONFLICT
                        (owner_id, guild_id)
                    DO UPDATE SET
                        money = inventory.money + excluded.money
                    RETURNING
                        money
                    """,
                    ctx.user.id, ctx.guild.id, sell_price * amount,
                )
        await ctx.update(
            content=(
                ctx._("You have sold **{amount:,}x {item}**! You now have **{money:,} gold** :3")
                .format(
                    amount=amount,
                    item=animal.value.product[0 if amount == 1 else 1],
                    money=new_money,
                )
            ),
            components=None,
        )
