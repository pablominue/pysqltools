"""Logger"""

import logging
from typing import Any, Callable

import pandas as pd
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.progress import Progress
from rich.table import Table

COLORS = [
    "purple",
    "magenta",
    "turquoise2",
    "blue_violet",
    "orange3",
    "dark_red",
    "yellow4",
    "green",
    "deep_pink3",
    "dark_goldenrod",
    "aquamarine1",
    "chartreuse1",
]


class PabLog:
    """Logger"""

    def __init__(
        self, log_name: str = "Logger", __format: str = "- %(message)s"
    ) -> None:
        """Logger Constructor"""
        self.avaliable_colors = []
        self.rich_handler = RichHandler(rich_tracebacks=True)

        self.avaliable_colors = COLORS

        __handlers = [self.rich_handler]

        logging.basicConfig(format=__format, handlers=__handlers, level=logging.DEBUG)

        self.log = logging.getLogger(log_name)
        self.log.setLevel(logging.INFO)
        self.console = Console()

    def add_table(self, df: pd.DataFrame, title: str = "", max_rows: int = 10) -> None:
        """Add a table in terminal"""
        table = Table(title=title)
        color = 0
        for col in df.columns:
            if color >= len(self.avaliable_colors) - 1:
                color = 0
            else:
                color += 1

            table.add_column(str(col), style=self.avaliable_colors[color])

        for _, row in df.head(max_rows).iterrows():
            table.add_row(*[str(r) for r in row])

        self.console.print(table)

    def add_md(self, markdown: str):
        """Add markdown in terminal"""
        md = Markdown(markdown)
        self.console.print(md)

    def add_title(self, title: str):
        """Add markdown title in terminal"""
        md_ = f" # **{title}** "
        md = Markdown(md_)
        self.console.print(md)


def progress_function(
    task_name: str = "Task in progress...", color: str = "green", total: int = 100
):
    """
    Decorator to use a rich progress bar
    """

    def decorator(fun: Callable[..., Any]):
        """Decorator"""

        def inner(*args, **kwargs):
            """Wrapped"""
            with Progress() as progress:
                task = progress.add_task(f"[{color}] {task_name}...", total=total)
                prog = {"progress": progress, "task": task}
                result = fun(*args, **kwargs, **prog)
                progress.update(task, advance=total)
            return result

        return inner

    return decorator
