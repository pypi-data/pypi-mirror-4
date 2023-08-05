import os
import ptah
import shutil
import tempfile
from pyramid.config import ConfigurationConflictError

ptah.register_migration('ptah', 'ptah:tests/migrations')


class TestRegisterMigration(ptah.PtahTestCase):

    _init_ptah = False

    def test_register(self):
        from ptah.migrate import MIGRATION_ID

        ptah.register_migration(
            'test', 'ptah.tests:migrations', 'Ptah database migration')
        self.init_ptah()

        st = ptah.get_cfg_storage(MIGRATION_ID)

        self.assertIn('test', st)
        self.assertEqual(st['test'], 'ptah.tests:migrations')

    def test_register_conflict(self):
        ptah.register_migration(
            'test', 'ptah.tests:migrations', 'Ptah database migration')
        ptah.register_migration(
            'test', 'ptah.tests:migrations', 'Ptah database migration')

        self.assertRaises(ConfigurationConflictError, self.init_ptah)


class TestPyramidDirective(ptah.PtahTestCase):

    def setUp(self):
        from ptah import migrate

        self._pkgs = []
        def upgrade(pkg):
            self._pkgs.append(pkg)

        self.orig_upgrade = migrate.upgrade
        migrate.upgrade = upgrade

        super(TestPyramidDirective, self).setUp()

    def tearDown(self):
        super(TestPyramidDirective, self).tearDown()

        from ptah import migrate
        migrate.upgrade = self.orig_upgrade

    def test_pyramid_directive(self):
        from pyramid.config import Configurator

        config = Configurator()
        config.include('ptah')

        self.assertTrue(hasattr(config, 'ptah_migrate'))

    def test_directive_execution(self):
        from pyramid.config import Configurator

        config = Configurator()
        config.include('ptah')
        config.scan(self.__class__.__module__)
        config.ptah_migrate()
        config.commit()

        self.assertEqual(self._pkgs, ['ptah'])


class TestScriptDirectory(ptah.PtahTestCase):

    _init_ptah = False

    def test_unknown_package(self):
        self.init_ptah()

        from ptah.migrate import ScriptDirectory

        self.assertRaises(ValueError, ScriptDirectory, 'unknown')

    def test_normal(self):
        self.init_ptah()
        self.config.get_cfg_storage(
            'ptah:migrate')['ptah']='ptah:tests/migrations'

        from ptah.migrate import ScriptDirectory

        script = ScriptDirectory('ptah')

        self.assertEqual(
            script.dir,
            os.path.join(os.path.dirname(ptah.__file__), 'scripts'))

        self.assertEqual(
            script.versions,
            os.path.join(os.path.dirname(ptah.__file__), 'tests', 'migrations'))

    def test_doesnt_exist(self):
        from alembic.util import CommandError
        from ptah.migrate import ScriptDirectory

        ptah.register_migration('test', 'ptah:unknown_migrations')
        self.init_ptah()

        self.assertRaises(CommandError, ScriptDirectory, 'test')


class BaseScript(ptah.PtahTestCase):

    def setUp(self):
        from ptah import migrate

        self.dirs = dirs = {}

        class ScriptDirectory(migrate.ScriptDirectory):

            def __init__(self, pkg):
                if pkg in dirs:
                    dir = dirs[pkg]
                else:
                    dir = tempfile.mkdtemp()
                    dirs[pkg] = dir

                self.dir = os.path.join(
                    os.path.dirname(ptah.__file__), 'scripts')
                self.versions = dir

        self.orig_ScriptDirectory = migrate.ScriptDirectory
        migrate.ScriptDirectory = ScriptDirectory

        super(BaseScript, self).setUp()

    def tearDown(self):
        super(BaseScript, self).tearDown()

        for dir in self.dirs.values():
            shutil.rmtree(dir)

        from ptah import migrate
        migrate.ScriptDirectory = self.orig_ScriptDirectory


class TestRevision(BaseScript):

    def test_revision_default(self):
        from ptah.migrate import revision

        rev = revision('test', message='Test message')
        self.assertIn('{0}.py'.format(rev), os.listdir(self.dirs['test']))

    def test_revision_custom(self):
        from ptah.migrate import revision

        rev = revision('test', rev='001', message='Test message')
        self.assertEqual(rev, '001')
        self.assertIn('001.py', os.listdir(self.dirs['test']))

        self.assertRaises(
            KeyError, revision, 'test', rev='001')


