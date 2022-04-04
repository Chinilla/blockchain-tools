import click
import sqlite3

from blockchain_tools.blockchain_tools_assert import (
    blockchain_tools_assert_env_set
)

from blockchain_tools.blockchain_tools_env import (
    BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH
)

from blockchain_tools.blockchain_tools_print import (
    blockchain_tools_print_none,
    blockchain_tools_print_block_many
)


def blockchain_tools_cmd_block(
        ctx: click.Context,
        by: str,
        value: str
) -> None:
    blockchain_tools_assert_env_set(BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH)

    db_bc_cursor: sqlite3.Cursor = ctx.obj['bc_db'].cursor()
    block_records: list = []

    if by == 'height':
        db_bc_cursor.execute(
            f"SELECT * "
            f"FROM full_blocks "
            f"WHERE height == {int(value)} "
            f"ORDER BY height DESC")
        block_records = db_bc_cursor.fetchall()

    if by == 'hash':
        db_bc_cursor.execute(
            f"SELECT * "
            f"FROM full_blocks "
            f"WHERE header_hash LIKE '{value}%' "
            f"ORDER BY height DESC")
        block_records = db_bc_cursor.fetchall()

    if block_records is None or len(block_records) == 0:
        blockchain_tools_print_none(pre=1)
        return

    blockchain_tools_print_block_many(block_records, pre=0)
