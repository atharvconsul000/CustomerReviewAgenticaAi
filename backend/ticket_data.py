from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TicketSeed:
    category: str
    title: str
    phrases: tuple[str, ...]


TICKET_SEEDS: tuple[TicketSeed, ...] = (
    TicketSeed(
        "Billing",
        "Billing and invoice issue",
        (
            "charged twice after upgrading my plan",
            "invoice total does not match the checkout price",
            "refund has not appeared on my card",
            "coupon code was accepted but not applied",
            "subscription renewed after I cancelled",
        ),
    ),
    TicketSeed(
        "Login",
        "Login and account access issue",
        (
            "cannot sign in even after resetting my password",
            "two factor authentication code never arrives",
            "account is locked after one failed login attempt",
            "single sign on redirects back to the login page",
            "password reset link says it has expired immediately",
        ),
    ),
    TicketSeed(
        "Performance",
        "Slow dashboard or app performance",
        (
            "dashboard takes more than a minute to load",
            "reports freeze when filtering by date range",
            "mobile app crashes when opening analytics",
            "search results are delayed during business hours",
            "export gets stuck at ninety nine percent",
        ),
    ),
    TicketSeed(
        "Feature Request",
        "Product feature request",
        (
            "need bulk editing for customer tags",
            "please add custom fields to the export",
            "want a dark mode setting for agents",
            "need Slack notifications for urgent tickets",
            "please support saved filters for queues",
        ),
    ),
    TicketSeed(
        "Data Sync",
        "Integration and sync issue",
        (
            "Salesforce contacts are not syncing overnight",
            "Shopify orders import without customer emails",
            "webhook retries are creating duplicate records",
            "CSV upload drops rows with special characters",
            "API sync stopped after rotating the token",
        ),
    ),
)


def generate_support_tickets(count: int = 120) -> list[dict[str, str]]:
    """Generate deterministic demo tickets with enough variation for clustering."""
    tickets: list[dict[str, str]] = []
    severity_cycle = ("low", "medium", "high", "urgent")
    channels = ("email", "chat", "phone", "portal")

    names = ["Radhia", "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Parker", "Sam", "Jamie"]

    for idx in range(count):
        seed = TICKET_SEEDS[idx % len(TICKET_SEEDS)]
        phrase = seed.phrases[(idx // len(TICKET_SEEDS)) % len(seed.phrases)]
        severity = severity_cycle[idx % len(severity_cycle)]
        channel = channels[(idx // 3) % len(channels)]
        customer_name = names[idx % len(names)]
        text = (
            f"{customer_name} contacted support by {channel}. "
            f"They reported that they {phrase}. "
            f"The issue severity is {severity}. "
            f"Please investigate the {seed.category.lower()} workflow and follow up."
        )
        tickets.append(
            {
                "id": f"TKT-{idx + 1:04d}",
                "category": seed.category,
                "title": seed.title,
                "text": text,
                "severity": severity,
                "channel": channel,
            }
        )

    return tickets
