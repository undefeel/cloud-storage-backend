import inspect
from collections.abc import Callable
from typing import Any, TypeVar, get_type_hints

from fastapi import APIRouter, Depends
from pydantic.typing import is_classvar
from starlette.routing import Route, WebSocketRoute

T = TypeVar('T')

CBV_CLASS_KEY = '__cbv_class__'


def cbv(router: APIRouter) -> Callable[[type[T]], type[T]]:

    def decorator(cls: type[T]) -> type[T]:
        return _cbv(router, cls)

    return decorator


def _cbv(router: APIRouter, cls: type[T]) -> type[T]:
    _init_cbv(cls)
    cbv_router = APIRouter()
    function_members = inspect.getmembers(cls, inspect.isfunction)
    function_set = {func for _, func in function_members}
    cbv_routes = [
        route
        for route in router.routes
        if isinstance(route, (Route, WebSocketRoute)) and route.endpoint in function_set
    ]
    for route in cbv_routes:
        router.routes.remove(route)
        _update_cbv_route_endpoint_signature(cls, route)
        cbv_router.routes.append(route)

    router.include_router(cbv_router)
    return cls


def _init_cbv(cls: type[Any]) -> None:
    if getattr(cls, CBV_CLASS_KEY, False):
        return
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[1:]
    new_parameters = [
        x for x in old_parameters if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]
    dependency_names: list[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        parametr_kwargs = {'default': getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(
                name=name, kind=inspect.Parameter.KEYWORD_ONLY, annotation=hint, **parametr_kwargs)
        )
    new_signature = old_signature.replace(parameters=new_parameters)

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, *args, **kwargs)
        old_init(self, *args, **kwargs)

    setattr(cls, '__signature__', new_signature)
    setattr(cls, '__init__', new_init)
    setattr(cls, CBV_CLASS_KEY, True)


def _update_cbv_route_endpoint_signature(cls: type[Any], route: Route | WebSocketRoute) -> None:
    old_endpoints = route.endpoint
    old_signature = inspect.signature(old_endpoints)
    old_parameters: list[inspect.Parameter] = list(
        old_signature.parameters.values())
    old_first_parametr = old_parameters[0]
    new_first_parametr = old_first_parametr.replace(default=Depends(cls))
    new_parameters = [
        parametr.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parametr in old_parameters[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, '__signature__', new_signature)
