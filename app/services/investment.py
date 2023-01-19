from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


def close_object(obj: Union[CharityProject, Donation]) -> None:
    obj.fully_invested = True
    obj.invested_amount = obj.full_amount
    obj.close_date = datetime.now()


async def investment_process(session: AsyncSession) -> None:
    donation_to_invest = await donation_crud.get_open(session)
    open_project = await charity_project_crud.get_open(session)

    if not open_project or not donation_to_invest:
        return

    for donation in donation_to_invest:
        for project in open_project:

            left_to_close = project.full_amount - project.invested_amount
            left_to_donate = donation.full_amount - donation.invested_amount

            if left_to_close == left_to_donate:
                close_object(donation)
                close_object(project)

            if left_to_close < left_to_donate:
                to_add = left_to_donate - left_to_close
                donation.invested_amount += to_add
                close_object(project)

            if left_to_close > left_to_donate:
                project.invested_amount += left_to_donate
                close_object(donation)

    await session.commit()
