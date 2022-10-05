"""This `@endpoint` decorator pattern comes from.

[api-client](https://github.com/MikeWooster/api-client/blob/master/apiclient/decorates.py) and the
following license applies to that original code:

    Copyright (c) 2018 The Python Packaging Authority

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import inspect
from typing import Any


def endpoint(cls_: Any = None, base_url: Any = None) -> Any:
    """Decorator for automatically constructing urls from a base and defined
    resources.

    ```python-repl
    >>> @endpoint(base_url="https://somewhere.com")
    ... class Endpoints:
    ...     path = "/path"
    ...
    >>> assert Endpoints.path == "https://somewhere.com/path"

    ```
    """

    def wrap(cls: Any) -> Any:
        return _process_class(cls, base_url)

    if cls_ is None:
        # Decorator is called as @endpoint with parens.
        return wrap
    # Decorator is called as @endpoint without parens.
    return wrap(cls_)


def _process_class(cls: Any, base_url: Any) -> Any:
    if base_url is None:
        raise RuntimeError("A decorated endpoint must define a base_url as @endpoint(base_url='https://foo.com').")
    base_url = base_url.rstrip("/")

    for name, value in inspect.getmembers(cls):
        if name.startswith("_") or inspect.ismethod(value) or inspect.isfunction(value):
            # Ignore any private or class attributes.
            continue
        new_value = str(value).lstrip("/")
        resource = f"{base_url}/{new_value}"
        setattr(cls, name, resource)
    return cls
