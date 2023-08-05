##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from slapos.recipe.librecipe import GenericBaseRecipe
import zc.buildout
import sys
import zc.recipe.egg

class Request(GenericBaseRecipe):
  def install(self):
    """
    Taken out from the old "lamp" recipe. Allows do configure a LAMP instance.
    """
    document_root = self.options['htdocs']
    url = self.options['url']
    mysql_conf = {'mysql_host': self.options['mysql-host'],
                  'mysql_port': self.options['mysql-port'],
                  'mysql_user': self.options['mysql-username'],
                  'mysql_password': self.options['mysql-password'],
                  'mysql_database': self.options['mysql-database'],
                 }
    self.configureInstallation(document_root, url, mysql_conf)

  def configureInstallation(self, document_root, url, mysql_conf):
    """Start process which can launch python scripts, move or remove files or
    directories when installing software.
    """
    if not self.options.has_key('delete') and not self.options.has_key('rename') and not\
        self.options.has_key('chmod') and not self.options.has_key('script'):
      return ""
    delete = []
    chmod = []
    data = []
    rename = []
    rename_list = ""
    argument = [self.options['lampconfigure_directory'].strip(),
                             "-H", mysql_conf['mysql_host'], "-P", mysql_conf['mysql_port'],
                             "-p", mysql_conf['mysql_password'], "-u", mysql_conf['mysql_user']]
    if not self.options.has_key('file_token'):
      argument = argument + ["-d", mysql_conf['mysql_database'],
                             "--table", self.options['table_name'].strip(), "--cond",
                             self.options['constraint'].strip()]
    else:
      argument = argument + ["-f", self.options['file_token'].strip()]
    argument += ["-t", document_root]

    if self.options.has_key('delete'):
      delete = ["delete"]
      for fname in self.options['delete'].split(','):
        delete.append(fname.strip())
    if self.options.has_key('rename'):
      for fname in self.options['rename'].split(','):
        if fname.find("=>") < 0:
          old_name = fname
          fname = []
          fname.append(old_name)
          fname.append(old_name + '-' + mysql_conf['mysql_user'])
        else:
          fname = fname.split("=>")
        cmd = ["rename"]
        if self.options.has_key('rename_chmod'):
          cmd += ["--chmod", self.options['rename_chmod'].strip()]
        rename.append(cmd + [fname[0].strip(), fname[1].strip()])
        rename_list += fname[0] + " to " + fname[1] + " "
    if self.options.has_key('chmod'):
      chmod = ["chmod", self.options['mode'].strip()]
      for fname in self.options['chmod'].split(','):
        chmod.append(fname.strip())
    if self.options.has_key('script') and \
        self.options['script'].strip().endswith(".py"):
      data = ["run", self.options['script'].strip(), "-v", mysql_conf['mysql_database'], url, document_root]
    self.path_list.extend(zc.buildout.easy_install.scripts(
        [('configureInstall', __name__ + '.runner', 'executeRunner')], self.ws,
        sys.executable, self.wrapper_directory, arguments=[argument, delete, rename,
            chmod, data]))
    return rename_list