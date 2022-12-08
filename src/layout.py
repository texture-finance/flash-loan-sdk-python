from borsh_construct import U8, U64, CStruct, Enum

PUB_KEY_TYPE = U8[32]

CONTRACT_LAYOUT = Enum(
    "InitLendingMarket",
    "SetLendingMarketOwner",
    "InitReserve",
    "Deposit",
    "Withdraw",
    "FlashLoan",
    "UpdateReserveConfig",
    "FlashBorrow" / CStruct("amount" / U64),
    "FlashRepay" / CStruct("amount" / U64),
    "Sync",
    enum_name="LendingInstruction",
)

reserve_liquidity = CStruct(
    "mint_pubkey" / PUB_KEY_TYPE,
    "mint_decimals" / U64,
    "supply_pubkey" / PUB_KEY_TYPE,
    "available_amount" / U64,
)

reserve_lp_tokens = CStruct(
    "mint_pubkey" / PUB_KEY_TYPE,
    "mint_total_supply" / U64,
    "supply_pubkey" / PUB_KEY_TYPE,
)

reserve_fees = CStruct(
    "flash_loan_fee_wad" / U64,
    "texture_fee_percentage" / U8,
    "padding" / U8[7],
)

reserve_config = CStruct(
    "fees" / reserve_fees,
    "deposit_limit" / U64,
    "fee_receiver" / PUB_KEY_TYPE,
    "future_padding1" / U8[32],
    "future_padding2" / U8[32],
)

RESERVE_LAYOUT = CStruct(
    "version" / U8,
    "padding" / U8[7],
    "last_update" / U64,
    "lending_market" / PUB_KEY_TYPE,
    "liquidity" / reserve_liquidity,
    "lp_tokens_info" / reserve_lp_tokens,
    "config" / reserve_config,
    "future_padding" / U64[5],
)
