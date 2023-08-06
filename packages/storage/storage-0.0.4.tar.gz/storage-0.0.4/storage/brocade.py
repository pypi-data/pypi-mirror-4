import re
from ssh import SSHSession

WWN_REGEX = re.compile('[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}'
                       , re.I)


class BrocadeSwitch(SSHSession):
    """
    Establish SSH Connection to Brocade FC Switch which can be used
    to run commands against it.

    Provide commonly used commands as methods and also command method to add more functionality
    """
    @staticmethod
    def command_with_fid(cmd, fid):
        """
        Add fosexec syntax to command, so it can run in given fid
        """
        return 'fosexec --fid %s --cmd "%s" ' % (fid, cmd)

    def aliShow(self, pattern='*', fid=None):
        """
        Returns dictionary with alias name as key and it's members as values. Default pattern '*' will return all aliases


        """
        aliases = {}
        cmd = 'aliShow %s' % pattern

        if fid:
            cmd = self.command_with_fid(cmd, fid)

        output, error = self.command(cmd)

        if output and not re.search('does not exist', " ".join(output), re.IGNORECASE):
            alias_regex = re.compile('alias:(.*)')

            key = None
            values = []

            for line in output:
                line = line.strip()
                if alias_regex.search(line):
                    key = alias_regex.search(line).group(1).strip()
                    values = []
                elif WWN_REGEX.search(line):
                    values = values + WWN_REGEX.findall(line)

                if key:
                    aliases[key] = list(set(values))

        return aliases

    def fabricShow(self, membership=False, chassis=False, fid=None):
        """
        Returns fabricshow output with each switch as dictionary
        """
        fabric = {}
        cmd = 'fabricShow'

        if membership and chassis:
            pass # Defaults to fabricShow as both arguments can't be True
        elif membership:
            cmd = 'fabricShow -membership'
        elif chassis:
            cmd = 'fabricShow -chassis'

        if fid: cmd = self.command_with_fid(cmd, fid)

        output, error = self.command(cmd)

        #print output

        print cmd

        if output:
            for line in output:
                line = line.strip()
                if re.match(r'^\d+:', line):
                    values = line.split()
                    key = values.pop(0).replace(':','')
                    fabric[key] = values

        return fabric

    def switchName(self):
        """
        Returns Switch Name.
        FID not required here
        """
        output, error = self.command('switchName')
        if output:
            return "".join(output).strip()

    def version(self):
        """
        Returns dictionary with version information.
        FID not required here
        """
        dct = {}
        output, error = self.command('version')
        #print output
        for line in output:
            line = line.strip()
            if re.split('\W+ ', line) and len(re.split('\W+ ', line))==2:
                key, value = re.split('\W+ ', line)
                dct[key] = value
        return dct

    def zoneShow(self, pattern='*', fid=None):
        """
        Returns dictionary with alias name as key and it's members as values

        Pattern:'*' will return all aliases.
        """
        zones = {}
        cmd = 'zoneShow %s' % pattern

        if fid:
            cmd = self.command_with_fid(cmd, fid)

        output, error = self.command(cmd)

        if output and not re.search('does not exist', " ".join(output), re.IGNORECASE):
            zone_regex = re.compile('zone:(.*)')

            key = None
            values = []

            for line in output:
                line = line.strip()
                if zone_regex.search(line):
                    key = zone_regex.search(line).group(1).strip()
                    values = []
                else:
                    items = [x.strip() for x in line.split(';') if x]
                    if items:
                        values = values + items
                if key:
                    zones[key] = list(set(values))

        return zones

    def find_wwn(self, wwn, fid=None):
        """
        Search for given pWWN or nWWN on Fabric and
        return True if exists, otherwise False.
        """
        cmd = 'nodefind %s' % wwn
        if fid:
            cmd = self.command_with_fid(cmd, fid)

        output, error = self.command(cmd)

        if output and re.search(wwn ,  " ".join(output), re.IGNORECASE):
            return True
        else:
            return False

    def get_wwn_aliases(self, wwn, fid=None):
        """
        Returns a list of Aliases for given wwn
        """
        aliases = []
        cmd = 'aliShow *'
        if fid:
            cmd = self.command_with_fid(cmd, fid)

        output, error = self.command(cmd)


        if output:
            for entry in output:
                print entry
                #aliases.append(entry.split(':')[1].strip())

        return aliases

    def find_wwn_get_aliases(self, wwn, fid=None):
        """
        Find wwn on fabric and gets aliases and returns tuple
        """
        if self.find_wwn(wwn, fid):
            aliases = self.get_wwn_aliases(wwn, fid)
            return True, aliases
        else:
            return False, []

