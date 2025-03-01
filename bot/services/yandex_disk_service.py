import asyncio


async def is_user_in_reference_table(fullname):
    firstname, middlename, lastname = fullname.split(" ")
    return True