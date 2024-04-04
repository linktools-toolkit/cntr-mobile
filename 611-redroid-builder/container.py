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
import json
import os.path
import subprocess
from typing import Dict

from linktools import Config, utils
from linktools.cli import subcommand, subcommand_argument
from linktools.cli.argparse import KeyValueAction
from linktools.container import BaseContainer
from linktools.decorator import cached_property


class Container(BaseContainer):
    """build android image"""

    @cached_property
    def configs(self):
        return dict(
            REDROID_BUILD_PATH=Config.Prompt(cached=True, type="path"),
        )

    def get_envvars(self) -> Dict[str, str]:
        path = self.get_app_path("configs", "env.json", create_parent=True)
        return json.loads(utils.read_file(path)) \
            if os.path.exists(path) \
            else dict()

    @subcommand("set-env", help="Set redroid build environment")
    @subcommand_argument("envs", action=KeyValueAction, nargs="+", help="environment variables")
    def on_exec_set_env(self, envs: Dict[str, str]):
        path = self.get_app_path("configs", "env.json", create_parent=True)
        utils.write_file(path, json.dumps(envs, indent=2))

    @subcommand("init-repo", help="Initialize redroid repo")
    @subcommand_argument("-u", "--manifest-url", metavar="URL",
                         default="https://github.com/redroid-rockchip/platform_manifests.git",
                         help="manifest repository location")
    @subcommand_argument("-b", "--manifest-branch", metavar="REVISION",
                         default="redroid-12.0.0",
                         help="manifest branch or revision (use HEAD for default)")
    def on_exec_repo_init(self, manifest_url: str, manifest_branch: str):
        self.manager.create_docker_process(
            "exec", "-it", "redroid_builder",
            "repo", "init", "-u", manifest_url, "-b", manifest_branch, "--depth=1", "--git-lfs",
        ).check_call()

    @subcommand("sync-repo", help="Sync redroid repo")
    def on_exec_repo_sync(self):
        self.manager.create_docker_process(
            "exec", "-it", "redroid_builder",
            "repo", "sync", "-c",
        ).check_call()

        self.manager.create_docker_process(
            "exec", "-it", "redroid_builder",
            "repo", "forall", "-g", "lfs", "-c", "git", "lfs", "pull",
        ).check_call()

    @subcommand("build-arm64", help="Build redroid arm64 image")
    def on_exec_build_arm64(self):
        self.manager.create_docker_process(
            "exec", "-it", "redroid_builder",
            "build-arm64.sh",
        ).check_call()

    @subcommand("make-arm64-image", help="Build redroid arm64 image")
    def on_exec_make_arm64_image(self):
        p1 = p2 = None
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

            p1 = self.manager.create_process(
                "sh", "-c", "tar --xattrs -c vendor -C system --exclude=\"./vendor\" . ",
                cwd=path,
                stdout=subprocess.PIPE,
                privilege=True
            )

            p2 = self.manager.create_docker_process(
                "import",
                "-c", "ENTRYPOINT [\"/init\", \"androidboot.hardware=redroid\"]",
                "--platform", "linux/arm64",
                "-", "redroid",
                append_env=dict(DOCKER_DEFAULT_PLATFORM="linux/arm64"),
                stdin=p1.stdout
            )

            p1.wait()
            p2.wait()

        finally:
            if p1:
                utils.ignore_error(p1.kill)
            if p2:
                utils.ignore_error(p2.kill)

            self.manager.create_process(
                "sh", "-c", "umount system vendor",
                cwd=path,
                privilege=True
            ).call()

    @subcommand("fix-permission", help="fix redroid source permission")
    def on_exec_fix_permission(self):
        self.manager.create_docker_process(
            "exec", "-it", "redroid_builder",
            "sudo", "chown", "-R", self.manager.config.get("DOCKER_USER"), "/src/"
        ).check_call()
