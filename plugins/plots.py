from datetime import timedelta
import itertools
import random
from typing import Any, Callable, overload
import asyncio

import novus as n
from novus import types as t
from novus.utils import Localization as LC
from novus.ext import client, database as db

import utils


BUTTON_POSITIONS = set(list(itertools.permutations([0, 1, 2, 3, 4] * 2, 2)))


class Plots(client.Plugin):

    @client.loop(60)
    async def animal_item_production(self):
        """
        Loop through every animal, making the animal produce an item inside its
        relevant plot.
        """

        random_key = random.random()

        # And do our stuff
        async with db.Database.acquire() as conn:

            # Get all animals that can produce
            animal_rows = await conn.fetch(
                """
                SELECT
                    *
                FROM
                    animals
                WHERE
                    production_rate >= $1
                """,
                random_key,
            )
            animals = [utils.Animal.from_row(i) for i in animal_rows]

            # Get each plot that can support more items
            all_plot_ids = list(set([i.plot_id for i in animals]))
            plot_rows = await conn.fetch(
                """
                SELECT
                    plot_id,
                    SUM(amount)
                FROM
                    plot_items
                WHERE
                    plot_id = ANY($1::TEXT[])
                GROUP BY
                    plot_id
                HAVING
                    SUM(amount) >= 100
                """,
                all_plot_ids,
            )

            # Produce an item
            invalid_plot_ids = [r["plot_id"] for r in plot_rows]
            producing_animal_ids = [
                (i.plot_id, i.type.name)
                for i in animals
                if i.plot_id not in invalid_plot_ids
            ]
            await conn.executemany(
                """
                INSERT INTO
                    plot_items
                    (
                        plot_id,
                        item,
                        amount
                    )
                VALUES
                    (
                        $1,
                        $2,
                        1
                    )
                ON CONFLICT
                    (plot_id, item)
                DO UPDATE
                SET
                    amount = plot_items.amount + excluded.amount
                """,
                producing_animal_ids,
            )
        if producing_animal_ids:
            self.log.info(
                "Animals produced! %s animals produced an item this loop (%s)",
                len(producing_animal_ids), random_key,
            )
        else:
            self.log.info(
                "No animals produced anything this loop (%s)",
                random_key,
            )

    @staticmethod
    def get_plot_type(
            guild_id: int,
            user_id: int,
            x: int,
            y: int) -> utils.PlotType:
        """
        Generate a plot type from a user ID. This is random, seeded with the
        user ID, and generated from the X and Y coordinate's hash.
        """

        r = random.Random(hash((guild_id, user_id, x, y,)))
        return r.choice(list(utils.PlotType))

    @overload
    @classmethod
    def get_user_plots(
            cls,
            guild_id: int,
            user_id: int,
            owned_plots: None = ...
            ) -> dict[tuple[int, int], utils.PlotType]:
        ...

    @overload
    @classmethod
    def get_user_plots(
            cls,
            guild_id: int,
            user_id: int,
            owned_plots: list[utils.Plot] = ...
            ) -> dict[tuple[int, int], utils.PlotType | utils.Plot]:
        ...

    @classmethod
    def get_user_plots(
            cls,
            guild_id: int,
            user_id: int,
            owned_plots: list[utils.Plot] | None = None
            ) -> dict[tuple[int, int], Any]:
        """
        Get all of the plots available for a given user.
        """

        user_plots: dict[tuple[int, int], utils.PlotType | utils.Plot]
        user_plots = {
            (x, y): cls.get_plot_type(guild_id, user_id, x, y)
            for x, y in BUTTON_POSITIONS
        }
        if owned_plots:
            for p in owned_plots:
                user_plots[p.position] = p
        return user_plots

    @classmethod
    def get_plot_buttons(
            cls,
            guild_id: int,
            user_id: int,
            plots: list[utils.Plot],
            *,
            owned_plots_enabled: bool,
            open_plots_enabled: bool,
            content: Callable[[int, int, int, utils.PlotType | utils.Plot], str] = lambda user_id, x, y, plot: "\u200b",
            custom_id: Callable[[int, int, int, utils.PlotType | utils.Plot], str] = lambda user_id, x, y, plot: "",
            ) -> list[n.ActionRow]:
        """
        Get the buttons for the user's plots.
        """

        # See what plots they own
        owned_plots = {i: False for i in BUTTON_POSITIONS}
        plot_dict = {i.position: i for i in plots}
        for p in plots:
            owned_plots[p.position] = True

        # Show buttons with plots they can purchase
        plot_types = cls.get_user_plots(guild_id, user_id)
        components = [
            n.ActionRow([
                n.Button(
                    label=content(
                        user_id,
                        x,
                        y,
                        plot_dict.get((x, y)) or plot_types[(x, y)]
                    ),
                    custom_id=custom_id(
                        user_id,
                        x,
                        y,
                        plot_dict.get((x, y)) or plot_types[(x, y)]
                    ),
                    disabled=(
                        (owned_plots[(x, y)] and (not owned_plots_enabled))
                        or ((not owned_plots[(x, y)]) and (not open_plots_enabled))
                    ),
                    style=plot_types[(x, y)].value.style,
                )
                for y in range(5)
            ])
            for x in range(5)
        ]
        return components

    @staticmethod
    def get_plot_price(current_plot_count: int) -> int:
        """
        Get the price that a new plot of land will cost a given user.
        """

        return (30_000 * current_plot_count) + ((3 ** (current_plot_count - 1)) * 1_000)

    plot = client.CommandDescription(
        # "plot" command command name
        name_localizations=LC._("plot"),
    )

    @client.command(
        name="plot get",
        # "plot get" subcommand command name
        name_localizations=LC._("get"),
        # "plot get" subcommand description
        description_localizations=LC._("Create a new plot of land to rear animals on.")
    )
    async def create_plot(self, ctx: t.CommandI):
        """
        Create a new plot of land to rear animals on.
        """

        # Check they have no other plots of land
        assert ctx.guild
        async with db.Database.acquire() as conn:
            plots = await utils.Plot.fetch_for_user(
                conn,
                ctx.guild.id,
                ctx.user.id,
            )

            # They have plots already - lets see if they have the money to buy
            # a new plot as is
            if plots:
                inventory = await utils.Inventory.fetch(
                    conn,
                    ctx.guild.id,
                    ctx.user.id,
                )
                required_gold = self.get_plot_price(len(plots))
                if required_gold > inventory.money:
                    return await ctx.send(
                        ctx._(
                            "You need **{required_gold:,}** gold to get a "
                            "new plot of land (you currently have "
                            "**{current_gold:,}**) :<"
                        ).format(
                            required_gold=required_gold,
                            current_gold=inventory.money,
                        ),
                        ephemeral=True,
                    )

        # Show available plots
        components = self.get_plot_buttons(
            ctx.guild.id,
            ctx.user.id,
            plots,
            owned_plots_enabled=False,
            open_plots_enabled=True,
            custom_id=lambda user_id, x, y, plot: f"PLOT_PURCHASE {user_id} {x} {y}",
        )
        await ctx.send(components=components)

    @client.event.filtered_component(r"PLOT_PURCHASE \d+ \d \d")
    async def create_plot_button(self, ctx: t.ComponentI):
        """
        The plot purchase button has been pressed.
        """

        # Split the custom ID
        _, required_id, x, y = ctx.data.custom_id.split(" ")

        # Check that the user ID matches up with the component ID
        if int(required_id) != ctx.user.id:
            return await ctx.send(
                ctx._(
                    "Only **{user_mention}** can use these buttons! Please "
                    "run {command_mention} to get buttons you can use."
                ).format(
                    user_mention=f"<@{required_id}>",
                    command_mention=self.create_plot.mention,
                ),
                ephemeral=True,
            )

        # Check they have no other plots of land
        assert ctx.guild
        async with db.Database.acquire() as conn:
            plots = await utils.Plot.fetch_for_user(
                conn,
                ctx.user.id,
                ctx.guild.id,
            )

            # They have plots already - lets see if they have the money to buy
            # a new plot as is
            if plots:
                inventory = await utils.Inventory.fetch(
                    conn,
                    ctx.guild.id,
                    ctx.user.id,
                )
                required_gold = self.get_plot_price(len(plots))
                if required_gold > inventory.money:
                    return await ctx.send(
                        ctx._(
                            "You need **{required_gold:,}** gold to get a "
                            "new plot of land (you currently have "
                            "**{current_gold:,}**) :<"
                        ).format(
                            required_gold=required_gold,
                            current_gold=inventory.money,
                        ),
                        ephemeral=True,
                    )
                assert inventory
                assert required_gold

                # Take the money from their inventory
                await conn.execute(
                    """
                    UPDATE
                        inventory
                    SET
                        money = money - $3
                    WHERE
                        user_id = $1
                        AND guild_id = $2
                    """,
                    inventory.user_id, inventory.guild_id, required_gold,
                )

            # Commit to database
            position = (int(x), int(y),)
            plot_type = self.get_user_plots(ctx.guild.id, ctx.user.id)[position]
            new_plot = await utils.Plot(
                id=None,
                owner_id=ctx.user.id,
                guild_id=ctx.guild.id,
                position=position,
                type=plot_type,
            ).save(conn)

            # Add a single animal to that plot of land
            possible_animals = [
                i for i in utils.AnimalType
                if i.value.plot_type == new_plot.type
            ]
            new_animal_type = random.choice(possible_animals)
            new_animal = await utils.Animal(
                id=None,
                type=new_animal_type,
                plot_id=new_plot.id,
            ).save(conn)

        # And done :)
        await ctx.update(
            content=(
                ctx._(
                    "Yay, **{user}**! You have a new plot of land! It even "
                    "came with a **{animal}**! :D"
                ).format(
                    user=ctx.user.mention,
                    animal=new_animal,
                )
            ),
            components=None,
        )

    @client.command(
        name="plot show",
        # "plot show" subcommand name
        name_localizations=LC._("show"),
        # "plot show" subcommand description
        description_localizations=LC._("Show you buttons for all of your plots of land."),
    )
    async def show_plot(self, ctx: t.CommandI):
        """
        Show you buttons for all of your plots of land.
        """

        # Get the plots that the user owns
        assert ctx.guild
        async with db.Database.acquire() as conn:
            plots = await utils.Plot.fetch_for_user(
                conn,
                ctx.guild.id,
                ctx.user.id,
            )
        components = self.get_plot_buttons(
            ctx.guild.id,
            ctx.user.id,
            plots,
            owned_plots_enabled=True,
            open_plots_enabled=False,
            custom_id=lambda user_id, x, y, plot: f"PLOT_SHOW {user_id} {x} {y}",
        )
        if ctx.custom_id:
            await ctx.update(content=None, embeds=None, components=components)
        else:
            await ctx.send(components=components)

    @client.event.filtered_component(r"PLOT_SHOW_ALL \d+")
    async def plot_show_all_button_pressed(self, ctx: t.ComponentI):
        """
        Pinged when a user pressed the "show all plots" button.
        """

        _, user_id = ctx.data.custom_id.split(" ")
        user_id = int(user_id)
        if user_id != ctx.user.id:
            return await ctx.send(
                ctx._(
                    "Only **{user_mention}** can use these buttons! Please "
                    "run {command_mention} to get buttons you can use."
                ).format(
                    user_mention=f"<@{user_id}>",
                    command_mention=self.show_plot.mention,
                ),
                ephemeral=True,
            )
        return await self.show_plot(ctx)

    @client.event.filtered_component(r"PLOT_SHOW \d+ \d \d")
    async def plot_show_button_pressed(self, ctx: t.ComponentI):
        """
        Pinged when a plot show button is pressed.
        """

        # Split the custom ID
        _, user_id, x, y = ctx.data.custom_id.split(" ")
        user_id, x, y = int(user_id), int(x), int(y)

        if user_id != ctx.user.id:
            return await ctx.send(
                ctx._(
                    "Only **{user_mention}** can use these buttons! Please "
                    "run {command_mention} to get buttons you can use."
                ).format(
                    user_mention=f"<@{user_id}>",
                    command_mention=self.show_plot.mention,
                ),
                ephemeral=True,
            )

        # Get the plot
        assert ctx.guild
        async with db.Database.acquire() as conn:
            plot = await utils.Plot.fetch_for_user(
                conn,
                ctx.guild.id,
                user_id,
                (x, y,)
            )
            if plot is None:
                # We shouldn't get here
                return await ctx.send("You don't own that plot :(")

            # Get the animals and items for the plot
            plot = await plot.fetch_animals(conn)
            plot_inventory = await utils.PlotItems.fetch(conn, plot.id)

        # Format items on the plot
        text: str = ""
        for i in sorted(plot_inventory.items, key=lambda i: i.amount):
            text += f"\N{BULLET} {i!s}\n"
        text = text or ctx._("Nothing yet :(")

        # See if we should add a "move to inventory" button
        ar = n.ActionRow([
            n.Button(
                ctx._("Show all plots"),
                custom_id=f"PLOT_SHOW_ALL {user_id}",
                style=n.ButtonStyle.primary,
            ),
            n.Button(
                ctx._("Move items to inventory"),
                custom_id=f"PLOT_MOVE_ITEMS {user_id} {x} {y}",
                disabled=not bool(plot_inventory.items)
            )
        ])

        # And send
        return await ctx.update(
            content=str(plot),
            embeds=[
                n.Embed().add_field(
                    ctx._("Items"),
                    text.strip(),
                    inline=False,
                ),
            ],
            components=[ar],
        )

    @client.event.filtered_component(r"PLOT_MOVE_ITEMS \d+ \d \d")
    async def plot_move_items_button_pressed(self, ctx: t.ComponentI):
        """
        Pinged when a plot move items button is pressed.
        """

        # Split the custom ID
        _, user_id, x, y = ctx.data.custom_id.split(" ")
        user_id, x, y = int(user_id), int(x), int(y)

        if user_id != ctx.user.id:
            return await ctx.send(
                ctx._(
                    "Only **{user_mention}** can use these buttons! Please "
                    "run {command_mention} to get buttons you can use."
                ).format(
                    user_mention=f"<@{user_id}>",
                    command_mention=self.show_plot.mention,
                ),
                ephemeral=True,
            )

        # Get the plot
        assert ctx.guild
        async with db.Database.acquire() as conn:
            plot = await utils.Plot.fetch_for_user(
                conn,
                ctx.guild.id,
                user_id,
                (x, y,)
            )
            if plot is None:
                # We shouldn't get here
                return await ctx.send("You don't own that plot :(")
            plot = await plot.fetch_animals(conn)
            assert plot

            # Move
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO
                        user_items
                        (
                            owner_id,
                            guild_id,
                            item,
                            amount
                        )
                    SELECT
                        $1,
                        $2,
                        item,
                        amount
                    FROM
                        plot_items
                    WHERE
                        plot_id = $3
                    ON CONFLICT (owner_id, guild_id, item)
                    DO UPDATE
                    SET
                        amount = user_items.amount + excluded.amount
                    """,
                    plot.owner_id,
                    plot.guild_id,
                    plot.id,
                )
                await conn.execute(
                    "DELETE FROM plot_items WHERE plot_id = $1",
                    plot.id,
                )

        # And send
        await ctx.update(
            content=str(plot),
            embeds=[
                n.Embed().add_field(
                    ctx._("Items"),
                    ctx._("Nothing yet :("),
                    inline=False,
                ),
            ],
            components=[
                n.ActionRow([
                    n.Button(
                        ctx._("Show all plots"),
                        custom_id=f"PLOT_SHOW_ALL {user_id}",
                        style=n.ButtonStyle.primary,
                    ),
                    n.Button(
                        ctx._("Move items to inventory"),
                        custom_id=f"PLOT_MOVE_ITEMS {user_id} {x} {y}",
                        disabled=True,
                    )
                ])
            ],
        )
