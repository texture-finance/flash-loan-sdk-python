import json
import logging
from abc import ABC
from typing import List

import borsh_construct
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized
from solana.rpc.types import TxOpts
from solana.transaction import Transaction, TransactionInstruction

from config import cfg
from src.entities import AccountKeysStructure, FlashBorrowParams, FlashRepayParams
from src.layout import CONTRACT_LAYOUT

logging.getLogger().setLevel(logging.INFO)


class FlashLoanExecutor(ABC):
    CONTRACT_LAYOUT: borsh_construct.Enum = CONTRACT_LAYOUT
    MAIN_PROGRAM_ID: PublicKey = cfg.program_id

    def __init__(self):
        self.__client = Client(cfg.validator)
        self.__instructions = []

    def _append_instruction(
        self,
        instruction_name: str,
        acc_keys: AccountKeysStructure,
        data: dict,
    ):
        instruction = getattr(self.CONTRACT_LAYOUT.enum, instruction_name)

        logging.info(f"Append instruction {instruction_name}")
        logging.info(
            (
                f"Account Keys: \n {acc_keys.as_account_keys()} \n"
                f"Data: \n {json.dumps(data, sort_keys=True, indent=4, default=str)}"
            )
        )

        data = self.CONTRACT_LAYOUT.build(instruction(**data))

        self.__instructions.append(
            TransactionInstruction(
                keys=acc_keys.as_account_keys(),
                program_id=self.MAIN_PROGRAM_ID,
                data=data,
            )
        )

    def execute(self, fee_payer: PublicKey, signers: List[Keypair]):
        if not self.__instructions:
            raise ValueError("Executor has no instructions")

        logging.info(
            (
                f"Execute transaction with:\n"
                f"Fee Payer: {fee_payer}\n"
                f"Signers: {[sig.public_key for sig in signers]}\n"
            )
        )

        transaction = Transaction(
            fee_payer=fee_payer,
            instructions=self.__instructions,
        )

        resp = self.__client.send_transaction(
            transaction,
            *set(signers),
            opts=TxOpts(skip_confirmation=False, preflight_commitment=Finalized),
        )

        self.reset()

        return resp

    def reset(self):
        self.__instructions = []

    def flash_borrow(
        self,
        source_liquidity: PublicKey,
        destination_liquidity: PublicKey,
        reserve: PublicKey,
        lending_market: PublicKey,
        amount: int,
    ):
        """
        Flash borrow reserve liquidity
        :param source_liquidity:
        :param destination_liquidity:
        :param reserve:
        :param lending_market:
        :param amount:
        :return:
        """

        self._append_instruction(
            instruction_name="FlashBorrow",
            acc_keys=FlashBorrowParams(
                source_liquidity=source_liquidity,
                destination_liquidity=destination_liquidity,
                reserve=reserve,
                lending_market=lending_market,
                program_id=self.MAIN_PROGRAM_ID,
            ),
            data=dict(amount=amount),
        )

        return self

    def flash_repay(
        self,
        source_liquidity: PublicKey,
        destination_liquidity: PublicKey,
        reserve: PublicKey,
        reserve_liquidity_fee_receiver: PublicKey,
        lending_market: PublicKey,
        user_transfer_authority: PublicKey,
        amount: int,
    ):
        """
        Flash repay reserve liquidity
        :param source_liquidity:
        :param destination_liquidity:
        :param reserve:
        :param reserve_liquidity_fee_receiver:
        :param lending_market:
        :param user_transfer_authority:
        :param amount:
        :return:
        """

        self._append_instruction(
            instruction_name="FlashRepay",
            acc_keys=FlashRepayParams(
                source_liquidity=source_liquidity,
                destination_liquidity=destination_liquidity,
                reserve=reserve,
                reserve_liquidity_fee_receiver=reserve_liquidity_fee_receiver,
                lending_market=lending_market,
                user_transfer_authority=user_transfer_authority,
            ),
            data=dict(amount=amount),
        )

        return self
