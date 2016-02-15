################################################################################
# patch_db.py
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
import stat
import getopt
import zipfile
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
    patches_loc = options.get("-l", base_dir)
    ora_base = options.get("-o")
    ora_home = options.get("-h", os.path.join(ora_base, "product", "12.1.0", "dbhome_1"))
    ocmrf = options.get("--ocmrsp_file", "")

    # Patch OPatch if needed
    for opatchfile in install_metadata.get("opatch", []):
        opatch = zipfile.ZipFile(os.path.join(patches_loc, opatchfile), allowZip64=True)
        for zipinfo in opatch.infolist():
            extractedfile = opatch.extract(zipinfo.filename, ora_home)
            os.chmod(extractedfile, zipinfo.external_attr >> 16 & 0xFFF | stat.S_IWUSR)
        opatch.close()

    if not os.path.isfile(ocmrf) and \
    os.path.isfile(os.path.join(ora_home, "ccr", "bin", "setupCCR")):
        command = [os.path.join(ora_home, "ccr", "bin", "setupCCR"), "-s", "-d"]
        patch_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = patch_process.communicate()
        print out, err
        if patch_process.returncode > 0: sys.exit(patch_process.returncode)

    for patchfile in install_metadata.get("patches", []):
        filelist = []
        patch = zipfile.ZipFile(os.path.join(patches_loc, patchfile), allowZip64=True)
        filelist.extend(patch.namelist())
        for zipinfo in patch.infolist():
            extractedfile = patch.extract(zipinfo.filename, scratch)
            os.chmod(extractedfile, zipinfo.external_attr >> 16 & 0xFFF)
        patch.close()
        command = [os.path.join(ora_home, "OPatch", "opatch")]
        command.extend(["apply", "-silent", "-force", "-oh", ora_home])
        if os.path.isfile(ocmrf): command.extend("-ocmrf", ocmrf)
        command.append(os.path.join(scratch, patchfile[1:9]))
        patch_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = patch_process.communicate()
        print out, err
        while len(filelist) > 0:
            fsobj = filelist.pop()
            if os.path.isdir(os.path.join(scratch, fsobj)):
                os.rmdir(os.path.join(scratch, fsobj))
            else:
                os.remove(os.path.join(scratch, fsobj))

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?l:o:h:", ["ocmrsp_file="])
    options = dict(options)

    if "-?" in options:
        print "Usage: python %s %s %s" %("patch_db.py",
        "[-?] -l patches_location -o oracle_base [-h oracle_home]",
        "[--ocmrsp_file ocm_response_file]")
        sys.exit(0)

    main(options, arguments)
