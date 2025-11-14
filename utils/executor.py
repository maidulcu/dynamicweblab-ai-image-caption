"""Thread pool executor for blocking AI operations."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

# Global thread pool executor for CPU-bound/blocking AI operations
_executor: ThreadPoolExecutor = None


def get_executor(max_workers: int = 4) -> ThreadPoolExecutor:
    """Get or create the global thread pool executor.

    Args:
        max_workers: Maximum number of worker threads

    Returns:
        ThreadPoolExecutor instance
    """
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=max_workers)
    return _executor


async def run_in_executor(func: Callable, *args, **kwargs) -> Any:
    """Run a blocking function in the thread pool executor.

    Args:
        func: Blocking function to run
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function (will be passed via lambda)

    Returns:
        Result from the function

    Example:
        result = await run_in_executor(analyzer.analyze_image, str(file_path))
    """
    executor = get_executor()
    loop = asyncio.get_event_loop()

    if kwargs:
        # If we have kwargs, wrap in a lambda
        return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))
    else:
        # If only args, can call directly
        return await loop.run_in_executor(executor, func, *args)


def shutdown_executor():
    """Shutdown the executor gracefully."""
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=True)
        _executor = None
