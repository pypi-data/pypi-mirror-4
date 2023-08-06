#!/usr/bin/python
# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import unittest
import dougrain

class ParseSimpleTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.from_object({"name": "David Bowman"})

    def testParseSimple(self):
        self.assertEquals(self.doc.properties['name'], "David Bowman")

    def testHasEmptyLinks(self):
        self.assertEquals(self.doc.links, {})


class ParseLinksTest(unittest.TestCase):
    OBJECT = {
        "_links": {
            "self": {"href": "dougrain"},
            "next": {
                "href": "http://localhost/wharris/esmre",
                "title": "Next"
            },
            "parent": {"href": "/wharris/"},
            "images": [
                {"href": "/foo"},
                {"href": "/bar"}
            ],
        }
    }

    def setUp(self):
        self.doc = dougrain.Document.from_object(
            self.OBJECT, base_uri="http://localhost/wharris/dougrain")

    def testLoadsSingleLinkHref(self):
        self.assertEquals("http://localhost/wharris/esmre",
                          self.doc.links["next"].href)

    def testLoadsSingleLinkURL(self):
        self.assertEquals("http://localhost/wharris/esmre",
                          self.doc.links["next"].url())

    def testLoadsRelativeURLHref(self):
        self.assertEquals("/wharris/",
                          self.doc.links["parent"].href)

    def testAbsolutesRelativeURL(self):
        self.assertEquals("http://localhost/wharris/",
                          self.doc.links["parent"].url())

    def testLoadsSelfAsLinkAndAttribute(self):
        self.assertEquals("dougrain", self.doc.links["self"].href)
        self.assertEquals("http://localhost/wharris/dougrain",
                          self.doc.links["self"].url())

        self.assertEquals(self.doc.links["self"].url(), self.doc.url())

    def testLoadsTitle(self):
        self.assertEquals("Next", self.doc.links["next"].title)
        self.assertFalse(hasattr(self.doc.links["parent"], "title"))
        self.assertFalse(hasattr(self.doc.links["self"], "title"))

    def testLoadsArrayOfLinks(self):
        self.assertEquals(["/foo", "/bar"],
                          [link.href for link in self.doc.links['images']])

    def testLinksIsNotAnAttribute(self):
        self.assertFalse('_links' in self.doc.properties)
        self.assertFalse(hasattr(self.doc, '_links'))


class ParseEmbeddedObjectsTest(unittest.TestCase):
    OBJECT = {
        "_embedded": {
            "foo": {
                "name": "Foo",
                "size": 88888888
            },
            "bar": [
                {
                    "title": "Bar 1"
                },
                {
                    "title": "Bar 2"
                }
            ],
            "bundy": {
                "_links": {
                    "next": {"href": "/people/2"}
                }
            }
        }
    }

    def setUp(self):
        self.doc = dougrain.Document.from_object(
            self.OBJECT,
            base_uri="http://localhost/people/")

    def testLoadsSingleEmbeddedObject(self):
        foo = self.doc.embedded["foo"]
        self.assertEquals("Foo", foo.properties['name'])
        self.assertEquals(88888888, foo.properties['size'])

    def testLoadsArrayOfEmbeddedObjects(self):
        self.assertEquals(["Bar 1", "Bar 2"],
                          [bar.properties['title']
                           for bar in self.doc.embedded['bar']])

    def testLoadsLinksInEmbeddedObject(self):
        link = self.doc.embedded["bundy"].links["next"]
        self.assertEquals("/people/2", link.href)
        self.assertEquals("http://localhost/people/2", link.url())

    def testEmbeddedIsNotAnAttribute(self):
        self.assertFalse('_embedded' in self.doc.properties)
        self.assertFalse(hasattr(self.doc, '_embedded'))


