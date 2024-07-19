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
import os
import shutil

from linktools import Config
from linktools.cli import subcommand
from linktools.container import BaseContainer
from linktools.decorator import cached_property
from linktools.rich import confirm


class Container(BaseContainer):

    @cached_property
    def configs(self):
        return dict(
            REDROID_IMAGE="iceblacktea/redroid-arm64:12.0.0-240328",
            REDROID_COUNT=Config.Prompt(default=3, type=int, cached=True),
            REDROID_ADB_PORT=Config.Prompt(default=5555, type=int, cached=True),
            REDROID_GPU_MODE=Config.Prompt(default="mali", type=str, choices=["auto", "host", "guest", "mali"], cached=True),
            REDROID_VIRTUAL_WIFI=Config.Confirm(default=True, cached=True),
        )

    @cached_property
    def overlay_files(self):
        result = dict()
        for root, dirs, files in os.walk(self.get_app_path("overlay")):
            root = os.path.abspath(root)
            for name in files:
                path = os.path.join(root, name)
                result[path] = path[len(root):]
        return result

    @subcommand("clean", help="Clean redroid data files")
    def on_exec_clean(self):
        service = self.choose_service()
        name = service.get("container_name")
        path = self.get_app_path("data", name)
        if confirm(f"Clean {name} data files", default=False) is False:
            self.logger.warning(f"Cancel clean {path}")
            return -1
        shutil.rmtree(path, ignore_errors=True)