class TestUpdateVersions(BaseScript):

    _init_ptah = False

    def test_update_force(self):
        from ptah.migrate import Version, revision, update_versions

        ptah.register_migration(
            'test', 'ptah.tests:migrations', force=True)
        self.init_ptah()

        revision('test', message='Test message')

        update_versions(self.registry)

        session = ptah.get_session()

        versions = dict((v.package, v.version_num)
                        for v in session.query(Version).all())
        self.assertNotIn('test', versions)

    def test_update_versions(self):
        from ptah.migrate import Version, revision, update_versions

        ptah.register_migration('test', 'ptah.tests:migrations')
        self.init_ptah()

        rev = revision('test', message='Test message')

        update_versions(self.registry)

        session = ptah.get_session()

        versions = dict((v.package, v.version_num)
                        for v in session.query(Version).all())
        self.assertIn('test', versions)
        self.assertEqual(versions['test'], rev)

    def test_update_version_exists(self):
        from ptah.migrate import Version, revision, update_versions

        ptah.register_migration('test', 'ptah.tests:migrations')
        self.init_ptah()

        revision('test', message='Test message')

        session = ptah.get_session()

        session.add(Version(package='test', version_num='123'))
        session.flush()

        update_versions(self.registry)

        versions = dict((v.package, v.version_num)
                        for v in session.query(Version).all())
        self.assertIn('test', versions)
        self.assertEqual(versions['test'], '123')


class TestUpgrade(BaseScript):

    _init_ptah = False

    def test_upgrade_to_rev(self):
        from ptah.migrate import Version, revision, upgrade

        ptah.register_migration(
            'test', 'ptah.tests:migrations', force=True)
        self.init_ptah()

        rev1 = revision('test', message='Test message1')
        revision('test', message='Test message2')

        upgrade('test:%s'%rev1)

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())
        self.assertEqual(versions['test'], rev1)

    def test_upgrade_to_head(self):
        from ptah.migrate import Version, revision, upgrade

        ptah.register_migration(
            'test', 'ptah.tests:migrations', force=True)
        self.init_ptah()

        revision('test', message='Test message1')
        rev2 = revision('test', message='Test message2')

        upgrade('test:head')

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())
        self.assertEqual(versions['test'], rev2)

    def test_upgrade_to_head_by_default(self):
        from ptah.migrate import Version, revision, upgrade

        ptah.register_migration(
            'test', 'ptah.tests:migrations', force=True)
        self.init_ptah()

        revision('test', message='Test message1')
        rev2 = revision('test', message='Test message2')

        upgrade('test')

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())
        self.assertEqual(versions['test'], rev2)

    def test_upgrade_to_same_rev(self):
        from ptah.migrate import Version, revision, upgrade

        ptah.register_migration(
            'test', 'ptah.tests:migrations', force=True)
        self.init_ptah()

        revision('test', message='Test message1')
        rev2 = revision('test', message='Test message2')

        upgrade('test')

        upgrade('test')

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())
        self.assertEqual(versions['test'], rev2)

    def test_upgrade_in_two_steps(self):
        from ptah.migrate import Version, revision, upgrade

        ptah.register_migration(
            'test', 'ptah.tests:migrations', force=True)
        self.init_ptah()

        rev1 = revision('test', message='Test message1')
        rev2 = revision('test', message='Test message2')

        upgrade('test:%s'%rev1)
        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())
        self.assertEqual(versions['test'], rev1)

        upgrade('test')
        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())
        self.assertEqual(versions['test'], rev2)

    def test_startup_check_version(self):
        from ptah.migrate import Version, revision, check_version

        ptah.register_migration(
            'test1', 'ptah.tests1:migrations')
        ptah.register_migration(
            'test2', 'ptah.tests2:migrations')
        self.init_ptah()

        rev1 = revision('test1', message='Test message1')
        rev2 = revision('test2', message='Test message2')

        session = ptah.get_session()
        session.add(Version(package='test1', version_num=rev1))
        session.add(Version(package='test2', version_num=rev2))
        session.flush()

        exc = None
        try:
            check_version(None)
        except SystemExit as err: # pragma: no cover
            exc = err

        self.assertIsNone(exc)

    def test_startup_check_version_exit(self):
        from ptah.migrate import revision, check_version

        ptah.register_migration(
            'test1', 'ptah.tests1:migrations')
        ptah.register_migration(
            'test2', 'ptah.tests2:migrations')
        self.init_ptah()

        revision('test1', message='Test message1')
        revision('test2', message='Test message2')

        exc = None
        try:
            check_version(None)
        except SystemExit as err: # pragma: no cover
            exc = err

        self.assertIsInstance(exc, SystemExit)
