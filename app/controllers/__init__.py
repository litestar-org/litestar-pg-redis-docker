from starlite import Router

from . import authors

__all__ = ["router"]

router = Router(path="/", route_handlers=[authors.router])