class CurieExpansionTest(unittest.TestCase):
    OBJECT = {
        '_links': {
            'curies': [
                {
                    'href': "http://localhost/roles/{rel}",
                    'name': 'role',
                    'templated': True
                },
                {
                    'href': "http://localhost/images/{rel}",
                    'name': 'image',
                    'templated': True
                }
            ],
            'role:host': {'href': "/hosts/1"}
        },
        '_embedded': {
            'role:sizing': {
                '_links': {
                    'curies': [
                        {
                            'href': "http://localhost/dimension/{rel}",
                            'name': 'dim',
                            'templated': True
                        }
                    ]
                }
            },
            'role:coloring': {
                '_links': {
                    'curies': [
                        {
                            'href':
                            "http://localhost/imagefiles/{rel}",
                            'name': 'image',
                            'templated': True
                        }
                    ]
                }
            },
        }
    }

    def setUp(self):
        self.doc = dougrain.Document.from_object(self.OBJECT)

    def testExposesCurieCollection(self):
        self.assertEquals("http://localhost/roles/category",
                          self.doc.expand_curie('role:category'))

    def testEmbeddedObjectHasParentCuries(self):
        sizing_doc = self.doc.embedded['role:sizing']
        self.assertEquals("http://localhost/roles/host",
                          sizing_doc.expand_curie('role:host'))

    def testParentObjectDoesNotHaveEmbeddedCuried(self):
        self.assertEquals('dim:weight', self.doc.expand_curie('dim:weight'))

    def testEmbeddedObjectExtendsParentCuries(self):
        sizing_doc = self.doc.embedded['role:sizing']
        self.assertEquals("http://localhost/dimension/weight",
                          sizing_doc.expand_curie('dim:weight'))

    def testEmbeddedObjectCurieOverridesParentCurie(self):
        coloring_doc = self.doc.embedded['role:coloring']
        self.assertEquals("http://localhost/imagefiles/photo",
                          coloring_doc.expand_curie('image:photo'))

class CurieExpansionTestDraft3(CurieExpansionTest):
    OBJECT = {
        '_links': {
            'curie': [
                {
                    'href': "http://localhost/roles/{rel}",
                    'name': 'role',
                    'templated': True
                },
                {
                    'href': "http://localhost/images/{rel}",
                    'name': 'image',
                    'templated': True
                }
            ],
            'role:host': {'href': "/hosts/1"}
        },
        '_embedded': {
            'role:sizing': {
                '_links': {
                    'curie': {
                        'href': "http://localhost/dimension/{rel}",
                        'name': 'dim',
                        'templated': True
                    }
                }
            },
            'role:coloring': {
                '_links': {
                    'curie': {
                        'href': "http://localhost/imagefiles/{rel}",
                        'name': 'image',
                        'templated': True
                    }
                }
            },
        }
    }


class RelsTest(unittest.TestCase):
    OBJECT = {
        '_links': {
            'curies': [
                {
                    'href': "/roles/{rel}",
                    'name': 'role',
                    'templated': True
                },
                {
                    'href': "http://localhost/images/{rel}",
                    'name': 'image',
                    'templated': True
                }
            ],
            'role:host': {'href': "/hosts/1"},
            'role:application': {'href': "/apps/1"},
            'role:dept': [
                {'href': "/departments/1"},
                {'href': "/departments/2"}
            ]
        },
        '_embedded': {
            'role:consumer': {
                '_links': {
                    'self': {
                        'href': '/clients/1'
                    }
                },
                'name': "Client 1"
            },
            'role:application': {
                '_links': {
                    'self': { 'href': "/apps/2" }
                }
            },
            'role:dept': [
                {
                    '_links': {
                        'self': {
                            'href': "http://localhost/departments/2"
                        }
                    },
                },
                {
                    '_links': {
                        'self': { 'href': "/departments/3" }
                    }
                }
            ]
        }
    }
    
    def setUp(self):
        self.doc = dougrain.Document(self.OBJECT, "http://localhost")

    def testHasHostLinkRel(self):
        host_role = self.doc.expand_curie('role:host')
        self.assertTrue(host_role in self.doc.rels)
        self.assertEquals(["http://localhost/hosts/1"],
                          [x.url() for x in self.doc.rels[host_role]])

    def testHasConsumerEmbeddedRel(self):
        consumer_role = self.doc.expand_curie('role:consumer')
        self.assertTrue(consumer_role in self.doc.rels)
        consumer = self.doc.rels[consumer_role][0]
        self.assertEquals("http://localhost/clients/1", consumer.url())
        self.assertEquals("Client 1", consumer.properties['name'])

    def testHasApplicationLinkAndEmbeddedRels(self):
        application_role = self.doc.expand_curie('role:application')
        applications = self.doc.rels[application_role]
        self.assertTrue(self.doc.embedded['role:application'] in applications)
        self.assertTrue(self.doc.links['role:application'] in applications)

    def testEmbeddedRelOverridesLinkRelWithSameHref(self):
        dept_role = self.doc.expand_curie('role:dept')

        dept_2_link = [link for link in self.doc.links['role:dept']
                       if link.url() == "http://localhost/departments/2"][0]
        dept_2_embedded = [link for link in self.doc.embedded['role:dept']
                           if link.url() == "http://localhost/departments/2"][0]
        
        departments = self.doc.rels[dept_role]
        self.assertTrue(dept_2_embedded in departments)
        self.assertFalse(dept_2_link in departments)

        urls = [x.url() for x in departments]
        urls.sort()
        self.assertEquals(
            ["http://localhost/departments/%d" % x for x in [1,2,3]],
            urls)


