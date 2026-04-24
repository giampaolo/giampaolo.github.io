Detecting memory leaks in C extensions with psutil and psleak
#############################################################

:date: 2025-12-23
:tags: psutil, psleak, python, c, memory
:slug: psutil-heap-introspection-apis

Memory leaks in Python are usually straightforward to diagnose. Just look at RSS, track Python object counts, follow reference graphs, etc. But leaks inside C extension modules are another story. Traditional memory metrics such as RSS and VMS fail to reveal them because Python's memory allocator (`pymalloc <https://docs.python.org/3/c-api/memory.html#the-pymalloc-allocator>`__) sits above the platform's native heap. If something in an extension calls ``malloc()`` without a corresponding ``free()``, that memory often won't show up in RSS / VMS. You have a leak, and you don't know.

psutil 7.2.0 introduces two new APIs for **C heap introspection**, designed specifically to catch these kinds of native leaks. They give you a window directly into the underlying platform allocator (e.g. glibc's malloc), letting you track how much memory the C layer actually allocates. If your RSS is flat but your C heap usage climbs, you now have a way to see it.

Why native heap introspection matters
-------------------------------------

Many Python projects rely on C extensions: psutil, NumPy, pandas, PIL, lxml, psycopg, PyTorch, custom in-house modules, etc. And even CPython itself, which implements many of its standard library modules in C. If any of these components mishandle memory at the C level, you get a leak that doesn't show up in:

- Python reference counts (``sys.getrefcount``).
- ``tracemalloc`` module.
- Python's ``gc`` stats.
- RSS, VMS or USS due to allocator caching, especially for small objects. This can happen, for example, when you forget to ``Py_DECREF`` a Python object.

psutil's new functions let you query the allocator (e.g. glibc) directly, returning low-level metrics from the platform's native heap.

heap_info(): direct allocator statistics
----------------------------------------

``psutil.heap_info()`` exposes the following metrics:

- ``heap_used``: total number of bytes currently allocated via ``malloc()`` (small allocations).
- ``mmap_used``: total number of bytes currently allocated via ``mmap()`` or via large ``malloc()`` allocations.
- ``heap_count``: (Windows only) number of private heaps created via ``HeapCreate()``.

Example:

.. code-block:: pycon

   >>> import psutil
   >>> psutil.heap_info()
   pheap(heap_used=5177792, mmap_used=819200)

Reference for what contributes to each field:

.. list-table::
   :header-rows: 1

   * - Platform
     - Allocation type
     - Field affected
   * - UNIX / Windows
     - small ``malloc()`` ≤128 KB without ``free()``
     - ``heap_used``
   * - UNIX / Windows
     - large ``malloc()`` >128 KB without ``free()``, or ``mmap()`` without ``munmap()`` (UNIX)
     - ``mmap_used``
   * - Windows
     - ``HeapAlloc()`` without ``HeapFree()``
     - ``heap_used``
   * - Windows
     - ``VirtualAlloc()`` without ``VirtualFree()``
     - ``mmap_used``
   * - Windows
     - ``HeapCreate()`` without ``HeapDestroy()``
     - ``heap_count``

heap_trim(): returning unused heap memory
-----------------------------------------

``psutil.heap_trim()`` provides a cross-platform way to request that the underlying allocator free any unused memory it's holding in the heap (typically small ``malloc()`` allocations).

In practice, modern allocators rarely comply, so this is not a general-purpose memory-reduction tool and won't meaningfully shrink RSS in real programs. Its primary value is in leak detection tools. Calling ``psutil.heap_trim()`` before taking measurements helps reduce allocator noise, giving you a cleaner baseline so that changes in ``heap_used`` come from the code you're testing, not from internal allocator caching or fragmentation.

Real-world use: finding a C extension leak
------------------------------------------

The workflow is simple:

1. Take a baseline snapshot of the heap.
2. Call the C extension hundreds of times.
3. Take another snapshot.
4. Compare.

.. code-block:: python

   import psutil

   psutil.heap_trim()  # reduce noise

   before = psutil.heap_info()
   for _ in range(200):
       my_cext_function()
   after = psutil.heap_info()

   print("delta heap_used =", after.heap_used - before.heap_used)
   print("delta mmap_used =", after.mmap_used - before.mmap_used)

If ``heap_used`` or ``mmap_used`` values increase consistently, you've found a native leak.

To reduce false positives, repeat the test multiple times, increasing the number of calls on each retry. This approach helps distinguish real leaks from random noise or transient allocations.

A new tool: psleak
------------------

The strategy described above is exactly what I implemented in a new PyPI package, which I called `psleak <https://github.com/giampaolo/psleak>`__. It runs the target function repeatedly, trims the allocator before each run, and tracks differences across retries. Memory that grows consistently after several runs is flagged as a leak.

A minimal test suite looks like this:

.. code-block:: python

     from psleak import MemoryLeakTestCase

     class TestLeaks(MemoryLeakTestCase):
         def test_fun(self):
             self.execute(some_c_function)

If the function leaks memory, the test will fail with a descriptive exception:

.. code-block:: none

   psleak.MemoryLeakError: memory kept increasing after 10 runs
   Run # 1: heap=+388160  | uss=+356352  | rss=+327680  | (calls= 200, avg/call=+1940)
   Run # 2: heap=+584848  | uss=+614400  | rss=+491520  | (calls= 300, avg/call=+1949)
   Run # 3: heap=+778320  | uss=+782336  | rss=+819200  | (calls= 400, avg/call=+1945)
   Run # 4: heap=+970512  | uss=+1032192 | rss=+1146880 | (calls= 500, avg/call=+1941)
   Run # 5: heap=+1169024 | uss=+1171456 | rss=+1146880 | (calls= 600, avg/call=+1948)
   Run # 6: heap=+1357360 | uss=+1413120 | rss=+1310720 | (calls= 700, avg/call=+1939)
   Run # 7: heap=+1552336 | uss=+1634304 | rss=+1638400 | (calls= 800, avg/call=+1940)
   Run # 8: heap=+1752032 | uss=+1781760 | rss=+1802240 | (calls= 900, avg/call=+1946)
   Run # 9: heap=+1945056 | uss=+2031616 | rss=+2129920 | (calls=1000, avg/call=+1945)
   Run #10: heap=+2140624 | uss=+2179072 | rss=+2293760 | (calls=1100, avg/call=+1946)

Psleak is now part of the psutil test suite. All psutil APIs are tested (see `test_memleaks.py <https://github.com/giampaolo/psutil/blob/1a946cfe738045cecf031222cd5078da21946af4/tests/test_memleaks.py>`__), making it a de facto **regression-testing tool**.

It's worth noting that without inspecting heap metrics, missing calls in the C code such as ``Py_CLEAR`` and ``Py_DECREF`` often go unnoticed, because they don't affect RSS, VMS, and USS. I confirmed this by commenting them out. Monitoring the heap is therefore essential to reliably detect memory leaks in Python C extensions.

Under the hood
--------------

For those interested in seeing how I did this in terms of code:

- `Linux <https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/linux/heap.c>`__: uses glibc's `mallinfo2() <https://man7.org/linux/man-pages/man3/mallinfo.3.html>`__ to report ``uordblks`` (heap allocations) and ``hblkhd`` (mmap-backed blocks).
- `Windows <https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/windows/heap.c>`__: enumerates heaps and aggregates ``HeapAlloc`` / ``VirtualAlloc`` usage.
- `macOS <https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/osx/heap.c>`__: uses malloc zone statistics.
- `BSD <https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/bsd/heap.c>`__: uses jemalloc's arena and stats interfaces.

References
----------

- `psleak <https://github.com/giampaolo/psleak>`__, the new memory leak testing framework.
- `PR-2692 <https://github.com/giampaolo/psutil/pull/2692>`__, the implementation.
- `#1275 <https://github.com/giampaolo/psutil/issues/1275>`__, the original proposal from 8 years earlier.

Discussion
----------

- `Reddit <https://www.reddit.com/r/Python/comments/1puqgfg/detect_memory_leaks_of_c_extensions_with_psutil/>`__
- `Hacker News <https://news.ycombinator.com/item?id=46376608>`__
- `Medium <https://medium.com/@g.rodola/detect-memory-leaks-of-c-extensions-with-psutil-and-psleak-a0521ba6315f>`__
