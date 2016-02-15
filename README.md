## Oracle Database 12c Cloud Tooling Scripts
Project to install Oracle Database 12c, create and configure an instance using scripts.

### Pre-requisites
These scripts assume that the Hardware, Software and the Kernel Parameters pre-requisites have all been met for the Oracle Database. You can review these pre-requisites on the [Oracle Database Documentation][oradocs] website.

Apart from these requirements, these scripts use python to perform its tasks. This means that the all product installs, configuration, domain creation and configuration commands will be run from a python shell. Note that Python 2.6 or later must be installed on the servers for the scripts to work properly.

### Usage
To install the Oracle Database Software, download the zip archives and make it available in the installer_location. There is no need to extract the software; the script will take care of it.

To install the software:

`/usr/bin/python install_db.py [-?] -l installers_location -o oracle_base [-h oracle_home] [--hostname host_name] [--rsp_file install_response_file] [--tmp_loc tmp_location] [--inst_group install_group] [--dba_group dba_group] [--oper_group oper_group] [--backupdba_group backupdba_group] [--dgdba_group dgdba_group] [--kmdba_group kmdba_group] [--inventory_loc inventory_loc]`

To patch the database software:

`/usr/bin/python patch_db.py [-?] -l patches_location -o oracle_base [-h oracle_home] [--ocmrsp_file ocm_response_file]`

To manage listeners:

`/usr/bin/python create_listener.py [-?] -o oracle_base [-h oracle_home] [--delete] [--rsp_file netca_response_file]`

To manage instances:

`/usr/bin/python create_instance.py [-?] -o oracle_base [-h oracle_home] [-n global-database-name] [-w password_file] [--sys_password sys_password]  [--system_password system_password] [--sid sid] [--delete] [--rsp_file dbca_response_file]`

### License
This program is free software: you can redistribute it and/or modify it as long as you retain the name of the original author and under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

[oradocs]: http://docs.oracle.com/database/121/LADBI/chklist.htm#LADBI8045 "Oracle Database Documentation"
