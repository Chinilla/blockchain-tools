import os

from blockchain_tools.blockchain_tools_print import (
    blockchain_tools_print_require_env
)


def blockchain_tools_assert_env_set(
        env: str
) -> None:
    if env not in os.environ:
        blockchain_tools_print_require_env(env)
        exit(1)
