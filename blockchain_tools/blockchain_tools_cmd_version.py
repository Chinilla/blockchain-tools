import click

from blockchain_tools.blockchain_tools_print import (
    blockchain_tools_print_raw
)

from blockchain_tools.blockchain_tools_version import (
    BLOCKCHAIN_TOOLS_VERSION
)


def blockchain_tools_cmd_version(
        ctx: click.Context
) -> None:
    blockchain_tools_print_raw(BLOCKCHAIN_TOOLS_VERSION)
