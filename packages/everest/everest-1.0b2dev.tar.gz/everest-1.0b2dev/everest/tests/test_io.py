"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Feb 21, 2012.
"""
from StringIO import StringIO
from everest.mime import CsvMime
from everest.repositories.rdb.utils import RdbTestCaseMixin
from everest.repositories.rdb.utils import reset_metadata
from everest.representers.config import IGNORE_OPTION
from everest.resources.io import ConnectedResourcesSerializer
from everest.resources.io import build_resource_dependency_graph
from everest.resources.io import dump_resource
from everest.resources.io import dump_resource_to_files
from everest.resources.io import dump_resource_to_zipfile
from everest.resources.io import find_connected_resources
from everest.resources.io import get_collection_filename
from everest.resources.io import get_collection_name
from everest.resources.io import load_collection_from_file
from everest.resources.io import load_collection_from_url
from everest.resources.io import load_into_collections_from_zipfile
from everest.resources.utils import get_collection_class
from everest.resources.utils import get_member_class
from everest.resources.utils import get_root_collection
from everest.resources.utils import new_stage_collection
from everest.testing import ResourceTestCase
from everest.tests.complete_app.entities import MyEntity
from everest.tests.complete_app.entities import MyEntityChild
from everest.tests.complete_app.entities import MyEntityGrandchild
from everest.tests.complete_app.entities import MyEntityParent
from everest.tests.complete_app.interfaces import IMyEntity
from everest.tests.complete_app.interfaces import IMyEntityChild
from everest.tests.complete_app.interfaces import IMyEntityGrandchild
from everest.tests.complete_app.interfaces import IMyEntityParent
from everest.tests.complete_app.resources import MyEntityChildMember
from everest.tests.complete_app.resources import MyEntityGrandchildMember
import glob
import os
import shutil
import tempfile
import zipfile
from everest.resources.io import load_into_collection_from_url

__docformat__ = 'reStructuredText en'
__all__ = ['ConnectedResourcesTestCase',
           'ResourceDependencyGraphTestCase',
           'ResourceLoadingTestCase',
           ]


def _make_test_entity_member():
    parent = MyEntityParent(id=0)
    entity = MyEntity(id=0, parent=parent)
    parent.child = entity
    child = MyEntityChild(id=0, parent=entity)
    entity.children.append(child)
    grandchild = MyEntityGrandchild(id=0, parent=child)
    child.children.append(grandchild)
    coll = new_stage_collection(IMyEntity)
    return coll.create_member(entity)


class ResourceGraphTestCase(ResourceTestCase):
    package_name = 'everest.tests.complete_app'
    config_file_name = 'configure_no_rdb.zcml'
    _interfaces = [IMyEntityParent, IMyEntity, IMyEntityChild,
                   IMyEntityGrandchild]


class ResourceDependencyGraphTestCase(ResourceGraphTestCase):

    def test_dependency_graph(self):
        grph = build_resource_dependency_graph(self._interfaces)
        self.assert_equal(len(grph.nodes()), 4)
        entity_mb_cls = get_member_class(IMyEntity)
        entity_parent_mb_cls = get_member_class(IMyEntityParent)
        entity_child_mb_cls = get_member_class(IMyEntityChild)
        entity_grandchild_mb_cls = get_member_class(IMyEntityGrandchild)
        # Entity Parent resource deps should be empty.
        self.assert_equal(grph.neighbors(entity_parent_mb_cls), [])
        # Entity Child has Grandchild.
        self.assert_equal(grph.neighbors(entity_child_mb_cls),
                          [entity_grandchild_mb_cls])
        # Entity Grandchild has Child, but backrefs are excluded by default.
        self.assert_equal(grph.neighbors(entity_grandchild_mb_cls),
                          [])
        # Entity has Parent and Child.
        self.assert_equal(set(grph.neighbors(entity_mb_cls)),
                          set([entity_parent_mb_cls, entity_child_mb_cls]))


class ConnectedResourcesTestCase(ResourceGraphTestCase):

    def test_find_connected_with_member(self):
        member = _make_test_entity_member()
        coll_map = find_connected_resources(member)
        for coll in coll_map.itervalues():
            self.assert_equal(len(coll), 1)

    def test_find_connected_with_collection(self):
        member = _make_test_entity_member()
        coll_map = find_connected_resources(member.__parent__)
        for coll in coll_map.itervalues():
            self.assert_equal(len(coll), 1)

    def test_find_connected_with_deps(self):
        member = _make_test_entity_member()
        dep_grph = \
            build_resource_dependency_graph(self._interfaces,
                                            include_backrefs=True)
        coll_map = find_connected_resources(member,
                                            dependency_graph=dep_grph)
        # Backrefs should not make a difference since we check for duplicates.
        for coll in coll_map.itervalues():
            self.assert_equal(len(coll), 1)

    def test_find_connected_with_custom_deps(self):
        member = _make_test_entity_member()
        ent = member.get_entity()
        # Point grandchild's parent to new child.
        new_child = MyEntityChild(id=1, parent=ent)
        ent.children[0].children[0].parent = new_child
        # When backrefs are excluded, we should not pick up the new parent
        # of the grandchild; when backrefs are included, we should.
        dep_grph = build_resource_dependency_graph(self._interfaces)
        self.assert_false(dep_grph.has_edge((MyEntityGrandchildMember,
                                             MyEntityChildMember)))
        coll_map = find_connected_resources(member)
        self.assert_equal(len(coll_map[MyEntityChildMember]), 1)
        dep_grph = \
            build_resource_dependency_graph(self._interfaces,
                                            include_backrefs=True)
        self.assert_true(dep_grph.has_edge((MyEntityGrandchildMember,
                                            MyEntityChildMember)))
        coll_map = find_connected_resources(member,
                                            dependency_graph=dep_grph)
        self.assert_equal(len(coll_map[MyEntityChildMember]), 2)

    def test_convert_to_strings(self):
        member = _make_test_entity_member()
        srl = ConnectedResourcesSerializer(CsvMime)
        rpr_map = srl.to_strings(member)
        self.assert_equal(len(rpr_map), 4)


class _ResourceIoTestCaseBase(ResourceTestCase):
    package_name = 'everest.tests.complete_app'

    def set_up(self):
        ResourceTestCase.set_up(self)
        # We need to switch off non-standard resource attributes manually.
        self.config.add_resource_representer(
                    IMyEntity, CsvMime,
                    attribute_options=
                            {('nested_parent',):{IGNORE_OPTION:True},
                             ('children',):{IGNORE_OPTION:True}
                             })


class _ZipResourceIoTestCaseBase(_ResourceIoTestCaseBase):
    def test_load_from_zipfile(self):
        member = _make_test_entity_member()
        strm = StringIO('w')
        dump_resource_to_zipfile(member, strm)
        colls = [
                 get_root_collection(IMyEntityParent),
                 get_root_collection(IMyEntity),
                 get_root_collection(IMyEntityChild),
                 get_root_collection(IMyEntityGrandchild),
                 ]
        colls = load_into_collections_from_zipfile(colls, strm,
                                                   resolve_urls=True)
        self.assert_equal(len(colls[0]), 1)
        self.assert_equal(len(colls[1]), 1)
        self.assert_equal(len(colls[2]), 1)
        self.assert_equal(len(colls[3]), 1)


class ZipResourceIoTestCaseNoRdb(_ZipResourceIoTestCaseBase):
    config_file_name = 'configure_no_rdb.zcml'

    def test_load_from_zipfile_invalid_extension(self):
        strm = StringIO('w')
        zipf = zipfile.ZipFile(strm, 'w')
        coll_name = get_collection_name(get_collection_class(IMyEntity))
        zipf.writestr('%s.foo' % coll_name, '')
        zipf.close()
        colls = [get_root_collection(IMyEntity)]
        with self.assert_raises(ValueError) as cm:
            dummy = load_into_collections_from_zipfile(colls, strm)
        exc_msg = 'Could not infer MIME type'
        self.assert_true(cm.exception.message.startswith(exc_msg))

    def test_load_from_zipfile_filename_not_found(self):
        strm = StringIO('w')
        zipf = zipfile.ZipFile(strm, 'w')
        zipf.writestr('foo.foo', '')
        zipf.close()
        colls = [get_root_collection(IMyEntity)]
        colls = load_into_collections_from_zipfile(colls, strm)
        self.assert_equal(len(colls[0]), 0)


class ZipResourceIoTestCaseRdb(RdbTestCaseMixin, _ZipResourceIoTestCaseBase):
    config_file_name = 'configure.zcml'

    @classmethod
    def teardown_class(cls):
        reset_metadata()


class StreamResourceIoTestCase(_ResourceIoTestCaseBase):
    config_file_name = 'configure_no_rdb.zcml'
    def test_dump_no_content_type(self):
        member = _make_test_entity_member()
        strm = StringIO()
        dump_resource(member, strm)
        self.assert_true(strm.getvalue().startswith('"id",'))


class FileResourceIoTestCase(_ResourceIoTestCaseBase):
    config_file_name = 'configure_no_rdb.zcml'
    def _test_load(self, load_func, fn_func, is_into):
        member = _make_test_entity_member()
        tmp_dir = tempfile.mkdtemp()
        try:
            dump_resource_to_files(member, directory=tmp_dir)
            file_names = glob.glob1(tmp_dir, "*.csv")
            self.assert_equal(len(file_names), 4)
            for ifc in [IMyEntityParent,
                        IMyEntity,
                        IMyEntityChild,
                        IMyEntityGrandchild]:
                coll_cls = get_collection_class(ifc)
                root_coll = get_root_collection(ifc)
                file_name = get_collection_filename(coll_cls)
                file_path = fn_func(os.path.join(tmp_dir, file_name))
                if not is_into:
                    coll = load_func(coll_cls, file_path)
                    self.assert_equal(len(coll), 1)
                    for mb in coll:
                        root_coll.add(mb)
                else:
                    load_func(root_coll, file_path)
                    self.assert_equal(len(root_coll), 1)
        finally:
            shutil.rmtree(tmp_dir)

    def test_load_from_invalid_file(self):
        coll_cls = get_collection_class(IMyEntity)
        with self.assert_raises(ValueError) as cm:
            dummy = \
              load_collection_from_file(coll_cls, 'my-entity-collection.foo')
        exc_msg = 'Could not infer MIME type'
        self.assert_true(cm.exception.message.startswith(exc_msg))

    def test_load_from_file(self):
        self._test_load(load_collection_from_file, lambda fn: fn, False)

    def test_load_from_file_url(self):
        self._test_load(load_collection_from_url,
                        lambda fn: "file://%s" % fn, False)

    def tetst_load_from_file_url_into(self):
        self._test_load(load_into_collection_from_url,
                        lambda fn: "file://%s" % fn, True)

    def test_load_from_invalid_file_url(self):
        self.assert_raises(ValueError,
                           self._test_load,
                           load_collection_from_url,
                           lambda fn: "http://%s" % fn, False)
