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
    blockchain_tools_print_coin_many
)


def blockchain_tools_cmd_coin(
        ctx: click.Context,
        by: str,
        value: str
):
    blockchain_tools_assert_env_set(BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH)

    db_bc_cursor: sqlite3.Cursor = ctx.obj['bc_db'].cursor()
    coin_records: list = []

    if by == 'hash':
        db_bc_cursor.execute(
            f"SELECT * "
            f"FROM coin_record "
            f"WHERE coin_name LIKE '{value}%' "
            f"ORDER BY timestamp DESC")
        coin_records = db_bc_cursor.fetchall()

    if by == 'hash_parent':
        db_bc_cursor.execute(
            f"SELECT * "
            f"FROM coin_record "
            f"WHERE coin_parent LIKE '{value}%' "
            f"ORDER BY timestamp DESC")
        coin_records = db_bc_cursor.fetchall()

    if by == 'hash_puzzle':
        db_bc_cursor.execute(
            f"SELECT * "
            f"FROM coin_record "
            f"WHERE puzzle_hash LIKE '{value}%' "
            f"ORDER BY timestamp DESC")
        coin_records = db_bc_cursor.fetchall()

    if coin_records is None or len(coin_records) == 0:
        blockchain_tools_print_none(pre=1)
        return

    blockchain_tools_print_coin_many(coin_records, pre=0)
