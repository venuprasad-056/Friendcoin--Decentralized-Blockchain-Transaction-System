import hashlib, time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending = []
        # create genesis block
        self.create_block(previous_hash='0')

    def create_block(self, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.pending,
            "previous_hash": previous_hash,
            "hash": self.hash_block(len(self.chain)+1, previous_hash)
        }
        self.pending = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount):
        tx = {"sender": sender, "receiver": receiver, "amount": amount}
        self.pending.append(tx)
        return self.last_block["index"] + 1

    def hash_block(self, index, previous_hash):
        data = f"{index}{previous_hash}{time.time()}"
        return hashlib.blake2b(data.encode(), digest_size=32).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
