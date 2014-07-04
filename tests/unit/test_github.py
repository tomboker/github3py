import pytest

from github3 import GitHubError
from github3.github import GitHub

from .helper import UnitHelper, UnitIteratorHelper


def url_for(path=''):
    return 'https://api.github.com/' + path.strip('/')


class TestGitHub(UnitHelper):
    described_class = GitHub
    example_data = None

    def test_two_factor_login(self):
        self.instance.login('username', 'password',
                            two_factor_callback=lambda *args: 'foo')

    def test_can_login_without_two_factor_callback(self):
        self.instance.login('username', 'password')
        self.instance.login(token='token')


class TestGitHubIterators(UnitIteratorHelper):
    described_class = GitHub
    example_data = None

    def test_starred(self):
        """
        Show that one can iterate over an authenticated user's stars.
        """
        i = self.instance.starred()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/starred'),
            params={'per_page': 100},
            headers={}
        )

    def test_starred_requires_auth(self):
        """Show that one needs to authenticate to use #starred."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.starred()

    def test_starred_by(self):
        """Show that one can iterate over a user's stars."""
        i = self.instance.starred_by('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/starred'),
            params={'per_page': 100},
            headers={}
        )

    def test_subscriptions(self):
        """
        Show that one can iterate over an authenticated user's subscriptions.
        """
        i = self.instance.subscriptions()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/subscriptions'),
            params={'per_page': 100},
            headers={}
        )

    def test_subscriptions_for(self):
        """Show that one can iterate over a user's subscriptions."""
        i = self.instance.subscriptions_for('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/subscriptions'),
            params={'per_page': 100},
            headers={}
        )

    def test_user_issues(self):
        """Test that one can iterate over a user's issues."""
        i = self.instance.user_issues()
        # Get the next item from the iterator
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/issues'),
            params={'per_page': 100},
            headers={}
        )

    def test_user_issues_requires_auth(self):
        """
        Test that one must authenticate to interate over a user's issues.
        """
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.user_issues()

    def test_user_issues_with_parameters(self):
        """Test that one may pass parameters to GitHub#user_issues."""
        # Set up the parameters to be sent
        params = {'filter': 'assigned', 'state': 'closed', 'labels': 'bug',
                  'sort': 'created', 'direction': 'asc',
                  'since': '2012-05-20T23:10:27Z', 'per_page': 25}

        # Make the call with the paramters
        i = self.instance.user_issues(**params)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/issues'),
            params=params,
            headers={}
        )

    def test_user_repos(self):
        """Test that one can iterate over a user's repositories."""
        i = self.instance.user_repos('sigmavirus24')

        # Get the next item from the iterator
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/repos'),
            params={'per_page': 100},
            headers={}
        )

    def test_user_repos_with_type(self):
        """
        Test that one can iterate over a user's repositories with a type.
        """
        i = self.instance.user_repos('sigmavirus24', 'all')

        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/repos'),
            params={'per_page': 100, 'type': 'all'},
            headers={}
        )


class TestGitHubAuthorizations(UnitHelper):
    described_class = GitHub
    example_data = None

    def create_session_mock(self, *args):
        session = super(TestGitHubAuthorizations,
                        self).create_session_mock(*args)
        session.retrieve_client_credentials.return_value = ('id', 'secret')
        return session

    def test_revoke_authorization(self):
        """Test that GitHub#revoke_authorization calls the expected methods.

        It should use the session's delete and temporary_basic_auth methods.
        """
        self.instance.revoke_authorization('access_token')
        self.session.delete.assert_called_once_with(
            'https://api.github.com/applications/id/tokens/access_token',
            params={'client_id': None, 'client_secret': None}
        )
        self.session.temporary_basic_auth.assert_called_once_with(
            'id', 'secret'
        )

    def test_revoke_authorizations(self):
        """Test that GitHub#revoke_authorizations calls the expected methods.

        It should use the session's delete and temporary_basic_auth methods.
        """
        self.instance.revoke_authorizations()
        self.session.delete.assert_called_once_with(
            'https://api.github.com/applications/id/tokens',
            params={'client_id': None, 'client_secret': None}
        )
        self.session.temporary_basic_auth.assert_called_once_with(
            'id', 'secret'
        )
