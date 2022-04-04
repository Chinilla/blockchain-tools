import click
import requests
import sqlite3
import urllib3

from chia.pools.pool_puzzles import (
    SINGLETON_MOD_HASH,
    create_p2_singleton_puzzle
)

from chia.util.bech32m import (
    decode_puzzle_hash
)

from chia.util.byte_types import (
    hexstr_to_bytes
)

from chia.util.ints import (
    uint64
)

from chia.types.blockchain_format.program import (
    Program,
    SerializedProgram
)

from chia.types.blockchain_format.sized_bytes import (
    bytes32
)

from blockchain_tools.blockchain_tools_assert import (
    blockchain_tools_assert_env_set
)

from blockchain_tools.blockchain_tools_cst import (
    BLOCKCHAIN_TOOLS_CST_AGGREGATED_SIGNATURE
)

from blockchain_tools.blockchain_tools_env import (
    BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH,
    BLOCKCHAIN_TOOLS_ENV_WT_DB_PATH
)

from blockchain_tools.blockchain_tools_print import (
    blockchain_tools_print_raw,
    blockchain_tools_print_coin_lite_many,
    blockchain_tools_print_value
)


def blockchain_tools_cmd_nft_recover(
        ctx: click.Context,
        delay: int,
        launcher_hash: str,
        pool_contract_address: str,
        node_host: str,
        node_port: int,
        cert_path: str,
        cert_key_path: str,
        cert_ca_path: str
) -> None:
    pre: int = 1
    blockchain_tools_assert_env_set(BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH)
    blockchain_tools_assert_env_set(BLOCKCHAIN_TOOLS_ENV_WT_DB_PATH)

    delay_u64: uint64 = uint64(delay)
    launcher_hash_b32: bytes32 = bytes32(hexstr_to_bytes(launcher_hash))
    contract_hash_b32: bytes32 = decode_puzzle_hash(pool_contract_address)
    contract_hash_hex: str = contract_hash_b32.hex()

    program_puzzle_hex: str = None

    db_wallet_cursor: sqlite3.Cursor = ctx.obj['wt_db'].cursor()
    db_wallet_cursor.execute(
        "SELECT * "
        "FROM  derivation_paths")

    while True:
        derivation_paths: list = db_wallet_cursor.fetchmany(10)

        if len(derivation_paths) == 0:
            break

        for row in derivation_paths:
            puzzle_hash: str = row[2]
            puzzle_hash_b32: bytes32 = bytes32(hexstr_to_bytes(puzzle_hash))

            puzzle = create_p2_singleton_puzzle(
                SINGLETON_MOD_HASH,
                launcher_hash_b32,
                delay_u64,
                puzzle_hash_b32
            )

            if contract_hash_b32 == puzzle.get_tree_hash():
                program_puzzle_hex = bytes(SerializedProgram.from_program(puzzle)).hex()
                break

    if program_puzzle_hex is None:
        blockchain_tools_print_raw('A valid puzzle program could not be created for the given arguments and the selected wallet.',
                         pre=pre)
        return

    db_bc_cursor: sqlite3.Cursor = ctx.obj['bc_db'].cursor()
    db_bc_cursor.execute(
        f"SELECT * "
        f"FROM coin_record "
        f"WHERE spent == 0 "
        f"AND timestamp <= (strftime('%s', 'now') - {delay}) "
        f"AND puzzle_hash LIKE '{contract_hash_hex}' "
        f"ORDER BY timestamp DESC")

    coin_records: list = []

    for coin in db_bc_cursor.fetchall():
        coin_amount: int = int.from_bytes(coin[7], byteorder='big', signed=False)

        if coin_amount > 0:
            coin_records.append(coin)

    if len(coin_records) == 0:
        blockchain_tools_print_raw(f'No coins are eligible for recovery yet. '
                         f'Notice that 604800 seconds must pass since coin creation to recover it.', pre=pre)
        return
    else:
        blockchain_tools_print_raw('Coins eligible for recovery:', pre=pre)
        blockchain_tools_print_coin_lite_many(coin_records, pre=pre + 1)

    coin_solutions: list[dict] = []

    for coin in coin_records:
        coin_parent: str = coin[6]
        coin_amount: int = int.from_bytes(coin[7], byteorder='big', signed=False)

        coin_solution_hex: str = bytes(SerializedProgram.from_program(
            Program.to([uint64(coin_amount), 0])
        )).hex()

        coin_solutions.append({
            'coin': {
                'amount': coin_amount,
                'parent_coin_info': coin_parent,
                'puzzle_hash': contract_hash_hex
            },
            'puzzle_reveal': program_puzzle_hex,
            'solution': coin_solution_hex
        })

    balance_recovered: int = 0

    if not cert_ca_path:
        urllib3.disable_warnings()

    for coin_solutions_b in [coin_solutions[x:x + 50] for x in range(0, len(coin_solutions), 50)]:

        balance_batch: int = 0

        for coin_solution in coin_solutions_b:
            balance_batch += coin_solution['coin']['amount']

        exception: Exception = None
        guard_success: bool = False

        try:
            response = requests.post(
                url=f'https://{node_host}:{node_port}/push_tx',
                cert=(cert_path, cert_key_path),
                verify=cert_ca_path if cert_ca_path else False,
                json={
                    'spend_bundle': {
                        'aggregated_signature': BLOCKCHAIN_TOOLS_CST_AGGREGATED_SIGNATURE,
                        'coin_solutions': coin_solutions_b
                    }
                })

            response.raise_for_status()
            guard_success = True
        except Exception as e:
            exception = e

        if not guard_success:
            try:
                response = requests.post(
                    url=f'https://{node_host}:{node_port}/push_tx',
                    cert=(cert_path, cert_key_path),
                    verify=cert_ca_path if cert_ca_path else False,
                    json={
                        'spend_bundle': {
                            'aggregated_signature': BLOCKCHAIN_TOOLS_CST_AGGREGATED_SIGNATURE,
                            'coin_spends': coin_solutions_b
                        }
                    })

                response.raise_for_status()
                guard_success = True
            except Exception as e:
                exception = e

        if guard_success:
            blockchain_tools_print_raw(
                f'A new network transaction has been sent to recover a total of '
                f'{balance_batch / (10 ** 12):.12f} coins.',
                pre=pre)
            balance_recovered += balance_batch
        else:
            blockchain_tools_print_raw(
                'An error occurred while sending the recovery transaction.', pre=pre)

            if exception is not None:
                blockchain_tools_print_raw(exception, pre=pre)

    if balance_recovered == 0:
        blockchain_tools_print_raw(
            'Coins could not be recovered. '
            'Please check your input parameters, network connection and try again.', pre=pre)
        return

    blockchain_tools_print_raw('', pre=pre)
    blockchain_tools_print_raw(f'Sent transactions to recover a total of '
                     f'{balance_recovered / (10 ** 12):.12f} coins.', pre=pre)
    blockchain_tools_print_raw(f'Coins should be spendable in few network confirmations.', pre=pre)
