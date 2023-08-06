# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.
"""
Manipulating HAL documents.
"""

import urlparse
import itertools
import curie
import link
import UserDict
from functools import wraps

class CanonicalRels(UserDict.DictMixin):
    def __init__(self, rels, curie, base_uri):
        if hasattr(rels, 'iteritems'):
            items = rels.iteritems()
        else:
            items = rels

        self.curie = curie
        self.base_uri = base_uri
        self.rels = {}

        for key, value in items:
            canonical_key = self.canonical_key(key)
            if not canonical_key in self.rels:
                self.rels[canonical_key] = (key, value)
                continue

            original_key, current_value = self.rels[canonical_key]

            if not hasattr(current_value, 'append'):
                current_value = [current_value]
                self.rels[canonical_key] = original_key, current_value

            current_value.append(value)

        self.rels = self.rels

    def canonical_key(self, key):
        if key.startswith('/'):
            return urlparse.urljoin(self.base_uri, key)
        else:
            return self.curie.expand(key)

    def original_key(self, key):
        return self.rels[self.canonical_key(key)][0]

    def __getitem__(self, key):
        return self.rels[self.canonical_key(key)][1]

    def __contains__(self, key):
        return self.canonical_key(key) in self.rels

    def keys(self):
        return [original_key for original_key, _ in self.rels.itervalues()]

    def __equals__(self, other):
        canonical_other = CanonicalRels(other, self.curie, self.base_uri).links
        return self.rels == canonical_other


class Relationships(UserDict.DictMixin):
    """Merged view of relationships from a HAL document.

    Relationships, that is links and embedded resources, are presented as a
    dictionary-like object mapping the full URI of the link relationship type
    to a list of relationships.
    
    If there are both embedded resources and links for the same link relation
    type, the embedded resources will appear before the links. Otherwise,
    relationships are presented in the order they appear in their respective
    collection.

    Relationionships are deduplicated by their URL, as defined by their
    ``self`` link in the case of embedded resources and by their ``href``
    in the case of links. Only the first relationship with that URL will be
    included.
    
    """

    def __init__(self, links, embedded, curie):
        """Initialize a ``Relationships`` object.

        Parameters:

        - ``links``:    a dictionary mapping a link relationship type to a
                        ``Link`` instance or a ``list`` of ``Link``
                        instances.
        - ``embedded``: a dictionary mapping a link relationship type to a
                        ``Document`` instance or a ``list`` of ``Document``
                        instances.
        - ``curie``:    a ``CurieCollection`` instance used to expand
                        link relationship type into full link relationship type
                        URLs.

        """
        self.rels = {}

        item_urls = set()
        for key, values in itertools.chain(embedded.iteritems(),
                                           links.iteritems()):
            rel_key = curie.expand(key)

            for value in values:
                url = value.url()
                if url is not None and url in item_urls:
                    continue
                item_urls.add(url)
                
                self.rels.setdefault(rel_key, []).append(value)

    def __getitem__(self, key):
        return self.rels[key]

    def keys(self):
        return self.rels.keys()
         

