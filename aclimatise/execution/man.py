import os
import subprocess
from typing import Collection, List, Optional

from aclimatise.execution import Executor
from aclimatise.integration import parse_help
from aclimatise.model import Command


class ManPageExecutor(Executor):
    def __init__(
        self,
        man_paths: List[str] = [],
        subcommand_sep: Collection[str] = ("-", "_"),
        man_flags: Collection[str] = ["--no-subpages"],
        **kwargs
    ):
        """
        :param man_paths: Additional paths within which to look for man pages
        :param subcommand_sep: A list of separators to use to generate man paths from subcommands. For example
            ``git branch`` has an associated man page at ``git-branch``, using the hyphen as a separator.
        :param man_flags: Additional flags to pass to the ``man`` command
        """
        super().__init__(**kwargs)
        self.man_paths = man_paths
        self.subcommand_sep = subcommand_sep
        self.man_flags = man_flags

    def execute(self, command: List[str], separator: str = "-") -> str:
        """
        Returns the man page text for the provided command, using the provided subcommand separator, or an empty string
        if this man page doesn't exist
        """
        env = {**os.environ.copy(), "MANPAGER": "cat"}  # Don't use a pager
        if len(self.man_paths) > 0:
            env.update({"MANPATH": ":".join(self.man_paths)})

        sub_man = separator.join(command)
        result = subprocess.run(
            ["man", *self.man_flags, sub_man], env=env, capture_output=True
        )
        if result.returncode == 0:
            return result.stdout.decode()

        return ""

    def explore(
        self, command: List[str], max_depth: int = 2, parent: Optional[Command] = None
    ) -> Command:
        if len(command) == 1:
            return parse_help(
                command, self.execute(command), max_length=self.max_length
            )
        else:
            commands = []
            for sep in self.subcommand_sep:
                man_text = self.execute(command, sep)
                commands.append(
                    parse_help(command, man_text, max_length=self.max_length)
                )
            return Command.best(commands)
