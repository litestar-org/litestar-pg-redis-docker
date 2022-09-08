from typing import TYPE_CHECKING

from starlite import Controller as BaseController
from starlite import delete, get, put

from app.core.handlers import create_pagination_dependencies, resolve_id_guards

from .service import Service

if TYPE_CHECKING:
    from .schema import Provider


class Controller(BaseController):
    tags = ["Providers"]
    member_path = "{provider_id:uuid}"

    @get(dependencies=create_pagination_dependencies())
    async def list_providers(self, service: Service) -> list["Provider"]:
        """A paginated list of all registered providers."""
        return await service.list()

    @get(path=member_path)
    async def get_provider(self, service: Service) -> "Provider":
        """Individual provider detail view."""
        return await service.show()

    @put(path=member_path, guards=resolve_id_guards("provider_id"))
    async def register_provider(self, data: "Provider", service: Service) -> "Provider":
        """Register, or update a provider."""
        return await service.upsert(data=data)

    @delete(path=member_path)
    async def delete_provider(self, service: Service) -> None:
        """Delete the provider and return its representation."""
        await service.destroy()