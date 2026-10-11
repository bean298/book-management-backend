from sqlalchemy import select
from sqlalchemy.sql import func

from app.models.user_model import User
from app.orm.repository import Repository


class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(session, User)

    # Def to get user by email
    async def get_user_by_email(self, user_email: str) -> User:
        stmt = select(User).where(User.email == user_email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Def to count new users by period
    async def count_new_users_by_period(self, period: str = "day") -> list[dict]:
        # DATE_TRUNC('day', created_at) AS period
        # DATE_TRUNC: Truncate a timestamp to the beginning of a specified time unit.
        # Example: DATE_TRUNC('day', '2026-10-11 14:30:00') → '2026-10-11 00:00:00'
        # DATE_TRUNC('week', '2026-10-11 14:30:00')  → '2026-10-05 00:00:00'
        # DATE_TRUNC('month', '2026-10-11 14:30:00') → '2026-10-01 00:00:00'
        # DATE_TRUNC('year', '2026-10-11 14:30:00')  → '2026-01-01 00:00:00'
        col = func.date_trunc(period, User.created_at).label("period")

        # SELECT
        # DATE_TRUNC('day', created_at) AS period,
        # COUNT(id) as count,
        # JSON_AGG(
        #     JSON_BUILD_OBJECT(
        #         'id', users.id,
        #         'name', users.name,
        #         'email', users.email
        #     )
        # ) AS auth.users
        # FROM User GROUP BY DATE_TRUNC('day', created_at) ORDER BY period;
        stmt = (
            select(
                col,
                func.count(User.id).label("count"),
                func.json_agg(
                    func.json_build_object(
                        "id",
                        User.id,
                        "name",
                        User.name,
                        "email",
                        User.email,
                    )
                ).label("users"),
            )
            .group_by(col)
            .order_by(col)
        )
        rows = (await self.session.execute(stmt)).all()

        return [
            {
                "period": r.period,
                "count": r.count,
                "users": r.users,
            }
            for r in rows
        ]
