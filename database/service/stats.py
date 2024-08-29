from utils.logging import logger

from ..models.users import Users

from peewee import fn, Case


def get_users_stats():
    return Users.select().count()
