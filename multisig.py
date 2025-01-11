# Copyright © Aptos Foundation
# SPDX-License-Identifier: Apache-2.0

import asyncio
import subprocess
import time

from aptos_sdk.account import Account, RotationProofChallenge
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.authenticator import Authenticator, MultiEd25519Authenticator
from aptos_sdk.bcs import Serializer
from aptos_sdk.ed25519 import MultiPublicKey, MultiSignature
from aptos_sdk.transactions import (
    EntryFunction,
    RawTransaction,
    Script,
    ScriptArgument,
    SignedTransaction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.type_tag import StructTag, TypeTag

# Network configuration - using devnet for testing. Check current urls at:
# https://github.com/aptos-labs/aptos-python-sdk/blob/main/examples/common.py
NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1"
FAUCET_URL = "https://faucet.devnet.aptoslabs.com"

should_wait = True

def wait():
    """Wait for user to press Enter before starting next section."""
    if should_wait:
        input("\nPress Enter to continue...")

async def main(should_wait_input=True):
    global should_wait
    should_wait = should_wait_input

    # Initialize our blockchain clients
    rest_client = RestClient(NODE_URL)
    faucet_client = FaucetClient(FAUCET_URL, rest_client)

    # Create three key holders, these are accounts on aptos
    alice = Account.generate()
    bob = Account.generate()
    chad = Account.generate()
    
    print("\n=== Account addresses ===")
    print(f"Alice: {alice.address()}")
    print(f"Bob:   {bob.address()}")
    print(f"Chad:  {chad.address()}")

    wait()

    print("\n=== Authentication keys ===")
    print(f"Alice: {alice.auth_key()}")
    print(f"Bob:   {bob.auth_key()}")
    print(f"Chad:  {chad.auth_key()}")

    print("\n=== Public keys ===")
    print(f"Alice: {alice.public_key()}")
    print(f"Bob:   {bob.public_key()}")
    print(f"Chad:  {chad.public_key()}")\

    wait()

    # Configure a 2-of-3 multisig account
    threshold = 2

    multisig_public_key = MultiPublicKey(
        [alice.public_key(), bob.public_key(), chad.public_key()],
        threshold
    )

    multisig_address = AccountAddress.from_key(multisig_public_key)
    
    print("\n=== 2-of-3 Multisig account ===")
    print(f"Account public key: {multisig_public_key}")
    print(f"Account address:    {multisig_address}")

    wait()

    print("\n=== Funding accounts ===")
    alice_start = 10_000_000
    bob_start = 20_000_000
    chad_start = 30_000_000
    multisig_start = 40_000_000

    # Fund all accounts concurrently
    alice_fund = faucet_client.fund_account(alice.address(), alice_start)
    bob_fund = faucet_client.fund_account(bob.address(), bob_start)
    chad_fund = faucet_client.fund_account(chad.address(), chad_start)
    multisig_fund = faucet_client.fund_account(multisig_address, multisig_start)
    await asyncio.gather(*[alice_fund, bob_fund, chad_fund, multisig_fund])
    
    # Check all balances
    alice_balance = rest_client.account_balance(alice.address())
    bob_balance = rest_client.account_balance(bob.address())
    chad_balance = rest_client.account_balance(chad.address())
    multisig_balance = rest_client.account_balance(multisig_address)
    [alice_balance, bob_balance, chad_balance, multisig_balance] = await asyncio.gather(
        *[alice_balance, bob_balance, chad_balance, multisig_balance]
    )
    
    print(f"Alice's balance:  {alice_balance}")
    print(f"Bob's balance:    {bob_balance}")
    print(f"Chad's balance:   {chad_balance}")
    print(f"Multisig balance: {multisig_balance}")

    wait()
    
    # Create the transfer transaction
    entry_function = EntryFunction.natural(
        module="0x1::coin",
        function="transfer",
        ty_args=[TypeTag(StructTag.from_str("0x1::aptos_coin::AptosCoin"))],
        args=[
            TransactionArgument(chad.address(), Serializer.struct),
            TransactionArgument(100, Serializer.u64),
        ],
    )

    # Build the raw transaction
    chain_id = await rest_client.chain_id()
    raw_transaction = RawTransaction(
        sender=multisig_address,
        sequence_number=0,
        payload=TransactionPayload(entry_function),
        max_gas_amount=2000,
        gas_unit_price=100,
        expiration_timestamps_secs=int(time.time()) + 600,
        chain_id=chain_id,
    )

    alice_signature = alice.sign(raw_transaction.keyed())
    bob_signature = bob.sign(raw_transaction.keyed())

    print("\n=== Individual signatures ===")
    print(f"Alice: {alice_signature}")
    print(f"Bob:   {bob_signature}")

    wait()

    # Combine the signatures (map from signatory public key index to signature)
    sig_map = [(0, alice_signature), (1, bob_signature)]
    multisig_signature = MultiSignature(sig_map)

    # Create the authenticator with our multisig configuration
    authenticator = Authenticator(
        MultiEd25519Authenticator(multisig_public_key, multisig_signature)
    )

    # Create and submit the signed transaction
    signed_transaction = SignedTransaction(raw_transaction, authenticator)

    print("\n=== Submitting transfer transaction ===")
    tx_hash = await rest_client.submit_bcs_transaction(signed_transaction)
    await rest_client.wait_for_transaction(tx_hash)
    print(f"Transaction hash: {tx_hash}")

    print("\n=== New account balances ===")
    [alice_balance, bob_balance, chad_balance, multisig_balance] = await asyncio.gather(
        *[
            rest_client.account_balance(alice.address()),
            rest_client.account_balance(bob.address()),
            rest_client.account_balance(chad.address()),
            rest_client.account_balance(multisig_address),
        ]
    )

    print(f"Alice's balance:  {alice_balance}")
    print(f"Bob's balance:    {bob_balance}")
    print(f"Chad's balance:   {chad_balance}")
    print(f"Multisig balance: {multisig_balance}")
    # Add additional code here

if __name__ == "__main__":
	  asyncio.run(main())
