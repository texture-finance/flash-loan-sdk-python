import logging

from solana.keypair import Keypair
from solana.publickey import PublicKey

from config import cfg
from src.executor import FlashLoanExecutor
from src.helpers import Account, Wallet, available_liquidity, calculate_flash_loan_fees
from src.layout import RESERVE_LAYOUT

logging.getLogger().setLevel(logging.INFO)


def start_flash_borrow_repay():
    logging.info(f"Solana cluster: {cfg.validator}")
    logging.info(f"Flash loan program id: {cfg.program_id}")
    logging.info(f"Flash loan reserve: {cfg.reserve}")

    reserve = cfg.reserve

    # Get account information for Reserve to read info about accounts and fees
    reserve_acc = Account(public_key=reserve).get_info(RESERVE_LAYOUT)
    reserve_source_liquidity = PublicKey(reserve_acc["liquidity"]["supply_pubkey"])
    lending_market = PublicKey(reserve_acc["lending_market"])
    reserve_liquidity_fee_receiver = PublicKey(reserve_acc["config"]["fee_receiver"])

    # All token amounts in this SDK are in lamports
    flash_loan_amount = 100000000  # 0.1 SOL
    logging.info(f"FlashLoan amount: {flash_loan_amount}")

    # We need to return borrow amount + fee at the end of the flash loan transaction.
    # So its worth to make sure that we have enough money to pay fees.
    # Get the fees amount via calculate_flash_loan_fees() call.
    flash_loan_fee, texture_fee = calculate_flash_loan_fees(reserve, flash_loan_amount)
    logging.info(
        f"Fee to borrow {flash_loan_amount} lamports "
        f"will be: {flash_loan_fee} lamports"
    )

    available_amount = available_liquidity(reserve)
    logging.info(f"Available liquidity: {available_amount}")

    # Create transfer authority address. Also it will be fee payer of transaction
    # and owner of native SPL token account
    transfer_authority = Keypair()
    logging.info(f"Transfer authority address: {transfer_authority.public_key}")

    # Create native SPL token account: wrap lamports (fee) from transfer authority
    # to new SPL token account
    native_account = Keypair()
    Wallet(keypair=transfer_authority).air_drop_sol(2)  # max airdrop limit for devnet
    Wallet(keypair=native_account).create_native_spl_token_account(
        payer=transfer_authority,
        source_transfer_wallet=transfer_authority,
        amount=flash_loan_fee,
    )
    logging.info(f"Native SPL token account: {native_account.public_key}")

    (
        FlashLoanExecutor()
        # Construct FlashBorrow instruction.
        # Here we specify flash_loan_amount without fees.
        .flash_borrow(
            source_liquidity=reserve_source_liquidity,
            destination_liquidity=native_account.public_key,
            reserve=reserve,
            lending_market=lending_market,
            amount=flash_loan_amount,
        )
        # Construct FlashRepay instruction.
        # Again we specify amount_to_borrow without fees.
        # But when contract will be executing this instruction
        # it will transfer flash_loan_amount + flash_loan_fee from user's wallet!
        .flash_repay(
            source_liquidity=native_account.public_key,
            destination_liquidity=reserve_source_liquidity,
            reserve=reserve,
            reserve_liquidity_fee_receiver=reserve_liquidity_fee_receiver,
            lending_market=lending_market,
            user_transfer_authority=transfer_authority.public_key,
            amount=flash_loan_amount,
        ).execute(
            fee_payer=transfer_authority.public_key,
            signers=[transfer_authority],
        )
    )


if __name__ == "__main__":
    start_flash_borrow_repay()
