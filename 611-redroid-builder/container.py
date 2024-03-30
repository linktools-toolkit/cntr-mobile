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
   /  oooooooooooooooo  .o.  oooo /,   \,"-----------
  / ==ooooooooooooooo==.o.  ooo= //   ,`\--{)B     ,"
 /_==__==========__==_ooo__ooo=_/'   /___________,"
"""
import os.path

from linktools import Config
from linktools.cli import subcommand
from linktools.container import BaseContainer
from linktools.decorator import cached_property


class Container(BaseContainer):
    """build android image"""

    @cached_property
    def configs(self):
        return dict(
            REDROID_BUILD_USER=Config.Lazy(lambda cfg: ''.join(filter(str.isalpha, cfg.get("DOCKER_USER")))),
            REDROID_BUILD_PATH=Config.Prompt(cached=True, type="path"),
        )

    @subcommand("make-arm64-image", help="Build redroid arm64 image")
    def on_exec_build(self):
        path = os.path.join(
            self.manager.config.get("REDROID_BUILD_PATH", type="path"),
            "out", "target", "product", "redroid_arm64"
        )

        try:
            self.manager.create_process(
                "sh", "-c", "mount system.img system -o ro",
                cwd=path,
                privilege=True
            ).check_call()

            self.manager.create_process(
                "sh", "-c", "mount vendor.img vendor -o ro",
                cwd=path,
                privilege=True
            ).check_call()

            self.manager.create_process(
                "sh", "-c",
                "tar --xattrs -c vendor -C system --exclude=\"./vendor\" . | "
                "DOCKER_DEFAULT_PLATFORM=linux/arm64 "
                "docker import -c 'ENTRYPOINT [\"/init\", \"androidboot.hardware=redroid\"]' - redroid",
                cwd=path,
                privilege=True
            ).check_call()

        finally:
            self.manager.create_process(
                "sh", "-c", "umount system vendor",
                cwd=path,
                privilege=True
            ).call()
