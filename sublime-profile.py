import os, datetime
import sublime
import sublime_plugin
import subprocess


def run_command(args):
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            startupinfo=startupinfo, stderr=subprocess.PIPE)

    print('=>', ' '.join(args))

    result = proc.stdout.read()
    err = proc.stderr.read()

    return (result, err, proc.returncode)


def load_settings():
    # self.settings = sublime.load_settings('GitGutter.sublime-settings')
    self.user_settings = sublime.load_settings('Preferences.sublime-settings')

    # Git Binary Setting
    self.git_binary_path = 'git'
    git_binary = self.user_settings.get('git_binary') or self.settings.get('git_binary')
    if git_binary:
        self.git_binary_path = git_binary


def write_gitignore():

    tpl = '''
Package Control.last-run
Package Control.ca-list
Package Control.ca-bundle
Package Control.system-ca-bundle
Package Control.cache/
Package Control.ca-certs/
    '''.strip()

    gitignore_path = os.path.join(sublime.packages_path(), 'User', '.gitignore')

    if not os.path.isfile(gitignore_path):
        with open(gitignore_path, 'w') as gitignore_file:
            gitignore_file.write(tpl)

class GitHelper:

    def __init__(self):
        self.git_binary_path = 'git'

    def git_command(self, command, args):

        a = list(args)
        a.insert(0, command)

        (result, err, returncode) = run_command([self.git_binary_path] + a)

        print('=>', err)

        return returncode

    def init(self):

        user_dir = os.path.join(sublime.packages_path(), 'User')

        os.chdir(user_dir)

        if not os.path.isdir(os.path.join(user_dir, '.git')):

            print('Creating repo in {}...'.format(user_dir))

            self.git_command('init')

    # def __getattribute__(self, name):

        # print('calling get attr', name)

        # return self.git_command(name, )

    def add(self, *args):

        return self.git_command('add', args)

    def commit(self, *args):

        return self.git_command('commit', args)

    def remote(self, *args):

        return self.git_command('remote', args)

    def push(self, *args):

        return self.git_command('push', args)

    def fetch(self, *args):

        return self.git_command('fetch', args)

    def checkout(self, github_user):

        args = []

        if (run_command(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/{}'.format(github_user)]) is 0):
            args.append('-b')

        args.append(github_user)

        return self.git_command('checkout', args)

git = GitHelper()

class SublimeprofileSaveCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.git_binary_path = 'git'
        self.view = view

    def run(self, edit):

        # Init git repo if not there
        write_gitignore()
        git.init()

        git.add('.')

        git.commit('-am', '{}'.format(datetime.datetime.now()))

        # Add username as remote
        github_user = 'third-eye-brown'
        github_pass = 'Ws3Qa2ii'

        repo_name = 'sublime-profile'

        # rm Package\ Control.{last-run,ca-list,ca-bundle,system-ca-bundle,ca-certs}

        # git.remote('add', github_user, 'https://{0}@github.com/{0}/{1}.git'.format(github_user, repo_name))

        # git.push(github_user, 'HEAD:master')

class SublimeprofileUseCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        # git.feltch

        self.view.window().show_input_panel("username:", "", self.on_done, None, None)

    def on_done(self, github_user):
        write_gitignore()
        git.init()

        repo_name = 'sublime-profile'

        # git.remote('add', github_user, 'https://{0}@github.com/{0}/{1}.git'.format(github_user, repo_name))

        git.fetch(github_user)

        git.checkout(github_user)

        # sublime.load_settings('Package Control.sublime-settings')
