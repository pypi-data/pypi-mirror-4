from time import sleep
import re
import paramiko

class BrocadeException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class BrocadeConnectionException(BrocadeException):
    pass

class BrocadeCommandException(BrocadeException):
    pass

class BrocadeSwitch(object):
    """
    Establish SSH Connection to Brocade FC Switch which can be used
    to run commands against it
    """
    def __init__(self, hostname, username, password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=hostname, username=username, password=password)
        except paramiko.BadHostKeyException:
            raise BrocadeConnectionException('SSH Server host key could not be verified')
        except paramiko.AuthenticationException:
            raise BrocadeConnectionException('SSH Authentication failed')
        except paramiko.SSHException:
            raise BrocadeConnectionException('Paramiko SSH Connection Problem')
        except Exception, e:
            raise BrocadeConnectionException('SSH Connection Error:%s ' % e)

    def __del__(self):
        try:
            sleep(1)
            self.ssh.close()
        except Exception:
            pass

    def run_command(self, command):
        """
        Runs given command and returns output, error
        """
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.readlines()
            error = stdout.readlines()
            return output, error
        except Exception, e:
            raise BrocadeCommandException('Unable to run given command %s. Error %s' % (command,e) )

    def find_wwn(self, wwn, fid=None):
        """
        Search for give pWWN or nWWN on Fabric and return True if exists
        """
        if fid:
            command = 'fosexec --fid %s --cmd "nodefind %s" ' % (fid, wwn)
        else:
            command = 'nodefind %s' % wwn

        output, error = self.run_command(command)
        if output and re.search(wwn ,  " ".join(output), re.IGNORECASE):
            return True
        else:
            return False

    def get_wwn_aliases(self, wwn, fid=None):
        """
        Returns a list of Aliases for given wwn
        """
        aliases = []
        if fid:
            command = 'fosexec --fid %s --cmd "aliShow" | grep -iEB 1 "%s" | grep "alias:"' % (fid, wwn)
        else:
            command = 'aliShow | grep -iEB 1 %s | grep alias:' % wwn

        output, error = self.run_command(command)

        if output:
            for entry in output:
                aliases.append(entry.split(':')[1].strip())

        return aliases

    def get_pattern_aliases(self, pattern, fid=None):
        """
        Returns a list of Aliases that match pattern
        """
        aliases = []
        if fid:
            command = 'fosexec --fid %s --cmd "aliShow %s" | grep "alias:" ' % (fid, pattern)
        else:
            command = 'alishow %s' % pattern

        output, error = self.run_command(command)

        if output and not re.search('does not exist', " ".join(output)):
            for entry in output:
                aliases.append(entry.split(':')[1].strip())
        return  aliases

    def find_wwn_get_aliases(self, wwn, fid=None):
        """
        Find wwn on fabric and gets aliases and returns tuple
        """

        if self.find_wwn(wwn, fid):
            aliases = self.get_wwn_aliases(wwn, fid)
            return True, aliases
        else:
            return False, []

