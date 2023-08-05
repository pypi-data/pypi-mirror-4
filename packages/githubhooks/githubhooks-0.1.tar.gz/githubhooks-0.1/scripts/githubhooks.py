#!/usr/bin/env python
'''
    githubhooks
    ~~~~~~~~~~~
    A simple script that lists or tests github hooks via their v3 API.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: WTFPL, see COPYING for more details
'''
import os
import sys
import argparse
import github


def parse_args():
    '''%(prog)s -h
       %(prog)s [--token <token>] list
       %(prog)s [--token <token>] --hook <repo_name>:<hook_id> [--hook ...] run
       %(prog)s [--token <token>] --config hooks.txt run
    '''
    parser = argparse.ArgumentParser(usage=parse_args.__doc__)

    parser.add_argument('action', choices=['list', 'run'],
                        help='Either list available hooks by repository or run'
                        ' specific hooks.')

    parser.add_argument('--config', type=argparse.FileType('r'),
                        help='A config file that lists hooks to run, one on '
                        'each line.')

    parser.add_argument('--hook', action='append',
                        help='A hook to run. Should be in the format '
                        '"<repo_name>:<hook_id>". This argument can be repeated'
                        ' multiple times.')

    parser.add_argument('--token', default=os.getenv('GITHUB_TOKEN'),
                        help='Your gihub oauth token. Defaults to the '
                        'value of the environment variable "GITHUB_TOKEN".')

    args = parser.parse_args()

    if not args.token:
        parser.error('you must provied a github token. Either provide a '
                     '--token argument, or set the GITHUB_TOKEN environment '
                     'variable.')

    if args.action == 'run' and not args.hook and not args.config:
        parser.error('you must provided at least one hook to run.')

    if args.config and args.hook:
        print >> sys.stderr, ('Warning: Skipping hooks provided with --hook '
                              'since you also specified a config file.')

    return args


def parse_lines(inp):
    '''Returns lines for the given file that are non-blank and whose first
    non-whitespace character is not a "#".
    '''
    return [line.strip() for line in inp.readlines()
            if line.strip() and not line.strip().startswith('#')]


def list_hooks(api):
    '''Lists all active hooks by repository for the currently authed user.'''
    print '.. Listing Hooks by Repository ..'
    for repo in api.get_user().get_repos():
        try:
            for hook in repo.get_hooks():
                print '%s:%s (%s)' % (repo.name, hook.id, hook.name)
        except github.GithubException:
            print >> sys.stderr, ('Warning: Skipping  %s since I couldn\'t '
                                  'access hooks. Perhaps you don\'t have '
                                  'permission.' % repo.name)


def run_hooks(api, hooks):
    '''Triggers each of the provided hooks. Hooks should be in the format
    "<repo_name>:<hook_id>".
    '''
    for hook in hooks:
        repo_name, hook_id = hook.split(':', 1)
        repo = api.get_user().get_repo(repo_name)
        hook = repo.get_hook(int(hook_id))
        print 'Triggering hook %s for %s...' % (hook.name, repo_name),
        hook.test()
        print 'OK'


def main():
    '''Main entry point of the script.'''
    args = parse_args()
    api = github.Github(args.token)

    if args.action == 'list':
        list_hooks(api)
    elif args.action == 'run':
        hooks = args.hook
        if args.config:
            hooks = parse_lines(args.config)
        run_hooks(api, hooks)


if __name__ == '__main__':
    main()
