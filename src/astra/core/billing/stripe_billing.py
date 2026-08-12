"""Stripe Checkout integration with demo fallback when keys are not configured."""

import json
import os
from typing import Optional

PORTAL_BASE = os.environ.get("ASTRA_PORTAL_URL", "http://localhost:8503")

PRICE_ENV_KEYS = {
    "campus": "STRIPE_PRICE_CAMPUS",
    "startup": "STRIPE_PRICE_STARTUP",
}


def stripe_configured() -> bool:
    secret = os.environ.get("STRIPE_SECRET_KEY", "")
    return bool(secret and secret.startswith("sk_"))


def price_configured(tier_id: str) -> bool:
    env_key = PRICE_ENV_KEYS.get(tier_id)
    return bool(env_key and os.environ.get(env_key))


def checkout_available(tier_id: str) -> bool:
    return stripe_configured() and price_configured(tier_id)


def create_checkout_session(
    tier_id: str,
    customer_email: str = "",
    success_url: str = "",
    cancel_url: str = "",
) -> Optional[dict]:
    if not checkout_available(tier_id):
        return None

    try:
        import stripe
    except ImportError:
        return None

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    price_id = os.environ.get(PRICE_ENV_KEYS[tier_id])

    success = success_url or f"{PORTAL_BASE}/?checkout=success&tier={tier_id}"
    cancel = cancel_url or f"{PORTAL_BASE}/?checkout=cancel"

    metadata = {"tier_id": tier_id, "product": "astra_command_os"}

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success + "&session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel,
        customer_email=customer_email or None,
        metadata=metadata,
        subscription_data={"metadata": metadata},
    )

    return {"url": session.url, "session_id": session.id}


def verify_webhook(payload: bytes, signature: str) -> Optional[dict]:
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        return None

    try:
        import stripe
    except ImportError:
        return None

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    try:
        event = stripe.Webhook.construct_event(payload, signature, secret)
    except Exception:
        return None

    return event


def tier_from_checkout_event(event: dict) -> Optional[str]:
    event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        tier = obj.get("metadata", {}).get("tier_id")
        if tier:
            return tier

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        tier = obj.get("metadata", {}).get("tier_id")
        if tier:
            return tier

    return None


def billing_status() -> dict:
    return {
        "stripe_configured": stripe_configured(),
        "campus_checkout": checkout_available("campus"),
        "startup_checkout": checkout_available("startup"),
        "portal_url": PORTAL_BASE,
        "mode": "live" if stripe_configured() else "demo",
    }
