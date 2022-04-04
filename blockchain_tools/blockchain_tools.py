import os
import click

from blockchain_tools.blockchain_tools_db import (
    blockchain_tools_db_get_connection
)

from blockchain_tools.blockchain_tools_env import (
    BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH,
    BLOCKCHAIN_TOOLS_ENV_WT_DB_PATH
)

from blockchain_tools.blockchain_tools_cmd_coin import (
    blockchain_tools_cmd_coin
)

from blockchain_tools.blockchain_tools_cmd_block import (
    blockchain_tools_cmd_block
)

from blockchain_tools.blockchain_tools_cmd_nft_recover import (
    blockchain_tools_cmd_nft_recover
)

from blockchain_tools.blockchain_tools_cmd_version import (
    blockchain_tools_cmd_version
)


@click.group(
    context_settings={}
)
@click.pass_context
def blockchain_tools(
        ctx: click.Context,
) -> None:
    ctx.ensure_object(dict)

    if BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH in os.environ:
        ctx.obj['bc_db'] = blockchain_tools_db_get_connection(os.environ[BLOCKCHAIN_TOOLS_ENV_BC_DB_PATH])
    else:
        ctx.obj['bc_db'] = None

    if BLOCKCHAIN_TOOLS_ENV_WT_DB_PATH in os.environ:
        ctx.obj['wt_db'] = blockchain_tools_db_get_connection(os.environ[BLOCKCHAIN_TOOLS_ENV_WT_DB_PATH])
    else:
        ctx.obj['wt_db'] = None


def blockchain_tools_assert_env_set(
        env: str
) -> None:
    if env not in os.environ:
        blockchain_tools_print_require_env(env)
        exit(1)


@blockchain_tools.command(
    'block',
    help='Retrieve block data.'
)
@click.option(
    '-b',
    '--by',
    required=True,
    type=click.Choice(
        [
            'hash',
            'height',
        ],
        case_sensitive=False
    ),
    help="Interpret 'value' as."
)
@click.argument(
    'value',
    required=True
)
@click.pass_context
def blockchain_tools_block(
        ctx: click.Context,
        by: str,
        value: str
) -> None:
    blockchain_tools_cmd_block(
        ctx=ctx,
        by=by,
        value=value
    )


@blockchain_tools.command(
    'coin',
    help='Retrieve coin data.'
)
@click.option(
    '-b',
    '--by',
    required=True,
    type=click.Choice(
        [
            'hash',
            'hash_parent',
            'hash_puzzle'
        ],
        case_sensitive=False
    ),
    help="Interpret 'value' as."
)
@click.argument(
    'value',
    required=True
)
@click.pass_context
def blockchain_tools_coin(
        ctx: click.Context,
        by: str,
        value: str
) -> None:
    blockchain_tools_cmd_coin(
        ctx=ctx,
        by=by,
        value=value
    )


@blockchain_tools.command(
    'nft-recover',
    help="NFT prizes recovery."
)
@click.option(
    '-d',
    '--delay',
    required=True,
    type=int,
    default=604800,
    show_default=True
)
@click.option(
    '-l',
    '--launcher_hash',
    required=True,
    type=str
)
@click.option(
    '-p',
    '--pool_contract_address',
    required=True,
    type=str
)
@click.option(
    '-nh',
    '--node-host',
    required=True,
    type=str
)
@click.option(
    '-np',
    '--node-port',
    required=True,
    type=int,
)
@click.option(
    '-ct',
    '--cert-path',
    required=True,
    type=str
)
@click.option(
    '-ck',
    '--cert-key-path',
    required=True,
    type=str
)
@click.option(
    '-ca',
    '--cert-ca-path',
    required=False,
    type=str,
)
@click.pass_context
def blockchain_tools_nft_recover(
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
    blockchain_tools_cmd_nft_recover(
        ctx=ctx,
        delay=delay,
        launcher_hash=launcher_hash,
        pool_contract_address=pool_contract_address,
        node_host=node_host,
        node_port=node_port,
        cert_path=cert_path,
        cert_key_path=cert_key_path,
        cert_ca_path=cert_ca_path
    )


@blockchain_tools.command(
    'version',
    help='Retrieve version.'
)
@click.pass_context
def blockchain_tools_version(
        ctx: click.Context
) -> None:
    blockchain_tools_cmd_version(
        ctx=ctx
    )


def main() -> None:
    blockchain_tools()


if __name__ == '__main__':
    blockchain_tools()
