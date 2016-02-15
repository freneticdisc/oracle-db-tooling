################################################################################
# install_db.py
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
import os
import grp
import sys
import stat
import getopt
import shutil
import socket
import zipfile
import datetime
import platform
import tempfile
import subprocess

def main(options, arguments):
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()

    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        with open(os.path.join(base_dir, "metadata.json"), "r") as mfile:
            install_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    scratch = options.get("--tmp_loc", tempfile.gettempdir())
    installer_loc = options.get("-l", base_dir)
    ora_base = options.get("-o")
    ora_home = options.get("-h", os.path.join(ora_base, "product", "12.1.0", "dbhome_1"))
    hostname = options.get("--hostname", socket.gethostname())
    rsp_file = options.get("--rsp_file", "")
    inst_grp = options.get("--inst_group", grp.getgrgid(os.getgid()).gr_name)
    dba_grp = options.get("--dba_group", inst_grp)
    oper_grp = options.get("--oper_group", inst_grp)
    bkdba_grp = options.get("--backupdba_group", inst_grp)
    dgdba_grp = options.get("--dgdba_group", inst_grp)
    kmdba_grp = options.get("--kmdba_group", inst_grp)
    inventory_loc = options.get("--inventory_loc", os.path.join(ora_base, "oraInventory"))

    tmp_file = tempfile.mktemp()
    with open(tmp_file, "w") as bfile:
        bfile.write("inventory_loc=%s\n" %inventory_loc)
        bfile.write("inst_group=%s\n" %inst_grp)
        bfile.flush()

    filelist = []
    for file in install_metadata.get("files"):
        installer = zipfile.ZipFile(os.path.join(installer_loc, file), allowZip64=True)
        filelist.extend(installer.namelist())
        for zipinfo in installer.infolist():
            extractedfile = installer.extract(zipinfo.filename, scratch)
            os.chmod(extractedfile, zipinfo.external_attr >> 16 & 0xFFF)
        installer.close()

    executable = "setup.exe" if platform.system() == "Windows" else "runInstaller"
    command = [os.path.join(scratch, "database", executable)]
    command.extend(["-silent", "-noconfig", "-ignoreSysPrereqs", "-ignorePrereq"])
    command.extend(["-force", "-waitforcompletion", "-invPtrLoc", tmp_file])

    if os.path.isfile(rsp_file):
        command.extend(["-responseFile", rsp_file])
    else:
        command.append("oracle.install.option=INSTALL_DB_SWONLY")
        command.append("SECURITY_UPDATES_VIA_MYORACLESUPPORT=false")
        command.append("DECLINE_SECURITY_UPDATES=true")
        command.append("ORACLE_HOSTNAME=%s" %hostname)
        command.append("ORACLE_HOME_NAME=OraDBHome%s" \
                       %datetime.datetime.now().strftime("%m%d%Y%H%M%S"))
        command.append("ORACLE_BASE=%s" %ora_base)
        command.append("ORACLE_HOME=%s" %ora_home)
        command.append("oracle.install.db.DBA_GROUP=%s" %dba_grp)
        command.append("oracle.install.db.OPER_GROUP=%s" %oper_grp)
        command.append("oracle.install.db.BACKUPDBA_GROUP=%s" %bkdba_grp)
        command.append("oracle.install.db.DGDBA_GROUP=%s" %dgdba_grp)
        command.append("oracle.install.db.KMDBA_GROUP=%s" %kmdba_grp)

    if not os.path.exists(ora_base): os.makedirs(ora_base, 0750)
    install_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = install_process.communicate()
    print out, err

    # Fix an issue on UNIX based systems
    if not os.path.isfile(os.path.join(ora_home, "lib", "libjavavm12.a")):
        shutil.copy(os.path.join(ora_home, "javavm", "jdk", "jdk6", "lib", "libjavavm12.a"),
                    os.path.join(ora_home, "lib"))

    while len(filelist) > 0:
        fsobj = filelist.pop()
        if os.path.isdir(os.path.join(scratch, fsobj)):
            os.rmdir(os.path.join(scratch, fsobj))
        else:
            os.remove(os.path.join(scratch, fsobj))

    os.unlink(tmp_file)

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?l:o:h:", ["rsp_file=",
                                        "tmp_loc=", "hostname=", "inst_group=",
                                        "dba_group=", "oper_group=", "backupdba_group=",
                                        "dgdba_group=", "kmdba_group=", "inventory_loc="])
    options = dict(options)

    if "-?" in options:
        print "Usage: python %s %s %s %s %s %s %s" %("install_db.py",
        "[-?] -l installers_location -o oracle_base [-h oracle_home]",
        "[--hostname host_name] [--rsp_file install_response_file]",
        "[--tmp_loc tmp_location] [--inst_group install_group]",
        "[--dba_group dba_group] [--oper_group oper_group]",
        "[--backupdba_group backupdba_group] [--dgdba_group dgdba_group]",
        "[--kmdba_group kmdba_group] [--inventory_loc inventory_loc]")
        sys.exit(0)

    main(options, arguments)
