# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
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


import asyncio
import gc
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Literal


class TaskDescheduler:
    def __init__(self) -> None:
        self.active_tasks: list[asyncio.Future[Any]] = []
        gc.callbacks.append(self.__collect_finished_tasks)

    def __getitem__(self, item: asyncio.Future[Any]) -> None:
        self.active_tasks.append(item)

    def __collect_finished_tasks(
        self, phase: Literal["start", "stop"], info: dict[str, int]
    ) -> None:
        del info

        if phase == "stop":
            return

        active_tasks = self.active_tasks.copy()

        for task in active_tasks:
            if task.done():
                self.active_tasks.remove(task)

        del active_tasks


Tasks = TaskDescheduler()


@asynccontextmanager
async def tasks() -> AsyncGenerator[TaskDescheduler, Any]:
    yield Tasks
