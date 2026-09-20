"""OAuth2 client setup — Google OAuth2 using authlib."""

from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from customer_analytics.app.config import settings

# OAuth instance — singleton for the app
oauth = OAuth()

# Register Google OAuth2 client
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
