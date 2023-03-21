from litestar import Router

from app.domain.authors import Author
from app.domain.countries import Country

from . import authors, countries

__all__ = ["create_router"]


def create_router() -> Router:
    return Router(
        path="/v1",
        route_handlers=[authors.AuthorController, countries.CountryController],
        signature_namespace={"Author": Author, "Country": Country},
    )
