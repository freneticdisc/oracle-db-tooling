################################################################################
# create_instance.py
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
import sys
import getopt
import subprocess

def main(options, arguments):
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()
    
    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        with open(os.path.join(base_dir, "metadata.json"), "r") as mfile:
            dbca_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    ora_base = options.get("-o")
    ora_home = options.get("-h", os.path.join(ora_base, "product", "12.1.0", "dbhome_1"))
    gdb_name = options.get("-n")
    pwd_file = options.get("-w", "")
    db_sid = options.get("--sid")
    sys_pass = options.get("--sys_password", dbca_metadata["instance"].get("sys-password"))
    system_pass = options.get("--system_password", dbca_metadata["instance"].get("system-password"))
    rsp_file = options.get("--rsp_file", "")
    delete_db = True if "--delete" in options else False

    dbc_input = "%s\n%s\n" %(sys_pass, system_pass)
    if os.path.isfile(pwd_file):
        with open(pwd_file, "r") as bfile:
            dbc_input = bfile.read()

    command = [os.path.join(ora_home, "bin", "dbca"), "-silent"]

    if not delete_db:
        if os.path.isfile(os.path.join(ora_home, "network", "admin", "tnsnames.ora")):
            return

        command.append("-createDatabase")
        if os.path.isfile(rsp_file):
            if gdb_name: command.extend(["-gdbName", gdb_name])
            if db_sid: command.extend(["-sid", db_sid])
            command.extend(["-responseFile", rsp_file])
        else:
            if not gdb_name:
                gdb_name = dbca_metadata["instance"].get("global-database-name")
            if not db_sid:
                db_sid = gdb_name.split(".")[0]
            command.extend(["-gdbName", gdb_name, "-sid", db_sid, "-ignorePreReqs",
                            "-templateName", dbca_metadata["instance"].get("template"),
                            "-createAsContainerDatabase", "false", "-emConfiguration",
                            "NONE", "-recoveryAreaDestination", "NONE", "-storageType",
                            "FS", "-characterSet",dbca_metadata["instance"].get("character-set"),
                            "-nationalCharacterSet", dbca_metadata["instance"].get("national-character-set"),
                            "-registerWithDirService", "false", "-listeners",
                            dbca_metadata["listener"].get("name"), "-initParams",
                            ",".join(dbca_metadata["instance"].get("init-parameters")),
                            "-automaticMemoryManagement", dbca_metadata["instance"].get("automatic-memory-management"),
                            "-totalMemory", str(dbca_metadata["instance"].get("total-memory")),
                            "-databaseType", dbca_metadata["instance"].get("type")])

        inst_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = inst_process.communicate(input=dbc_input)
        print out, err
        
        with open(os.path.join(os.environ["HOME"], ".bash_profile"), "a") as pfile:
            pfile.write("\nexport ORACLE_BASE=%s" %ora_base)
            pfile.write("\nexport ORACLE_HOME=%s" %ora_home)
            pfile.write("\nexport ORACLE_GDN=%s" %gdb_name)
            pfile.write("\nexport ORACLE_SID=%s" %db_sid)
            pfile.flush()
    else:
        command.append("-deleteDatabase")
        if os.path.isfile(rsp_file):
            if db_sid: command.extend(["-sourceDB", db_sid])
            command.extend(["-responseFile", rsp_file])
        else:
            if not gdb_name:
                gdb_name = dbca_metadata["instance"].get("global-database-name")
            if not db_sid:
                db_sid = gdb_name.split(".")[0]
            command.extend(["-sourceDB", db_sid])

        inst_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = inst_process.communicate()
        print out, err

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?o:h:n:w:", ["rsp_file=",
                                        "delete", "sid=", "sys_password=",
                                        "system_password="])
    options = dict(options)

    if "-?" in options:
        print "Usage: python %s %s %s %s %s" %("create_instance.py",
        "[-?] -o oracle_base [-h oracle_home] [-n global-database-name]",
        "[-w password_file] [--sys_password sys_password]",
        " [--system_password system_password] [--sid sid] [--delete]",
        "[--rsp_file dbca_response_file]")
        sys.exit(0)

    main(options, arguments)
