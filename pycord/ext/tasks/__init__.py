"""
pycord.ext.tasks
~~~~~~~~~~~~~~~~
Pycord utility extension for an extended asyncio task system.

:copyright: 2021-present Pycord
:license: MIT
"""

import asyncio
import inspect
import logging
import time
import traceback
from datetime import timedelta
from typing import Callable, Generic, TypeVar

from ...custom_types import AsyncFunc

T = TypeVar("T")

_log = logging.getLogger(__name__)


class PycordTask(Generic[T]):
    """Class for handling a repeatable task

    Attributes
    ----------
    interval: :class:`datetime.timedelta`
        The interval in which this task repeats in.
    interval_secs: :class:`float`
        The number of seconds this tasks repeats.
    loop_started_at: :class:`float`
        The `time.time` result of when the loop started.
    running: :class:`bool`
        Whether the loop is currently running.
    failed: :class:`bool`
        Whether the loop has failed.
    count: :class:`int`
        The amount of times the loop should repeat.
    """

    def __init__(
        self, callback: T, interval: timedelta, count: int | None = None
    ) -> None:
        self._callback = callback
        self.interval = interval
        self.interval_secs = interval.total_seconds()
        self.loop_started_at: float | None = None
        self.running: bool = False
        self.failed: bool = False
        self._running_loop_task = None
        self._on_error_coro = None
        self._pre_loop_coro = None
        self._post_loop_coro = None
        self.count = count

        self.__doc__ = self._callback.__doc__

    def error(self, coro: AsyncFunc) -> None:
        """A decorator for handling exceptions raised by the callback"""

        if not inspect.iscoroutinefunction(coro):
            raise TypeError(
                "PycordTask.error handling only accepts coroutine functions"
            )

        self._on_error_coro = coro

    def pre_loop(self, coro: AsyncFunc) -> None:
        """A decorator for running a function before a task.
        Could be useful to setup some sort of state.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError("PycordTask.pre_loop only accepts coroutine functions")

        self._pre_loop_coro = coro

    def post_loop(self, coro: AsyncFunc) -> None:
        """A decorator for running a function after a task.
        Could be useful for state cleanup.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError("PycordTask.post_loop only accepts coroutine functions")

        self._post_loop_coro = coro

    def change_interval(
        self,
        *,
        microseconds: int = 0,
        milliseconds: int = 0,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        weeks: int = 0,
    ) -> None:
        """Change the interval in which this task runs in

        .. warning::
            Do not run this too often as it could make tasks run more inconsistent.
        """

        self.interval = timedelta(
            microseconds=microseconds,
            milliseconds=milliseconds,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks,
        )
        self.interval_secs = self.interval.total_seconds()

    def start(self) -> None:
        """Start the loop. Should be done *after* the asyncio loop or your bot is started."""

        _log.debug(f"[{self._callback}] starting loop")
        self._running_loop_task = asyncio.create_task(self._loop())
        self.loop_started_at = int(time.time())

    async def _loop(self) -> None:
        self.running = True
        await asyncio.sleep(self.interval_secs)
        _log.debug(f"[{self._callback}] starting new loop")
        if self._pre_loop_coro:
            _log.debug(f"[{self._callback}] doing pre-loop setup")
            await self._pre_loop_coro()

        try:
            _log.debug(f"[{self._callback}] calling function")
            await self._callback()
        except Exception as exc:
            _log.debug(
                f"[{self._callback}] function finished with error:\n\n{traceback.format_exc()}"
            )
            if self._on_error_coro:
                _log.debug(f"[{self._callback}] error handled")
                await self._on_error_coro(exc)
            else:
                _log.debug(f"[{self._callback}] loop failed")
                self.running = False
                self._running_loop_task = None
                self.failed = True
                raise exc
        else:
            _log.debug(f"[{self._callback}] function finished without any errors")

        if self._post_loop_coro:
            _log.debug(f"[{self._callback}] doing post-loop cleanup")
            await self._post_loop_coro()

        _log.debug(f"[{self._callback}] re-running loop")

        if self.count:
            self.count -= 1
            if self.count == 0:
                return

        self._running_loop_task = asyncio.create_task(self._loop())

    def cancel(self) -> bool:
        """Cancel the current loop
        
        Returns
        -------
        True:
            The loop is running and was canceled successfully.
        False:
            The loop isn't running and wasn't canceled.
        """

        _log.debug(f"[{self._callback}] canceling loop")
        if not self.running and self._running_loop_task is None:
            return False

        self._running_loop_task.cancel()
        self._running_loop_task = None
        self.running = False
        return True

    def restart(self) -> None:
        """Restart the current loop"""

        _log.debug(f"[{self._callback}] prematurely restarting loop")
        self.cancel()
        self.start()

    def __call__(self, *args, **kwargs):
        return self._callback(*args, **kwargs)


def loop(
    *,
    microseconds: int = 0,
    milliseconds: int = 0,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
    weeks: int = 0,
    count: int | None = None,
) -> Callable[[T], PycordTask[T]]:
    """A decorator to create a task from a callback.
    
    Takes the same parameters as timedelta with an added `count` field
    to determine how much times the task should repeat.
    """

    if count is not None and count <= 0:
        raise ValueError("Count cannot be negative or 0")

    interval = timedelta(
        microseconds=microseconds,
        milliseconds=milliseconds,
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        days=days,
        weeks=weeks,
    )

    def decorator(coro: T) -> PycordTask[T]:
        return PycordTask[coro](coro, interval, count)

    return decorator
