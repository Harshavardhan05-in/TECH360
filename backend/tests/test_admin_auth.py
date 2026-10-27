import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.auth_service import reset_anonymous_view_store
from backend.scripts.setup_admin import provision_admin


@pytest.mark.asyncio
async def test_admin_provisioning_and_rbac():
    reset_anonymous_view_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Provision admin user
        admin_email = "harshavardhan.ushakola14@gmail.com"
        admin_pass = "96325481"
        ok = await provision_admin(admin_email, admin_pass, full_name="Harshavardhan Ushakola", role="admin")
        assert ok is True

        # 2. Authenticate as admin
        admin_login = await client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": admin_pass
        })
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        assert admin_login.json()["user"]["role"] == "admin"

        # 3. Access admin stats endpoint
        stats_resp = await client.get("/api/v1/admin/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert stats_resp.status_code == 200
        data = stats_resp.json()
        assert "total_published_events" in data
        assert "total_sources" in data
        assert data["total_sources"] >= 1

        # 4. Register or login a standard non-admin user
        user_email = f"standard.dev.{int(__import__('time').time())}@example.com"
        user_reg = await client.post("/api/v1/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Standard Dev"
        })
        assert user_reg.status_code == 200
        user_token = user_reg.json()["access_token"]
        assert user_reg.json()["user"]["role"] == "user"

        # 5. Non-admin user attempts to access admin stats -> 403 Forbidden
        user_stats = await client.get("/api/v1/admin/stats", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert user_stats.status_code == 403
        assert "privileges" in user_stats.json()["detail"].lower()

        # 6. Anonymous attempt with clear client -> 401 Unauthorized
        client.cookies.clear()
        anon_stats = await client.get("/api/v1/admin/stats")
        assert anon_stats.status_code == 401
