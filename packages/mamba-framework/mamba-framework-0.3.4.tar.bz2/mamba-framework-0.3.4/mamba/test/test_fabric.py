
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

import tempfile
from os import sep

from twisted.trial import unittest
from twisted.python import filepath
from doublex.matchers import called
from doublex import ProxySpy, assert_that, is_

try:
    from mamba.deployment.fabric_deployer import (
        FabricDeployer,
        FabricMissingConfigFile,
        FabricConfigFileDontExists,
        FabricNotValidConfigFile
    )
    from fabric import state
    FABRIC_SUPPORT = True
except ImportError:
    FABRIC_SUPPORT = False


class FabricDeployerTest(unittest.TestCase):
    """Tests for mamba.deployment.fabric
    """

    def setUp(self):
        if not FABRIC_SUPPORT:
            raise unittest.SkipTest('Fabric is not available!')
        self.fabric = FabricDeployer()

    def tearDown(self):
        tmpdir = tempfile.gettempdir()
        f = filepath.FilePath(tmpdir + sep + 'fabric_deployer_test.dc')
        if f.exists():
            f.remove()

    def test_fabric_identify(self):
        self.assertEqual(self.fabric.identify(), 'Fabric')

    def test_fabric_operation_default_mode(self):
        self.assertEqual(self.fabric.operation_mode(), 'remote')

    def test_fabric_deploy_method_exsist_and_is_callable(self):
        self.assertTrue(callable(self.fabric.deploy))

    def test_fabric_deploy_raises_on_no_config_file(self):
        self.assertRaises(FabricMissingConfigFile, self.fabric.deploy)

    def test_fabric_deploy_Raises_on_config_file_dont_exists(self):
        self.assertRaises(
            FabricConfigFileDontExists, self.fabric.deploy, 'fail')

    def test_fabric_deploy_raises_on_invalid_config_file(self):
        tmpdir = tempfile.gettempdir()
        self.__prepare_file(False)
        self.assertRaises(
            FabricNotValidConfigFile,
            self.fabric.deploy,
            tmpdir + sep + 'fabric_deployer_test.dc'
        )

    def test_fabric_deploy_works(self):
        self.__prepare_file(True)
        fab = ProxySpy(FabricDeployer())

        state.output.update({
            'status': False, 'stdout': False,
            'warnings': False, 'debug': False,
            'running': False, 'user': False,
            'stderr': False, 'aborts': False
        })

        tmpdir = tempfile.gettempdir()
        assert_that(
            fab.deploy(tmpdir + sep + 'fabric_deployer_test.dc'), is_(None))
        assert_that(fab.deploy, called().times(1))

    def __prepare_file(self, valid):
        # we need to delete binary files from previous tests because we get
        # invalid magic method error on buildbot and PyPy
        binary = filepath.FilePath('/tmp/fabric_deployer_test.dco')
        if binary.exists():
            binary.remove()
        del binary

        tmpdir = tempfile.gettempdir()
        content = '''{}
from fabric.api import local


def host_type():
    local('whoami')
        '''.format('# -*- mamba-deployer: fabric -*-' if valid is True else '')
        with open(tmpdir + sep + 'fabric_deployer_test.dc', 'w') as fd:
            fd.write(content)
