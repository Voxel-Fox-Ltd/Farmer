import novus as n
from novus import types as t
from novus.utils import Localization as LC
from novus.ext import client, database as db

import utils


class User(client.Plugin):

    @client.command(
        name="inventory",
        # "inventory [user?]" command name
        name_localizations=LC._("inventory"),
        # "inventory [user?]" command description
        description_localizations=LC._("Show you the inventory for a user."),
        options=[
            n.ApplicationCommandOption(
                name="user",
                description="The user whose inventory you want to see.",
                # "inventory [user]" command option name
                name_localizations=LC._("user"),
                # "inventory [user]" command option description
                description_localizations=LC._("The user whose inventory you want to see."),
                type=n.ApplicationOptionType.user,
                required=False,
            ),
        ],
        dm_permission=False,
    )
    async def inventory(
            self,
            ctx: t.CommandI,
            user: n.GuildMember | None = None) -> None:
        """
        Show you the inventory for a user.
        """

        # Get the relevant inventory
        assert ctx.guild
        user = user or ctx.user  # pyright: ignore
        assert user
        async with db.Database.acquire() as conn:
            money = await utils.Inventory.fetch(conn, ctx.guild.id, user.id)
            inventory = await utils.UserItems.fetch(conn, ctx.guild.id, user.id)

        # Format items
        description_lines = []
        for r in inventory.items:
            description_lines.append(f"* {r!s}")
        embed = n.Embed(
            title="Inventory",
            description=(
                f"* **{money.money:,} gold**\n"
                + "\n".join(description_lines)
            ),
            color=0xf17824,
        ).set_author_from_user(user)
        await ctx.send(embeds=[embed])
