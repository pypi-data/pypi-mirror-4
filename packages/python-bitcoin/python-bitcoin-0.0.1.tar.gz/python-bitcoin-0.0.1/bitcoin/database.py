#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

from python_patterns.utils.decorators import Property

from .core import Block, Merkle, Transaction

__all__ = [
    'Chain',
    'Engine',
]

# ===----------------------------------------------------------------------===

class Engine(object):
    def __init__(self, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)
        self.chains_create()

    def chains_create(self):
        self.chains = set()
    chains_clear = chains_create

    def Chain(self, *args, **kwargs):
        chain = Chain(self, *args, **kwargs)
        self.chains.add(chain)
        return chain

# ===----------------------------------------------------------------------===

SENTINAL = object()

from threading import RLock

from .defaults import CHAIN_PARAMETERS
from .serialize import deserialize_list
from .utils import StringIO, target_from_compact

# For each block, (height, work)
# blocks_by_height :: [set([Block])]

class Chain(object):
    def __init__(self, engine, parameters=None, listeners=None,
                 *args, **kwargs):
        if parameters is None:
            parameters = CHAIN_PARAMETERS['org.bitcoin']
        super(Chain, self).__init__(*args, **kwargs)
        self.parameters = parameters or ()
        self.listeners = listeners or ()
        self._mutex = RLock()

        # blocks :: dict(hashBlock = Block)
        # merkles :: dict(hashMerkleRoot = Merkle)
        # transactions :: dict(hashTransaction = Transaction)
        self.blocks_create()
        self.merkles_create()
        self.transactions_create()

        # orphans :: set([])
        # dependencies :: dict(hash = set())
        self.orphans_create()
        self.dependencies_create()

        # set([Terminus])
        self.termini_create()

        input_ = StringIO(parameters.genesis)
        block = Block.deserialize(self, input_)
        vtx = list(deserialize_list(input_, Transaction.deserialize))
        for tx in vtx:
            self.put(tx)
        self.put(Merkle(children=(tx.hash for tx in vtx)))
        self.put(block)

    def blocks_create(self):
        self.blocks = {}
    def merkles_create(self):
        self.merkles = {}
    def transactions_create(self):
        self.transactions = {}
    def orphans_create(self):
        self.orphans = set()
    def dependencies_create(self):
        self.dependencies = set()

    def termini_create(self):
        self.termini = set()
    termini_clear = termini_create

    def put(self, obj):
        self._mutex.acquire()
        if obj.hash in self.dependencies:
            self._mutex.release(); return
        dependencies = set()
        if isinstance(obj, Block):
            if obj.hashPrevBlock not in self.blocks:
                dependencies.add(obj.hashPrevBlock)
            if obj.hashMerkleRoot not in self.merkles:
                dependencies.add(obj.hashMerkleRoot)
            if dependencies:
                self.dependencies[obj.hash] = dependencies
                self.orphans.add(obj)
            else:
                self.blocks.add(obj)
        elif isinstance(obj, Merkle):
            self._mutex.release()
            raise NotImplementedError
        elif isinstance(obj, Transaction):
            self._mutex.release()
            raise NotImplementedError

    def get(self, hash, value=SENTINAL):
        if hasattr(hash, 'hash'):
            hash = hash.hash
        if hash in self.blocks:
            return self.blocks[hash]
        if hash in self.merkles:
            return self.merkles[hash]
        if hash in self.transactions:
            return self.transactions[hash]
        if value is not SENTINAL:
            return value
        raise IndexError(
            u"no object found for hash %(repr)s" % repr(hash))

    @Property
    def tip():
        def fget(self):
            if not self.blocks:
                return None
            if len(self.blocks) == 1:
                return self.blocks.values()[0]
            raise NotImplementedError
        return locals()

# ===----------------------------------------------------------------------===

# For each transaction, (blkhash, txhash, spentmask, [(blkhash, txhash)])

class Terminus(object):
    def __init__(self, asset, tip=None, frozen=False, *args, **kwargs):
        if not isinstance(tip, numbers.Integral) and hasattr(tip, 'hash'):
            tip = tip.hash
        if not isinstance(tip, numbers.Integral) and tip is not None:
            raise ValueError(u"tip must be a Block object or its hash, or None")
        super(Terminus, self).__init__(*args, **kwargs)
        self.engine = asset.engine
        self.asset = asset

        self.tip = tip
        self.frozen = frozen

        self.height = 0L
        self.work = 0L
        self.aggregate_work = 0L
        # [Block]
        self.blocks = []
        # set([UnspentOutput])
        self.unspent_outputs = set()
        # dict(zip(Script, set([UnspentOutput])))
        self.script_balances = dict()
        # set([Transaction])
        self.memory_pool = set()

    def connect(self, block):
        pass

#
# End of File
#
