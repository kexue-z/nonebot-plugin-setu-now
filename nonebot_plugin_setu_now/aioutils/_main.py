import functools
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

import anyio
from anyio._core._eventloop import get_asynclib, threadlocals
from anyio.abc import TaskGroup as _TaskGroup

T_Retval = TypeVar("T_Retval")
T_ParamSpec = ParamSpec("T_ParamSpec")
T = TypeVar("T")


class PendingType:
    def __repr__(self) -> str:
        return "AsyncerPending"


Pending = PendingType()


class PendingValueException(Exception):
    pass


class SoonValue(Generic[T]):
    def __init__(self) -> None:
        self._stored_value: Union[T, PendingType] = Pending

    @property
    def value(self) -> T:
        if isinstance(self._stored_value, PendingType):
            raise PendingValueException(
                "The return value of this task is still pending!"
            )
        return self._stored_value

    @property
    def ready(self) -> bool:
        return not isinstance(self._stored_value, PendingType)


class TaskGroup(_TaskGroup):
    def soonify(
        self, async_function: Callable[T_ParamSpec, Awaitable[T]], name: object = None
    ) -> Callable[T_ParamSpec, SoonValue[T]]:
        @functools.wraps(async_function)
        def wrapper(
            *args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs
        ) -> SoonValue[T]:
            partial_f = functools.partial(async_function, *args, **kwargs)
            soon_value: SoonValue[T] = SoonValue()

            @functools.wraps(partial_f)
            async def value_wrapper() -> None:
                value = await partial_f()
                soon_value._stored_value = value

            self.start_soon(value_wrapper, name=name)
            return soon_value

        return wrapper

    async def __aenter__(self) -> "TaskGroup":  # pragma: nocover
        """Enter the task group context and allow starting new tasks."""
        return await super().__aenter__()  # type: ignore


def create_task_group() -> "TaskGroup":
    LibTaskGroup = get_asynclib().TaskGroup

    class ExtendedTaskGroup(LibTaskGroup, TaskGroup):  # type: ignore
        pass

    return ExtendedTaskGroup()


def runnify(
    async_function: Callable[T_ParamSpec, Coroutine[Any, Any, T_Retval]],
    backend: str = "asyncio",
    backend_options: Optional[Dict[str, Any]] = None,
) -> Callable[T_ParamSpec, T_Retval]:
    @functools.wraps(async_function)
    def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> T_Retval:
        partial_f = functools.partial(async_function, *args, **kwargs)

        return anyio.run(partial_f, backend=backend, backend_options=backend_options)

    return wrapper


def syncify(
    async_function: Callable[T_ParamSpec, Coroutine[Any, Any, T_Retval]],
    raise_sync_error: bool = True,
) -> Callable[T_ParamSpec, T_Retval]:
    @functools.wraps(async_function)
    def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> T_Retval:
        current_async_module = getattr(threadlocals, "current_async_module", None)
        partial_f = functools.partial(async_function, *args, **kwargs)
        if current_async_module is None and raise_sync_error is False:
            return anyio.run(partial_f)
        return anyio.from_thread.run(partial_f)

    return wrapper


def asyncify(
    function: Callable[T_ParamSpec, T_Retval],
    *,
    cancellable: bool = False,
    limiter: Optional[anyio.CapacityLimiter] = None
) -> Callable[T_ParamSpec, Awaitable[T_Retval]]:
    async def wrapper(
        *args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs
    ) -> T_Retval:
        partial_f = functools.partial(function, *args, **kwargs)
        return await anyio.to_thread.run_sync(
            partial_f, cancellable=cancellable, limiter=limiter
        )

    return wrapper
