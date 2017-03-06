from __future__ import absolute_import

from ..hubstorage.activity import Activity as _Activity
from ..hubstorage.collectionsrt import Collections as _Collections
from ..hubstorage.project import Settings as _Settings

from .activity import Activity
from .collections import Collections
from .frontiers import _HSFrontier, Frontiers
from .jobs import Jobs
from .spiders import Spiders
from .utils import _Proxy
from .utils import parse_project_id


class Projects(object):
    """Collection of projects available to current user.

    Not a public constructor: use :class:`Scrapinghub` client instance to get
    a :class:`Projects` instance. See :attr:`Scrapinghub.projects` attribute.

    Usage::

        >>> client.projects
        <scrapinghub.client.Projects at 0x1047ada58>
    """

    def __init__(self, client):
        self._client = client

    def get(self, projectid):
        """Get project for a given project id.

        :param projectid: integer or string numeric project id.
        :return: :class:`Project` object.
        :rtype: scrapinghub.client.Project.

        Usage::

            >>> project = client.projects.get(123)
            >>> project
            <scrapinghub.client.Project at 0x106cdd6a0>
        """
        return Project(self._client, parse_project_id(projectid))

    def list(self):
        """Get list of projects available to current user.

        :return: a list of integer project ids.

        Usage::

            >>> client.projects.list()
            [123, 456]
        """
        return self._client._connection.project_ids()

    def iter(self):
        """Iterate through list of projects available to current user.

        Provided for the sake of API consistency.
        """
        return iter(self.list())

    def summary(self, **params):
        """Get short summaries for all available user projects.

        :return: a list of dictionaries: each dictionary represents a project
            summary (amount of pending/running/finished jobs and a flag if it
            has a capacity to schedule new jobs).

        Usage::

            >>> client.projects.summary()
            [{'finished': 674,
              'has_capacity': True,
              'pending': 0,
              'project': 123,
              'running': 1},
             {'finished': 33079,
              'has_capacity': True,
              'pending': 0,
              'project': 456,
              'running': 2}]
        """
        return self._client._hsclient.projects.jobsummaries(**params)


class Project(object):
    """Class representing a project object and its resources.

    Not a public constructor: use :class:`ScrapinghubClient` instance or
    :class:`Projects` instance to get a :class:`Project` instance. See
    :meth:`Scrapinghub.get_project` or :meth:`Projects.get_project` methods.

    :ivar id: integer project id.
    :ivar activity: :class:`Activity` resource object.
    :ivar collections: :class:`Collections` resource object.
    :ivar frontier: :class:`Frontier` resource object.
    :ivar jobs: :class:`Jobs` resource object.
    :ivar settings: :class:`Settings` resource object.
    :ivar spiders: :class:`Spiders` resource object.

    Usage::

        >>> project = client.get_project(123)
        >>> project
        <scrapinghub.client.Project at 0x106cdd6a0>
        >>> project.key
        '123'
    """

    def __init__(self, client, projectid):
        self.key = str(projectid)
        self._client = client

        # sub-resources
        self.jobs = Jobs(client, projectid)
        self.spiders = Spiders(client, projectid)

        # proxied sub-resources
        self.activity = Activity(_Activity, client, projectid)
        self.collections = Collections(_Collections, client, projectid)
        self.frontiers = Frontiers(_HSFrontier, client, projectid)
        self.settings = Settings(_Settings, client, projectid)


class Settings(_Proxy):
    """Class representing job metadata.

    Not a public constructor: use :class:`Project` instance to get a
    :class:`Settings` instance. See :attr:`Project.settings` attribute.

    Usage::

    - request project settings

        >>> settings = project.settings
        >>> settings
        Settings({'default_job_units': 1, 'job_runtime_limit': 24})

    - get length of project settings

        >>> len(project.settings)
        2

    - iterate through project settings keys

        >>> project.settings.iter()
        <dict_keyiterator at 0x106ae9cc8>

    - list project settings keys

        >>> project.settings.list()
        ['default_job_units', 'job_runtime_limit']

    - get setting value by name

        >>> project.settings['default_job_units']
        1

    - get setting value by name from server

        >>> project.settings.liveget('default_job_units')
        1

    - update setting value (some settings are read-only)

        >>> project.setting['default_job_units'] = 2

    - save updated settings on server

        >>> project.settings.save()

    - expire project settings local cache

        >>> project.settings.expire()
    """
