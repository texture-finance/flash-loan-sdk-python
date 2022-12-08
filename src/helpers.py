import json
import logging

import spl.token.instructions as spl_token
from borsh_construct import CStruct
from solana import system_program
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized
from solana.rpc.types import RPCResponse, TxOpts
from solana.transaction import Transaction
from solana.utils.helpers import decode_byte_string
from spl.token import constants as spl_constants
from spl.token.client import Token

from config import cfg
from src import utils
from src.layout import RESERVE_LAYOUT

logger = logging.getLogger(__name__)


class Account:
    def __init__(self, public_key: PublicKey = None, keypair: Keypair = None):
        self.validator = cfg.validator
        self.client = Client(self.validator)
        self.public_key = public_key or keypair.public_key
        self.keypair = keypair

    def get_info(self, schema, is_anchor: bool = False):
        """
        Get account info from solana and parse by current schema
        """
        logger.debug(f"Get Account info for key: {self.public_key}")

        client = Client(cfg.validator)
        resp = client.get_account_info(self.public_key)

        data = self.__parse_account_data(resp, schema, is_anchor)

        logger.debug(
            f"Parsed account data:\n {json.dumps(data, indent=4, default=str)}"
        )

        return data

    def __parse_account_data(self, resp: RPCResponse, schema: CStruct, is_anchor: bool):
        try:
            b58decoded = decode_byte_string(resp["result"]["value"]["data"][0])
            if is_anchor:
                # remove anchor account descriptor
                b58decoded = bytearray(b58decoded)[8:]
        except TypeError:
            raise ValueError(f"Account not found")

        return schema.parse(b58decoded)


class Wallet:
    def __init__(self, public_key: PublicKey = None, keypair: Keypair = None):
        self.validator = cfg.validator
        self.client = Client(self.validator)
        self.public_key = public_key or keypair.public_key
        self.keypair = keypair

    @utils.wait_transaction_finalized
    def __air_drop(self, sol_amount: int):
        """
        Air drop sol for wallet
        """
        return self.client.request_airdrop(self.public_key, sol_amount)

    def air_drop_sol(self, amount: int):
        return self.__air_drop(int(1000000000 * amount))

    def air_drop_lamports(self, amount: int):
        return self.__air_drop(amount)

    def create_native_spl_token_account(
        self, payer: Keypair, source_transfer_wallet: Keypair, amount: int
    ):
        client = Client(cfg.validator)
        tnx = Transaction(fee_payer=payer.public_key)
        tnx.add(
            system_program.create_account(
                system_program.CreateAccountParams(
                    from_pubkey=payer.public_key,
                    new_account_pubkey=self.keypair.public_key,
                    lamports=Token.get_min_balance_rent_for_exempt_for_account(client),
                    space=spl_constants.ACCOUNT_LEN,
                    program_id=spl_constants.TOKEN_PROGRAM_ID,
                )
            )
        )
        tnx.add(
            system_program.transfer(
                system_program.TransferParams(
                    from_pubkey=source_transfer_wallet.public_key,
                    to_pubkey=self.keypair.public_key,
                    lamports=amount,
                )
            )
        )
        tnx.add(
            spl_token.initialize_account(
                spl_token.InitializeAccountParams(
                    program_id=spl_constants.TOKEN_PROGRAM_ID,
                    account=self.keypair.public_key,
                    mint=spl_constants.WRAPPED_SOL_MINT,
                    owner=payer.public_key,
                )
            )
        )
        return client.send_transaction(
            tnx,
            payer,
            source_transfer_wallet,
            self.keypair,
            opts=TxOpts(skip_confirmation=False, preflight_commitment=Finalized),
        )


def available_liquidity(reserve: PublicKey) -> int:
    reserve_acc = Account(public_key=reserve).get_info(RESERVE_LAYOUT)
    return reserve_acc["liquidity"]["available_amount"]


def calculate_flash_loan_fees(reserve: PublicKey, amount: int) -> any:
    reserve_acc = Account(public_key=reserve).get_info(RESERVE_LAYOUT)
    flash_loan_fee_wad = reserve_acc["config"]["fees"]["flash_loan_fee_wad"] / (
        10**18
    )
    texture_fee_percentage = (
        reserve_acc["config"]["fees"]["texture_fee_percentage"] / 100
    )
    if flash_loan_fee_wad > 0 and amount > 0:
        need_to_assess_texture_fee = texture_fee_percentage > 0
        minimum_fee = 2 if need_to_assess_texture_fee else 1
        borrow_fee_amount = amount * flash_loan_fee_wad
        borrow_fee = max(borrow_fee_amount, minimum_fee)
        if borrow_fee >= amount:
            raise Exception(
                "Borrow amount is too small to receive liquidity after fees"
            )
        if need_to_assess_texture_fee:
            texture_fee_amount = borrow_fee * texture_fee_percentage
            texture_fee = max(texture_fee_amount, 1)
        else:
            texture_fee = 0

        return int(borrow_fee), int(texture_fee)

    return 0, 0
