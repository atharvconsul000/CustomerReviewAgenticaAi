from __future__ import annotations

import json
from pathlib import Path

try:
    from .ticket_data import generate_support_tickets
except ImportError:
    from ticket_data import generate_support_tickets


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(exist_ok=True)
    tickets = generate_support_tickets()
    output_path = output_dir / "tickets.json"
    output_path.write_text(json.dumps(tickets, indent=2), encoding="utf-8")
    print(f"Wrote {len(tickets)} tickets to {output_path}")


if __name__ == "__main__":
    main()