class RelsTestDraft3(RelsTest):
    OBJECT = {
        '_links': {
            'curie': [
                {
                    'href': "/roles/{rel}",
                    'name': 'role',
                    'templated': True
                },
                {
                    'href': "http://localhost/images/{rel}",
                    'name': 'image',
                    'templated': True
                }
            ],
            'role:host': {'href': "/hosts/1"},
            'role:application': {'href': "/apps/1"},
            'role:dept': [
                {'href': "/departments/1"},
                {'href': "/departments/2"}
            ]
        },
        '_embedded': {
            'role:consumer': {
                '_links': {
                    'self': {
                        'href': '/clients/1'
                    }
                },
                'name': "Client 1"
            },
            'role:application': {
                '_links': {
                    'self': { 'href': "/apps/2" }
                }
            },
            'role:dept': [
                {
                    '_links': {
                        'self': {
                            'href': "http://localhost/departments/2"
                        }
                    },
                },
                {
                    '_links': {
                        'self': { 'href': "/departments/3" }
                    }
                }
            ]
        }
    }


class SerializeTests(unittest.TestCase):
    def checkEqualObjects(self, obj):
        doc = dougrain.Document.from_object(obj, "http://localhost")
        self.assertEquals(obj, doc.as_object())

    def testSimple(self):
        self.checkEqualObjects({})

    def testAttributes(self):
        self.checkEqualObjects({"latlng": [53.0, -0.001],
                                "altitude": 10.0,
                                "haccuracy": 5.0,
                                "vacuracy": 10.0})

    def testLinks(self):
        self.checkEqualObjects(ParseLinksTest.OBJECT)

    def testEmbeddedObjects(self):
        self.checkEqualObjects(ParseEmbeddedObjectsTest.OBJECT)

    def testRels(self):
        self.checkEqualObjects(CurieExpansionTest.OBJECT)
        self.checkEqualObjects(RelsTest.OBJECT)

    def testRelsDraft3(self):
        self.checkEqualObjects(CurieExpansionTestDraft3.OBJECT)
        self.checkEqualObjects(RelsTestDraft3.OBJECT)


class AttributeMutationTests(unittest.TestCase):
    def testSetAttributeAddsAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_property('foo', "bar")

        self.assertEquals("bar", doc.properties['foo'])

    def testSetAttributeUpdatesAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_property('foo', "bar")

        doc.set_property('foo', "bundy")

        self.assertEquals("bundy", doc.properties['foo'])

    def testRemoveAttributeRemovesAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_property('foo', "bar")

        doc.delete_property('foo')

        self.assertFalse(hasattr(doc, 'foo'))
        self.assertFalse('foo' in doc.properties)

    def testBuildObjectFromEmpty(self):
        target = {"latlng": [53.0, -0.001],
                  "altitude": 10.0,
                  "haccuracy": 5.0,
                  "vacuracy": 10.0}
        target_doc = dougrain.Document.from_object(target)

        doc = dougrain.Document.empty()

        for key, value in target_doc.properties.iteritems():
            doc.set_property(key, value)

        self.assertEquals(target_doc.as_object(), doc.as_object())


