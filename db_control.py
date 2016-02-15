################################################################################
# db_control.py
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
import tempfile
import subprocess

def main(options, arguments):
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()

    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        with open(os.path.join(base_dir, "metadata.json"), "r") as mfile:
            db_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    ora_base = options.get("-o", "")
    ora_home = options.get("-h", os.path.join(ora_base, "product", "12.1.0", "dbhome_1"))
    pwd_file = options.get("-w", "")
    sys_pass = options.get("--sys_password", db_metadata["instance"].get("sys-password"))
    tmp_file = tempfile.mktemp() + ".sql"
    
    sql_input = "%s\n" %sys_pass
    if os.path.isfile(pwd_file):
        with open(pwd_file, "r") as bfile:
            sql_input = bfile.read()

    if "--start" in options:
        command = [os.path.join(ora_home, "bin", "lsnrctl"), "start"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        print out, err
        
        with open(tmp_file, "w") as bfile:
            bfile.write("startup")
            bfile.flush()
        command = [os.path.join(ora_home, "bin", "sqlplus"), "SYS", "AS", "SYSDBA", "@%s" %tmp_file]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate(input=sql_input)
        print out, err
    elif "--stop" in options:
        with open(tmp_file, "w") as bfile:
            bfile.write("shutdown immediate")
            bfile.flush()
        command = [os.path.join(ora_home, "bin", "sqlplus"), "SYS", "AS", "SYSDBA", "@%s" %tmp_file]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate(input=sql_input)
        print out, err

        command = [os.path.join(ora_home, "bin", "lsnrctl"), "stop"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        print out, err

    if os.path.isfile(tmp_file): os.unlink(tmp_file)

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?o:h:w:", ["start",
                                        "stop", "sys_password="])
    options = dict(options)

    if "-?" in options:
        print "Usage: python %s %s %s" %("db_control.py",
        "[-?] -o oracle_base [-h oracle_home] [--start | --stop]",
        "[-w password_file] [--sys_password sys_password]")
        sys.exit(0)

    main(options, arguments)
