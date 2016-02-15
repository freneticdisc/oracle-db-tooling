################################################################################
# main.py
#
# Copyright (C) 2016 Justin Paul <justinpaulthekkan@gmail.com>
#
# @author: Justin Paul
#
# This program is free software: you can redistribute it and/or modify
# it as long as you retain the name of the original author and under
# the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
import sys
import getopt
import install_db
import patch_db
import create_listener
import create_instance
import db_control

options, arguments = getopt.getopt(sys.argv[1:], "?ipcl:o:h:n:w:", ["sid=",
                                    "hostname=", "rsp_file=", "tmp_loc=",
                                    "inst_group=", "dba_group=", "oper_group=",
                                    "backupdba_group=", "dgdba_group=",
                                    "kmdba_group=", "inventory_loc=",
                                    "ocmrsp_file=", "sys_password=",
                                    "system_password=", "delete",
                                    "start", "stop"])
options = dict(options)

if "-?" in options:
    print "Usage: python %s %s %s %s %s %s %s %s %s" %("main.py",
    "[-?ipc] -l installers_patches_location -o oracle_base [-h oracle_home]",
    "[-n global-database-name] [-w password_file] [--sid sid]",
    "[--hostname host_name] [--rsp_file response_file] [--tmp_loc tmp_location]",
    "[--inst_group install_group] [--dba_group dba_group] [--oper_group oper_group]",
    "[--backupdba_group backupdba_group] [--dgdba_group dgdba_group]",
    "[--kmdba_group kmdba_group] [--inventory_loc inventory_loc]",
    "[--ocmrsp_file ocm_response_file] [--sys_password sys_password]",
    "[--system_password system_password] [--delete] [--start | --stop]")
    sys.exit(0)

if "--delete" in options:
    suboptions = {}
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    if "-n" in options: suboptions["-n"] = options.get("-n")
    if "-w" in options: suboptions["-w"] = options.get("-w")
    if "--sys_password" in options: suboptions["--sys_password"] = options.get("--sys_password")
    if "--system_password" in options: suboptions["--system_password"] = options.get("--system_password")
    if "--sid" in options: suboptions["--sid"] = options.get("--sid")
    suboptions["--delete"] = options.get("--delete")
    if "--rsp_file" in options: suboptions["--rsp_file"] = options.get("--rsp_file")
    create_instance.main(suboptions, arguments)

    suboptions = {}
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    suboptions["--delete"] = options.get("--delete")
    if "--rsp_file" in options: suboptions["--rsp_file"] = options.get("--rsp_file")
    create_listener.main(suboptions, arguments)
    sys.exit(0)

if "-i" in options:
    suboptions = {}
    if "-l" in options: suboptions["-l"] = options.get("-l")
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    if "--hostname" in options: suboptions["--hostname"] = options.get("--hostname")
    if "--rsp_file" in options: suboptions["--rsp_file"] = options.get("--rsp_file")
    if "--tmp_loc" in options: suboptions["--tmp_loc"] = options.get("--tmp_loc")
    if "--inst_group" in options: suboptions["--inst_group"] = options.get("--inst_group")
    if "--dba_group" in options: suboptions["--dba_group"] = options.get("--dba_group")
    if "--oper_group" in options: suboptions["--oper_group"] = options.get("--oper_group")
    if "--backupdba_group" in options: suboptions["--backupdba_group"] = options.get("--backupdba_group")
    if "--dgdba_group" in options: suboptions["--dgdba_group"] = options.get("--dgdba_group")
    if "--kmdba_group" in options: suboptions["--kmdba_group"] = options.get("--kmdba_group")
    if "--inventory_loc" in options: suboptions["--inventory_loc"] = options.get("--inventory_loc")
    install_db.main(suboptions, arguments)

if "-p" in options:
    suboptions = {}
    if "-l" in options: suboptions["-l"] = options.get("-l")
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    if "--ocmrsp_file" in options: suboptions["--ocmrsp_file"] = options.get("--ocmrsp_file")
    patch_db.main(suboptions, arguments)

if "-c" in options:
    suboptions = {}
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    if "--rsp_file" in options: suboptions["--rsp_file"] = options.get("--rsp_file")
    create_listener.main(suboptions, arguments)

    suboptions = {}
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    if "-n" in options: suboptions["-n"] = options.get("-n")
    if "-w" in options: suboptions["-w"] = options.get("-w")
    if "--sys_password" in options: suboptions["--sys_password"] = options.get("--sys_password")
    if "--system_password" in options: suboptions["--system_password"] = options.get("--system_password")
    if "--sid" in options: suboptions["--sid"] = options.get("--sid")
    if "--rsp_file" in options: suboptions["--rsp_file"] = options.get("--rsp_file")
    create_instance.main(suboptions, arguments)

if "--start" in options or "--stop" in options:
    suboptions = {}
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-h" in options: suboptions["-h"] = options.get("-h")
    if "-w" in options: suboptions["-w"] = options.get("-w")
    if "--sys_password" in options: suboptions["--sys_password"] = options.get("--sys_password")
    if "--start" in options: suboptions["--start"] = options.get("--start")
    if "--stop" in options: suboptions["--stop"] = options.get("--stop")
    db_control.main(suboptions, arguments)
