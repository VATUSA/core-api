import asyncio
import uuid
from app import auth
from app.database.lightning import connection, models as lightning

SEPARATOR = "***"


async def main():
    if not connection.database.is_connected:
        await connection.database.connect()

    print(SEPARATOR)
    print('Generating a new API token')
    print(SEPARATOR)

    name = input("Token Name: ")

    print(SEPARATOR)
    print("The following prompts concern the global permissions for this token. ")
    print("These permissions grant considerable access to all data and should be carefully considered before granting.")
    read_all_in = input("Read All Data? (y/n): ")
    write_all_in = input("Write All Data? (y/n): ")
    print(SEPARATOR)

    token_value = uuid.uuid4()

    token = lightning.CoreAPIToken(
        name=name,
        token=str(token_value),
        enabled=True,
        can_read_all=read_all_in.lower() == 'y',
        can_write_all=write_all_in.lower() == 'y',
    )
    await token.save()

    assign_objects_in = input("Do you want to assign permissions for individual objects? (y/n): ")
    if assign_objects_in.lower() == 'y':
        objects = iter(auth.PermissionObject)

        for obj in objects:
            print(f'Permissions for {obj.value}:')
            permission_in = input('\tOptions: 0 - None, 1 - Read Only, 2 - Write Only, 3 - Read and Write')
            while permission_in not in ['0', '1', '2', '3']:
                print("Invalid Input")
                permission_in = input('\tOptions: 0 - None, 1 - Read Only, 2 - Write Only, 3 - Read and Write')
            if permission_in in ['1', '2', '3']:
                permission = lightning.CoreAPITokenPermission(
                    api_token=token,
                    object=obj.value,
                    can_read=permission_in in ['1', '3'],
                    can_write=permission_in in ['2', '3']
                )
                await permission.save()

    print(SEPARATOR)
    print("API Token Created")
    print(f"\tName: {token.name}")
    print(f"\tToken: {token.token}")
    print(SEPARATOR)

loop = asyncio.get_event_loop()
coroutine = main()
loop.run_until_complete(coroutine)
