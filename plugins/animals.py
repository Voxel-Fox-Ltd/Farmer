import novus 
from novus.ext import client, database as db


class Animals(client.Plugin):

    @client.command(
        "animal get",
    )
    async def get_animal(self, ):
        """
        Get a new animal for one of your plots.
        """
