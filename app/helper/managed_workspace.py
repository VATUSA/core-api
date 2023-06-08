from app import constants
from app.database.legacy import models as legacy
from app.database.lightning import models as lightning


def should_controller_have_account(controller: legacy.Controller) -> bool:
    if controller.flag_homecontroller is False:
        return False
    if controller.rating < constants.rating.OBS:
        return False
    roles = [r.role for r in controller.roles]
    return True in [role in roles for role in constants.workspace.account_roles]


async def configure_for_controller(controller: legacy.Controller):
    account: lightning.ManagedWorkspaceAccount = \
        await lightning.ManagedWorkspaceAccount.query().filter(cid=controller.cid).get_or_none()

    prospect_username = f'{controller.fname}.{controller.lname}'.lower()
    username_conflict_count = await lightning.ManagedWorkspaceAccount.query().filter(username=prospect_username).count()
    if username_conflict_count > 0:
        prospect_username = None
    elif not all([x.isalpha() or x == '.' for x in prospect_username]):
        prospect_username = None
        # TODO: Log and notify
    if account is None and should_controller_have_account(controller):
        # Create account record
        account = lightning.ManagedWorkspaceAccount(
            cid=controller.cid,
            username=prospect_username,
            can_self_serve=prospect_username is not None
        )
        await account.save()
    elif account is not None and not should_controller_have_account(controller):
        # TODO: Disable account
        # TODO: Send notification
        return

    # Add Facility Staff aliases
    await account.load()
    if controller.is_facility_staff(controller.facility):
        await add_facility_alias(account, controller.facility, prospect_username)
    for visit in controller.visits:
        if controller.is_facility_staff(visit.facility):
            await add_facility_alias(account, visit.facility, prospect_username)
    for role in controller.roles:
        if role.role in constants.roles.facility_unique_roles:
            await add_staff_position_alias(account, role.facility, role.role)

    # TODO: Configure Group Membership


async def add_staff_position_alias(account: lightning.ManagedWorkspaceAccount, facility: str, position: str):
    zhq_alias = f'{facility}-{position}'.lower()
    await add_facility_alias(account, 'ZHQ', zhq_alias)
    await add_facility_alias(account, facility, position)


async def add_facility_alias(account: lightning.ManagedWorkspaceAccount, facility: str, alias: str):
    if account is None:
        raise Exception("Tried to add facility alias but user does not have an account!")

    domains: list[lightning.ManagedWorkspaceDomain] = await lightning.ManagedWorkspaceDomain.all_by_facility(facility)
    for domain in domains:
        if any([a for a in account.aliases if a.domain == domain and a.alias == alias]):
            continue
        alias = lightning.ManagedWorkspaceAccountAlias(
            account=account,
            domain=domain,
            alias=alias,
        )
        await alias.save()
