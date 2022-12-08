[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
# FLash Loan SDK

## Usage:
SDK can call FlashBorrow and FlashRepay instructions of FLashLoan contract

### Functions
* ```available_liquidity``` - Returns maximum amount of tokens which could be flash borrowed from given reserve. Use this function when you have deserialized Reserve structure.
* ```calculate_flash_loan_fees``` -	Calculates total fees for flash borrow of specified amount Type of token to be borrowed is determined by reserve
* ```get_info``` -	Returns deserialized account info (Reserve structure getting it from account specified by reserve_key via provided RpcClient)
* ```flash_borrow``` -	Creates a ‘FlashBorrow’ instruction.
* ```flash_repay``` -	Creates a ‘FlashRepay’ instruction.

Usage example see in ```flash_borrow_repay_example.py```

### Addresses
Program ID of Flash Loan contract on devnet and mainnet: F1aShdFVv12jar3oM2fi6SDqbefSnnCVRzaxbPH3you7
It is defined as FLASH_LOAN_ID constant in this SDK.

wSOL reserve on devnet: 9Wys2sCHcAGZm3jgSnfP8xyq1ZiK2qthQ4Ki5fSdkqP

### Quick Start
1. Clone, or download repo
2. Run the **Install Requirements** below.
3. Create .env (See .env.example)
4. Run example script ``` poetry run python3 flash_borrow_repay_example.py ``` for flash borrow and flash repay in flash-loan-sdk/ directory.

### Install Requirements
In CMD:
``` 
pip3 install poetry

poetry install
```
