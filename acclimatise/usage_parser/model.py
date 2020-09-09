from typing import List, Optional

from dataclasses import dataclass

from acclimatise.model import Flag, Positional


@dataclass
class UsageElement:
    text: str
    """
    The name of this element, as defined in the usage section
    """

    optional: bool = False
    """
    Whether or not this element is required
    """

    variable: bool = False
    """
    True if this is a variable, ie you are supposed to replace this text with your own, False if this is a constant
    that you shouldn't change, e.g. the name of the application
    """

    # flag: bool = False
    """
    True if this is a flag (starts with dashes) and not a regular element
    """

    repeatable: bool = False
    """
    If this flag/argument can be used multiple times
    """


@dataclass
class UsageInstance:
    items: List[UsageElement]
    """
    The string of elements that make up a valid command invocation
    """

    description: Optional[str] = None
    """
    Description of this invocation
    """

    @property
    def positionals(self) -> List[Positional]:
        """
        Return all the positional arguments that could be derived from this instance
        """
        return [
            Positional(description="", position=i, name=el.text, optional=el.optional)
            for i, el in enumerate(self.items)
            if isinstance(el, UsageElement)
        ]

    @property
    def flags(self) -> List[Flag]:
        """
        Return all the flags that could be derived from this instance
        """
        return [el for el in self.items if isinstance(el, Flag)]
