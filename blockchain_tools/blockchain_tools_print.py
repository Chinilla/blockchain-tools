import typing

# noinspection PyPackageRequirements
import chia.types.full_block


def blockchain_tools_print_raw(
        value: typing.Any,
        pre: int = 0,
        fill: int = 25
) -> None:
    if pre == 0:
        print(f'{value:{fill}s}')
    else:
        print(f'{" " * pre * 4}{value:{fill}s}')


def blockchain_tools_print_value(
        token: str,
        value: typing.Any,
        pre: int = 0,
        fill: int = 25
) -> None:
    if pre == 0:
        print(f'{token + ":":{fill}s} {value}')
    else:
        print(f'{" " * pre * 4}{token + ":":{fill}s} {value}')


def blockchain_tools_print_require_env(
        env: str,
        pre: int = 0
) -> None:
    blockchain_tools_print_raw(f"Environment variable '{env}' is missing.", pre=pre)


def blockchain_tools_print_none(
        pre: int = 0,
) -> None:
    blockchain_tools_print_raw('none', pre=pre)


def blockchain_tools_print_separator(
        pre: int = 0
) -> None:
    blockchain_tools_print_raw("--------", pre=pre)


def blockchain_tools_print_many(
        ctx: list,
        blockchain_tools_print_cb: typing.Callable,
        pre: int = 0,
) -> None:
    items = ctx
    items_len = len(ctx)

    for item in items:
        blockchain_tools_print_cb(item, pre=pre + 1)

        if items_len > 1:
            blockchain_tools_print_separator(pre=pre + 1)
            items_len -= 1


def blockchain_tools_print_block(
        ctx: list,
        pre: int = 0
) -> None:
    obj: chia.types.full_block.FullBlock = chia.types.full_block.FullBlock.from_bytes(ctx[4])

    blockchain_tools_print_value('height', f'{obj.height}', pre=pre)
    blockchain_tools_print_value('weight', f'{obj.weight}', pre=pre)
    blockchain_tools_print_value('header_hash', f'{obj.header_hash}', pre=pre)
    blockchain_tools_print_value('previous_header_hash', f'{obj.prev_header_hash}', pre=pre)
    blockchain_tools_print_value('total_iterations', f'{obj.total_iters}', pre=pre)

    blockchain_tools_print_raw('transactions_info:', pre=pre)
    if obj.transactions_info is None or \
            obj.transactions_info.reward_claims_incorporated is None or \
            len(obj.transactions_info.reward_claims_incorporated) == 0:
        blockchain_tools_print_raw('none', pre=pre + 1)
    else:
        blockchain_tools_print_value('fees', f'{obj.transactions_info.fees}', pre=pre + 1)
        blockchain_tools_print_value('cost', f'{obj.transactions_info.cost}', pre=pre + 1)

        txs = obj.transactions_info.reward_claims_incorporated
        txs_len = len(txs)

        blockchain_tools_print_raw('transactions:', pre=pre + 1)
        for tx in txs:
            blockchain_tools_print_value('amount', f'{tx.amount}', pre=pre + 2)
            blockchain_tools_print_value('puzzle_hash', f'{tx.puzzle_hash}', pre=pre + 2)
            blockchain_tools_print_value('parent_coin_info', f'{tx.parent_coin_info}', pre=pre + 2)

            if txs_len > 1:
                blockchain_tools_print_separator(pre=pre + 2)
                txs_len -= 1

    blockchain_tools_print_raw('farmer_info:', pre=pre)
    if obj.foliage is None or obj.foliage.foliage_block_data is None:
        blockchain_tools_print_raw('none', pre=pre + 1)
    else:
        blockchain_tools_print_value('pool_puzzle_hash', f'{obj.foliage.foliage_block_data.pool_target.puzzle_hash}', pre=pre + 1)
        blockchain_tools_print_value('farmer_puzzle_hash', f'{obj.foliage.foliage_block_data.farmer_reward_puzzle_hash}',
                           pre=pre + 1)


def blockchain_tools_print_block_many(
        ctx: list,
        pre: int = 0
) -> None:
    blockchain_tools_print_many(
        ctx,
        blockchain_tools_print_block,
        pre=pre
    )


def blockchain_tools_print_coin(
        ctx: list,
        pre: int = 0
) -> None:
    hash: str = ctx[0]
    confirmed_at: int = ctx[1]
    spent_at: int = ctx[2]
    spent: bool = ctx[3] == 1
    coinbase: bool = ctx[4] == 1
    puzzle_hash: str = ctx[5]
    parent_coin: str = ctx[6]
    amount: int = int.from_bytes(ctx[7], byteorder='big', signed=False)
    timestamp: int = ctx[8]

    blockchain_tools_print_value('hash', hash, pre=pre)
    blockchain_tools_print_value('confirmed_at', confirmed_at, pre=pre)
    blockchain_tools_print_value('spent', 'yes' if spent else 'no', pre=pre)
    blockchain_tools_print_value('spent_at', spent_at, pre=pre)
    blockchain_tools_print_value('coinbase', 'yes' if coinbase else 'no', pre=pre)
    blockchain_tools_print_value('puzzle_hash', puzzle_hash, pre=pre)
    blockchain_tools_print_value('parent_coin', parent_coin, pre=pre)
    blockchain_tools_print_value('amount', amount, pre=pre)
    blockchain_tools_print_value('timestamp', timestamp, pre=pre)


def blockchain_tools_print_coin_lite(
        ctx: list,
        pre: int = 0
) -> None:
    hash: str = ctx[0]
    puzzle_hash: str = ctx[5]
    amount: int = int.from_bytes(ctx[7], byteorder='big', signed=False)
    timestamp: int = ctx[8]

    blockchain_tools_print_value('hash', hash, pre=pre)
    blockchain_tools_print_value('puzzle_hash', puzzle_hash, pre=pre)
    blockchain_tools_print_value('amount', amount, pre=pre)
    blockchain_tools_print_value('timestamp', timestamp, pre=pre)


def blockchain_tools_print_coin_many(
        ctx: list,
        pre: int = 0
) -> None:
    blockchain_tools_print_many(
        ctx,
        blockchain_tools_print_coin,
        pre=pre
    )


def blockchain_tools_print_coin_lite_many(
        ctx: list,
        pre: int = 0
) -> None:
    blockchain_tools_print_many(
        ctx,
        blockchain_tools_print_coin_lite,
        pre=pre
    )
