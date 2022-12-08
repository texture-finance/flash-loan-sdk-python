import os

from betterconf import Config, field
from betterconf.config import EnvironmentProvider
from dotenv import load_dotenv
from solana.publickey import PublicKey

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_DIR = os.path.join(ROOT_DIR, '.creds')


class PublicKeyProvider(EnvironmentProvider):
    def get(self, name: str) -> PublicKey:
        val = super().get(name)
        try:
            val = int(val)
        except ValueError:
            val = str(val)

        return PublicKey(val)


class FlashLoanConfig(Config):
    validator = field('VALIDATOR', provider=EnvironmentProvider())
    reserve = field('RESERVE', provider=PublicKeyProvider())
    program_id = field('FLASH_LOAN_PROGRAM', provider=PublicKeyProvider())


cfg = FlashLoanConfig()
