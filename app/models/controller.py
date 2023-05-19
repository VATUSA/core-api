from __future__ import annotations

import pydantic


class Controller(pydantic.BaseModel):
    cid: int
    display_name: str
    email: str
    facility: str
    rating: int
    rating_short: str
    rating_long: str
    discord_id: str
    in_division: bool
    receive_broadcast_emails: bool
    prevent_staff_assignment: bool
    is_promotion_eligible: bool
    is_transfer_eligible: bool
    is_visit_eligible: bool
    is_controller_interest: bool
    roles: list[ControllerRole]
    visits: list[str]


class ControllerRole(pydantic.BaseModel):
    role: str
    facility: str


Controller.update_forward_refs()

