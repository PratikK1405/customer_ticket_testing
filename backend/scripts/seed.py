import asyncio
from sqlalchemy import select
from backend.app.database import AsyncSessionLocal
from backend.app.core.supabase_client import supabase_admin
from backend.app.models.department import Department
from backend.app.models.category import Category
from backend.app.models.sla_policy import SLAPolicy
from backend.app.models.user import User
from backend.app.models.enums import TicketPriority, UserRole

DEPARTMENTS = ["IT Support", "Billing", "Sales", "General"]
CATEGORIES = [
    ("Technical Issue", "Bugs, login problems, outages"),
    ("Billing Issue", "Payments, invoices, refunds"),
    ("Feature Request", "New feature suggestions"),
    ("General Inquiry", "Anything else"),
]
SLA_POLICIES = [
    (TicketPriority.low, 480, 4320),
    (TicketPriority.medium, 240, 1440),
    (TicketPriority.high, 60, 480),
    (TicketPriority.urgent, 15, 120),
]

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Passw0rd!"


async def seed():
    async with AsyncSessionLocal() as db:
        # Departments
        for name in DEPARTMENTS:
            exists = await db.execute(select(Department).where(Department.name == name))
            if not exists.scalar_one_or_none():
                db.add(Department(name=name))

        # Categories
        for name, desc in CATEGORIES:
            exists = await db.execute(select(Category).where(Category.name == name))
            if not exists.scalar_one_or_none():
                db.add(Category(name=name, description=desc))

        # SLA Policies
        for priority, resp, resol in SLA_POLICIES:
            exists = await db.execute(select(SLAPolicy).where(SLAPolicy.priority == priority))
            if not exists.scalar_one_or_none():
                db.add(SLAPolicy(priority=priority, response_minutes=resp, resolution_minutes=resol))

        await db.commit()
        print("Departments, categories, and SLA policies seeded.")

        # Admin user — create in Supabase Auth (service role bypasses email confirm) then mirror to public.users
        existing_admin = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
        if not existing_admin.scalar_one_or_none():
            auth_res = supabase_admin.auth.admin.create_user({
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "email_confirm": True,
            })
            db.add(User(
                id=auth_res.user.id,
                email=auth_res.user.email,
                password_hash="MANAGED_BY_SUPABASE_AUTH",
                role=UserRole.admin,
            ))
            await db.commit()
            print(f"Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            print("Admin user already exists, skipping.")


if __name__ == "__main__":
    asyncio.run(seed())