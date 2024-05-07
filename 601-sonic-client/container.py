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

from linktools import Config, utils
from linktools.container import BaseContainer
from linktools.decorator import cached_property


class Container(BaseContainer):

    @cached_property
    def configs(self):
        return dict(
            SONIC_TAG="v2.6.3",
            SONIC_SERVER_HOST=Config.Prompt(default="10.10.10.1", cached=True),
            SONIC_SERVER_PORT=Config.Prompt(default=4000, cached=True, type=int),
            SONIC_AGENT_HOST=Config.Prompt(default=utils.get_lan_ip()),
            SONIC_AGENT_PORT=Config.Prompt(default=7777, cached=True, type=int),
            SONIC_AGENT_KEY=Config.Prompt(cached=True),
            WDA_BUNDLE_ID=Config.Prompt(default="com.facebook.WebDriverAgentRunner1mosec", cached=True),
        )
