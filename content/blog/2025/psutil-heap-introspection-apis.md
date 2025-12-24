Title: Detect memory leaks of C extensions with psutil and psleak
Slug: psutil-heap-introspection-apis
Date: 2025-12-23
Tags: psutil, python, c, memory-leak, psleak
Authors: Giampaolo Rodola

Memory leaks in Python are often straightforward to diagnose. Just look at RSS,
track Python object counts, follow reference graphs. But leaks inside **C
extension modules** are another story. Traditional memory metrics such as RSS
and VMS frequently fail to reveal them because Python's memory allocator sits
above the platform's native heap (see
[pymalloc](https://docs.python.org/3/c-api/memory.html#the-pymalloc-allocator)).
If something in an extension calls ``malloc()`` without a corresponding
``free()``, that memory often won't show up where you expect it. You have a
leak, and **you don't know**.

psutil 7.2.0 introduces two new APIs for **C heap introspection**, designed
specifically to catch these kinds of native leaks. They give you a window
directly into the underlying platform allocator (e.g. glibc's malloc), letting
you track how much memory the C layer is actually consuming.

These C functions bypass Python entirely. They don't reflect Python object
memory, arenas, pools, or anything managed by
[pymalloc](https://docs.python.org/3/c-api/memory.html). Instead, they examine
the allocator that C extensions actually use. If your RSS is flat but your C
heap usage climbs, you now have a way to see it.

## Why native heap introspection matters

Many Python projects rely on C extensions: psutil, NumPy, pandas, PIL, lxml,
psycopg, PyTorch, custom in-house modules, etc. And even cPython itself, which
implements many of its standard library modules in C. If any of these
components mishandle memory at the C level, you get a leak that:

- Doesn't show up in Python reference counts ([sys.getrefcount](https://docs.python.org/dev/library/sys.html#sys.getrefcount)).
- Doesn't show up in [tracemalloc module](https://docs.python.org/3/library/tracemalloc.html).
- Doesn't show up in Python's [gc](https://docs.python.org/dev/library/gc.html) stats.
- Often don't show up in RSS, VMS or
  [USS](https://gmpy.dev/blog/2016/real-process-memory-and-environ-in-python)
  due to allocator caching, especially for small objects. This can happen, for
  example, when you forget to `Py_DECREF` a Python object.

psutil's new functions solve this by inspecting platform-native allocator
state, in a manner similar to Valgrind.

## heap_info(): direct allocator statistics

`heap_info()` exposes the following metrics:

- ``heap_used``: total number of bytes currently allocated via ``malloc()``
  (small allocations).
- ``mmap_used``: total number of bytes currently allocated via ``mmap()`` or
  via large ``malloc()`` allocations.
- ``heap_count``: (Windows only) number of private heaps created via
  ``HeapCreate()``.

Example:

```python
>>> import psutil
>>> psutil.heap_info()
pheap(heap_used=5177792, mmap_used=819200)
```

Reference for what contributes to each field:

| Platform       | Allocation type                                                                          | Field affected |
|----------------|------------------------------------------------------------------------------------------|----------------|
| UNIX / Windows | small `malloc()` ≤128 KB without `free()`                                                | `heap_used`    |
| UNIX / Windows | large `malloc()` >128 KB without `free()`, or `mmap()` without `munmap()` (UNIX)         | `mmap_used`    |
| Windows        | `HeapAlloc()` without `HeapFree()`                                                       | `heap_used`    |
| Windows        | `VirtualAlloc()` without `VirtualFree()`                                                 | `mmap_used`    |
| Windows        | `HeapCreate()` without `HeapDestroy()`                                                   | `heap_count`   |

## heap_trim(): returning unused heap memory

``heap_trim()`` provides a cross-platform way to request that the underlying
allocator free any unused memory it's holding in the heap (typically small
`malloc()` allocations).

In practice, modern allocators rarely comply, so this is not a general-purpose
memory-reduction tool and won't meaningfully shrink RSS in real programs. Its
primary value is in **leak detection tools**.

Calling ``heap_trim()`` before taking measurements helps reduce allocator
noise, giving you a cleaner baseline so that changes in `heap_used` come from
the code you're testing, not from internal allocator caching or fragmentation.

## Real-world use: finding a C extension leak

The workflow is simple:

1. Take a baseline snapshot of the heap.
1. Call the C extension hundreds of times.
1. Take another snapshot.
1. Compare.

```python
import psutil

psutil.heap_trim()  # reduce noise

before = psutil.heap_info()
for _ in range(200):
    my_cext_function()
after = psutil.heap_info()

print("delta heap_used =", after.heap_used - before.heap_used)
print("delta mmap_used =", after.mmap_used - before.mmap_used)
```

If `heap_used` or `mmap_used`  values increase consistently, you've found a
native leak.

To reduce false positives, repeat the test multiple times, increasing the
number of calls on each retry. This approach helps distinguish real leaks from
random noise or transient allocations.

## A new tool: psleak

The strategy described above is exactly what I implemented in a new PyPI
package, which I called **[psleak](https://github.com/giampaolo/psleak)**. It
runs the target function repeatedly, trims the allocator before each run, and
tracks differences across retries. Memory that grows consistently after several
runs is flagged as a leak.

A minimal test suite looks like this:

```python
  from psleak import MemoryLeakTestCase

  class TestLeaks(MemoryLeakTestCase):
      def test_fun(self):
          self.execute(some_c_function)
```

If the function leaks memory, the test will fail with a descriptive exception:

```
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
```

Psleak is now part of the psutil test suite, to make sure that the C code does
not leak memory. All psutil APIs are tested (see
[test_memleaks.py](https://github.com/giampaolo/psutil/blob/1a946cfe738045cecf031222cd5078da21946af4/tests/test_memleaks.py)),
making it a de facto **regression-testing tool**.

It's worth noting that without inspecting heap metrics, missing calls such as
`Py_CLEAR` and `Py_DECREF` often go unnoticed, because they don't affect RSS,
VMS, and USS. Something I confirmed from experimenting by commenting them
out. Monitoring the heap is therefore essential to reliably detect memory
leaks in Python C extensions.

## Under the hood

For those interested in seeing how I did this in terms of code:

- **[Linux](https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/linux/heap.c)**:
  uses glibc's
  [mallinfo2()](https://man7.org/linux/man-pages/man3/mallinfo.3.html) to report
  ``uordblks`` (heap allocations) and ``hblkhd`` (mmap-backed blocks).
- **[Windows](https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/windows/heap.c)**:
  enumerates heaps and aggregates ``HeapAlloc`` / ``VirtualAlloc`` usage.
- **[macOS](https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/osx/heap.c)**:
  uses malloc zone statistics.
- **[BSD](https://github.com/giampaolo/psutil/blob/d40164f1/psutil/arch/bsd/heap.c)**:
  uses jemalloc's arena and stats interfaces.

## Summary

psutil 7.2.0 fills a long-standing observability gap: native-level memory leaks
in C extensions are now visible directly from Python. You now have a simple
method to **test C extensions for leaks**. This turns psutil into not just a
monitoring library, but a practical debugging tool for Python projects that
rely on native C extension modules.

To make leak detection practical, I created
[psleak](https://github.com/giampaolo/psleak), a test-regression framework
designed to integrate into Python unit tests.

## References

- **[psleak](https://github.com/giampaolo/psleak)**, the new memory leak
  testing framework.
- **[psutil PR #2692](https://github.com/giampaolo/psutil/pull/2692/)**, the
  implementation.
- **[psutil issue #1275](https://github.com/giampaolo/psutil/issues/1275)**,
  the original proposal from 8 years earlier.

## Discussion

- [Reddit](https://www.reddit.com/r/Python/comments/1puqgfg/detect_memory_leaks_of_c_extensions_with_psutil/)
- [Hacker News](https://news.ycombinator.com/item?id=46376608)
