import os
import sys
import argparse
from web3 import Web3

from eth_utils import (
    decode_hex,
    to_canonical_address,
    to_wei,
)

from eth import constants
from eth.chains.base import (
    Chain,
)

from eth.db.backends.memory import MemoryDB
# TODO: tests should not be locked into one set of VM rules.  Look at expanding
# to all mainnet vms.
from eth.vm.forks.spurious_dragon import SpuriousDragonVM

NORMALIZED_ADDRESS_A = "0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6"
NORMALIZED_ADDRESS_B = "0xcd1722f3947def4cf144679da39c4c32bdc35681"
CANONICAL_ADDRESS_A = to_canonical_address("0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6")
CANONICAL_ADDRESS_B = to_canonical_address("0xcd1722f3947def4cf144679da39c4c32bdc35681")

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Test a Contract')
    parser.add_argument('--ori', dest='origin', default=CANONICAL_ADDRESS_B, type=str)
    parser.add_argument('--gas_price', dest='gasPrice', default='0x1', type=str)
    parser.add_argument('--gas', dest='gas', default='0xffffffffffff', type=str)
    # to = '': create a contract
    parser.add_argument('--to', dest='address', default=CANONICAL_ADDRESS_A, type=str)
    parser.add_argument('--sender', dest='caller', default=CANONICAL_ADDRESS_B, type=str)
    parser.add_argument('--value', dest='value', default='0x0', type=str)
    parser.add_argument('--data', dest='data', default='', type=str)
    parser.add_argument('--code', dest='code', default='6040', type=str)

    args = parser.parse_args()
    return args

def args_to_bytecode_computation(args, code, vm):
    return vm.execute_bytecode(
        origin=to_canonical_address(args.origin),
        gas_price=int(args.gasPrice, 16),
        gas=int(args.gas, 16),
        to=to_canonical_address(args.address),
        sender=to_canonical_address(args.caller),
        value=int(args.value, 16),
        data=args.data.encode(),
        code=decode_hex(code),
    )

def funded_address_initial_balance():
    return to_wei(1000, 'ether')

def base_genesis_state(funded_address, funded_address_initial_balance):
    return {
        funded_address: {
            'balance': funded_address_initial_balance,
            'nonce': 0,
            'code': b'',
            'storage': {},
        }
    }

def chain_with_block_validation(base_db, genesis_state):
    """
    Return a Chain object containing just the genesis block.
    The Chain's state includes one funded account, which can be found in the
    funded_address in the chain itself.
    This Chain will perform all validations when importing new blocks, so only
    valid and finalized blocks can be used with it. If you want to test
    importing arbitrarily constructe, not finalized blocks, use the
    chain_without_block_validation fixture instead.
    """
    genesis_params = {
        "bloom": 0,
        "coinbase": to_canonical_address("8888f1f195afa192cfee860698584c030f4c9db1"),
        "difficulty": 131072,
        "extra_data": b"B",
        "gas_limit": 3141592,
        "gas_used": 0,
        "mix_hash": decode_hex("56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"),  # noqa: E501
        "nonce": decode_hex("0102030405060708"),
        "block_number": 0,
        "parent_hash": decode_hex("0000000000000000000000000000000000000000000000000000000000000000"),  # noqa: E501
        "receipt_root": decode_hex("56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"),  # noqa: E501
        "timestamp": 1422494849,
        "transaction_root": decode_hex("56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"),  # noqa: E501
        "uncles_hash": decode_hex("1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347")  # noqa: E501
    }
    klass = Chain.configure(
        __name__='TestChain',
        vm_configuration=(
            (constants.GENESIS_BLOCK_NUMBER, SpuriousDragonVM),
        ),
        network_id=1337,
    )
    chain = klass.from_genesis(base_db, genesis_params, genesis_state)
    return chain

def main ():
    args = parse_args()
    # print('Called with args:')
    # print(args)

    # create an vm
    base_db = MemoryDB()
    # genesis address
    init_address = to_canonical_address("8888f1f195afa192cfee860698584c030f4c9db1")
    genesis_state = base_genesis_state(init_address, funded_address_initial_balance())
    chain = chain_with_block_validation(base_db, genesis_state)
    vm = chain.get_vm()

    # print('Excuting...')
    args_to_bytecode_computation(args, args.code, vm)
    # print('End.')

if __name__ == '__main__':
    main()

