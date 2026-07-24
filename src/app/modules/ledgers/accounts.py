from app.modules.ledgers.models import AccountModel


async def get_active_account_by_id(account_id: int) -> AccountModel | None:
    from sqlalchemy import select

    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.is_active,
            )
        )
        return result.scalar_one_or_none()


async def get_active_accounts_by_user_id(user_id: int) -> list[AccountModel]:
    from sqlalchemy import select

    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        return result.scalars().all()


async def create_account_for_user(user_id: int, account_name: str) -> AccountModel:
    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        account = AccountModel(user_id=user_id, name=account_name)
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account


async def update_active_account_name(
    account_id: int, user_id: int, account_name: str
) -> AccountModel | None:
    from sqlalchemy import select

    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        account.name = account_name
        await session.commit()
        await session.refresh(account)
        return account
