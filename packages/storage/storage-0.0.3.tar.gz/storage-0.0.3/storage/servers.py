from time import sleep
import re
import paramiko

class ServerException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class ServerConnectionException(ServerException):
    pass

class ServerCommandException(ServerException):
    pass

class LinuxServer(Exception):
    """
    Establish SSH Connection to Linux Server which can be used
    to run commands against it
    """
    def __init__(self, hostname, username, password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=hostname, username=username, password=password)
        except paramiko.BadHostKeyException:
            raise ServerConnectionException('SSH Server host key could not be verified')
        except paramiko.AuthenticationException:
            raise ServerConnectionException('SSH Authentication failed')
        except paramiko.SSHException:
            raise ServerConnectionException('Paramiko SSH Connection Problem')
        except Exception, e:
            raise ServerConnectionException('SSH Connection Error:%s ' % e)

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
            raise ServerCommandException('Unable to run given command %s. Error %s' % (command,e) )

    def get_hostname(self):
        """
        Returns Server Hostname
        """
        output, error = self.run_command('hostname')
        hostname = " ".join(output).strip()
        return hostname

    def has_hbas(self):
        """
        Return True if Server has HBA's, otherwise NO
        """
        output, error = self.run_command('/sbin/lspci | grep -i fibre')
        if output:
            return True
        else:
            return False

    def get_hba_manufacturer(self):
        """
        Returns HBA Manufacturer
        """
        manufacturer = None
        if self.has_hbas():
            output, error = self.run_command('/sbin/lspci | grep -i fibre')
            if re.search("Brocade", " ".join(output), re.IGNORECASE) and not re.search("QLogic|Emulex", " ".join(output), re.IGNORECASE):
                manufacturer = "Brocade"
            elif re.search("QLogic", " ".join(output), re.IGNORECASE) and not re.search("Brocade|Emulex", " ".join(output), re.IGNORECASE):
                manufacturer = "QLogic"
            elif re.search("QLogic", " ".join(output), re.IGNORECASE) and not re.search("Brocade|QLogic", " ".join(output), re.IGNORECASE):
                manufacturer = "Emulex"
            else:
                manufacturer = "Unknown"
        return manufacturer

class RedhatServer(LinuxServer):

    def get_os_version(self):
        """
        Returns OS Version
        """
        output, error = self.run_command('cat /etc/redhat-release')
        return " ".join(output).strip()

    def get_packages(self, package):
        """
        Return Installed Packages
        package can be actual package or pattern
        """
        packages = []
        output, error = self.run_command('rpm -qa %s' % package)

        if output and not re.search('is not installed', " ".join(output)):
            for entry in output:
                packages.append(entry.strip())
        return packages

    def get_wwpns(self):
        """
        Returns a list with WWPN's
        """
        wwpns = []
        if self.get_hba_manufacturer():
            output, error = self.run_command('cat /sys/class/fc_host/host*/port_name')
            if output and not re.search('No such file or directory', " ".join(output), re.IGNORECASE):
                for item in output:
                    item = item.strip()
                    if re.match("0x", item) and len(item) == 18:
                        wwpns.append(":".join(re.findall('..', item.strip('0x'))))
                    else:
                        pass
        return wwpns


class ESXServer(LinuxServer):
    def get_os_version(self):
        """
        Returns OS Version
        """
        command = "head -1 /proc/vmware/version | awk '{split($0,array,\",\")} END{print array[1]}'"
        output, error = self.run_command(command)
        return " ".join(output).strip()

    def get_wwpns(self):
        """
        Returns a list with WWPN's
        """
        wwpns = []
        manufacturer = self.get_hba_manufacturer()
        if manufacturer:
            if manufacturer == "Brocade":
                output, error = self.run_command('cat /proc/scsi/bfa/* | grep WWPN')
                if output and not re.search('No such file or directory', " ".join(output), re.IGNORECASE):
                    for item in output:
                        item = item.strip()
                        if re.match("WWPN: ", item) and len(item) == 29:
                            wwpns.append(item.strip("WWPN: "))
            elif manufacturer == "QLogic":
                output, error = self.run_command('cat /proc/scsi/qla2xxx/* | grep adapter-port')
                if output and not re.search('No such file or directory', " ".join(output), re.IGNORECASE):
                    for item in output:
                        item = item.strip()
                        if re.match('scsi-qla.+-adapter-port=[A-Fa-f0-9]{16}:', item):
                            wwpn = re.match('scsi-qla.+-adapter-port=[A-Fa-f0-9]{16}:', item).group().split('=')[
                                   1].strip(':')
                            wwpns.append(":".join(re.findall('..', wwpn)))

        return wwpns