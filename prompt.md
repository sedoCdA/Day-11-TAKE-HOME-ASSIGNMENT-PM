# AI-Augmented Task — Retry Decorator with Exponential Backoff

---

## 1. Prompt Used

"Write a Python decorator called @retry(max_attempts=3, delay=1) that
automatically retries a function if it raises an exception, with
exponential backoff."

---

## 2. AI-Generated Output
```python
import time
import functools

def retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (2 ** attempt))
            raise Exception("Max attempts reached")
        return wrapper
    return decorator
```

---

## 3. Testing the AI Code
```python
import random

@retry(max_attempts=3, delay=1)
def unreliable_function():
    if random.random() < 0.5:
        raise ConnectionError("Service unavailable")
    return "Success"

print(unreliable_function())
```

### Test results

| Run | Attempts needed | Result |
|-----|----------------|--------|
| 1   | 2              | Success |
| 2   | 1              | Success |
| 3   | 3              | Success |
| 4   | 3              | Raised Exception |

---

## 4. Critical Evaluation (200 words)

The AI code works for the basic case and correctly implements exponential
backoff using `delay * (2 ** attempt)`. The structure of a decorator
factory returning a decorator returning a wrapper is correct.

However several issues exist. The most obvious is the missing
`functools.wraps(func)` on the wrapper — without it the wrapped
function loses its original `__name__`, `__doc__`, and other metadata,
which breaks introspection and documentation tools.

The final `raise Exception("Max attempts reached")` is too vague. It
discards the original exception entirely, making debugging much harder.
It should re-raise the last caught exception using `raise last_exception`.

The decorator catches all exceptions with bare `except Exception` and
retries everything equally. In production systems some exceptions should
not be retried at all — for example a `ValueError` caused by bad input
will fail every time and retrying wastes time. The decorator should
accept a `retryable_exceptions` parameter.

Finally there is no logging — in a production system every failed
attempt should be logged so engineers can monitor retry patterns.

---

## 5. Improved Version
```python
import time
import logging
import functools

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)

def retry(max_attempts=3, delay=1, retryable_exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    wait = delay * (2 ** (attempt - 1))
                    logging.warning(
                        f"'{func.__name__}' attempt {attempt}/{max_attempts} "
                        f"failed: {e}. Retrying in {wait}s..."
                    )
                    if attempt < max_attempts:
                        time.sleep(wait)
            raise last_exception
        return wrapper
    return decorator


# Test 1 — retries on ConnectionError, succeeds eventually
import random

@retry(max_attempts=4, delay=1, retryable_exceptions=(ConnectionError,))
def unstable_api():
    if random.random() < 0.6:
        raise ConnectionError("Service unavailable")
    return "Response received"

print(unstable_api())

# Test 2 — ValueError is not retried (not in retryable_exceptions)
@retry(max_attempts=3, delay=1, retryable_exceptions=(ConnectionError,))
def bad_input():
    raise ValueError("Wrong input type")

try:
    bad_input()
except ValueError as e:
    print(f"Not retried, caught immediately: {e}")

# Test 3 — exhausts all attempts and re-raises original exception
@retry(max_attempts=2, delay=1)
def always_fails():
    raise TimeoutError("Always times out")

try:
    always_fails()
except TimeoutError as e:
    print(f"All attempts failed: {e}")
```

---

## 6. Improvements Summary

| Issue | AI Code | Improved Version |
|-------|---------|-----------------|
| functools.wraps | Missing | Added — preserves metadata |
| Final exception | Raises generic Exception | Re-raises original last exception |
| Retryable exceptions | Retries everything | Configurable retryable_exceptions |
| Logging | No logging | logging.warning on each failed attempt |
| Backoff on last attempt | Sleeps before giving up | Skips sleep on final attempt |
