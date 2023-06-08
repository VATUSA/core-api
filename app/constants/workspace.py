from . import roles

vatusa_staff_alias_map = {
    f'US{i}': f'vatusa{i}' for i in range(1, 10)
}

account_roles = [
    roles.AIR_TRAFFIC_MANAGER,
    roles.DEPUTY_AIR_TRAFFIC_MANAGER,
    roles.TRAINING_ADMINISTRATOR,
    roles.EVENT_COORDINATOR,
    roles.FACILITY_ENGINEER,
    roles.WEBMASTER,
    roles.DICE_TEAM,
] + roles.vatusa_staff_roles
