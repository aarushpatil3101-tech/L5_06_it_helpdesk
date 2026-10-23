"""IT helpdesk ticket allocator: raise, assign, annotate, close, save."""
import json
import os
import re
import subprocess  # nosec B404 - needed for ping; called without a shell
from dataclasses import dataclass, field
from datetime import datetime

MIN_URGENCY = 1
MAX_URGENCY = 5
HIGH_PRIORITY = 4

# Secret comes from the environment, never from source control
ADMIN_PASSWORD = os.environ.get("HELPDESK_ADMIN_PASSWORD")
HOSTNAME_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


@dataclass
class TicketStore:
    """Holds all tickets plus the running ticket counter (replaces globals)."""

    tickets: dict = field(default_factory=dict)
    counter: int = 100


STORE = TicketStore()


def parse_urgency(value):
    """Convert user input to an int urgency in 1-5, else raise ValueError."""
    try:
        urgency = int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"urgency must be a whole number, got {value!r}"
        ) from None
    if not MIN_URGENCY <= urgency <= MAX_URGENCY:
        raise ValueError(
            f"urgency must be {MIN_URGENCY}-{MAX_URGENCY}, got {urgency}"
        )
    return urgency


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a ticket, log it to audit_trail (if given) and return its id."""
    priority = parse_urgency(urgency)  # validate before touching any state
    if audit_trail is None:
        audit_trail = []
    STORE.counter += 1
    ticket_id = STORE.counter
    STORE.tickets[ticket_id] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": [],
    }
    audit_trail.append(f"{user} raised #{ticket_id} at {datetime.now()}")
    return ticket_id


def assign_ticket(ticket_id, technician):
    """Assign a technician to an existing ticket."""
    STORE.tickets[ticket_id]["tech"] = technician


def add_note(ticket_id, note):
    """Append a note to a ticket. Return False if the ticket does not exist."""
    try:
        STORE.tickets[ticket_id]["notes"].append(note)
    except KeyError:
        print(f"add_note: no such ticket #{ticket_id}")
        return False
    return True


def close_ticket(ticket_id, password):
    """Delete a ticket if the admin password matches; True on success."""
    if not ADMIN_PASSWORD or password != ADMIN_PASSWORD:
        print("close_ticket: not authorised")
        return False
    if ticket_id not in STORE.tickets:
        print(f"close_ticket: no such ticket #{ticket_id}")
        return False
    del STORE.tickets[ticket_id]
    return True


def unresolved_high_priority():
    """Return ids of unassigned tickets with priority >= HIGH_PRIORITY."""
    return [
        ticket_id
        for ticket_id, ticket in STORE.tickets.items()
        if ticket["priority"] >= HIGH_PRIORITY and ticket["tech"] is None
    ]


def ping_user_machine(hostname):
    """Ping a host once. Raises ValueError for a malformed hostname."""
    if not HOSTNAME_RE.match(hostname):
        raise ValueError(f"invalid hostname: {hostname!r}")
    # argument list + no shell => hostname can never be parsed as a command
    return subprocess.call(["ping", "-c", "1", hostname])  # nosec B603 B607


def save_tickets(file="tickets.json"):
    """Write all tickets to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(STORE.tickets, handle)


def main():
    """Demo run of the helpdesk workflow."""
    first = raise_ticket("anil", "printer", "5")
    raise_ticket("meera", "wifi", "4")
    third = raise_ticket("joe", "vpn", "2")
    assign_ticket(first, "Tech-Kiran")
    add_note(999, "Called user")
    print("Unassigned high priority:", unresolved_high_priority())
    while True:
        level = input("Urgency for new laptop ticket (1-5, Enter=3): ") or "3"
        try:
            raise_ticket("sana", "laptop", level)
            break
        except ValueError as err:
            print("Invalid input:", err)
    close_ticket(third, os.environ.get("HELPDESK_ADMIN_PASSWORD", ""))
    save_tickets()
    print("Open tickets:", list(STORE.tickets.keys()))


if __name__ == "__main__":
    main()
