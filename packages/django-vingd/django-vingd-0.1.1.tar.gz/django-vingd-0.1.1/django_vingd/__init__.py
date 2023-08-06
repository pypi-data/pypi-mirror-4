from . import consts

from vingd import Vingd

VINGD_CLIENT = Vingd(
    username = consts.VINGD_USR,
    password = consts.VINGD_PWD,
    endpoint = consts.VINGD_BACKEND,
    frontend = consts.VINGD_FRONTEND,
)
