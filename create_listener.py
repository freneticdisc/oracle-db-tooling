################################################################################
# create_listener.py
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
            netca_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    ora_base = options.get("-o")
    ora_home = options.get("-h", os.path.join(ora_base, "product", "12.1.0", "dbhome_1"))
    rsp_file = options.get("--rsp_file", "")
    delete_listener = True if "--delete" in options else False

    command = [os.path.join(ora_home, "bin", "netca")]
    tmprsp_file = tempfile.mktemp()

    if not delete_listener:
        if os.path.isfile(os.path.join(ora_home, "network", "admin", "listener.ora")):
            return

        command.extend(["-silent", "-responseFile"])
        if os.path.isfile(rsp_file):
            command.append(rsp_file)
        else:
            with open(tmprsp_file, "w") as bfile:
                bfile.write("[GENERAL]\n")
                bfile.write("RESPONSEFILE_VERSION=\"12.1\"\n")
                bfile.write("CREATE_TYPE=\"CUSTOM\"\n")
                bfile.write("[oracle.net.ca]\n")
                bfile.write("INSTALLED_COMPONENTS={\"server\",\"net8\",\"javavm\"}\n")
                bfile.write("INSTALL_TYPE=\"\"typical\"\"\n")
                bfile.write("LISTENER_NUMBER=1\n")
                bfile.write("LISTENER_NAMES={\"%s\"}\n" %netca_metadata["listener"].get("name"))
                bfile.write("LISTENER_PROTOCOLS={%s}\n" %",".join(["\"%s;%s\"" \
                            %(prot["protocol"], prot["port"]) \
                            for prot in netca_metadata["listener"].get("protocols")]))
                bfile.write("LISTENER_START=\"\"%s\"\"\n" %netca_metadata["listener"].get("name"))
                bfile.write("NAMING_METHODS={\"TNSNAMES\",\"ONAMES\",\"HOSTNAME\"}\n")
                bfile.write("NSN_NUMBER=1\n")
                bfile.write("NSN_NAMES={\"%s\"}\n" %netca_metadata["netservicename"].get("name"))
                bfile.write("NSN_SERVICE={\"%s\"}\n" %netca_metadata["netservicename"].get("service"))
                bfile.write("LISTENER_PROTOCOLS={%s}\n" %",".join(["\"%s;%s;%s\"" \
                            %(prot["protocol"], prot["servertype"], prot["port"]) \
                            for prot in netca_metadata["netservicename"].get("protocols")]))
                bfile.flush()
            command.append(tmprsp_file)
    else:
        command.append("-deinst")

    lsnr_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = lsnr_process.communicate()
    print out, err

    if os.path.isfile(tmprsp_file): os.unlink(tmprsp_file)

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?o:h:", ["rsp_file=",
                                                               "delete"])
    options = dict(options)

    if "-?" in options:
        print "Usage: python %s %s %s" %("create_listener.py",
        "[-?] -o oracle_base [-h oracle_home] [--delete]",
        "[--rsp_file netca_response_file]")
        sys.exit(0)

    main(options, arguments)