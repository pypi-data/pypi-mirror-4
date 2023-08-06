import os
import subprocess
import logging
import shutil
import urlparse
import urllib

from StringIO import StringIO
from ConfigParser import ConfigParser, NoOptionError

from utils import working_directory_keeper
from utils import use_or_open
logger = logging.getLogger(__name__)

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['PYTHONPATH'] = SUBPROCESS_ENV.pop(
    'BUILDOUT_ORIGINAL_PYTHONPATH', '')

SUPPORTED = {}


class UpdateError(subprocess.CalledProcessError):
    """Specific class for errors occurring during updates of existing repos.
    """


def update_check_call(*args, **kwargs):
    """Variant on subprocess.check_call that raises UpdateError."""
    try:
        subprocess.check_call(*args, **kwargs)
    except subprocess.CalledProcessError, e:
        raise UpdateError(e.returncode, e.cmd)


class BaseRepo(object):

    def __init__(self, target_dir, url, clear_retry=False,
                 offline=False, clear_locks=False, **options):

        self.target_dir = target_dir
        self.url = url
        self.clear_retry = clear_retry
        self.offline = offline
        self.clear_locks = clear_locks

        # additional options that may depend on the VCS subclass
        self.options = options

    def clear_target(self):
        shutil.rmtree(self.target_dir)

    def __call__(self, revision):
        try:
            self.get_update(revision)
        except UpdateError:
            if self.offline or not self.clear_retry:
                raise
            self.clear_target()
            self.get_update(revision)

    @classmethod
    def is_versioned(cls, path):
        """True if path exists and is versioned under this vcs.

        Common implementation based on vcs_control_dir class attribute.
        """
        return os.path.exists(os.path.join(path, cls.vcs_control_dir))

    @classmethod
    def fix_target(cls, target_dir):
        """Take into account that some targets are actually shifted below.

        That is the case of standalon addon (see launchpad #1012899).
        """

        if os.path.exists(target_dir) and not cls.is_versioned(target_dir):
            name = os.path.split(target_dir)[-1]
            new_target = os.path.join(target_dir, name)
            manifest = os.path.join(new_target, '__openerp__.py')
            if cls.is_versioned(new_target) and os.path.exists(manifest):
                return new_target
        return target_dir

    def uncommitted_changes(self):
        """True if we have uncommitted changes."""
        raise NotImplementedError

    def parents(self):
        """Return universal identifier for parent nodes, aka current revisions.

        There might be more than one with some VCSes (ex: pending merge in hg).
        """
        raise NotImplementedError


def get_update(vcs_type, target_dir, url, revision, **options):
    """General entry point."""
    cls = SUPPORTED.get(vcs_type)
    if cls is None:
        raise ValueError("Unsupported VCS type: %r" % vcs_type)

    # case of standalon addon (see launchpad #1012899)
    target_dir = cls.fix_target(target_dir)
    cls(target_dir, url, **options)(revision)


