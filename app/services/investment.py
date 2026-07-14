from datetime import datetime
from typing import List

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def invest_available_funds(
    projects: List[CharityProject],
    donations: List[Donation]
) -> None:
    """
    Распределяет средства между открытыми проектами и пожертвованиями.
    Модифицирует переданные объекты (изменяет invested_amount,
    устанавливает fully_invested и close_date).
    """
    projects.sort(key=lambda p: p.create_date)
    donations.sort(key=lambda d: d.create_date)

    project_idx = 0
    donation_idx = 0
    while project_idx < len(projects) and donation_idx < len(donations):
        project = projects[project_idx]
        donation = donations[donation_idx]

        project_remain = project.full_amount - project.invested_amount
        donation_remain = donation.full_amount - donation.invested_amount

        if project_remain <= 0:
            project_idx += 1
            continue
        if donation_remain <= 0:
            donation_idx += 1
            continue

        invest_amount = min(project_remain, donation_remain)
        project.invested_amount += invest_amount
        donation.invested_amount += invest_amount

        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            project_idx += 1

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            donation_idx += 1
