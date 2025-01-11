# Your First Aptos Multisig (Python SDK)

Imagine a high-security bank vault that requires multiple key holders to open it where each key holder must be present and provide their unique key before any access is granted. This is exactly how multisig (multi-signature) works in Aptos, but with digital signatures instead of physical keys.

In this tutorial, you'll learn how to create and manage a multisig account that requires 2 out of 3 people to approve any transaction.

You'll learn how to:

1. Set up a development environment for Aptos
2. Create multiple accounts to act as key holders
3. Configure a multisig account requiring 2-of-3 signatures
4. Fund accounts and verify balances
5. Create and execute multisig transactions

<aside>
💡

If you're coming from Ethereum/Solidity, note that Aptos handles multisig differently. Instead of deploying a smart contract like Gnosis Safe, Aptos implements multisig at the protocol level through its account abstraction system. 

We’re interfacing with Aptos using the [Aptos Python SDK](https://aptos.dev/en/build/sdks/python-sdk).

</aside>

## Setup

First, let's prepare our development environment. We'll create an isolated workspace and install all necessary dependencies.

### Steps

1. Check if you have Python installed by opening Terminal:
    
    ```bash
    python3 --version
    ```
    
    You should see something like "Python 3.7" or higher. If you see an error or a lower version, download Python from [python.org](http://python.org/).
    
2. Create a new folder for our project:
    
    ```bash
    mkdir my-first-multisig
    ```
    
3. Move into this new folder:
    
    ```bash
    cd my-first-multisig
    ```
    
4. Create a virtual environment:
    
    ```bash
    python3 -m venv venv
    ```
    
    <aside>
    💡
    
    On Windows, use `python -m venv venv` instead (without the '3').
    
    </aside>
    
    This command:
    
    - Creates an isolated Python environment
    - Installs a fresh Python instance
    - Keeps project dependencies separate from your system Python
    - Creates a `venv` folder (you can view but don't modify its contents!)
5. Activate the virtual environment:
    
    ```bash
    source venv/bin/activate
    ```
    
    <aside>
    💡
    
    On Windows, use `.\venv\Scripts\activate` instead.
    
    </aside>
    
    This command:
    
    - Modifies your terminal's environment variables
    - Makes your terminal use the Python from `venv` instead of your system Python
    - You'll see `(venv)` appear at the start of your terminal line
    - To deactivate later, simply type `deactivate`
6. Install the Aptos SDK:
    
    ```bash
    pip install aptos-sdk
    ```
    
    This command:
    
    - Downloads the Aptos SDK package from PyPI (Python Package Index)
    - Installs it inside your `venv` folder
    - Creates files in `venv/lib/python3.x/site-packages/aptos_sdk`
    - You can view these files by navigating to that directory
7. Create our empty Python script:
    
    ```bash
    touch multisig.py
    ```
    

## Creating the Foundation

Let's start building our multisig implementation. First, we'll set up our imports, main loop, and base configuration.

### Steps

1. Open `multisig.py` in your text editor and add the following code:
    
    ```python
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
    ```
    
    This code imports all the necessary modules from the Aptos SDK. The `aptos_sdk.account` module provides essential functionality for managing accounts and signatures, while `aptos_sdk.transactions` gives us the tools to create and submit blockchain transactions.
    
2. Add this code for waiting and define our main loop below the FAUCET_URL.
    
    ```python
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
        
        # Add additional code here
        
    if __name__ == "__main__":
    	  asyncio.run(main())
    ```
    
    Like in banks, we should wait and verify; we added a helper function for interactive learning for our interactive learning environment. The `RestClient` connects to the Aptos blockchain network, while the `FaucetClient` allows us to get test tokens on devnet. The `wait()` function helps us pause between steps so you can see what's happening.
    
    <aside>
    💡
    
    Aptos devnet resets weekly and is a great place to start developing. Along with testnet (which doesn’t reset weekly), you can get free tokens from our faucet.
    
    </aside>
    

## Creating Our Key Holders

Just like a bank vault needs designated key holders, our multisig needs authorized signers. Let's create the accounts for our key holders.

### Steps

1. Add the following code to create three accounts after setting up the blockchain clients and before `if __name__ == "__main__":`:
    
    ```python
    # Create three accounts to act as our key holders
    alice = Account.generate()
    bob = Account.generate()
    chad = Account.generate()
    ```
    
    The `Account.generate()` function creates a new Aptos account with a fresh keypair. Each account will have its own private key (for signing) and public key (for verification). This is similar to how each bank vault key holder would have their own unique physical key.
    
    <aside>
    💡
    
    Each time you run this script it will generate new accounts on the devnet. You’ll need to save the private key and account address if you want to continue working with that account.
    
    </aside>
    
2. Add this code below the account creation: 
    
    ```python
    		# For tutorial purposes only, remember to keep private key securely
    		print("\n=== Private keys ===")
    		print(f"Alice: {alice.private_key}")
    		print(f"Bob:   {bob.private_key}")
    		print(f"Chad:  {chad.private_key}")
    		
    		print("\n=== Account addresses ===")
    		print(f"Alice: {alice.address()}")
    		print(f"Bob:   {bob.address()}")
    		print(f"Chad:  {chad.address()}")
    		
    		wait()
    		
    		# Add additional code here, below the wait()
    ```
    
3. Let’s see what the private key and addresses of our devnet accounts look like. Run our [`multisig.py`](http://multisig.py) from your terminal.
    
    ```python
    python3 multisig.py
    ```
    
    We should see something like:
    
    ```python
    === Private keys ===
    Alice: 0xddf382a01369a8c2684d4c50906dc5a41dcf8d065aa95620e72177dd4491a71d
    Bob:   0x25c0d641851db824c499d06aec2fdb3234a3a9886b47e84c2a1178876a1302df
    Chad:  0x5a4f7d08aabf8784892166c1c117cef88c63acd38698fe4b49499cb164eb7413
    
    === Account addresses ===
    Alice: 0x2d9f9779b86937f616a20d76333093777976a5a9e817dccfe2c4373acd9a6b54
    Bob:   0x9bf01ed926fea3c9cd7ed8e4ef2045411bb9a237bf7b428b5974035ddb372f96
    Chad:  0x04116237c27e55b0a979cd42987d4772c2405e4ccf62803a592bf154c162a89c
    
    Press Enter to continue...
    ```
    
    These private keys and addresses uniquely control and identify each account on the Aptos blockchain. Let’s get rid of them.
    
    <aside>
    💡
    
    Just like bank account numbers, the addresses will be used to send and receive funds. However, unlike traditional bank accounts, these keys give full control over the account - so they must be kept extremely secure in a real application.
    
    </aside>
    
4. Delete the print statements for the private keys (the 4 lines of code beginning with`print("\n=== Private keys ===")`).
5. Add the following code to print out the rest of the public account information:
    
    ```python
    print("\n=== Authentication keys ===")
    print(f"Alice: {alice.auth_key()}")
    print(f"Bob:   {bob.auth_key()}")
    print(f"Chad:  {chad.auth_key()}")
    
    print("\n=== Public keys ===")
    print(f"Alice: {alice.public_key()}")
    print(f"Bob:   {bob.public_key()}")
    print(f"Chad:  {chad.public_key()}")
    
    wait()
    
    # Add additional code below this wait
    ```
    
    Clear receipts like these print statements can help with debugging and testing later.
    
6. Run the code to see three newly generated accounts:
    
    ```bash
    python3 multisig.py.
    ```
    
7. Press enter after seeing the new account numbers to see all three pieces of information.
    - Address: Like a permanent bank account number others can send funds to.
    - Auth key: This authorization key controls account access and can be changed later.
    - Public key: Used to verify signatures (like checking ID at a bank).
    
    <aside>
    ⚠️
    
    If you are getting an error, make sure you are putting your code above `if __name__ == "__main__":` and doing your imports and the indentation correctly.
    
    </aside>
    
    Example expected output:
    
    ```
    === Account addresses ===
    Alice: 0x5323a06f21b04af53fc57367b50d3bbb5675c655bc9bc62f33b5e083d5d06b8b
    Bob:   0x9f3e94fc92e0076336c122a576304c0b9fa8def13a98c469dce05e0836b9fe5b
    Chad:  0x1d0e7b790493dcf7bc7ce60bf4ccdcca1d38ce0d7f8dd26d2791a6d3ff6da708
    
    Press Enter to continue...
    
    === Authentication keys ===
    Alice: 0x5323a06f21b04af53fc57367b50d3bbb5675c655bc9bc62f33b5e083d5d06b8b
    Bob:   0x9f3e94fc92e0076336c122a576304c0b9fa8def13a98c469dce05e0836b9fe5b
    Chad:  0x1d0e7b790493dcf7bc7ce60bf4ccdcca1d38ce0d7f8dd26d2791a6d3ff6da708
    
    === Public keys ===
    Alice: 0x730264a36d4ec90af2e28e1cf9c4d686440598317123469a7c827d4fcdf74715
    Bob:   0xc8dcccf0e353dfeb16979eae71421fcaf51e58af3e9ccfa78aaf868d693a6530
    Chad:  0xeff5fe7837f72ad984c14eb616be8d53511023ef0f01bce6c5f25428bfcc9250
    
    Press Enter to continue...
    ```
    
    <aside>
    💡
    
    For each user, note the [account address](https://aptos.dev/en/network/blockchain/accounts#account-address) and [authentication key](https://aptos.dev/en/network/blockchain/accounts#authentication-key) are identical, but the [public key](https://aptos.dev/en/network/blockchain/accounts#creating-an-account) is different.
    
    The Aptos account model facilitates the unique ability to rotate an account’s private key.  Since an account’s address is the *initial* authentication key, the ability to sign for an account can be transferred to another private key without changing its public address.
    
    </aside>
    

## Configuring the Multisig Vault

Now that we have our key holders (Alice, Bob, and Chad), let's set up our multisig configuration. This is like setting the rules for our digital vault.

### Steps

1. Add code to configure a 2-of-3 multisig account:
    
    ```python
    # Configure a 2-of-3 multisig account
    threshold = 2
    
    multisig_public_key = MultiPublicKey(
        [alice.public_key(), bob.public_key(), chad.public_key()],
        threshold
    )
    
    multisig_address = AccountAddress.from_key(multisig_public_key)
    
    # Add additional code here
    ```
    
    The `threshold = 2` sets our requirement for two signatures out of three possible signers. The `MultiPublicKey` combines all three public keys into a single multisig configuration.
    
    <aside>
    💡
    
    This is like setting up a bank vault's access rules: "Any two of these three people must approve to access the vault."
    
    </aside>
    
2. Print the multisig account information by adding this code below our newly defined `multisig_address`:
    
    ```python
    print("\n=== 2-of-3 Multisig account ===")
    print(f"Account public key: {multisig_public_key}")
    print(f"Account address:    {multisig_address}")
    
    wait()
    
    # Add additional code here
    ```
    
    These print statements help verify our multisig configuration. The account address will be used for receiving funds and the public key will be used for verifying signatures.
    
3. You can run the code to verify the output and create a whole new set of key holders and the multisig account itself:
    
    ```bash
    python3 multisig.py
    ```
    
    You should see output showing your multisig account's public key type and its unique address on the Aptos blockchain.
    
    Example output:
    
    ```
    === 2-of-3 Multisig account ===
    Account public key: 2-of-3 Multi-Ed25519 public key
    Account address:    0x08cac3b7b7ce4fbc5b18bc039279d7854e4c898cbf82518ac2650b565ad4d364
    ```
    

## Funding Our Accounts

Just like new bank accounts need initial deposits, our blockchain accounts need funds to operate.

### Steps

1. Add code to fund all accounts:
    
    ```python
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
    ```
    
    The `fund_account()` function requests test tokens from the Aptos faucet to let us experiment without using real APT.  We fund all accounts simultaneously rather than one at a time by first initializing them as `[name]_fund` and then awaiting the async function call that gathers them:`asyncio.gather()`.
    
2. When we run it, there will be a slight pause here as it waits for the funding to go through. Below the `await` add this code to check all balances and print them out:
    
    ```python
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
    ```
    
    The `account_balance()` function queries the blockchain for each account's current balance. Again, we use `asyncio.gather()` to make all these queries efficiently in parallel.
    
    <aside>
    💡
    
    These print statements help us verify that our funding operations succeeded. Each number represents an amount in octas (1 APT = 100_000_000 octas).
    
    </aside>
    
3. Run the code with `python3 multisig_demo.py` to verify funding success:
    
    The output should show each account with its respective balance. For example:
    
    ```
    === 2-of-3 Multisig account ===
    Account public key: 2-of-3 Multi-Ed25519 public key
    Account address:    0x1f7e5d8f42544ce4e8ce3715ca4186d69d62789c1da3e018898913521840f331
    
    Press Enter to continue...
    \n=== Funding accounts ===
    Alice's balance:  10000000
    Bob's balance:    20000000
    Chad's balance:   30000000
    Multisig balance: 40000000
    
    Press Enter to continue...
    ```
    
    <aside>
    ⚠️
    
    If any balance shows as 0, you may need to rerun the funding command as the faucet occasionally has temporary issues.
    
    </aside>
    

<aside>
💡

Values are in octas (1 APT = 100_000_000 octas). This is similar to how 1 dollar = 100 cents.

</aside>

## Creating Our First Multisig Transaction

Now let's create a transaction that requires multiple signatures. We'll transfer 100 octas from the multisig account to Chad, similar to how a bank transfer would require two managers to approve a large withdrawal.

### Steps

1. Create the transfer transaction by defining its parameters:
    
    ```python
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
    ```
    
    The code above:
    
    - Uses `EntryFunction.natural()` to create a transfer of 100 octas (APT's smallest unit) to Chad's address
    - Sets up transaction parameters like gas limits and expiration time
    - Creates a raw transaction that still needs signatures before it can be submitted
2. Get signatures from Alice and Bob by adding this code below the raw transaction.
    
    ```python
    alice_signature = alice.sign(raw_transaction.keyed())
    bob_signature = bob.sign(raw_transaction.keyed())
    
    print("\n=== Individual signatures ===")
    print(f"Alice: {alice_signature}")
    print(f"Bob:   {bob_signature}")
    
    wait()
    ```
    
    The above code:
    
    - Has Alice sign the transaction with her private key
    - Has Bob sign the same transaction with his private key
    - Prints the signatures to verify they were created successfully

After you add the code for creating the transaction and getting signatures, you should see something like this when you run it:

```
=== Individual signatures ===
Alice: 0x360e66c75b1ba787ec7b05998cbc14276d7fc0c006fb10c33d5cc3c4cc2ec4f53a8c0996b8e746fd6d86b09b4f8bb128cbf62d8b375f5b974faae040e889ac0d
Bob:   0xdcfd1965e531deb79de9d8daf7f28f46023107ce4f11612ce76da33e808486a0a368b34563d4f89d6179a3957a266c1e8809691fddabba3c2a3d8be14d6f2f0c

Press Enter to continue...
```

This shows that both Alice and Bob have signed the transaction. Each signature is a unique hash that proves they authorized the transaction with their private keys.

<aside>
💡

Like gathering two bank managers to sign a withdrawal slip - we need both signatures before the transaction can proceed. 

</aside>

## Submitting the Multisig Transaction

Now we'll combine the signatures and submit the transaction. This is similar to gathering all the signed papers from bank managers and submitting them to process a large transfer.

### Steps

1. Combine the signatures into a multisig authenticator, here's the code to add next along with clear explanations of what you'll see:
    
    ```python
    # Combine the signatures (map from signatory public key index to signature)
    sig_map = [(0, alice_signature), (1, bob_signature)]
    multisig_signature = MultiSignature(sig_map)
    
    # Create the authenticator with our multisig configuration
    authenticator = Authenticator(
        MultiEd25519Authenticator(multisig_public_key, multisig_signature)
    )
    ```
    
    The `sig_map` links each signer's public key to their signature, proving that both Alice and Bob have approved this transaction. The `MultiSignature` and `Authenticator` objects package these signatures in a format the blockchain can verify.
    
2. Create and submit the signed transaction by adding:
    
    ```python
    # Create and submit the signed transaction
    signed_transaction = SignedTransaction(raw_transaction, authenticator)
    
    print("\n=== Submitting transfer transaction ===")
    tx_hash = await rest_client.submit_bcs_transaction(signed_transaction)
    await rest_client.wait_for_transaction(tx_hash)
    print(f"Transaction hash: {tx_hash}")
    ```
    
    The `SignedTransaction` combines the original transaction data with the authenticator proving both required signatures are present. We then submit this to the blockchain using `submit_bcs_transaction()` and wait for confirmation.
    
3. Let’s also check our new balances after transaction to verify the transfer worked:
    
    ```python
    print("\\n=== New account balances ===")
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
    ```
    
4. Run our script again with `python3 [multisig.py](http://multisig.py)` to get our transaction hash and multisig address for our successfully submitted transaction!
    
    You should see something like:
    
    ```bash
    === Submitting transfer transaction ===
    Transaction hash: 0x2f0b7fc8e69213f0c7e720e660f789b6e3d3564729a298f2b4f6794245833f2d
    
    === New account balances ===
    Alice's balance:  10000000
    Bob's balance:    20000000
    Chad's balance:   30000100        # Increased by 100 octas
    Multisig balance: 39999200        # Decreased by 100 octas plus gas fees
    ```
    
    Notice how:
    
    - Chad's balance increased by exactly 100 octas, but Alice and Bob's balances didn't change since they only signed
    - The multisig account paid for both the transfer amount and the gas fees

<aside>
💡

You can verify transaction on Aptos Explorer:

- Go to [Aptos Explorer](https://explorer.aptoslabs.com/)
- Search for your multisig address or transaction hash
- Review the transaction details and balance changes, cool huh!?
</aside>

## Going Further: Advanced Features

You've completed the basics of Aptos multisig - creating a "vault" (multisig account), adding "key holders" (signers), and making a simple transfer that requires multiple approvals. But just like modern banking, there's much more we can do:

### Vanity Addresses

Like having a custom bank account number, Aptos lets you create "vanity" addresses that start with specific characters. Imagine being able to choose a memorable account number like "0xdd..." for your company "Digital Dynamics"!

### Account Rotation

Banks let you update your security credentials without changing your account number. Similarly, Aptos multisig accounts can "rotate" their authentication keys while keeping the same address - perfect for updating security without disrupting existing payment setups.

### Governance & Smart Contracts

Just as banks have complex approval systems for large corporate accounts, Aptos multisig can interact with smart contracts and governance systems. Imagine setting up automated rules like:

- Required approvals based on transaction size
- Time-locked transactions
- Integration with DAO voting systems

<aside>
💡

 Interested in learning these advanced features? Please fill out [our quick survey](https://example.com/survey) to help us create more tutorials that match your needs! Let us know what excites you most about multisig on Aptos.

</aside>

## Next Steps

1. Review the complete code example which include all the Advanced Features (see above) in the [Python SDK repository](https://github.com/aptos-labs/aptos-python-sdk/blob/main/examples/multisig.py)
2. Learn about [multisig governance in this tutorial](https://aptos.dev/en/build/cli/working-with-move-contracts/multi-signature-tutorial)
3. Explore [account abstraction in Aptos](https://aptos.dev/concepts/accounts)
4. Join the [Aptos Discord](https://discord.gg/aptoslabs) for developer support