class AddLinkStringTests(unittest.TestCase):
    def add_link(self, doc, rel, href, **kwargs):
        doc.add_link(rel, href, **kwargs)

    def testAddSimpleLink(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/1"}
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/1")

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddLinkForSecondRelKeepsFirstRel(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/1"},
                'child': {'href': "http://localhost/1/1"}
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/1")
        self.add_link(doc, 'child', "http://localhost/1/1")

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddSecondLinkForSameRel(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [{'href': "http://localhost/2/1"},
                          {'href': "http://localhost/2/2"}]
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/2")
        self.add_link(doc, 'child', "http://localhost/2/1")
        self.add_link(doc, 'child', "http://localhost/2/2")

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddThirdLinkForSameRel(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [{'href': "http://localhost/2/1"},
                          {'href': "http://localhost/2/2"},
                          {'href': "http://localhost/2/3"}]
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/2")
        self.add_link(doc, 'child', "http://localhost/2/1")
        self.add_link(doc, 'child', "http://localhost/2/2")
        self.add_link(doc, 'child', "http://localhost/2/3")

        self.assertEquals(target, doc.as_object())

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddLinkWithExtraAttributes(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [{'href': "http://localhost/2/1",
                           'title': "First Child"},
                          {'href': "http://localhost/2/2",
                           'title': "Second Child"}]
            }
        }
        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/2")
        self.add_link(doc, 'child', "http://localhost/2/1",
                      title="First Child")
        self.add_link(doc, 'child', "http://localhost/2/2",
                      title="Second Child")

        self.assertEquals(target, doc.as_object())

class AddObjectLinkTests(AddLinkStringTests):
    def add_link(self, doc, rel, href, **kwargs):
        link = doc.link(href, **kwargs)
        doc.add_link(rel, link)


class AddDocumentLinkTests(AddLinkStringTests):
    def add_link(self, doc, rel, href, **kwargs):
        target = dougrain.Document.empty(href)
        self_link = target.link(href, **kwargs)
        target.add_link('self', self_link)
        doc.add_link(rel, target)


class DeleteLinkTests(unittest.TestCase):
    def testDeleteOnlyLinkForRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': {'href': "http://localhost/2/1"}
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")
        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc.delete_link("child")

        self.assertEquals(target_doc, doc)
        self.assertFalse('child' in doc.links)

    def testDeleteEveryLinkForRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [
                    {'href': "http://localhost/2/1"},
                    {'href': "http://localhost/2/2"},
                    {'href': "http://localhost/2/3"}
                ]
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/2"}
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")
        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc.delete_link("child")

        self.assertEquals(target_doc.as_object(), doc.as_object())
        self.assertFalse('child' in doc.links)


    def testDeleteLastLink(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': {'href': "http://localhost/2/1"}
            }
        }

        target = {}

        doc = dougrain.Document.from_object(initial, "http://localhost/")
        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc.delete_link("child")
        doc.delete_link("self")

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteIndividualLinks(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [
                    {'href': "http://localhost/2/1"},
                    {'href': "http://localhost/2/2"},
                    {'href': "http://localhost/2/3"}
                ]
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link("child", "http://localhost/2/1")
        self.assertEquals([{'href': "http://localhost/2/2"},
                           {'href': "http://localhost/2/3"}],
                          doc.as_object()['_links']['child'])

        doc.delete_link("child", "http://localhost/2/3")
        self.assertEquals({'href': "http://localhost/2/2"},
                          doc.as_object()['_links']['child'])
        
        doc.delete_link("child", "http://localhost/2/2")
        self.assertFalse("child" in doc.as_object()['_links'])

        doc.delete_link("self", "http://localhost/2")
        self.assertFalse('_links' in doc.as_object())

    def testDeleteLinksWithoutRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': {'href': "http://localhost/3/2"}
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link(href="http://localhost/3/1")

        self.assertEquals(target, doc.as_object())

    def testDeleteAllLinks(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        target = {}

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link()

        self.assertEquals(target, doc.as_object())

    def testDeleteLinkWithNoMatchingRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link(rel="".join(doc.links.keys()))

        self.assertEquals(target, doc.as_object())

    def testDeleteLinkWithNoLinks(self):
        doc = dougrain.Document.empty("http://localhost/3")
        target = dougrain.Document.empty("http://localhost/3")

        doc.delete_link()

        self.assertEquals(target, doc)


class EmbedTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.empty("http://localhost/")
        self.embedded1 = dougrain.Document.from_object({"foo": "bar"})
        self.embedded2 = dougrain.Document.from_object({"spam": "eggs"})
        self.embedded3 = dougrain.Document.from_object({"ham": "beans"})

    def testEmbed(self):
        expected = {
            '_embedded': {
                'child': self.embedded1.as_object()
            }
        }
        self.doc.embed('child', self.embedded1)
        self.assertEquals(expected, self.doc.as_object())
        self.assertEquals(self.embedded1, self.doc.embedded['child'])

    def testEmbedAnotherRel(self):
        expected = {
            '_embedded': {
                'prev': self.embedded2.as_object(),
                'next': self.embedded3.as_object(),
            }
        }
        self.doc.embed('prev', self.embedded2)
        self.doc.embed('next', self.embedded3)

        self.assertEquals(expected, self.doc.as_object())
        self.assertEquals(self.embedded2, self.doc.embedded['prev'])
        self.assertEquals(self.embedded3, self.doc.embedded['next'])

    def testEmbedSameRel(self):
        expected = {
            '_embedded': {
                'item': [
                    self.embedded1.as_object(),
                    self.embedded2.as_object(),
                    self.embedded3.as_object()
                ]
            }
        }
        self.doc.embed('item', self.embedded1)
        self.doc.embed('item', self.embedded2)
        self.doc.embed('item', self.embedded3)

        self.assertEquals(expected, self.doc.as_object())
        self.assertEquals([self.embedded1, self.embedded2, self.embedded3],
                          self.doc.embedded['item'])


class TestIteration(unittest.TestCase):
    def testASingleDocumentCanBeIterated(self):
        the_doc = dougrain.Document.empty("http://localhost/1")
        the_doc.add_link('self', "http://localhost/1")

        count = 0
        for a_doc in the_doc:
            count += 1
            self.assertEquals(the_doc, a_doc)

        self.assertEquals(1, count)


def make_doc(href, *args, **kwargs):
    result = dougrain.Document.empty("http://localhost", *args, **kwargs)
    result.add_link('self', href)
    return result


def make_draft_3_doc(href, *args, **kwargs):
    return make_doc(draft=dougrain.Draft.DRAFT_3)


class DeleteEmbeddedTests(unittest.TestCase):
    def testDeleteOnlyEmbedForRel(self):
        doc = make_doc("http://localhost/2")
        doc.embed('child', make_doc("http://localhost/2/1"))
        doc.embed('root', make_doc("http://localhost/"))

        target_doc = make_doc("http://localhost/2")
        target_doc.embed('root', make_doc("http://localhost/"))

        doc.delete_embedded("child")

        self.assertEquals(target_doc.as_object(), doc.as_object())
        self.assertFalse('child' in doc.embedded)
        self.assertTrue('root' in doc.embedded)

    def testDeleteEveryEmbedForRel(self):
        doc = make_doc("http://localhost/2")
        doc.embed('root', make_doc("http://localhost/"))
        doc.embed('child', make_doc("http://localhost/2/1"))
        doc.embed('child', make_doc("http://localhost/2/1"))
        doc.embed('child', make_doc("http://localhost/2/1"))

        target_doc = make_doc("http://localhost/2")
        target_doc.embed('root', make_doc("http://localhost/"))

        doc.delete_embedded("child")

        self.assertEquals(target_doc.as_object(), doc.as_object())
        self.assertFalse('child' in doc.embedded)
        self.assertTrue('root' in doc.embedded)

    def testDeleteLastEmbed(self):
        doc = make_doc("http://localhost/2")
        doc.embed('root', make_doc("http://localhost/"))
        doc.embed('child', make_doc("http://localhost/2/1"))

        target_doc = make_doc("http://localhost/2")

        doc.delete_embedded('root')
        doc.delete_embedded('child')

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteIndividualEmbeds(self):
        doc = make_doc("http://localhost/2")
        doc.embed('root', make_doc("http://localhost/"))
        doc.embed('child', make_doc("http://localhost/2/1"))
        doc.embed('child', make_doc("http://localhost/2/2"))
        doc.embed('child', make_doc("http://localhost/2/3"))

        doc2 = make_doc("http://localhost/2")
        doc2.embed('root', make_doc("http://localhost/"))
        doc2.embed('child', make_doc("http://localhost/2/2"))
        doc2.embed('child', make_doc("http://localhost/2/3"))

        doc3 = make_doc("http://localhost/2")
        doc3.embed('root', make_doc("http://localhost/"))
        doc3.embed('child', make_doc("http://localhost/2/2"))

        doc4 = make_doc("http://localhost/2")
        doc4.embed('root', make_doc("http://localhost/"))

        doc5 = make_doc("http://localhost/2")

        doc.delete_embedded("child", "http://localhost/2/1")
        self.assertEquals(doc2.as_object(), doc.as_object())

        doc.delete_embedded("child", "http://localhost/2/3")
        self.assertEquals(doc3.as_object(), doc.as_object())
        
        doc.delete_embedded("child", "http://localhost/2/2")
        self.assertEquals(doc4.as_object(), doc.as_object())

        doc.delete_embedded("root", "http://localhost/")
        self.assertEquals(doc5.as_object(), doc.as_object())

    def testDeleteEmbedsWithoutRel(self):
        doc = make_doc("http://localhost/3")
        doc.embed('child', make_doc("http://localhost/3/1"))
        doc.embed('child', make_doc("http://localhost/3/2"))
        doc.embed('favorite', make_doc("http://localhost/3/1"))

        target_doc = make_doc("http://localhost/3")
        target_doc.embed('child', make_doc("http://localhost/3/2"))

        doc.delete_embedded(href="http://localhost/3/1")

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteAllEmbeds(self):
        doc = make_doc("http://localhost/3")
        doc.embed('child', make_doc("http://localhost/3/1"))
        doc.embed('child', make_doc("http://localhost/3/2"))
        doc.embed('favorite', make_doc("http://localhost/3/1"))

        target_doc = make_doc("http://localhost/3")

        doc.delete_embedded()

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteEmbedWithMissingRel(self):
        doc = make_doc("http://localhost/3")
        doc.embed('child', make_doc("http://localhost/3/1"))
        doc.embed('child', make_doc("http://localhost/3/2"))
        doc.embed('favorite', make_doc("http://localhost/3/1"))

        target_doc = make_doc("http://localhost/3")
        target_doc.embed('child', make_doc("http://localhost/3/1"))
        target_doc.embed('child', make_doc("http://localhost/3/2"))
        target_doc.embed('favorite', make_doc("http://localhost/3/1"))

        missing_rel = ''.join(doc.embedded.keys()) + '_'
        doc.delete_embedded(missing_rel)

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteEmbedWithNoEmbeds(self):
        doc = make_doc("http://localhost/3")
        target_doc = make_doc("http://localhost/3")

        doc.delete_embedded()

        self.assertEquals(target_doc.as_object(), doc.as_object())


class CurieMutationTest(unittest.TestCase):
    def setUp(self):
        self.doc = make_doc("http://localhost/3")
        self.doc.set_curie('rel', "http://localhost/rels/{rel}")

    def testCurieJSONHasCorrectType(self):
        self.assertEquals(type(self.doc.as_object()['_links']['curies']), list)

    def testSetCurie(self):
        new_doc = dougrain.Document(self.doc.as_object(), self.doc.base_uri)
        self.assertEquals("http://localhost/rels/foo",
                          new_doc.expand_curie("rel:foo"))

    def testReplaceCurie(self):
        self.doc.set_curie('rel', "http://localhost/RELS/{rel}.html")

        new_doc = dougrain.Document(self.doc.as_object(), self.doc.base_uri)
        self.assertEquals("http://localhost/RELS/foo.html",
                          new_doc.expand_curie("rel:foo"))

    def testDropCurie(self):
        self.doc.set_curie('tm', "http://www.touchmachine.com/{rel}.html")
        self.doc.drop_curie('rel')

        new_doc = dougrain.Document(self.doc.as_object(), self.doc.base_uri)
        self.assertEquals("rel:foo", self.doc.expand_curie("rel:foo"))
        self.assertEquals("http://www.touchmachine.com/index.html",
                          new_doc.expand_curie("tm:index"))

    def testDropSingleCurie(self):
        self.doc.drop_curie('rel')
        self.assertEquals("rel:foo", self.doc.expand_curie("rel:foo"))


class CurieMutationTestDraft3(CurieMutationTest):
    def setUp(self):
        self.doc = dougrain.Document.empty("http://localhost/3",
                                           draft=dougrain.Draft.DRAFT_3)
        self.doc.set_curie('rel', "http://localhost/rels/{rel}")
        self.doc.add_link('self', "http://localhost/3")

    def testCurieJSONHasCorrectType(self):
        self.assertEquals(type(self.doc.as_object()['_links']['curie']), dict)


class CurieHidingTests(unittest.TestCase):
    def testCuriesAreNotLinks(self):
        doc = dougrain.Document({
            '_links': {
                'curies': [{
                    'href': "http://localhost/rel/{rel}",
                    'name': "rel",
                    'templated': True
                }],
                'self': {
                    'href': "http://localhost/0"
                }
            }
        }, "http://localhost/0")

        self.assertFalse('curies' in doc.links)

    def testDraft3CuriesAreNotLinks(self):
        doc = dougrain.Document({
            '_links': {
                'curie': {
                    'href': "http://localhost/rel/{rel}",
                    'name': "rel",
                    'templated': True
                },
                'self': {
                    'href': "http://localhost/0"
                }
            }
        }, "http://localhost/0")

        self.assertFalse('curie' in doc.links)

    def testDraft3CuriesAreLinksInDraft4Document(self):
        doc = dougrain.Document({
            '_links': {
                'curie': {
                    'href': "http://localhost/rel/{rel}",
                    'name': "rel",
                    'templated': True
                },
                'curies': [{
                    'href': "http://localhost/rel/{rel}",
                    'name': "rel",
                    'templated': True
                }],
                'self': {
                    'href': "http://localhost/0"
                }
            }
        }, "http://localhost/0")

        self.assertFalse('curies' in doc.links)
        self.assertTrue('curie' in doc.links)
                

class LinkCanonicalizationTests(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.empty("http://localhost/1/")
        self.doc.set_curie("role", "/roles/{rel}")

    def testFindsLinksByFullRelTypeURI(self):
        self.doc.add_link("role:app", "/apps/1")
        self.assertEquals(self.doc.links["role:app"],
                          self.doc.links["http://localhost/roles/app"])

    def testFindsLinksByRelTypePath(self):
        self.doc.add_link("role:app", "/apps/1")
        self.assertEquals(self.doc.links["role:app"],
                          self.doc.links["/roles/app"])

    def testMergesLinksAddedWithSynonymous(self):
        self.doc.add_link("role:app", "/apps/1")
        self.doc.add_link("/roles/app", "/apps/2")
        self.doc.add_link("http://localhost/roles/app", "/apps/3")

        self.assertEquals(["/apps/1", "/apps/2", "/apps/3"],
                           [link.href for link in self.doc.links["role:app"]])

    def testMergesLinkswhenLoading(self):
        self.doc = dougrain.Document.from_object(
            {
                "_links": {
                    "curies": [
                        {"href": "/roles/{rel}",
                         "name": "role",
                         "templated": True}
                    ],
                    "self": {"href": "/1"},
                    "role:app": {"href": "/apps/1"},
                    "/roles/app": {"href": "/apps/2"},
                    "http://localhost/roles/app": {"href": "/apps/3"},
                }
            },
            base_uri="http://localhost/1")
        self.doc.set_curie("role", "/roles/{rel}")
        
        self.assertEquals(set(["/apps/1", "/apps/2", "/apps/3"]),
                          set(link.href for link in self.doc.links["role:app"]))

    def testMergesLinkswhenLoadingDraft3(self):
        self.doc = dougrain.Document.from_object(
            {
                "_links": {
                    "curie": {
                        "href": "/roles/{rel}",
                        "name": "role",
                        "templated": True
                    },
                    "self": {"href": "/1"},
                    "role:app": {"href": "/apps/1"},
                    "/roles/app": {"href": "/apps/2"},
                    "http://localhost/roles/app": {"href": "/apps/3"},
                }
            },
            base_uri="http://localhost/1")
        self.doc.set_curie("role", "/roles/{rel}")
        
        self.assertEquals(set(["/apps/1", "/apps/2", "/apps/3"]),
                          set(link.href for link in self.doc.links["role:app"]))


class EmbeddedCanonicalizationTests(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.empty("http://localhost/1/")
        self.doc.set_curie("role", "/roles/{rel}")

    def new_doc(self, uri):
        doc = dougrain.Document.empty(uri)
        doc.add_link('self', uri)
        doc.set_property("name", uri)
        return doc

    def testFindsEmbeddedResourcesByFullRelTypeURI(self):
        self.doc.embed("role:app", self.new_doc("/apps/1"))
        self.assertEquals(self.doc.embedded["role:app"],
                          self.doc.embedded["http://localhost/roles/app"])

    def testFindsEmbeddedResourcesByRelTypePath(self):
        self.doc.embed("role:app", self.new_doc("/apps/1"))
        self.assertEquals(self.doc.embedded["role:app"],
                          self.doc.embedded["/roles/app"])

    def testMergesEmbeddedResourcesAddedWithSynonymous(self):
        self.doc.embed("role:app", self.new_doc("/apps/1"))
        self.doc.embed("/roles/app", self.new_doc("/apps/2"))
        self.doc.embed("http://localhost/roles/app", self.new_doc("/apps/3"))

        self.assertEquals(["/apps/1", "/apps/2", "/apps/3"],
                           [embedded.properties['name']
                            for embedded in self.doc.embedded["role:app"]])


class EdgeCasesTests(unittest.TestCase):
    def testUrlOfDocumentWithMultipleSelfLinksFromFirstSelfLink(self):
        doc = dougrain.Document.empty("http://localhost")
        doc.add_link('self', "/1")
        doc.add_link('self', "/2")
        self.assertEquals("http://localhost/1", doc.url())

    def testSetReservedAttributeSilentlyFails(self):
        doc = dougrain.Document.empty("http://localhost")
        doc.set_property('_links', {'self': {'href': "/1"}})
        doc.set_property('_embedded', {'child': {'foo': "bar"}})

        self.assertFalse('_links' in doc.properties)
        self.assertIsNone(doc.url())

        self.assertFalse('_embedded' in doc.properties)
        self.assertFalse('child' in doc.embedded)

    def testDeleteReservedAttributeSilentlyFails(self):
        doc = dougrain.Document.empty("http://localhost")
        doc.embed('child', dougrain.Document.from_object({'foo': "bar"},
                                                         "http://localhost"))
        doc.add_link('self', "/1")

        with self.assertRaises(KeyError):
            doc.delete_property('_links')
        with self.assertRaises(KeyError):
            doc.delete_property('_embedded')

        self.assertFalse('_links' in doc.properties)
        self.assertEquals("http://localhost/1", doc.url())

        self.assertFalse('_embedded' in doc.properties)
        self.assertEquals("bar", doc.embedded['child'].properties['foo'])


class ExplicitDraftTests(unittest.TestCase):
    def testDraft3DocumentHasOldCurieBehaviour(self):
        doc = dougrain.Document.empty("http://localhost",
                                      draft=dougrain.Draft.DRAFT_3)
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_3)
        doc.add_link('self', "/1")
        doc.set_curie('rel', "/rels/{rel}")

        links = doc.as_object()['_links']
        self.assertTrue('curie' in links)
        self.assertFalse('curies' in links)
        curie = links['curie']
        self.assertTrue(isinstance(curie, dict))
        doc.set_curie('foo', "/foos/{rel}")
        curie = links['curie']
        self.assertTrue(isinstance(curie, list))

    def testDraft4DocumentHasNewCurieBehaviour(self):
        doc = dougrain.Document.empty("http://localhost",
                                      draft=dougrain.Draft.DRAFT_4)
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_4)
        doc.add_link('self', "/1")
        doc.set_curie('rel', "/rels/{rel}")

        links = doc.as_object()['_links']
        self.assertFalse('curie' in links)
        self.assertTrue('curies' in links)
        curie = links['curies']
        self.assertTrue(isinstance(curie, list))
        doc.set_curie('foo', "/foos/{rel}")
        curie = links['curies']
        self.assertTrue(isinstance(curie, list))


class DraftDetectionTests(unittest.TestCase):
    def testDocumentsWithCurieAreDraft3(self):
        doc = dougrain.Document.from_object(
            {'_links': {'curie': {}}},
            "http://localhost/")
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_3)

    def testDocumentsWithCuriesAreDraft4(self):
        doc = dougrain.Document.from_object(
            {'_links': {'curies': []}},
            "http://localhost/")
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_4)

    def testDocumentsWithNoCurieKeyAreLatest(self):
        doc = dougrain.Document.empty("http://localhost/")
        self.assertEquals(doc.draft, dougrain.Draft.LATEST)

    def testLatestDraftIsDraft4(self):
        doc = dougrain.Document.from_object({}, "http://localhost/",
                                            draft=dougrain.Draft.LATEST)
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_4)

    def testExplicitDraftOverridesAutodetection(self):
        doc = dougrain.Document.from_object(
            {'_links': {'curie': {"href": "/roles/{rel}",
                                  "name": "role",
                                  "templated": True}}},
            "http://localhost/",
            draft=dougrain.Draft.DRAFT_4
        )
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_4)

        doc = dougrain.Document.from_object(
            {'_links': {'curies': []}},
            "http://localhost/",
            draft=dougrain.Draft.DRAFT_3
        )
        self.assertEquals(doc.draft, dougrain.Draft.DRAFT_3)


if __name__ == '__main__':
    unittest.main()
