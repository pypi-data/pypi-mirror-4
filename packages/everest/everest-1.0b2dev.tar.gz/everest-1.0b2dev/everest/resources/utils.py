"""
Resource related utilities.

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Nov 3, 2011.
"""
from everest.interfaces import IResourceUrlConverter
from everest.repositories.constants import REPOSITORY_TYPES
from everest.repositories.interfaces import IRepositoryManager
from everest.repositories.utils import as_repository
from everest.resources.interfaces import ICollectionResource
from everest.resources.interfaces import IMemberResource
from everest.resources.interfaces import IRelation
from everest.resources.interfaces import IResource
from everest.resources.interfaces import IService
from everest.utils import get_repository_manager
from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import get_current_request
from pyramid.traversal import model_path
from urlparse import urlparse
from urlparse import urlunparse
from zope.interface import providedBy as provided_by # pylint: disable=E0611,F0401
from zope.interface.interfaces import IInterface # pylint: disable=E0611,F0401

__docformat__ = 'reStructuredText en'
__all__ = ['as_member',
           'get_collection_class',
           'get_member_class',
           'get_resource_class_for_relation',
           'get_resource_url',
           'get_root_collection',
           'is_resource_url',
           'provides_collection_resource',
           'provides_member_resource',
           'provides_resource',
           'resource_to_url',
           'url_to_resource',
           ]


def get_root_collection(resource):
    """
    Returns a clone of the collection from the repository registered for the
    given registered resource.

    :param resource: registered resource
    :type resource: class implementing or instance providing or subclass of
        a registered resource interface.
    """
    repo = as_repository(resource)
    return repo.get_collection(resource)


def new_stage_collection(resource):
    """
    Returns a new, empty collection matching the given registered resource.

    :param resource: registered resource
    :type resource: class implementing or instance providing or subclass of
        a registered resource interface.
    """
    repo_mgr = get_repository_manager()
    new_repo = repo_mgr.new(REPOSITORY_TYPES.MEMORY)
    new_repo.register_resource(resource)
    new_repo.initialize()
    return new_repo.get_collection(resource)


def get_member_class(resource):
    """
    Returns the registered member class for the given resource.

    :param resource: registered resource
    :type resource: class implementing or instance providing or subclass of
        a registered resource interface.
    """
    reg = get_current_registry()
    if IInterface in provided_by(resource):
        member_class = reg.getUtility(resource, name='member-class')
    else:
        member_class = reg.getAdapter(resource, IMemberResource,
                                      name='member-class')
    return member_class


def get_collection_class(resource):
    """
    Returns the registered collection resource class for the given marker
    interface or member resource class or instance.

    :param rc: registered resource
    :type rc: class implementing or instance providing or subclass of
        a registered resource interface.
    """
    reg = get_current_registry()
    if IInterface in provided_by(resource):
        coll_class = reg.getUtility(resource, name='collection-class')
    else:
        coll_class = reg.getAdapter(resource, ICollectionResource,
                                    name='collection-class')
    return coll_class


def get_resource_class_for_relation(relation):
    """
    Returns the resource class that was registered for the given
    relation.
    
    :param str relation: relation string.
    """
    reg = get_current_registry()
    return reg.getUtility(IRelation, name=relation)


def as_member(entity, parent=None):
    """
    Adapts an object to a location aware member resource.

    :param entity: a domain object for which a resource adapter has been
        registered
    :type entity: an object implementing
        :class:`everest.entities.interfaces.IEntity`
    :param parent: optional parent collection resource to make the new member
        a child of
    :type parent: an object implementing
        :class:`everest.resources.interfaces.ICollectionResource`
    :returns: an object implementing
        :class:`everest.resources.interfaces.IMemberResource`
    """
    reg = get_current_registry()
    rc = reg.getAdapter(entity, IMemberResource)
    if not parent is None:
        rc.__parent__ = parent # interface method pylint: disable=E1121
    return rc


def is_resource_url(url_string):
    """
    Checks if the given URL string is a resource URL.

    Currently, this check only looks if the URL scheme is either "http" or
    "https".
    """
    return isinstance(url_string, basestring) \
           and urlparse(url_string).scheme in ('http', 'https') # pylint: disable=E1101


def get_resource_url(resource):
    """
    Returns the URL for the given resource.
    """
    path = model_path(resource)
    parsed = list(urlparse(path))
    parsed[1] = ""
    return urlunparse(parsed)


def provides_resource(obj):
    """
    Checks if the given type or instance provides the
    :class:`everest.resources.interfaces.IResource` interface.
    """
    if isinstance(obj, type):
        obj = object.__new__(obj)
    return IResource in provided_by(obj)


def provides_member_resource(obj):
    """
    Checks if the given type or instance provides the
    :class:`everest.resources.interfaces.IMemberResource` interface.
    """
    if isinstance(obj, type):
        obj = object.__new__(obj)
    return IMemberResource in provided_by(obj)


def provides_collection_resource(obj):
    """
    Checks if the given type or instance provides the
    :class:`everest.resources.interfaces.ICollectionResource` interface.
    """
    if isinstance(obj, type):
        obj = object.__new__(obj)
    return ICollectionResource in provided_by(obj)


def get_registered_collection_resources():
    """
    Returns a list of all registered collection resource classes.
    """
    reg = get_current_registry()
    return [util.component
            for util in reg.registeredUtilities()
            if util.name == 'collection-class']


def get_repository(name):
    """
    Returns the resource repository with the given name.
    """
    reg = get_current_registry()
    repo_mgr = reg.getUtility(IRepositoryManager)
    return repo_mgr.get(name)


def get_service():
    """
    Registers the object registered as the service utility.
    
    :returns: object implementing 
        :class:`everest.interfaces.IService`
    """
    reg = get_current_registry()
    return reg.getUtility(IService)


def resource_to_url(resource, request=None):
    """
    Converts the given resource to a URL.
    """
    if request is None:
        request = get_current_request()
#    cnv = request.registry.getAdapter(request, IResourceUrlConverter)
    reg = get_current_registry()
    cnv = reg.getAdapter(request, IResourceUrlConverter)
    return cnv.resource_to_url(resource)


def url_to_resource(url, request=None):
    """
    Converts the given URL to a resource.
    """
    if request is None:
        request = get_current_request()
#    cnv = request.registry.getAdapter(request, IResourceUrlConverter)
    reg = get_current_registry()
    cnv = reg.getAdapter(request, IResourceUrlConverter)
    return cnv.url_to_resource(url)

