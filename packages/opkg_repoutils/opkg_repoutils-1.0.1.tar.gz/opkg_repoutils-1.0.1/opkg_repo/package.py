"""
Package representation in Python.
"""

import Crypto.Hash.MD5 as MD5
import os
import string
import yaml


# template for an entry in the Packages file
PACKAGE_SKEL = """
Package: $package
Version: $version
Depends: $depends
Provides: $provides
Section: $section
Architecture: $architecture
Maintainer: $maintainer
MD5Sum: $file_MD5
Size: $file_size
Filename: $filename
Description: $description



"""
INVALID_CONFIG = 'Invalid package configuration.'


def validate_pkgconf(conf):
    """Ensure that a package config is valid."""
    # TODO: validate file references (i.e. package-doc)

    required_keys = ['package', 'version', 'section', 'architecture',
                     'maintainer', 'filename', 'description', 'libc',
                     'feed']
    for k in required_keys:
        if not k in conf:
            print '[!] missing key:', k
            raise Exception(INVALID_CONFIG)


class Package:
    """Representation of a package."""

    def __init__(self, config, conf_file=None, conn=None):
        validate_pkgconf(config)
        self.config = config
        if conf_file:
            self.conf_file = conf_file
            optional = ['depends', 'provides', 'doc', 'dev', 'dbg',
                        'staticdev']
            for k in optional:
                if not k in self.config:
                    self.config[k] = ""

            descr = self.config['description']
            descr = descr.strip()
            descr.replace('\n', '\n ')
            self.config['description'] = descr
            self.file_info = self.package_files()

            if type(self.config['depends']) != str:
                self.config['depends'] = ', '.join(self.config['depends'])
            if type(self.config['provides']) != str:
                self.config['provides'] = ', '.join(self.config['provides'])

        else:
            if not conn:
                raise Exception("cannot load from database")
            self.file_info = self.get_package_files_from_db(conn)

    def __repr__(self):
            return '%s-%s-%s' % (self.config['package'],
                             self.config['libc'],
                             self.config['architecture'])

    def __getitem__(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return None

    def __delitem__(self, key):
        if key in self.config:
            del self.config[key]

    def __setitem__(self, key, value):
        if key in self.config:
            self.config[key] = value

    def __len__(self):
        return len(self.config)

    def get_package_files_from_db(self, conn):
        """Load package files from database."""
        cur = conn.cursor()
        sql = 'select * from package_files where arch=? and libc=? '
        sql += 'and package=?'
        pf_data = (
            self['architecture'],
            self['libc'],
            self['package']
        )
        cur.execute(sql, pf_data)
        rows = cur.fetchall()
        cur.close()
        if len(rows) == 0:
                raise Exception("no package files found")
        filedata = []
        for row in rows:
            keys = ['filename', 'sum', 'size', 'name', 'package', 'arch',
                    'libc', 'flavour']
            entry = {}
            for i, k in enumerate(keys):
                entry[k] = row[i]
            filedata.append(entry)
        return filedata

    def store(self, conn):
        """Store package in database"""
        cur = conn.cursor()

        # store package data entry
        pd_values = [
            self['package'],
            self['version'],
            self['depends'],
            self['provides'],
            self['section'],
            self['architecture'],
            self['libc'],
            self['feed'],
            self['maintainer'],
            self['filename'],
            self['doc'],
            self['dev'],
            self['dbg'],
            self['staticdev'],
            self['description']
        ]

        sql = 'insert into package_data values (' + '?, ' * len(pd_values)
        sql = sql[:-2] + ')'

        # prevent duplicate entries
        cur.execute('select * from package_data where architecture=? and ' +
                    'libc=? and package=?', (self['architecture'],
                                             self['libc'],
                                             self['package']))
        if len(cur.fetchall()) > 0:
            print '[!] found entry for %s, deleting.' % (self['package'], )
            cur.execute('delete from package_data where architecture=? and ' +
                        'libc=? and package=?', (self['architecture'],
                                                 self['libc'],
                                                 self['package']))

        cur.execute(sql, pd_values)
        cur.close()
        conn.commit()
        for entry in self.file_info:
            store_file_info(entry, conn)

    def package_files(self):
        """
        Generate a list of file information for the various package flavours.
        """
        files = [{'file': self['filename'], 'flavour': ''}]
        file_keys = ['doc', 'dev', 'dbg', 'staticdev']
        for key in file_keys:
            if key in self.config and self[key]:
                files.append({'file': self[key], 'flavour': '-' + key})
        base_dir = os.path.dirname(self.conf_file)
        files_data = []
        for entry in files:
            flavour = entry['flavour']
            filename = entry['file']
            print '[+] processing', filename
            file_data = get_file_info(os.path.join(base_dir, filename))
            file_data['filename'] = os.path.join(base_dir, filename)
            file_data['name'] = filename
            file_data['package'] = self['package']
            file_data['arch'] = self['architecture']
            file_data['libc'] = self['libc']
            file_data['flavour'] = flavour
            files_data.append(file_data)
        return files_data

    def packages_entries(self):
        """Generate entries for the Packages file."""
        entries = []
        for entry in self.file_info:
            tpl = string.Template(PACKAGE_SKEL)
            package_entry = {
                'package': self['package'] + entry['flavour'],
                'version': self['version'],
                'depends': self['depends'],
                'provides': self['provides'],
                'section': self['section'],
                'architecture': self['architecture'],
                'maintainer': self['maintainer'],
                'file_MD5': entry['sum'],
                'file_size': entry['size'],
                'filename': entry['name'],
                'description': self['description']
            }
            entries.append(tpl.substitute(package_entry))
        return entries


def store_file_info(filedata, conn):
    """Store file information in the database."""
    cur = conn.cursor()
    cur.execute('select * from package_files where filename=?',
                (filedata['filename'], ))
    if len(cur.fetchall()) > 0:
        cur.execute('delete from package_files where filename=?',
                    (filedata['filename'], ))
    pf_values = (
        filedata['filename'],
        filedata['sum'],
        filedata['size'],
        filedata['name'],
        filedata['package'],
        filedata['arch'],
        filedata['libc'],
        filedata['flavour']
    )
    sql = 'insert into package_files values (' + '?, ' * len(pf_values)
    sql = sql[:-2] + ')'
    cur.execute(sql, pf_values)
    cur.close()
    conn.commit()


def get_file_info(filename):
    """Return basic information about a file."""
    return {
        'sum': md5sum(filename),
        'size': os.path.getsize(filename)
    }


def from_conf(conf_file):
    """Creates a Package from a configuration file."""
    conf_raw = open(conf_file).read()
    name_components = conf_file.split(os.sep)
    name_components = name_components[-4:-2]
    libc = name_components[0]
    arch = name_components[1]
    config = yaml.load(conf_raw)
    config['architecture'] = arch
    config['libc'] = libc
    return Package(config, conf_file=conf_file)


def from_db(conn, arch, libc, package):
    """Load package from database."""
    sql = 'select * from package_data where architecture=? and libc=? and '
    sql += 'package=?'
    cur = conn.cursor()
    cur.execute(sql, (arch, libc, package))
    rows = cur.fetchall()
    cur.close()
    assert_warning = "database inconsistency: multiple packages for "
    assert_warning += "the same arch and libc."
    assert len(rows) <= 1, assert_warning

    if len(rows) == 0:
        return None
    else:
        rows = rows[0]
    keys = ['package', 'version', 'depends', 'provides', 'section',
            'architecture', 'libc', 'feed', 'maintainer', 'filename',
            'doc', 'dev', 'dbg', 'staticdev', 'description']
    config = {}
    for i, k in enumerate(keys):
        config[k] = rows[i]
    pkg = Package(config, conn=conn)
    print '[+] loaded %s from database' % (repr(pkg), )
    return pkg


def md5sum(filename):
    """MD5 hash the contents of a file."""
    filesum = MD5.new()
    with open(filename) as fhandle:
        for line in fhandle:
            filesum.update(line)
    return filesum.hexdigest()
