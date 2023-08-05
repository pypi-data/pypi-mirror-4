#!/usr/bin/python
"""
Utility script for maintaining and generating an opkg repository.
"""

import argparse
import gzip
import os
import shutil
import sqlite3
import sys
import yaml

import opkg_repo.package as package


REPO_CONF_FILE = 'repo.conf'
REPO_CONF = {}
DB = sqlite3.connect('repo.db')
DB.row_factory = sqlite3.Row


def copy_package(pkg):
    """
    Copy a package to the feed directory and write its entries to the
    feed manifest.
    """
    pkg_dir = os.path.dirname(pkg.file_info[0]['filename'])
    pkg_dir = os.sep.join(pkg_dir.split(os.sep)[1:])
    src_path = os.path.join(REPO_CONF['source'], pkg_dir)
    pkg_dir = os.path.join(os.path.dirname(pkg_dir), pkg['feed'])
    out_path = os.path.join(REPO_CONF['feed'], pkg_dir)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    for entry in pkg.file_info:
        src_file = os.path.join(src_path, entry['name'])
        out_file = os.path.join(out_path, entry['name'])
        shutil.copy(src_file, out_file)
    package_entry = ''.join(pkg.packages_entries())
    with open(os.path.join(out_path, 'Packages'), 'a') as package_file:
        package_file.write(package_entry)


def build_feed(arch, libc, feed):
    """
    Build all the packages in a feed:

    * copy the package files over
    * write entries to package manifest
    * once all packages are copied, gzip the manifest
    """
    sql = 'select package from package_data where '
    sql += 'architecture=? and libc=? and feed=? order by package asc'
    cur = DB.cursor()
    cur.execute(sql, (arch, libc, feed))
    rows = cur.fetchall()
    cur.close()
    for row in rows:
        pkg = package.from_db(DB, arch, libc, row[0])
        copy_package(pkg)
    feed_dir = os.path.join(REPO_CONF['feed'], arch, libc, feed)
    manifest = open(os.path.join(feed_dir, 'Packages'))
    manifest_gz = gzip.open(os.path.join(feed_dir, 'Packages.gz'), 'wb')
    manifest_gz.writelines(manifest)
    manifest.close()
    manifest_gz.close()


def build_feeds(arch, libc):
    """
    Select every feed for the given arch-libc, and pass it off to be
    built.
    """
    sql = 'select distinct feed from package_data where architecture=? '
    sql += 'and libc=? order by libc asc'
    cur = DB.cursor()
    cur.execute(sql, (arch, libc))
    rows = cur.fetchall()
    cur.close()
    rows = [row[0] for row in rows]
    for row in rows:
        print '[+] building %s for %s-%s' % (row, arch, libc)
        build_feed(arch, libc, row)


def build_libc(arch):
    """
    Step through each architecture-libc and build it.
    """
    sql = 'select distinct libc from package_data where architecture=? '
    sql += 'order by libc asc'
    cur = DB.cursor()
    cur.execute(sql, (arch, ))
    rows = cur.fetchall()
    cur.close()
    rows = [row[0] for row in rows]
    for row in rows:
        print '[+] building for %s-%s' % (arch, row)
        build_feeds(arch, row)


def build_arch():
    """Step through each architecture and build each libc version."""
    sql = 'select distinct architecture from package_data order by '
    sql += 'architecture asc'
    cur = DB.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    rows = [row[0] for row in rows]
    for row in rows:
        print '[+] building %s' % (row, )
        build_libc(row)


def build_repo():
    """Prepare to build repository, building it afterwards."""
    print '[+] building repo'
    build_arch()


def printerr(text):
    """Print an error message to STDERR."""
    if not text.endswith('\n'):
        text += '\n'
    sys.stderr.write(text)


def config_repo():
    """Load the global repostory config."""
    global REPO_CONF

    REPO_CONF = yaml.load(open(REPO_CONF_FILE).read())
    if not 'source' in REPO_CONF:
        printerr('no source directory specified!')
        exit(1)
    elif not os.path.isdir(REPO_CONF['source']):
        printerr('%s is not a directory!' % (REPO_CONF['source']))
        exit(1)
    else:
        print '[+] source directory:', REPO_CONF['source']

    if not 'feed' in REPO_CONF:
        printerr('no feed directory specified!')
        exit(1)
    feed = REPO_CONF['feed']
    if os.path.exists(feed) and not os.path.isdir(feed):
        printerr('%s is not a directory!' % (REPO_CONF['feed']))
        exit(1)
    else:
        print '[+] feed directory:', REPO_CONF['feed']


def scan_repo():
    """Scan the source directory and load the database."""
    if not 'source' in REPO_CONF:
        printerr('no source directory specified!')
        exit(1)

    cwd = os.getcwd()
    os.chdir(REPO_CONF['source'])
    for dirpath, dirnames, filenames in os.walk('.'):
        scan_configs(dirpath, filenames)
    os.chdir(cwd)


def scan_configs(dirpath, filenames):
    """Look for configuration files in the current directory."""
    for filename in filenames:
        if not filename.endswith('.conf'):
            continue
        print '[+] config file:', os.path.join(dirpath, filename)
        pkg = package.from_conf(os.path.join(dirpath, filename))
        pkg.store(DB)
        print '[+] loaded package: ' + repr(pkg)


def main():
    """
    opkg_repo_manager is used to generate and build the repository.
    """

    parser = argparse.ArgumentParser('opkg repository manager')
    parser.add_argument('-c', '--clean', action='store_true',
                        help='clean feed directory')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='do not build repository')
    parser.add_argument('-u', '--update', action='store_true',
                        help='update database from filesystem')
    args = parser.parse_args()

    config_repo()
    if args.update:
        scan_repo()
    if args.clean:
        print '[+] cleaning', REPO_CONF['feed']
        if os.path.exists(REPO_CONF['feed']):
            print '[+] removing directory tree'
            shutil.rmtree(REPO_CONF['feed'])
    if not args.dry_run:
        build_repo()

if '__main__' == __name__:
    main()
