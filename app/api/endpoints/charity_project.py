from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_name_duplicate,
                                check_project_before_deletion,
                                check_project_before_update,
                                check_project_exists, check_project_is_closed)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment import investment_process

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_new_charity_project(
    project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Создание проекта."""

    await check_name_duplicate(project.name, session)
    new_project = await charity_project_crud.create(project, session)
    await investment_process(session)
    await session.refresh(new_project)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """Список всех проектов.
    Для любого посетителя сайта."""

    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def partially_update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Невозможно редактировать закрытый проект.
    Нельзя установить новую требуемую сумму меньше уже внесённой."""

    project = await check_project_exists(project_id, session)
    project = await check_project_is_closed(project_id, session)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    if not obj_in.full_amount:
        await charity_project_crud.update(project, obj_in, session)
        return project

    await check_project_before_update(
        obj_in.full_amount, project.invested_amount, session
    )
    project = await charity_project_crud.update(project, obj_in, session)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Невозможно удалить закрытый проект.
    Можно удалять только проекты, в которые не было внесено средств."""

    project = await check_project_exists(project_id, session)
    await check_project_before_deletion(project, session)
    project = await charity_project_crud.remove(project, session)
    return project
