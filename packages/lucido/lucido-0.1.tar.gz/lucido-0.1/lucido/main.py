#!/usr/bin/env python

from __future__ import print_function
from subprocess import PIPE

import argparse
import datetime
import os
import sys
import subprocess
import yaml

def clear_replacements(config):
    '''Clear the replacements key in the luci.yml configuration file.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: Dict

    '''
    del config['replacements']
    write_config_file(config)
    return config

def get_grep_cmds(config):
    '''Create a list of grep commands designed to find each of the 'sensitive'
    keys within the current working directory.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: list

    '''
    # grep -Ri --exclude-dir "/var/directory_to_exclude" "search pattern" `pwd`
    cmds = {}
    base_cmd = 'grep -Ri --exclude "luci.yml" '
    for exclude in config['exclude']:
        base_cmd += '--exclude-dir "' + exclude + '" '

    for sensitive in config['sensitive']:
        cmds[sensitive] = base_cmd + '"' + sensitive + '" `pwd`'

    return cmds

def get_git_toplevel():
    '''Get the top-level directory of the git repository.

    Returns: String

    '''
    return subprocess.getoutput('git rev-parse --show-toplevel')

def init():
    '''If run within a git repository, add luci.yml to .gitignore, and add the
    git hooks.

    Returns: None

    '''

    if is_git_repository():
        git_toplevel = get_git_toplevel()

        print("Adding luci.yml to .gitignore..")
        git_ignore = git_toplevel + '/.gitignore'
        ignore = subprocess.Popen('echo "luci.yml" >> ' + git_ignore,
                                  shell=True)

        print("Adding git hooks...")
        stamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        base = os.path.dirname(__file__)
        hooks = ' ' + git_toplevel + '/.git/hooks/'

        files = ['pre-commit', 'post-commit', 'post-merge']
        for f in files:
            backup = 'cp' + hooks + f + hooks + f + '.bak.' + stamp
            status, _ = subprocess.getstatusoutput(backup)
            if status == 0:
                print("Moving" + hooks + f + ' to' + hooks + f +'.bak.' +
                      stamp + "...")

            path = os.path.abspath(os.path.join(base, 'script/' + f))

            cp_cmd = 'cp ' + path + hooks
            cp = subprocess.Popen(cp_cmd, shell=True)
            cp.wait()

            chmod_cmd = 'chmod +x' + hooks + f
            chmod = subprocess.Popen(chmod_cmd, shell=True)
            chmod.wait()

        print("Done.")

def is_git_repository():
    ''' Check if current working directory is within a git repository.

    Returns: True or False

    '''
    status, _ = subprocess.getstatusoutput('git status')
    return status == 0

def replace_data(config, find_key, replace_key):
    ''' Construct and execute sed commands designed to replace text within
    files.

    Keyword arguments:
    config -- the parsed YAML configuration
    find_key -- the config key for the text to be searched for
    replace_key -- the config key for the replacement text

    Returns: None

    '''
    base = ['sed', '-i', '-e']
    for r in config['replacements']:
        pattern = ['s/' + r[find_key] + '/' + r[replace_key] + '/g']
        cmd = base + pattern + [r['path']]
        replace = subprocess.Popen(cmd)
        replace.wait()

def restore_sensitive_data(config):
    '''Restore sensitive data in the current working directory.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: None

    '''
    print("Restoring sensitive data...")
    replace_data(config, 'scrubbed', 'original')
    clear_replacements(config)
    print("Done.")

def scrub_sensitive_data(config):
    '''Scrub sensitive data in the current working directory.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: None

    '''
    print("Scrubbing sensitive data...")
    config = update_replacements(config)
    replace_data(config, 'original', 'scrubbed')
    print("Done.")

def sensitive_data_is_present(config):
    '''Check for sensitive data in the current working directory.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: True if sensitive data is present, False otherwise

    '''
    cmds = get_grep_cmds(config)
    for key in cmds:
        status, _ = subprocess.getstatusoutput(cmds[key])
        # grep returns 0 if there's a match
        if status == 0:
            return True

    return False

def update_replacements(config):
    '''Update the luci.yml configuration file to contain the necessary
    information to scrub/restore the defined sensitive data.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: Dict

    '''
    replacements = config.get('replacements', [])

    cmds = get_grep_cmds(config)

    for key in cmds:
        grep = subprocess.Popen(cmds[key], shell=True, stdout=PIPE)
        grep.wait()

        with grep.stdout as output:
            for line in output:
                line = str(line, 'UTF-8')
                path, original = line.rstrip().split(':', 1)
                scrubbed = original.replace(key, '')
                replacements.append({'path': path, 'original': original,
                                     'scrubbed': scrubbed})

    config['replacements'] = replacements
    write_config_file(config)
    return config

def write_config_file(config):
    '''Write the contents of config to the luci.yml configuration file.

    Keyword arguments:
    config -- the parsed YAML configuration

    Returns: None

    '''

    try:
        if is_git_repository():
            f = open(get_git_toplevel() + '/luci.yml', 'w')
        else:
            f = open('luci.yml', 'w')
    except:
        print('Could not find luci.yml!')
        sys.exit(1)

    f.write(yaml.dump(config, default_flow_style=False))
    f.close()

def main():
    desc = 'An automatic sensitive data scrubber and restorer.'
    parser = argparse.ArgumentParser(description=desc)
    group = parser.add_mutually_exclusive_group(required=True)

    arguments = [
        {'s': '-c', 'o': '--check',
         'h': 'Checks for sensitive data in the current working directory.'},
        {'s': '-i', 'o': '--init',
         'h': 'Creates git hooks and adds luci.yml to .gitignore if run ' \
         'within a git repository.'},
        {'s': '-r', 'o': '--restore',
         'h': 'Restores sensitive data in the current working directory.'},
        {'s': '-s', 'o': '--scrub',
         'h': 'Scrubs sensitive data from the current working directory.'}
    ]

    for a in arguments:
        group.add_argument(a['s'], a['o'], help=a['h'], const=True, nargs='?')

    args = parser.parse_args()

    try:
        if is_git_repository():
            config_file = open(get_git_toplevel() + '/luci.yml', 'r')
        else:
            config_file = open('luci.yml', 'r')
    except:
        print('Could not find luci.yml!')
        sys.exit(1)

    config = yaml.load(config_file)
    config_file.close()

    if args.init:
        init()
    elif args.check and sensitive_data_is_present(config):
        print("Sensitive data is still present.")
        print("Run 'luci -s' to scrub it.")
        sys.exit(1)
    elif args.scrub:
        scrub_sensitive_data(config)
    elif args.restore:
        restore_sensitive_data(config)

if __name__ == '__main__':
    main()
