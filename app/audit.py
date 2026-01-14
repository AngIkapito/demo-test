"""
Simple audit helper for the `audit` logger configured in `trackapsite/settings.py`.

Provide either `audit_logger` for direct logging or `log()` for a small convenience wrapper.
"""

import logging

audit_logger = logging.getLogger('audit')


def log(action: str, user=None, **kwargs) -> None:
    """Log a simple audit entry.

    - `action`: short description of the action
    - `user`: optional user object (email/username or str)
    - `kwargs`: optional key/value pairs to include
    """
    parts = []
    if user is not None:
        try:
            user_repr = getattr(user, 'email', None) or getattr(user, 'username', None) or str(user)
        except Exception:
            user_repr = str(user)
        parts.append(f"user={user_repr}")
    parts.append(f"action={action}")
    if kwargs:
        extras = " ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extras)

    audit_logger.info(" | ".join(parts))
