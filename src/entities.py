import abc
from dataclasses import dataclass
from typing import List

from solana import sysvar
from solana.publickey import PublicKey
from solana.transaction import AccountMeta
from spl.token import constants as spl_constants

from src.address import find_lending_market_authority


class AccountKeysStructure(abc.ABC):
    @abc.abstractmethod
    def as_account_keys(self) -> List[AccountMeta]:
        pass

    def as_dict(self):
        return {k: str(v) for k, v in vars(self).items()}


@dataclass
class FlashBorrowParams(AccountKeysStructure):
    source_liquidity: PublicKey
    destination_liquidity: PublicKey
    reserve: PublicKey
    lending_market: PublicKey
    program_id: PublicKey

    def as_account_keys(self) -> List[AccountMeta]:
        lending_market_authority = find_lending_market_authority(
            self.lending_market, self.program_id
        )
        return [
            AccountMeta(self.source_liquidity, is_writable=True, is_signer=False),
            AccountMeta(self.destination_liquidity, is_writable=True, is_signer=False),
            AccountMeta(self.reserve, is_writable=True, is_signer=False),
            AccountMeta(self.lending_market, is_writable=False, is_signer=False),
            AccountMeta(lending_market_authority, is_writable=False, is_signer=False),
            AccountMeta(
                sysvar.SYSVAR_INSTRUCTIONS_PUBKEY, is_writable=False, is_signer=False
            ),
            AccountMeta(
                spl_constants.TOKEN_PROGRAM_ID, is_writable=False, is_signer=False
            ),
        ]


@dataclass
class FlashRepayParams(AccountKeysStructure):
    source_liquidity: PublicKey
    destination_liquidity: PublicKey
    reserve: PublicKey
    reserve_liquidity_fee_receiver: PublicKey
    lending_market: PublicKey
    user_transfer_authority: PublicKey

    def as_account_keys(self) -> List[AccountMeta]:
        return [
            AccountMeta(self.source_liquidity, is_writable=True, is_signer=False),
            AccountMeta(self.destination_liquidity, is_writable=True, is_signer=False),
            AccountMeta(
                self.reserve_liquidity_fee_receiver, is_writable=True, is_signer=False
            ),
            AccountMeta(self.reserve, is_writable=True, is_signer=False),
            AccountMeta(self.lending_market, is_writable=False, is_signer=False),
            AccountMeta(
                self.user_transfer_authority, is_writable=False, is_signer=True
            ),
            AccountMeta(
                sysvar.SYSVAR_INSTRUCTIONS_PUBKEY, is_writable=False, is_signer=False
            ),
            AccountMeta(
                spl_constants.TOKEN_PROGRAM_ID, is_writable=False, is_signer=False
            ),
        ]
