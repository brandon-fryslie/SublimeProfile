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


def fail(message):
    print(message)
    exit()

class GitHelper:

    def __init__(self):
        self.git_binary_path = 'git'
        self.repo_name = 'sublime-profile'

    def ensure_gitignore():

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

    def git_command(self, command, *args):
        a = list(args)

        a.insert(0, command)

        (result, err, returncode) = run_command([self.git_binary_path] + a)

        print('=>', err)

        return returncode

    def ensure_git_repo(self):

        user_dir = os.path.join(sublime.packages_path(), 'User')

        os.chdir(user_dir)

        if not os.path.isdir(os.path.join(user_dir, '.git')):

            print('Creating repo in {}...'.format(user_dir))

            self.ensure_gitignore()

            self.git_command('init')

            # Setting always rebase
            self.git_command('config', 'branch.autosetuprebase', 'always')

    def add(self, *args):

        return self.git_command('add', args)

    def save_profile(self, message):

        message = str(message)

        self.git_command('add', '.')

        current_branch = self.get_current_branch()

        print('current_branch: ', current_branch)

        self.ensure_remote(current_branch)

        self.git_command('commit', '-m', message)

        self.git_command('push', current_branch, 'HEAD:{}'.format(current_branch))

        return

    def load_profile(self, profile_name):
        self.git_command('fetch', profile_name)
        self.git_command('checkout', profile_name)

        sublime.load_settings('Package Control.sublime-settings')


    def get_current_dir(self):
        (result, _, _) = run_command(['pwd'])
        print(result)

    def get_current_branch(self):
        (result, _, _) = run_command([self.git_binary_path, 'symbolic-ref', 'HEAD', '2>/dev/null', '|', 'cut', '-d"/"', '-f', '3'])

        self.get_current_dir()

        return str(result)

    def ensure_on_branch(branch):
        if (this.get_current_branch()) != branch:
            self.checkout(branch)

    def ensure_remote(self, username):

        if (self.git_command('ls-remote', username) is 1):
            self.git_command('remote', 'https://{0}@github.com/{0}/{1}.git'.format(github_user, self.repo_name))

        return

    def push(self, *args):

        return self.git_command('push', args)

    def fetch(self, *args):

        return self.git_command('fetch', args)

    def checkout(self, github_user):

        args = []

        self.git_command('show-ref', '--verify', '--quiet', 'refs/heads/{}'.format(github_user))

        # Check if local branch already exists
        if (run_command(['git', ]) is 0):
            args.append('-b')

        args.append(github_user)

        return self.git_command('checkout', args)

git = GitHelper()

class SublimeprofileSaveCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.git_binary_path = 'git'
        self.view = view

    def run(self, edit):

        # self.view.window().show_input_panel("message:", "", self.on_done, None, None)
    
    # def on_done(self, message):

        git.ensure_git_repo()

        # if message is '':
        message = datetime.datetime.now()

        git.save_profile(message)

class SublimeprofileUseCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        self.view.window().show_input_panel("username:", "", self.on_done, None, None)

    def on_done(self, profile_name):

        git.ensure_git_repo()

        git.load_profile(profile_name)

class SublimeprofileEditCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_command(['subl', '-n', os.path.expanduser('~/Library/Application Support/Sublime Text 3/Packages/User')])