class HgRepo(BaseRepo):

    vcs_control_dir = '.hg'

    def update_hgrc_paths(self):
        """Update hgrc paths section if needed.

        Old paths are kept in renamed form: buildout_save_%d."""
        parser = ConfigParser()
        hgrc_path = os.path.join(self.target_dir, '.hg', 'hgrc')
        parser.read(hgrc_path)
        default = parser.get('paths', 'default')
        if default == self.url:
            return

        count = 1
        while True:
            save = 'buildout_save_%d' % count
            try:
                parser.get('paths', save)
            except NoOptionError:
                break
            count += 1

        parser.set('paths', save, default)
        parser.set('paths', 'default', self.url)
        f = open(hgrc_path, 'w')
        parser.write(f)
        f.close()

    def uncommitted_changes(self):
        """True if we have uncommitted changes."""
        p = subprocess.Popen(['hg', '--cwd', self.target_dir, 'status'],
                             stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
        return bool(p.communicate()[0])

    def parents(self):
        """Return full hash of parent nodes. """
        p = subprocess.Popen(['hg', '--cwd', self.target_dir, 'parents',
                              '--template={node}'],
                             stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
        return p.communicate()[0].split()

    def have_fixed_revision(self, revstr):
        """True if revstr is a fixed revision that we already have.

        Fixed in this case means that revstr is not an active branch
        """
        revstr = revstr.strip()
        if revstr == 'tip' or not revstr:
            return False
        try:
            subprocess.check_call(['hg', '--cwd', self.target_dir, 'log',
                                   '-r', revstr,
                                   '--template=[hg] found {rev}:{node}\n'],
                                  env=SUBPROCESS_ENV)
        except subprocess.CalledProcessError:
            return False

        # eliminate active branches
        p = subprocess.Popen(
            ['hg', '--cwd', self.target_dir, 'branches', '--active'],
            stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
        branches = p.communicate()[0]
        for branch in branches.split(os.linesep):
            if branch and branch.split()[0] == revstr:
                return False

        return True

    def get_update(self, revision):
        """Ensure that target_dir is a clone of url at specified revision.

        If target_dir already exists, does a simple pull.
        Offline-mode: no clone nor pull, but update.
        """
        target_dir = self.target_dir
        url = self.url
        offline = self.offline

        if not os.path.exists(target_dir):
            # TODO case of local url ?
            if offline:
                raise IOError(
                    "hg repository %r does not exist; "
                    "cannot clone it from %r (offline mode)" % (target_dir,
                                                                url))

            logger.info("Cloning %s ...", url)
            clone_cmd = ['hg', 'clone']
            if revision:
                clone_cmd.extend(['-r', revision])
            clone_cmd.extend([url, target_dir])
            subprocess.check_call(clone_cmd, env=SUBPROCESS_ENV)
        else:
            self.update_hgrc_paths()
            # TODO what if remote repo is actually local fs ?
            if self.have_fixed_revision(revision):
                self._update(revision)
                return

            if not offline:
                logger.info("Pull for hg repo %r ...", target_dir)
                subprocess.check_call(['hg', '--cwd', target_dir, 'pull'],
                                      env=SUBPROCESS_ENV)
            self._update(revision)

    def _update(self, revision):
        target_dir = self.target_dir
        logger.info("Updating %s to revision %s", target_dir, revision)
        up_cmd = ['hg', '--cwd', target_dir, 'up']
        if revision:
            up_cmd.extend(['-r', revision])
        update_check_call(up_cmd, env=SUBPROCESS_ENV)

    def archive(self, target_path):
        subprocess.check_call(['hg', '--cwd', self.target_dir,
                               'archive', target_path])

SUPPORTED['hg'] = HgRepo

try:
    from bzrlib.plugins.launchpad.lp_directory import LaunchpadDirectory
except ImportError:
    LPDIR = None
else:
    LPDIR = LaunchpadDirectory()


class BzrBranch(BaseRepo):
    """Represent a Bazaar branch tied to a reference branch."""

    vcs_control_dir = '.bzr'

    def __init__(self, *a, **kw):
        super(BzrBranch, self).__init__(*a, **kw)
        if self.url.startswith('lp:'):
            if LPDIR is None:
                raise RuntimeError(
                    "To use launchpad locations (lp:), bzrlib must be "
                    "importable. Please also take care that it's the same "
                    "or working exactly as the one behind the bzr executable")

            # first arg (name) of look_up is acturally ignored
            url = LPDIR.look_up('', self.url)
            parsed = list(urlparse.urlparse(url))
            parsed[2] = urllib.quote(parsed[2])
            self.url = urlparse.urlunparse(parsed)

    def conf_file_path(self):
        return os.path.join(self.target_dir, '.bzr', 'branch', 'branch.conf')

    def parse_conf(self, from_file=None):
        """Return a dict of paths from standard conf (or the given file-like)

        Reference: http://doc.bazaar.canonical.com/bzr.0.18/configuration.htm

        >>> from pprint import pprint
        >>> from StringIO import StringIO
        >>> branch = BzrBranch('', '')
        >>> pprint(branch.parse_conf(StringIO(os.linesep.join([
        ...        "parent_location = /some/path",
        ...        "submit_location = /other/path"]))))
        {'parent_location': '/some/path', 'submit_location': '/other/path'}
        """
        with use_or_open(from_file, self.conf_file_path()) as conffile:
            return dict((name.strip(), url.strip())
                        for name, url in (
                            line.split('=', 1) for line in conffile
                            if not line.startswith('#') and '=' in line))

    def write_conf(self, conf, to_file=None):
        """Write counterpart to read_conf (see docstring of read_conf)
        """
        lines = ('%s = %s' % (k, v) + os.linesep
                 for k, v in conf.items())
        with use_or_open(to_file, self.conf_file_path(), 'w') as conffile:
            conffile.writelines(lines)

    def update_conf(self):
        conf = self.parse_conf()
        old_parent = conf['parent_location']
        if old_parent == self.url:
            return
        count = 1
        while True:
            save = 'buildout_save_parent_location_%d' % count
            if save not in conf:
                conf[save] = old_parent
                break
            count += 1
        conf['parent_location'] = self.url
        self.write_conf(conf)

    def uncommitted_changes(self):
        """True if we have uncommitted changes."""
        p = subprocess.Popen(['bzr', 'status', self.target_dir],
                             stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
        return bool(p.communicate()[0])

    def parents(self):
        """Return current revision.

        Must be used in conjunction with uncommitted_changes to be sure
        that we are indeed on this revision
        """

        p = subprocess.Popen(['bzr', 'revno', '--tree', self.target_dir],
                             stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
        return [p.communicate()[0].strip()]

    def _update(self, revision):
        """Update existing branch at target dir to given revision.

        raise UpdateError in case of problems."""

        update_check_call(['bzr', 'up', '-r', revision, self.target_dir],
                          env=SUBPROCESS_ENV)
        logger.info("Updated %r to revision %s", self.target_dir, revision)

    def is_fixed_revision(self, revstr):
        """True iff the given revision string is for a fixed revision."""

        revstr = revstr.strip()  # one never knows
        if not revstr or revstr.startswith('last:'):
            return False
        try:
            revno = int(revstr)
        except TypeError:
            return True
        else:
            return revno >= 0

    def get_update(self, revision):
        """Ensure that target_dir is a branch of url at specified revision.

        If target_dir already exists, does a simple pull.
        Offline-mode: no branch nor pull, but update.
        In all cases, an attempt to update is performed before any pull
        """
        target_dir = self.target_dir
        url = self.url
        offline = self.offline
        clear_locks = self.clear_locks

        if not os.path.exists(target_dir):
            # TODO case of local url ?
            if offline:
                raise IOError(
                    "bzr branch %s does not exist; cannot branch it from "
                    "%s (offline mode)" % (target_dir, url))

            logger.info("Branching %s ...", url)
            branch_cmd = ['bzr', 'branch']
            if self.options.get('bzr-stacked-branches',
                                'false').strip().lower() == 'true':
                branch_cmd.append('--stacked')

            if revision:
                branch_cmd.extend(['-r', revision])
            branch_cmd.extend([url, target_dir])
            subprocess.check_call(branch_cmd, env=SUBPROCESS_ENV)
        else:
            # TODO what if bzr source is actually local fs ?
            if clear_locks:
                yes = StringIO()
                yes.write('y')
                yes.seek(0)
                logger.info("Break-lock for branch %s ...", target_dir)
                # GR newer versions of bzr have a --force option, but this call
                # works also for older ones (fortunately we don't need a pty)
                p = subprocess.Popen(['bzr', 'break-lock', target_dir],
                                     subprocess.PIPE)
                out, err = p.communicate(input='y')
                if p.returncode != 0:
                    raise subprocess.CalledProcessError(
                        p.returncode, repr(['bzr', 'break-lock', target_dir]))

            self.update_conf()

            if self.is_fixed_revision(revision):
                try:
                    self._update(revision)
                except UpdateError:
                    if offline:
                        raise
                else:
                    return

            logger.info("Pull for branch %s ...", target_dir)
            update_check_call(['bzr', 'pull', '-d', target_dir],
                              env=SUBPROCESS_ENV)
            self._update(revision)

    def archive(self, target_path):
        with working_directory_keeper:
            os.chdir(self.target_dir)
            subprocess.check_call(['bzr', 'export', target_path])


SUPPORTED['bzr'] = BzrBranch


class GitRepo(BaseRepo):
    """Represent a Git clone tied to a reference branch."""

    vcs_control_dir = '.git'

    def get_update(self, revision):
        """Ensure that target_dir is a branch of url at specified revision.

        If target_dir already exists, does a simple pull.
        Offline-mode: no branch nor pull, but update.
        """
        target_dir = self.target_dir
        url = self.url
        offline = self.offline
        rev_str = revision

        with working_directory_keeper:
            if not os.path.exists(target_dir):
                # TODO case of local url ?
                if offline:
                    raise IOError(
                        "git repository %s does not exist; cannot clone it "
                        "from %s (offline mode)" % (target_dir, url))

                os.chdir(os.path.split(target_dir)[0])
                logger.info("Cloning %s ...", url)
                subprocess.check_call(['git', 'clone', '-b',
                                       rev_str, url, target_dir])
            else:
                os.chdir(target_dir)
                # TODO what if remote repo is actually local fs ?
                if not offline:
                    logger.info("Pull for git repo %s (rev %s)...",
                                target_dir, rev_str)
                    subprocess.check_call(['git', 'pull',
                                          url, rev_str])
                elif revision:
                    logger.info("Checkout %s to revision %s",
                                target_dir, revision)
                    subprocess.check_call(['git', 'checkout', rev_str])


SUPPORTED['git'] = GitRepo


class SvnCheckout(BaseRepo):

    vcs_control_dir = '.svn'

    def get_update(self, revision):
        """Ensure that target_dir is a branch of url at specified revision.

        If target_dir already exists, does a simple pull.
        Offline-mode: no branch nor pull, but update.
        """
        target_dir = self.target_dir
        url = self.url
        offline = self.offline

        rev_str = revision and '-r ' + revision or ''

        with working_directory_keeper:
            if not os.path.exists(target_dir):
                # TODO case of local url ?
                if offline:
                    raise IOError(
                        "svn checkout %s does not exist; cannot checkout "
                        "from %s (offline mode)" % (target_dir, url))

                os.chdir(os.path.split(target_dir)[0])
                logger.info("Checkouting %s ...", url)
                subprocess.check_call('svn checkout %s %s %s' % (
                    rev_str, url, target_dir), shell=True)
            else:
                os.chdir(target_dir)
                # TODO what if remote repo is actually local fs ?
                if offline:
                    logger.warning(
                        "Offline mode: keeping checkout %s in its current rev",
                        target_dir)
                else:
                    logger.info("Updating %s to location %s, revision %s...",
                                target_dir, url, revision)
                    # switch is necessary in order to move in tags
                    # TODO support also change of svn root url
                    subprocess.check_call('svn switch %s' % url, shell=True)
                    subprocess.check_call('svn up %s' % rev_str,
                                          shell=True)

SUPPORTED['svn'] = SvnCheckout