def mutator(fn):
    """Decorator for ``Document`` methods that change the document.

    This decorator ensures that the object's caches are kept in sync
    when changes are made.
    
    """
    @wraps(fn)
    def deco(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        finally:
            self.prepare_cache()

    return deco


class Document(object):
    """Represents the document for a HAL resource.

    Constructors:

    - ``Document.empty(base_uri=None)``:
        returns an empty ``Document``.
    - ``Document.from_object(o, base_uri=None, parent_curie=None)``:
        returns a new ``Document`` based on a JSON object.

    Public Instance Attributes:

    - ``properties``: ``dict`` containing the properties of the HAL document,
                      excluding ``_links`` and ``_embedded``. ``properties``
                      should be treated as read-only.
    - ``links``: ``dict`` containing the document's links, excluding
                 ``curie``. Each link relationship type is mapped to a ``Link``
                 instance or a list of ``Link`` instances. ``links`` should be
                 treated as read-only.
    - ``embedded``: dictionary containing the document's embedded resources.
                    Each link relationship type is mapped to a ``Document``
                    instance.
    - ``rels``: a ``Relationships`` instance holding a merged view of the
                relationships from the document.

    """
    def __init__(self, o, base_uri, parent_curie=None):
        self.o = o
        self.parent_curie = parent_curie
        self.base_uri = base_uri
        self.prepare_cache()

    RESERVED_ATTRIBUTE_NAMES = ('_links', '_embedded')

    def prepare_cache(self):
        def properties_cache():
            properties = dict(self.o)
            for name in self.RESERVED_ATTRIBUTE_NAMES:
                properties[name] = None
                del properties[name]
            return properties

        def links_cache():
            links = {}

            for key, value in self.o.get("_links", {}).iteritems():
                if key == 'curie':
                    continue
                links[key] = link.Link.from_object(value, self.base_uri)

            return CanonicalRels(links, self.curie, self.base_uri)

        def load_curie_collection():
            result = curie.CurieCollection()
            if self.parent_curie is not None:
                result.update(self.parent_curie)

            curies = link.Link.from_object(
                self.o.get('_links', {}).get('curie', []),
                self.base_uri)

            if not isinstance(curies, list):
                curies = [curies]

            for curie_link in curies:
                result[curie_link.name] = curie_link

            return result

        def embedded_cache():
            embedded = {}
            for key, value in self.o.get("_embedded", {}).iteritems():
                embedded[key] = self.from_object(value,
                                                 self.base_uri,
                                                 self.curie)
            return CanonicalRels(embedded, self.curie, self.base_uri)

        self.properties = properties_cache()
        self.curie = load_curie_collection()
        self.links = links_cache()
        self.embedded = embedded_cache()
        self.rels = Relationships(self.links, self.embedded, self.curie)

    def url(self):
        """Returns the URL for the resource based on the ``self`` link.

        This method returns the ``href`` of the document's ``self`` link if it
        has one, or ``None`` if the document lacks a ``self`` link, or the
        ``href`` of the document's first ``self`` link if it has more than one.
        
        """
        if not 'self' in self.links:
            return None

        self_link = self.links['self']

        if isinstance(self_link, list):
            for link in self_link:
                return link.url()

        return self_link.url()

    def expand_curie(self, link):
        """Returns the expansion of a CURIE value.

        Arguments:
        - ``link``: a string holding a curie value to expand.

        This method attempts to expand ``link`` using the document's ``curie``
        collection (see ``curie.CurieCollection.expand``).

        """
        return self.curie.expand(link)

    def as_object(self):
        """Returns a dictionary representing the HAL JSON document."""
        return self.o

    def as_link(self):
        """Returns a `Link` to the resource."""
        return self.links['self']

    @mutator
    def set_property(self, key, value):
        """Set a property on the document.

        Calling code should use this method to add and modify properties
        on the document instead of modifying ``properties`` directly.

        If ``key`` is ``"_links"`` or ``"_embedded"`` this method will silently
        fail.

        If there is no property with the name in ``key``, a new property is
        created with the name from ``key`` and the value from ``value``. If
        the document already has a property with that name, it's value
        is replaced with the value in ``value``.

        """
        if key in self.RESERVED_ATTRIBUTE_NAMES:
            return
        self.o[key] = value

    @mutator
    def delete_property(self, key):
        """Remove an property from the document.

        Calling code should use this method to remove properties on the
        document instead of modifying ``properties`` directly.

        If there is a property with the name in ``key``, it will be removed.
        Otherwise, a ``KeyError`` will be thrown.

        """
        if key in self.RESERVED_ATTRIBUTE_NAMES:
            raise KeyError(key)
        del self.o[key]

    def link(self, href, **kwargs):
        """Retuns a new link relative to this resource."""
        return link.Link(dict(href=href, **kwargs), self.base_uri)

    @mutator
    def add_link(self, rel, target, **kwargs):
        """Adds a link to the document.

        Calling code should use this method to add links instead of
        modifying ``links`` directly.
        
        This method adds a link to the given ``target`` to the document with
        the given ``rel``. If one or more links are already present for that
        link relationship type, the new link will be added to the existing
        links for that link relationship type.

        If ``target`` is a string, a link is added with ``target`` as its
        ``href`` property and other properties from the keyword arguments.

        If ``target`` is a ``Link`` object, it is added to the document and the
        keyword arguments are ignored.

        If ``target`` is a ``Document`` object, ``target``'s ``self`` link is
        added to this document and the keyword arguments are ignored.

        Arguments:

        - ``rel``: a string specifying the link relationship type of the link.
          It should be a well-known link relation name from the IANA registry
          (http://www.iana.org/assignments/link-relations/link-relations.xml),
          a full URI, or a CURIE.
        - ``target``: the destination of the link.

        """
        if hasattr(target, 'as_link'):
            link = target.as_link()
        else:
            link = self.link(target, **kwargs)

        links = self.o.setdefault('_links', {})
        
        new_link = link.as_object()
        collected_links = CanonicalRels(links, self.curie, self.base_uri)
        if rel not in collected_links:
            links[rel] = new_link
            return

        original_rel = collected_links.original_key(rel)

        current_links = links[original_rel]
        if isinstance(current_links, list):
            current_links.append(new_link)
        else:
            links[original_rel] = [current_links, new_link]

    @mutator
    def delete_link(self, rel=None, href=lambda _: True):
        """Deletes links from the document.

        Calling code should use this method to remove links instead of
        modyfying ``links`` directly.

        The optional arguments, ``rel`` and ``href`` are used to select the
        links that will be deleted. If neither of the optional arguments are
        given, this method deletes every link in the document. If ``rel`` is
        given, only links for the matching link relationship type are deleted.
        If ``href`` is given, only links with a matching ``href`` are deleted.
        If both ``rel`` and ``href`` are given, only links with matching
        ``href`` for the matching link relationship type are delted.

        Arguments:

        - ``rel``: an optional string specifying the link relationship type of
                   the links to be deleted.
        - ``href``: optionally, a string specifying the ``href`` of the links
                    to be deleted, or a callable that returns true when its
                    single argument is in the set of ``href``s to be deleted.

        """
        if not '_links' in self.o:
            return

        if rel is None:
            for rel in self.o['_links'].keys():
                self.delete_link(rel, href)
            return

        if callable(href):
            href_filter = href
        else:
            href_filter = lambda x: x == href

        links = self.o['_links']
        links_for_rel = links.setdefault(rel, [])
        if isinstance(links_for_rel, dict):
            links_for_rel = [links_for_rel]

        new_links_for_rel = []
        for link in links_for_rel:
            if not href_filter(link['href']):
                new_links_for_rel.append(link)

        if new_links_for_rel:
            if len(new_links_for_rel) == 1:
                new_links_for_rel = new_links_for_rel[0]

            self.o['_links'][rel] = new_links_for_rel
        else:
            del self.o['_links'][rel]

        if not self.o['_links']:
            del self.o['_links']

    @classmethod
    def from_object(cls, o, base_uri=None, parent_curie=None):
        """Returns a new ``Document`` based on a JSON object.

        Arguments:

        - ``o``: a dictionary holding the deserializated JSON for the new
                 ``Document``, or a ``list`` of such documents.
        - ``base_uri``: optional URL used as the basis when expanding
                               relative URLs in the document.
        - ``parent_curie``: optional ``CurieCollection`` instance holding the
                            CURIEs of the parent document in which the new
                            document is to be embedded. Calling code should not
                            normally provide this argument.

        """
        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, base_uri), o)

        return cls(o, base_uri, parent_curie)

    @classmethod
    def empty(cls, base_uri=None):
        """Returns an empty ``Document``.

        Arguments:

        - ``base_uri``: optional URL used as the basis when expanding
                               relative URLs in the document.
        """
        return cls.from_object({}, base_uri=base_uri)

    @mutator
    def embed(self, rel, other):
        """Embeds a document inside this document.

        Arguments:

        - ``rel``: a string specifying the link relationship type of the
          embedded resource. ``rel`` should be a well-known link relation name
          from the IANA registry
          (http://www.iana.org/assignments/link-relations/link-relations.xml),
          a full URI, or a CURIE.
        - ``other``: a ``Document`` instance that will be embedded in this
          document.

        Calling code should use this method to add embedded resources instead
        of modifying ``embedded`` directly.
        
        This method embeds the given document in this document with the given
        ``rel``. If one or more documents have already been embedded for that
        ``rel``, the new document will be embedded in addition to those
        documents.

        """
        embedded = self.o.setdefault('_embedded', {})
        collected_embedded = CanonicalRels(embedded, self.curie, self.base_uri)

        if rel not in collected_embedded:
            embedded[rel] = other.as_object()
            return

        original_rel = collected_embedded.original_key(rel)

        current_embedded = embedded[original_rel]
        if isinstance(current_embedded, list):
            current_embedded.append(other.as_object())
        else:
            embedded[original_rel] = [current_embedded, other.as_object()]

    @mutator
    def delete_embedded(self, rel=None, href=lambda _: True):
        """Removes an embedded resource from this document.

        Calling code should use this method to remove embedded resources
        instead of modyfying ``embedded`` directly.

        The optional arguments, ``rel`` and ``href`` are used to select the
        embedded resources that will be removed. If neither of the optional
        arguments are given, this method removes every embedded resource from
        this document. If ``rel`` is given, only embedded resources for the
        matching link relationship type are removed. If ``href`` is given, only
        embedded resources with a ``self`` link matching ``href`` are deleted.
        If both ``rel`` and ``href`` are given, only embedded resources with
        matching ``self`` link for the matching link relationship type are
        removed.

        Arguments:

        - ``rel``: an optional string specifying the link relationship type of
                   the embedded resources to be removed.
        - ``href``: optionally, a string specifying the ``href`` of the
                    ``self`` links of the resources to be removed, or a
                    callable that returns true when its single argument matches
                    the ``href`` of the ``self`` link of one of the resources
                    to be removed.

        """
        if '_embedded' not in self.o:
            return

        if rel is None:
            for rel in self.o['_embedded'].keys():
                self.delete_embedded(rel, href)
            return

        if rel not in self.o['_embedded']:
            return

        if callable(href):
            url_filter = href
        else:
            url_filter = lambda x: x == href

        rel_embeds = self.o['_embedded'][rel]

        if isinstance(rel_embeds, dict):
            del self.o['_embedded'][rel]

            if not self.o['_embedded']:
                del self.o['_embedded']
            return

        new_rel_embeds = []
        for embedded in list(rel_embeds):
            embedded_doc = Document(embedded, self.base_uri)
            if not url_filter(embedded_doc.url()):
                new_rel_embeds.append(embedded)

        if not new_rel_embeds:
            del self.o['_embedded'][rel]
        elif len(new_rel_embeds) == 1:
            self.o['_embedded'][rel] = new_rel_embeds[0]
        else:
            self.o['_embedded'][rel] = new_rel_embeds

        if not self.o['_embedded']:
            del self.o['_embedded']

    def set_curie(self, name, href):
        """Sets a CURIE.

        A CURIE link with the given ``name`` and ``href`` is added to the
        document.

        """
        self.add_link('curie', href, name=name)

    @mutator
    def drop_curie(self, name):
        """Removes a CURIE.

        The CURIE link with the given name is removed from the document.

        """
        curies = self.o['_links']['curie']
        
        for i, curie in enumerate(curies):
            if curie['name'] == name:
                del curies[i]
                break

    def __iter__(self):
        yield self

    def __eq__(self, other):
        if not isinstance(other, Document):
            return False
        
        return self.as_object() == other.as_object()

    def __repr__(self):
        return "<Document %r>" % self.url()



