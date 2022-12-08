from solana.publickey import PublicKey


def find_lending_market_authority(
    lending_market: PublicKey, program_id: PublicKey
) -> PublicKey:
    return PublicKey.find_program_address([bytes(lending_market)], program_id)[0]
