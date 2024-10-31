#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author  : Hu Ji
@file    : deploy.py 
@time    : 2023/05/21
@site    :  
@software: PyCharm 

              ,----------------,              ,---------,
         ,-----------------------,          ,"        ,"|
       ,"                      ,"|        ,"        ,"  |
      +-----------------------+  |      ,"        ,"    |
      |  .-----------------.  |  |     +---------+      |
      |  |                 |  |  |     | -==----'|      |
      |  | $ sudo rm -rf / |  |  |     |         |      |
      |  |                 |  |  |/----|`---=    |      |
      |  |                 |  |  |   ,/|==== ooo |      ;
      |  |                 |  |  |  // |(((( [33]|    ,"
      |  `-----------------'  |," .;'| |((((     |  ,"
      +-----------------------+  ;;  | |         |,"
         /_)______________(_/  //'   | +---------+
    ___________________________/___  `,
   /  oooooooooooooooo  .o.  oooo /,   `,"-----------
  / ==ooooooooooooooo==.o.  ooo= //   ,``--{)B     ,"
 /_==__==========__==_ooo__ooo=_/'   /___________,"
"""
import random
import string

from linktools import Config
from linktools.decorator import cached_property
from linktools_cntr import BaseContainer, ExposeLink


class Container(BaseContainer):

    @property
    def dependencies(self) -> [str]:
        return ["nginx"]

    @cached_property
    def configs(self):
        return dict(
            SONIC_DOMAIN=self.get_nginx_domain("sonic"),
            SONIC_EXPOSE_PORT=Config.Alias(type=int, default=0),

            ##################
            # Service Config #
            ##################
            SONIC_TAG="v2.6.3",
            SONIC_SERVER_HOST=Config.Alias("SONIC_DOMAIN"),  # 必须填前端的域名
            SONIC_SERVER_PORT=Config.Alias("HTTP_PORT", type=int),  # 必须填前端的端口
            SONIC_EUREKA_USERNAME="sonic",
            SONIC_EUREKA_PASSWORD="sonic",
            SONIC_EUREKA_PORT=9090,

            ##################
            # Mysql Config   #
            ##################
            SONIC_MYSQL_HOST="sonic-server-mysql",
            SONIC_MYSQL_PORT="3306",
            SONIC_MYSQL_ROOT_PASSWORD="sonic_root_password",
            SONIC_MYSQL_USERNAME="sonic_username",
            SONIC_MYSQL_PASSWORD="sonic_password",
            SONIC_MYSQL_DATABASE="sonic",

            ################
            # User Config  #
            ################
            SONIC_SECRET_KEY=Config.Prompt(
                default="".join(random.sample(string.ascii_letters + string.digits, 12)),
                cached=True),
            SONIC_EXPIRE_DAY=14,
            SONIC_PERMISSION_ENABLE="true",
            SONIC_PERMISSION_SUPER_ADMIN="sonic",
            SONIC_REGISTER_ENABLE="true",
            SONIC_NORMAL_USER_ENABLE="true",
            SONIC_LDAP_USER_ENABLE="false",
            SONIC_LDAP_USER_ID="cn",
            SONIC_LDAP_BASE_DN="ou=users",
            SONIC_LDAP_BASE="ou=system",
            SONIC_LDAP_USERNAME="uid=admin,ou=system",
            SONIC_LDAP_PASSWORD="sonic",
            SONIC_LDAP_URL="ldap://192.168.1.1:10389"
        )

    @cached_property
    def exposes(self) -> [ExposeLink]:
        return [
            self.expose_public(
                "Sonic", "cellphone", "Sonic云真机",
                self.load_nginx_url("SONIC_DOMAIN", https=False)),
            self.expose_container(
                "Sonic", "cellphone", "Sonic云真机",
                self.load_port_url("SONIC_EXPOSE_PORT", https=False)),
        ]

    def on_starting(self):
        self.write_nginx_conf(
            self.get_config("SONIC_DOMAIN"),
            self.get_path("nginx.conf"),
            https=False,
        )
