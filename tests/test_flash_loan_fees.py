from config import cfg
from src.helpers import Account, calculate_flash_loan_fees
from src.layout import RESERVE_LAYOUT


def test_flash_loan_fees():
    reserve = cfg.reserve
    reserve_acc = Account(public_key=reserve).get_info(RESERVE_LAYOUT)

    amount = 100000000
    flash_loan_fee_wad = reserve_acc["config"]["fees"]["flash_loan_fee_wad"] / (
        10**18
    )
    texture_fee_percentage = (
        reserve_acc["config"]["fees"]["texture_fee_percentage"] / 100
    )

    flash_loan_fee, texture_fee = calculate_flash_loan_fees(reserve, amount)
    curr_flash_loan_fee = flash_loan_fee_wad * amount
    assert curr_flash_loan_fee == flash_loan_fee, "Incorrect FlashLoan fee"
    curr_texture_fee = texture_fee_percentage * curr_flash_loan_fee
    assert curr_texture_fee == texture_fee, "Incorrect Texture fee"
