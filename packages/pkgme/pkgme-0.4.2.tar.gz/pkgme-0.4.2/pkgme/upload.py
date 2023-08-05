import os

from launchpadlib import (
    errors,
    uris,
    )
from launchpadlib.launchpad import Launchpad

from pkgme.errors import PkgmeError
from pkgme.run_script import run_subprocess


APPLICATION_NAME = 'pkgme'
CACHE_DIR = os.path.expanduser('~/.launchpadlib/cache')
SERVICE_ROOT = uris.LPNET_SERVICE_ROOT


def upload(changes_file, ppa_name):
    """Upload 'changes_file' to 'ppa_name'.

    Raise errors if this is not allowed.
    """
    lp = MyLaunchpad.login()
    lp.check_can_upload_to_ppa(ppa_name)
    dput(ppa_name, changes_file)


def dput(ppa_name, changes_file):
    """Use 'dput' to upload to a PPA."""
    return run_subprocess(['dput', ppa_name, changes_file])


class InvalidPPAName(PkgmeError):

    def __init__(self, ppa_name):
        self.ppa_name = ppa_name

    def __str__(self):
        return 'Invalid PPA name: %s. Expected "ppa:<person>/<archive>".' % (
            self.ppa_name,)


class NotFound(PkgmeError):
    def __init__(self, name):
        super(PkgmeError, self).__init__()
        self.name = name


class NoSuchPerson(NotFound):
    def __str__(self):
        return 'No such person: %s' % (self.name,)


class NoSuchPPA(NotFound):
    def __str__(self):
        return 'No such PPA: %s' % (self.name,)


class CannotUpload(PkgmeError):

    def __init__(self, person, ppa_name, team):
        self.person = person
        self.ppa_name = ppa_name
        self.team = team

    def __str__(self):
        return '%s cannot upload to %s. Must be a member of ~%s' % (
            self.person.name, self.ppa_name, self.team.name)


def parse_ppa_name(ppa_name):
    """Parse 'ppa_name' into its components.

    'ppa_name' is expected to be of the form "ppa:<team_name>/<archive_name>".
    i.e. the form accepted by 'dput' and 'apt-add-repository'.

    :raise InvalidPPAName: If 'ppa_name' cannot be parsed.
    :return: (team_name, archive_name)
    """
    try:
        host, rest = ppa_name.split(':')
    except ValueError:
        raise InvalidPPAName(ppa_name)
    if host != 'ppa':
        raise InvalidPPAName(ppa_name)
    try:
        person_name, archive_name = rest.split('/')
    except ValueError:
        raise InvalidPPAName(ppa_name)
    return person_name, archive_name


class MyLaunchpad(object):

    def __init__(self, launchpad):
        self._launchpad = launchpad

    @classmethod
    def login(cls, service_root=SERVICE_ROOT):
        return cls(Launchpad.login_with(APPLICATION_NAME, service_root, CACHE_DIR))

    def _user_in_team(self, user, team):
        if user.name == team.name:
            return True
        return team in user.super_teams

    def check_can_upload_to_ppa(self, ppa_name, user=None):
        """Check to see if 'user' can upload to 'ppa_name'.

        Raise errors if they cannot.
        """
        if user is None:
            user = self._launchpad.me
        team_name, archive_name = parse_ppa_name(ppa_name)
        try:
            team = self._launchpad.people[team_name]
        except KeyError:
            raise NoSuchPerson(team_name)
        try:
            team.getPPAByName(name=archive_name)
        except errors.NotFound:
            raise NoSuchPPA(ppa_name)
        if not self._user_in_team(user, team):
            raise CannotUpload(user, ppa_name, team)
