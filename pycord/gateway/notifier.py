# cython: language_level=3
# Copyright (c) 2022-present Pycord Development
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .shard import Shard

if TYPE_CHECKING:
    from .manager import ShardManager

_log = logging.getLogger(__name__)


class Notifier:
    def __init__(self, manager: ShardManager) -> None:
        self.manager = manager

    async def shard_died(self, shard: Shard) -> None:
        _log.debug(f'Shard {shard.id} died, restarting it')
        shard_id = shard.id
        self.manager.remove_shard(shard)
        del shard

        new_shard = Shard(
            id=shard_id,
            state=self.manager._state,
            session=self.manager.session,
            notifier=self,
        )
        await new_shard.connect(token=self.manager._state.token)
        self.manager.add_shard(new_shard)
