from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from .plot_type import PlotType

__all__ = (
    'AnimalBase',
    'AnimalType',
)


class AnimalBase:
    """
    A type of animal that a user can have.
    """

    __slots__ = ("name", "emoji", "plot_type", "product",)

    name: str
    emoji: str
    plot_type: PlotType
    product: tuple[str, str]

    def __init__(
            self,
            name: str,
            emoji: str,
            plot_type: PlotType,
            product: tuple[str, str] = ("egg", "eggs")):
        self.name = name
        self.emoji = emoji
        self.plot_type = plot_type
        self.product = product


class AnimalType(Enum):
    # TIGER = AnimalBase("tiger", "🐅", "savanna")
    # LEOPARD = AnimalBase("leopard", "🐆", "savanna")

    # BISON = AnimalBase("bison", "🦬", "safari")
    # HORSE = AnimalBase("horse", "🐎", "safari")
    # OX = AnimalBase("ox", "🐂", "safari")
    # ELEPHANT = AnimalBase("elephant", "🐘", "safari")
    # MAMMOTH = AnimalBase("mammoth", "🦣", "safari")
    # GIRAFFE = AnimalBase("giraffe", "🦒", "safari")
    # CAMEL = AnimalBase("camel", "🐪", "safari")
    # LLAMA = AnimalBase("llama", "🦙", "safari")

    COW = AnimalBase("cow", "🐄", PlotType.FARM, ("bottle of milk", "bottles of milk",))
    PIG = AnimalBase("pig", "🐖", PlotType.FARM, ("pepper", "peppers",))
    SHEEP = AnimalBase("sheep", "🐑", PlotType.FARM, ("pound of wool", "pounds of wool",))
    GOAT = AnimalBase("goat", "🐐", PlotType.FARM, ("bottle of milk", "bottles of milk",))
    TURKEY = AnimalBase("turkey", "🦃", PlotType.FARM, ("pumpkin", "pumpkins",))
    ROOSTER = AnimalBase("rooster", "🐓", PlotType.FARM, ("egg", "eggs",))
    # CAT = AnimalBase("cat", "🐈", PlotType.FARM)
    # DOG = AnimalBase("dog", "🐕", PlotType.FARM)

    RABBIT = AnimalBase("rabbit", "🐇", PlotType.GARDEN, ("foot", "feet",))
    SKUNK = AnimalBase("skunk", "🦨", PlotType.GARDEN, ("perfume bottle", "perfume bottles",))
    BADGER = AnimalBase("badger", "🦡", PlotType.GARDEN, ("badge", "badges",))
    MOUSE = AnimalBase("mouse", "🐁", PlotType.GARDEN, ("ratatouille", "ratatouille",))
    HEDGEHOG = AnimalBase("hedgehog", "🦔", PlotType.GARDEN, ("quill", "quills",))
    BEAVER = AnimalBase("beaver", "🦫", PlotType.GARDEN, ("hat", "hats",))
    CHIPMUNK = AnimalBase("chipmunk", "🐿️", PlotType.GARDEN, ("nut", "nuts",))
    SNAIL = AnimalBase("snail", "🐌", PlotType.GARDEN, ("shell", "shells",))

    # LIZARD = AnimalBase("lizard", "🦎", "terrarium")
    # SNAKE = AnimalBase("snake", "🐍", "terrarium")

    # SCORPION = AnimalBase("scorpion", "🦂", "tree")
    # SLOTH = AnimalBase("sloth", "🦥", "tree")

    OTTER = AnimalBase("otter", "🦦", PlotType.LAKE, ("clam", "clams",))
    TURTLE = AnimalBase("turtle", "🐢", PlotType.LAKE, ("scute", "scutes",))
    CROCODILE = AnimalBase("crocodile", "🐊", PlotType.LAKE, ("handbag", "handbags",))
    DUCK = AnimalBase("duck", "🦆", PlotType.LAKE, ("loaf of bread", "loaves of bread",))
    PENGUIN = AnimalBase("penguin", "🐧", PlotType.LAKE, ("chocolate biscuit", "chocolate biscuits",))
    SWAN = AnimalBase("swan", "🦢", PlotType.LAKE, ("feather", "feathers",))
    WHALE = AnimalBase("whale", "🐳", PlotType.LAKE, ("bestselling book", "bestselling books",))
    SEAL = AnimalBase("seal", "🦭", PlotType.LAKE, ("flipper", "flippers",))
    FISH = AnimalBase("fish", "🐟", PlotType.LAKE, ("portion of caviar", "portions of caviar",))
    BLOWFISH = AnimalBase("blowfish", "🐡", PlotType.LAKE, ("vial of poison", "vials of poison",))
    SHARK = AnimalBase("shark", "🦈", PlotType.LAKE, ("DVD", "DVDs",))
    OCTOPUS = AnimalBase("octopus", "🐙", PlotType.LAKE, ("anime", "animes",))
    CRAB = AnimalBase("crab", "🦀", PlotType.LAKE, ("rave", "raves",))
    # TROPICAL_FISH = AnimalBase("tropical fish", "🐠", PlotType.LAKE, ("scale", "scales",))
    # HIPPO = AnimalBase("hippo", "🦛", PlotType.LAKE)
    # DOLPHIN = AnimalBase("dolphin", "🐬", PlotType.LAKE)
    # SHRIMP = AnimalBase("shrimp", "🦐", PlotType.LAKE)
    # SQUID = AnimalBase("squid", "🦑", PlotType.LAKE)
    # LOBSTER = AnimalBase("lobster", "🦞", PlotType.LAKE)

    DOVE = AnimalBase("dove", "🕊️", PlotType.SKY, ("bar of soap", "bars of soap",))
    EAGLE = AnimalBase("eagle", "🦅", PlotType.SKY, ("law degree", "law degrees",))
    OWL = AnimalBase("owl", "🦉", PlotType.SKY, ("pellet", "pellets",))
    FLAMINGO = AnimalBase("flamingo", "🦩", PlotType.SKY, ("shrimp", "shrimp",))
    PEACOCK = AnimalBase("peacock", "🦚", PlotType.SKY, ("pea", "peas",))
    PARROT = AnimalBase("parrot", "🦜", PlotType.SKY, ("cracker", "crackers",))
    BAT = AnimalBase("bat", "🦇", PlotType.SKY, ("riddle", "riddles",))
    # DODO = AnimalBase("dodo", "🦤", PlotType.SKY)

    if TYPE_CHECKING:
        value: AnimalBase
