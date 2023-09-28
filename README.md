# Farmer

## Commands

* `/plot show`; `/animal get`
    * Show an array of buttons for the user
    * Each button is a plot of land
    * The ones they don't own will be disabled
    * They ones they own will be enabled
    * `/plot show`:
        * If clicked on, goto `show plot button`
    * `/animal get`:
        * If clicked on, goto `get animal button`

* Show plot button
    * A row of 5 fence emojis are shown
    * A 5x5 block of grass emojis is shown, interspaced with emojis for the animals that are present in the plot.
    * An embed showing the produced and unclaimed items
    * Two buttons on the embed will be shown
        * One button will do the same as `/plot show`
        * The other button will claim all of the items that are in the plot and move them to the user's inventory

* Get animal button
    * A list of animals will be shown to the user
    * A price for each animal available for that type of plot will be generated
    * Prices will be generated based on the sell price of each item's animal
    * The animals will be added to the plot if the user selects the animal and has the relevant amount of money
    * A maximum of 10 animals can be added to a plot

* `/plot get`
    * If the user has enough money available (or no other plots) they will be shown an array of 5x5 buttons for which they can purchase plots of land
    * When a plot of land is created, a single animal will be added to that piece of land

* `/inventory [user?]`
    * Show you the inventory for a given user.
    * Defaults to yourself, of course.

* Selling items
    * Users should be able to sell items on the "market"
    * The market will be individualised per server (as best as I'm able)
    * Every item has a base price of 50 gold.
    * Each item will have a multiplier on its price based on the amount of that animal that is present in the guild after
        - the number of total animals in the guild gets higher than 10
        - the percentage of that animal's presence is higher than 5%
        - the user trying to sell items has more than 5 animals

* Timer: 30 minutes
    * Every 30\*N minutes, an animal in a plot of land will produce an item (up to 10 items)
    * Up to 100 items can be in a plot's inventory
    * The animal's N value is determined randomly from 0.1 to 0.9 upon its adoption
