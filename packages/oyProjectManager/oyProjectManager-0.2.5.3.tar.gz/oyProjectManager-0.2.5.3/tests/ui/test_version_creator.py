# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys
import os
import shutil
import tempfile
import unittest

import sip
from oyProjectManager.models.asset import Asset
from oyProjectManager.models.auth import User
from oyProjectManager.models.entity import EnvironmentBase
from oyProjectManager.models.project import Project
from oyProjectManager.models.sequence import Sequence
from oyProjectManager.models.shot import Shot
from oyProjectManager.models.version import Version, VersionType

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from oyProjectManager import conf, db
from oyProjectManager.ui import version_creator

import logging
logger = logging.getLogger("oyProjectManager.ui.version_creator")
logger.setLevel(logging.DEBUG)

# exceptions for test purposes
class ExportAs(Exception):
    pass

class TestEnvironment(EnvironmentBase):
    """A test environment which just raises errors to check if the correct
    method has been called
    """
    
    name = "TestEnv"
    
    test_data = {
        "export_as": {"call count": 0, "data": None},
        "save_as": {"call count": 0, "data": None},
        "open_": {"call count": 0, "data": None},
        "reference": {"call count": 0, "data": None},
        "import_": {"call count": 0, "data": None},
    }
    
    def export_as(self, version):
        self.test_data["export_as"]["call count"] += 1
        self.test_data["export_as"]["data"] = version

    def save_as(self, version):
        self.test_data["save_as"]["call count"] += 1
        self.test_data["save_as"]["data"] = version
    
    def open_(self, version, force=False):
        self.test_data["open_"]["call count"] += 1
        self.test_data["open_"]["data"] = version
    
    def reference(self, version):
        self.test_data["reference"]["call count"] += 1
        self.test_data["reference"]["data"] = version
    
    def import_(self, version):
        self.test_data["import_"]["call count"] += 1
        self.test_data["import_"]["data"] = version
    
    def get_last_version(self):
        """mock version of the original this returns None all the time
        """
        return None

class VersionCreatorTester(unittest.TestCase):
    """tests the oyProjectManager.ui.version_creator class
    """
    
    def setUp(self):
        """setup the test
        """
        # -----------------------------------------------------------------
        # start of the setUp
        conf.database_url = "sqlite://"
        
        db.setup()
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        # for PyQt4
        self.app = QtGui.QApplication(sys.argv)
    
    def tearDown(self):
        """clean up the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def show_dialog(self, dialog):
        """show the given dialog
        """
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
    
    def test_close_button_closes_ui(self):
        """testing if the close button is closing the ui
        """
        dialog = version_creator.MainDialog()
        dialog.show()

        self.assertEqual(dialog.isVisible(), True)
        
        # now run the UI
        QTest.mouseClick(dialog.close_pushButton, Qt.LeftButton)
        self.assertEqual(dialog.isVisible(), False)
    
    def test_projects_comboBox_no_problem_when_there_is_no_project(self):
        """testing if there will be no problem when there is no project created
        yet
        """
        dialog = version_creator.MainDialog()
    
    def test_projects_comboBox_is_filled_with_projects(self):
        """testing if the projects_combobox is filled with projects
        """
        # create a couple of test projects
        proj1 = Project("Test Project1")
        proj2 = Project("Test Project2")
        
        proj1.create()
        proj2.create()
        
        dialog = version_creator.MainDialog()
        
        # see if the projects filled with projects
        self.assertEqual(dialog.projects_comboBox.count(), 2)
    
    def test_projects_comboBox_lists_projects_alphabetically(self):
        """testing if the projects_comboBox is filled with projects and they
        are sorted alphabetically
        """
        # create a couple of test projects
        proj1 = Project("Test Project3")
        proj2 = Project("Test Project2")
        proj3 = Project("Test Project1")
        proj4 = Project("Test Project4")

        proj1.create()
        proj2.create()
        proj3.create()
        proj4.create()

        dialog = version_creator.MainDialog()

        # see if the projects filled with projects
        self.assertEqual(dialog.projects_comboBox.count(), 4)
        
        # check if the first element is proj3 and the second proj2 and the
        # third proj1 and forth proj4
        self.assertEqual(
            dialog.projects_comboBox.itemText(0),
            proj3.name
        )
        self.assertEqual(
            dialog.projects_comboBox.itemText(1),
            proj2.name
        )
        self.assertEqual(
            dialog.projects_comboBox.itemText(2),
            proj1.name
        )
        self.assertEqual(
            dialog.projects_comboBox.itemText(3),
            proj4.name
        )
    
    def test_projects_comboBox_is_filled_with_active_projects_only(self):
        """testing if the projects_comboBox is filled with active projects only
        """

        proj1 = Project("Test Project 1")
        proj1.save()
        
        proj2 = Project("Test Project 2")
        proj2.active = False
        proj2.save()
        
        proj3 = Project("Test Project 3")
        proj3.save()
        
        proj4 = Project("Test Project 4")
        proj4.active = False
        proj4.save()
        
        dialog = version_creator.MainDialog()
        
        # check if the projects listed are only the ones active
        item_count = dialog.projects_comboBox.count()
        self.assertEqual(item_count, 2)
        
        item_texts = []
        for i in range(item_count):
            item_texts.append(dialog.projects_comboBox.itemText(i))
        
        self.assertTrue(proj1.name in item_texts)
        self.assertFalse(proj2.name in item_texts)
        self.assertTrue(proj3.name in item_texts)
        self.assertFalse(proj4.name in item_texts)

    def test_projects_comboBox_first_project_is_selected(self):
        """testing if the first project is selected in the project combo box
        """
        # create a couple of test projects
        proj1 = Project("Test Project1")
        proj2 = Project("Test Project2")
        
        proj1.create()
        proj2.create()
        
        dialog = version_creator.MainDialog()
        # see if the projects filled with projects
        self.assertEqual(dialog.projects_comboBox.currentIndex(), 0)
    
    def test_projects_comboBox_has_projects_attribute(self):
        """testing if there is a project object holding the current Project
        instance
        """
        # create a couple of test projects
        proj1 = Project("TEST_PROJ1")
        proj2 = Project("TEST_PROJ2")
        proj3 = Project("TEST_PROJ3")
        
        proj1.create()
        proj2.create()
        proj3.create()
        
        dialog = version_creator.MainDialog()
        
        # check if the projects_comboBox has an attribute called project
        self.assertTrue(hasattr(dialog.projects_comboBox, "projects"))
    
    def test_projects_comboBox_projects_attribute_is_a_list_of_Project_instances(self):
        """testing if the project attribute in the projects_comboBox is a
        Project instance
        """
        # create a couple of test projects
        proj1 = Project("TEST_PROJ1")
        proj2 = Project("TEST_PROJ2")
        proj3 = Project("TEST_PROJ3")
        
        proj1.create()
        proj2.create()
        proj3.create()
        
        dialog = version_creator.MainDialog()
        
        # check if the project is a Project instance
        self.assertTrue(isinstance(dialog.projects_comboBox.projects, list))
        
        self.assertTrue(
            isinstance(dialog.projects_comboBox.projects[0], Project)
        )
        self.assertTrue(
            isinstance(dialog.projects_comboBox.projects[1], Project)
        )
        self.assertTrue(
            isinstance(dialog.projects_comboBox.projects[2], Project)
        )
    
    def test_project_comboBox_with_no_sequences_and_shots(self):
        """testing if no error will be raised when there are couple of projects
        but no sequences
        """
        
        proj1 = Project("TEST_PROJ1")
        proj1.create()
        
        proj2 = Project("TEST_PROJ2")
        proj2.create()
        
        dialog = version_creator.MainDialog()
    
    def test_project_comboBox_updates_the_sequences_if_and_only_if_the_tab_is_in_shots(self):
        """testing if the project_comboBox updates the sequences_comboBox if
        and only if the tab is in the "Shots"
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        proj2 = Project("TEST_PROJECT2")
        proj2.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        seq3 = Sequence(proj1, "TEST_SEQ3")
        
        seq1.save()
        seq2.save()
        seq3.save()
        
        # create the dialog
        dialog = version_creator.MainDialog()
        
        # the default tab should be asset
        self.assertEqual(dialog.tabWidget.currentIndex(), 0)
        
        # the sequences_comboBox should be empty
        self.assertEqual(dialog.sequences_comboBox.count(), 0)
        
        # changing the tabWidget to the Shots should fill the
        # sequences_comboBox
        
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if the sequences_comboBox is filled with sequences
        self.assertEqual(dialog.sequences_comboBox.count(), 3)
    
    def test_users_comboBox_is_filled_with_users_from_the_db(self):
        """testing if the users combobox is filled with the user names
        """
        # get the users from the config
        users = User.query().all()
        
        dialog = version_creator.MainDialog()
        
        # check if all the names in the users are in the comboBox
        content = [dialog.users_comboBox.itemText(i)
                   for i in range(dialog.users_comboBox.count())]
        
        for user in users:
            self.assertTrue(user.name in content)
    

    def test_users_comboBox_is_filled_with_only_active_users_from_the_db(self):
        """testing if the users combobox is filled only with active the user
        names
        """
        # create a couple of users
        user1 = User(name='user1')
        user1.save()
        
        user2 = User(name='user2')
        user2.save()
        
        user3 = User(name='user3', active=False)
        user3.save()
        
        # get the users from the config
        users = User.query().filter(User.active==True).all()
        
        dialog = version_creator.MainDialog()
        
        # check if only the active user names are in the comboBox
        content = [dialog.users_comboBox.itemText(i)
                   for i in range(dialog.users_comboBox.count())]
        
        # check the length
        self.assertEqual(len(content), len(users))
        
        for user in users:
            self.assertTrue(user.name in content)
     
    def test_users_comboBox_has_users_attribute(self):
        """testing if the users_comboBox has an attribute called users
        """
        dialog = version_creator.MainDialog()
        self.assertTrue(hasattr(dialog.users_comboBox, "users"))
    
    def test_users_comboBox_users_attribute_is_properly_filled(self):
        """testing if the users_comboBox users attribute is properly filled
        with User instances from the db
        """
        dialog = version_creator.MainDialog()
        users_from_UI = dialog.users_comboBox.users
        users_from_DB = User.query().all()
        
        # converting from assertItemsEqual
        self.assertTrue(len(users_from_UI)==len(users_from_DB))
        for item in users_from_UI:
            self.assertTrue(item in users_from_DB)
    
    def test_asset_names_list_filled(self):
        """testing if the asset names listWidget is filled with asset names
        """
        
        # create a new project
        proj1 = Project("TEST_PROJECT1a")
        proj2 = Project("TEST_PROJECT2")
        proj1.create()
        proj2.create()
        
        # create a couple of assets
        asset1 = Asset(proj1, "Test Asset 1", type='T1')
        asset2 = Asset(proj1, "Test Asset 2", type='T2')
        asset3 = Asset(proj2, "Test Asset 3", type='T3')
        asset4 = Asset(proj2, "Test Asset 4", type='T4')
        asset1.save()
        asset2.save()
        asset3.save()
        asset4.save()
        
        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
        
        # now check if their names are in the asset names tableWidget
        tableWidget = dialog.assets_tableWidget
        item_texts = [
            tableWidget.item(i, 1).text()
                for i in range(tableWidget.rowCount())
        ]
        
        self.assertTrue(asset1.name in item_texts)
        self.assertTrue(asset2.name in item_texts)
        self.assertTrue(asset3.name not in item_texts)
        self.assertTrue(asset4.name not in item_texts)
        
        # check their types
        item_texts = [
            tableWidget.item(i, 0).text()
                for i in range(tableWidget.rowCount())
        ]
        
        self.assertTrue(asset1.type in item_texts)
        self.assertTrue(asset2.type in item_texts)
        self.assertTrue(asset3.type not in item_texts)
        self.assertTrue(asset4.type not in item_texts)
        
        # now update the project to the second one
        dialog.projects_comboBox.setCurrentIndex(1)
        
        # now check if their names are in the asset names tableWidget
        tableWidget = dialog.assets_tableWidget
        item_texts = [
            tableWidget.item(i, 1).text()
                for i in range(tableWidget.rowCount())
        ]
        
        self.assertTrue(asset1.name not in item_texts)
        self.assertTrue(asset2.name not in item_texts)
        self.assertTrue(asset3.name in item_texts)
        self.assertTrue(asset4.name in item_texts)
    
    def test_takes_listWidget_lists_all_the_takes_of_current_asset_versions(self):
        """testing if the takes_listWidget lists all the takes of the current
        asset and current version_type
        """
        # TODO: test this when there is no asset in the project

        proj1 = Project("TEST_PROJECT1i")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        VersionType.query().filter_by(type_for="Asset").all()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[1], user1,
                        take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[2], user1,
                        take_name="Test3")
        vers6.save()

        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
        
        # check if Main and Test are in the takes_listWidget
        ui_take_names = []
        for i in range(dialog.takes_listWidget.count()):
            dialog.takes_listWidget.setCurrentRow(i)
            ui_take_names.append(
                dialog.takes_listWidget.currentItem().text()
            )

        for take in ["Main", "Test"]:
            self.assertTrue(take in ui_take_names)

    def test_takes_listWidget_lists_all_the_takes_of_current_shot_versions(self):
        """testing if the takes_listWidget lists all the takes of the current
        shot and current version_type
        """
        # TODO: test this when there is no shot in the project

        proj1 = Project("TEST_PROJECT1i")
        proj1.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq1.save()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)

        shot1.save()
        shot2.save()
        shot3.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        VersionType.query().filter_by(type_for="Asset").all()

        shot_vtypes =\
        VersionType.query().filter_by(type_for="Shot").all()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[1], user1,
                        take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[2], user1,
                        take_name="Test3")
        vers6.save()

        # versions for shots
        vers7 = Version(shot1, shot1.code, shot_vtypes[0], user1,
                        take_name="Main")
        vers7.save()

        vers8 = Version(shot1, shot1.code, shot_vtypes[0], user1,
                        take_name="Main")
        vers8.save()

        vers9 = Version(shot1, shot1.code, shot_vtypes[0], user1,
                        take_name="TestForShot")
        vers9.save()

        vers10 = Version(shot2, shot2.code, shot_vtypes[1], user1,
                         take_name="TestForShot2")
        vers10.save()

        vers11 = Version(shot3, shot2.code, shot_vtypes[2], user1,
                         take_name="TestForShot3")
        vers11.save()

        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)

        # set to the shot tab
        dialog.tabWidget.setCurrentIndex(1)

        # select shot1
        item = dialog.shots_listWidget.item(0)
        dialog.shots_listWidget.setCurrentItem(item)

        # check if Main and TestForShot are in the takes_listWidget
        ui_take_names = []
        for i in range(dialog.takes_listWidget.count()):
            dialog.takes_listWidget.setCurrentRow(i)
            ui_take_names.append(
                dialog.takes_listWidget.currentItem().text()
            )

        for take in ["Main", "TestForShot"]:
            self.assertTrue(take in ui_take_names)

        # check if shot2 has correct takes
        item = dialog.shots_listWidget.item(1)
        dialog.shots_listWidget.setCurrentItem(item)

        # check if Main and TestForShot are in the takes_listWidget
        ui_take_names = []
        for i in range(dialog.takes_listWidget.count()):
            dialog.takes_listWidget.setCurrentRow(i)
            ui_take_names.append(
                dialog.takes_listWidget.currentItem().text()
            )
    
        # converting from assertItemsEqual
        self.assertTrue(len(ui_take_names)==1)
        self.assertTrue("TestForShot2" in ui_take_names)
    
    def test_takes_listWidget_lists_Main_by_default(self):
        """testing if the takes_listWidget lists "Main" by default
        """
        
        dialog = version_creator.MainDialog()
        self.assertEqual(
            conf.default_take_name,
            dialog.takes_listWidget.currentItem().text()
        )
    
    def test_takes_listWidget_lists_Main_by_default_for_asset_with_no_versions(self):
        """testing if the takes_listWidget lists "Main" by default for an asset
        with no version
        """
        
        proj = Project("TEST_PROJECT1")
        proj.create()
        
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
        
        self.assertEqual(
            conf.default_take_name,
            dialog.takes_listWidget.currentItem().text()
        )
    
    def test_takes_listWidget_lists_Main_by_default_for_projects_with_no_assets(self):
        """testing if the takes_listWidget lists "Main" by default for an project
        with no assets
        """
        
        # TODO: mixed a lot of test cases in to one test, please separate them
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        proj2 = Project("TEST_PROJECT2")
        proj2.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq1.save()
        
        asset1 = Asset(proj1, "TEST_ASSET")
        asset1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        # create a version with take name is different than Main
        
        asset_vtypes = VersionType.query()\
            .filter(VersionType.type_for=="Asset").all()
        
        shot_vtypes = VersionType.query()\
            .filter(VersionType.type_for=="Shot").all()
        
        user = User("Test User")
        
        vers1 = Version(asset1, asset1.code, asset_vtypes[0], user,
                        take_name="TestTake")
        vers1.save()
        
        vers2 = Version(shot1, shot1.code, shot_vtypes[0], user,
                       take_name="TestTake1")
        vers2.save()
        
        # a project with only one sequence but no shot
        proj3 = Project("TEST_PROJECT3")
        proj3.create()
        
        seq2 = Sequence(proj3, "TEST_SEQ2")
        seq2.save()
        
        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
        
        # switch to project2
        dialog.projects_comboBox.setCurrentIndex(1)
        
        self.assertEqual(
            conf.default_take_name,
            dialog.takes_listWidget.currentItem().text()
        )
    
    def test_takes_listWidget_lists_Main_by_default_for_new_asset_version_types(self):
        """testing if the takes_listWidget lists "Main" by default for an asset
        with a new version added to the version_types comboBox
        """
        
        proj = Project("TEST_PROJECT")
        proj.create()
        
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        # create the dialog
        dialog = version_creator.MainDialog()
        
        # get all the asset version types for project
        asset_vtypes = VersionType.query()\
            .filter(VersionType.type_for=="Asset").all()
        
        type_name = asset_vtypes[0].name
        
        # add new version type by hand
        dialog.version_types_listWidget.addItem(type_name)
        dialog.version_types_listWidget.setCurrentRow(
            dialog.version_types_listWidget.count() - 1
        )
        
        for i in range(dialog.takes_listWidget.count()):
            item = dialog.takes_listWidget.item(i)
            print item.text()
        
        # now check if the takes_listWidget lists Main by default
        self.assertEqual(
            dialog.takes_listWidget.currentItem().text(),
            conf.default_take_name
        )
    
    def test_version_types_listWidget_lists_all_the_types_of_the_current_asset_versions(self):
        """testing if the version_types_listWidget lists all the types of
        the current asset
        """
        
        proj1 = Project("TEST_PROJECT1j")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()
        
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
            VersionType.query().filter_by(type_for="Asset").all()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
                        take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[1], user1,
                        take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[2], user1,
                        take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[3], user1,
                        take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[4], user1,
                        take_name="Test3")
        vers6.save()

        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)

        # check if Main and Test are in the takes_listWidget
        ui_type_names = []
        for i in range(dialog.version_types_listWidget.count()):
            dialog.version_types_listWidget.setCurrentRow(i)
            ui_type_names.append(
                dialog.version_types_listWidget.currentItem().text()
            )
        
        # converting from assertItemsEqual
        self.assertTrue(len(ui_type_names)==3)
        for item in [asset_vtypes[0].name, asset_vtypes[1].name, asset_vtypes[2].name]:
            self.assertTrue(item in ui_type_names)

    def test_version_types_listWidget_lists_all_the_types_of_the_current_asset_versions_compatible_with_the_environment(self):
        """testing if the version_types_listWidget lists all the types of
        the current asset
        """

        proj1 = Project("TEST_PROJECT1j")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
            email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        VersionType.query().filter_by(type_for="Asset").all()

        asset_vtypes[0].environments = ["TestEnv"]
        asset_vtypes[1].environments = ["TestEnv"]
        asset_vtypes[4].environments = ["TestEnv"]
        db.session.commit()

        vers1 = Version(asset1, asset1.name, asset_vtypes[0], user1,
            take_name="Main")
        vers1.save()

        vers2 = Version(asset1, asset1.name, asset_vtypes[0], user1,
            take_name="Main")
        vers2.save()

        vers3 = Version(asset1, asset1.name, asset_vtypes[1], user1,
            take_name="Test")
        vers3.save()

        vers4 = Version(asset1, asset1.name, asset_vtypes[2], user1,
            take_name="Test")
        vers4.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(asset2, asset2.name, asset_vtypes[3], user1,
            take_name="Test2")
        vers5.save()

        vers6 = Version(asset2, asset2.name, asset_vtypes[4], user1,
            take_name="Test3")
        vers6.save()

        tEnv = TestEnvironment()

        dialog = version_creator.MainDialog(tEnv)
        #self.show_dialog(dialog)

        # check if Main and Test are in the takes_listWidget
        ui_type_names = []
        for i in range(dialog.version_types_listWidget.count()):
            dialog.version_types_listWidget.setCurrentRow(i)
            ui_type_names.append(
                dialog.version_types_listWidget.currentItem().text()
            )

        # converting from assertItemsEqual
        self.assertTrue(len(ui_type_names)==2)
        for item in [asset_vtypes[0].name, asset_vtypes[1].name]:
            self.assertTrue(item in ui_type_names)

    def test_version_types_listWidget_lists_all_the_types_of_the_current_shot_versions_compatible_with_the_environment(self):
        """testing if the version_types_listWidget lists all the types of the
        current shot which is compatible with the current environment
        """

        proj1 = Project("TEST_PROJECT1j")
        proj1.create()
        
        seq1 = Sequence(proj1, "Test Sequence 1")
        seq1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()

        shot2 = Shot(seq1, 2)
        shot2.save()

        # new user
        user1 = User(name="User1", initials="u1",
            email="user1@test.com")

        # create a couple of versions
        shot_vtypes =\
            VersionType.query().filter_by(type_for="Shot").all()
        
        shot_vtypes[0].environments = ["TestEnv"]
        shot_vtypes[1].environments = ["TestEnv"]
        shot_vtypes[4].environments = ["TestEnv"]
        db.session.commit()
        
        vers1 = Version(shot1, shot1.code, shot_vtypes[0], user1,
            take_name="Main")
        vers1.save()

        vers2 = Version(shot1, shot1.code, shot_vtypes[0], user1,
            take_name="Main")
        vers2.save()

        vers3 = Version(shot1, shot1.code, shot_vtypes[1], user1,
            take_name="Test")
        vers3.save()

        vers4 = Version(shot1, shot1.code, shot_vtypes[2], user1,
            take_name="Test")
        vers4.save()

        # a couple of versions for shot2 to see if they are going to be mixed
        vers5 = Version(shot2, shot2.code, shot_vtypes[3], user1,
            take_name="Test2")
        vers5.save()

        vers6 = Version(shot2, shot2.code, shot_vtypes[4], user1,
            take_name="Test3")
        vers6.save()

        tEnv = TestEnvironment()

        dialog = version_creator.MainDialog(tEnv)
        #self.show_dialog(dialog)
        
        # set tabs to shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # check if Main and Test are in the takes_listWidget
        ui_type_names = []
        for i in range(dialog.version_types_listWidget.count()):
            dialog.version_types_listWidget.setCurrentRow(i)
            ui_type_names.append(
                dialog.version_types_listWidget.currentItem().text()
            )
        
        # converting from assertItemsEqual
        self.assertTrue(len(ui_type_names)==2)
        for item in [shot_vtypes[0].name, shot_vtypes[1].name]:
            self.assertTrue(item in ui_type_names)

    def test_previous_versions_tableWidget_is_updated_properly(self):
        """testing if the previous_versions_tableWidget is updated properly
        when the version_type is changed to a type with the same take_name
        """

        proj1 = Project("TEST_PROJECT1k")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
        VersionType.query().filter_by(type_for="Asset").all()

        vers1 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note"
        )
        vers1.save()

        vers2 = Version(
            asset1,
            asset1.name,
            asset_vtypes[1],
            user1,
            take_name="Main",
            note="test note 2"
        )
        vers2.save()

        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)

        # select the first asset
        table_item = dialog.assets_tableWidget.selectRow(0)

        # select the first type
        dialog.version_types_listWidget.setCurrentRow(0)

        # select the first take
        dialog.takes_listWidget.setCurrentRow(0)

        # which should list vers1

        # the row count should be 1
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            1
        )

        # now check if the previous versions tableWidget has the info
        self.assertEqual(
            int(dialog.previous_versions_tableWidget.item(0, 0).text()),
            vers1.version_number
        )

        self.assertEqual(
            dialog.previous_versions_tableWidget.item(0, 1).text(),
            vers1.created_by.name
        )

        #self.assertEqual(
        #    dialog.previous_versions_tableWidget.item(0, 3).text(),
        #    datetime.datetime.fromtimestamp(
        #            os.path.getmtime(vers1.full_path)
        #    ).strftime(conf.time_format)
        #)

        #self.assertEqual(
        #    dialog.previous_versions_tableWidget.item(0, 4).text(),
        #    vers1.note
        #)

    def test_previous_versions_tableWidget_is_filled_with_proper_info(self):
        """testing if the previous_versions_tableWidget is filled with proper
        information
        """

        proj1 = Project("TEST_PROJECT1l")
        proj1.create()

        asset1 = Asset(proj1, "TEST_ASSET1")
        asset1.save()

        asset2 = Asset(proj1, "TEST_ASSET2")
        asset2.save()

        # new user
        user1 = User(name="User1", initials="u1",
                     email="user1@test.com")

        # create a couple of versions
        asset_vtypes =\
            VersionType.query().filter_by(type_for="Asset").all()
        
        vers1 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note"
        )
        vers1.save()
        
        vers2 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note 2"
        )
        vers2.save()

        vers3 = Version(
            asset1,
            asset1.name,
            asset_vtypes[1],
            user1,
            take_name="Main",
            note="test note 3"
        )
        vers3.save()

        vers4 = Version(
            asset1,
            asset1.name,
            asset_vtypes[2],
            user1,
            take_name="Main",
            note="test note 4"
        )
        vers4.save()

        vers4a = Version(
            asset1,
            asset1.name,
            asset_vtypes[2],
            user1,
            take_name="NewTake",
            note="test note 4a"
        )
        vers4a.save()

        # a couple of versions for asset2 to see if they are going to be mixed
        vers5 = Version(
            asset2,
            asset2.name,
            asset_vtypes[3],
            user1,
            take_name="Test2",
            note="test note 5"
        )
        vers5.save()

        vers6 = Version(
            asset2,
            asset2.name,
            asset_vtypes[4],
            user1,
            take_name="Test3",
            note="test note 6",
            is_published=True
        )
        vers6.save()

        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
        
        # select the first asset
        table_item = dialog.assets_tableWidget.selectRow(0)

        # select the first type
        dialog.version_types_listWidget.setCurrentRow(0)

        # select the first take
        dialog.takes_listWidget.setCurrentRow(0)

        # which should list vers1 and vers2

        # the row count should be 2
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            2
        )

        # now check if the previous versions tableWidget has the info

        versions = [vers1, vers2]
        for i in range(2):

            self.assertEqual(
                int(dialog.previous_versions_tableWidget.item(i, 0).text()),
                versions[i].version_number
            )

            self.assertEqual(
                dialog.previous_versions_tableWidget.item(i, 1).text(),
                versions[i].created_by.name
            )

            # TODO: add test for file size column

            #self.assertEqual(
            #    dialog.previous_versions_tableWidget.item(i, 3).text(),
            #    datetime.datetime.fromtimestamp(
            #        os.path.getmtime(versions[i].full_path)
            #    ).strftime(conf.time_format)
            #)

            #self.assertEqual(
            #    dialog.previous_versions_tableWidget.item(i, 4).text(),
            #    versions[i].note
            #)

#    def test_speed_test(self):
#        """test the speed of the interface
#        """
#        
#        import logging
#        logger = logging.getLogger("oyProjectManager")
#        logger.setLevel(logging.FATAL)
#        
#        projects = []
#        for i in range(10):
#            # create projects
#            proj = Project("TEST_PROJ%03d" % i)
#            proj.create()
#            
##            data = []
#            
#            user = User("Test User 1", "tu1")
#            
#            for j in range(10):
#                # create assets
#                asset = Asset(proj, "TEST_ASSET%03d" % j)
##                asset.save()
#                proj.session.add(asset)
#                
#                asset_types = \
#                    VersionType.query().filter_by(type_for="Asset").all()
#                
##                data.append(asset)
#                
#                for asset_type in asset_types:
#                    
#                    take_list = ["Take1", "Take2", "Take3", "Take4"]
#                    
#                    for take in take_list:
#                        
#                        for k in range(10):
#                            # create versions
#                            vers = Version(asset, asset.name, asset_type, user,take)
##                            vers.save()
#                            proj.session.add(vers)
#                            
##                            data.append(vers)
#            
##            proj.session.add_all(data)
#            proj.session.commit()
#        
#        dialog = version_creator.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )

    def test_tab_changed_updates_types_comboBox(self):
        """testing if the the types_comboBox is updated according to the
        selected tab
        """

        # project
        proj1 = Project("TEST_PROJECT")
        proj1.create()

        # sequence
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        seq3 = Sequence(proj1, "TEST_SEQ3")
        seq4 = Sequence(proj1, "TEST_SEQ4")
        
        seq1.save()
        seq2.save()
        seq3.save()
        seq4.save()

        # user
        user1 = User("Test User", "tu")

        # assets
        asset1 = Asset(proj1, "TEST_ASSET1")
        asset2 = Asset(proj1, "TEST_ASSET2")
        asset1.save()
        asset2.save()

        # shots
        shot1 = Shot(seq1, 1)
        shot1.save()
        shot2 = Shot(seq1, 2)
        shot2.save()
        shot3 = Shot(seq1, 3)
        shot3.save()

        asset_vtypes = VersionType.query().\
            filter_by(type_for="Asset").all()

        shot_vtypes = VersionType.query().\
            filter_by(type_for="Shot").all()

        # versions
        vers1 = Version(asset1, asset1.code, asset_vtypes[0], user1)
        vers1.save()
        vers2 = Version(asset2, asset2.code, asset_vtypes[1], user1)
        vers2.save()
        vers3 = Version(shot1, shot1.code, shot_vtypes[0], user1)
        vers3.save()
        vers4 = Version(shot2, shot2.code, shot_vtypes[1], user1)
        vers4.save()

        dialog = version_creator.MainDialog()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # set the tab to Asset
        dialog.tabWidget.setCurrentIndex(0)

        # check if the type comboBox lists the asset type of the first asset
        self.assertEqual(
            dialog.version_types_listWidget.currentItem().text(),
            asset_vtypes[0].name
        )

        # set the tab to Shots
        dialog.tabWidget.setCurrentIndex(1)

        # check if the type comboBox lists the asset type of the first shot
        self.assertEqual(
            dialog.version_types_listWidget.currentItem().text(),
            shot_vtypes[0].name
        )

    def test_sequence_comboBox_changed_fills_shots_listWidget(self):
        """testing if the shots_listWidget is filled with proper shot codes
        when the sequences_comboBox is changed
        """

        proj1 = Project("TEST_PROJECT1")
        proj2 = Project("TEST_PROJECT2")

        proj1.create()
        proj2.create()

        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        seq1.save()
        seq2.save()

        # for seq1
        shot1_1 = Shot(seq1, 1)
        shot1_2 = Shot(seq1, 2)
        shot1_3 = Shot(seq1, "1A")
        shot1_4 = Shot(seq1, "2A")
        shot1_5 = Shot(seq1, "3")

        shot1_1.save()
        shot1_2.save()
        shot1_3.save()
        shot1_4.save()
        shot1_5.save()

        # for seq2
        shot2_1 = Shot(seq2, 1)
        shot2_2 = Shot(seq2, 2)
        shot2_3 = Shot(seq2, 3)
        shot2_4 = Shot(seq2, 4)
        shot2_5 = Shot(seq2, 5)

        shot2_1.save()
        shot2_2.save()
        shot2_3.save()
        shot2_4.save()
        shot2_5.save()

        # create the dialog
        dialog = version_creator.MainDialog()
        #        dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )

        # change the tabWidget to Shots
        dialog.tabWidget.setCurrentIndex(1)

        # set the sequences_comboBox to index 0
        dialog.sequences_comboBox.setCurrentIndex(0)

        # check if the shots_listWidget has the correct items
        listWidget = dialog.shots_listWidget
        item_texts = [listWidget.item(i).text() for i in range(listWidget.count())]
        
        for item_text in item_texts:
            self.assertTrue(
                item_text in 
                ["SH001", "SH002", "SH001A", "SH002A", "SH003"]
            )

        # change the sequence to sequence 2
        dialog.sequences_comboBox.setCurrentIndex(1)

        # check if the shots_listWidget has the correct items
        item_texts = [listWidget.item(i).text() for i in range(listWidget.count())]

        for item_text in item_texts:
            self.assertTrue(
                item_text in 
                ["SH001", "SH002", "SH003", "SH004", "SH005"]
            )
    
    def test_shots_listWidget_has_shots_attribute(self):
        """testing if the shot_listWidget has an attribute called shots
        """
        dialog = version_creator.MainDialog()
        self.assertTrue(hasattr(dialog.shots_listWidget, "shots"))
    
    def test_shots_listWidget_shots_attribute_is_filled_with_shots_instances(self):
        """testing if the shots_listWidget's shots attribute is filled with the
        current Shot instances of the current Sequence
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        seq1.save()
        seq2.save()
        
        # for seq1
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        shot5 = Shot(seq1, 5)
        
        # for seq2
        shot6 = Shot(seq2, 1)
        shot7 = Shot(seq2, 2)
        shot8 = Shot(seq2, 3)
        shot9 = Shot(seq2, 4)
        shot10 = Shot(seq2, 5)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        shot5.save()
        shot6.save()
        shot7.save()
        shot8.save()
        shot9.save()
        shot10.save()
        
        dialog = version_creator.MainDialog()
        
        # switch to the shots tab
        dialog.tabWidget.setCurrentIndex(1)
        
        # select the first sequence
        dialog.sequences_comboBox.setCurrentIndex(0)
        
        # check if the shots_listWidget's shot attribute is a list and has the
        # shots
        
        expected_list = [shot1, shot2, shot3, shot4, shot5]
        
        self.assertEqual(len(dialog.shots_listWidget.shots), 5)
        
        self.assertTrue(all([isinstance(shot, Shot) for shot in dialog.shots_listWidget.shots]))
        
        for shot in dialog.shots_listWidget.shots:
            self.assertTrue(
                shot in 
                expected_list
            )

    # TODO: update this test
#    def test_create_asset_pushButton_pops_up_a_QInputDialog(self):
#        """testing if the create_asset_pushButton pops up a QInputDialog
#        """
#
#        proj = Project("TEST_PROJ1")
#        proj.create()
#        
#        dialog = version_creator.MainDialog()
##        dialog.show()
##        self.app.exec_()
##        self.app.connect(
##            self.app,
##            QtCore.SIGNAL("lastWindowClosed()"),
##            self.app,
##            QtCore.SLOT("quit()")
##        )
#        
#        # push the create asset button
#        # spawn a new thread to click the button
##        class Thread1(QtCore.QThread):
##            def run(self):
##                """overridden run method
##                """
##                QTest.mouseClick(dialog.create_asset_pushButton, Qt.LeftButton)
##                self.exec_()
##        
##        thread1 = Thread1()
###        thread1.run()
##        thread1.start()
##        
##        print dialog.input_dialog
##        thread1.wait()
#        
##        print "something"
##        
##        thread2 = threading.Thread(
##            target=QTest.keyClicks,
##            args=(dialog.input_dialog, "test name"),
##        )
##        thread2.start()
##        thread2.join()
##        
##        thread3 = threading.Thread(
##            target=QTest.keyClick,
##            args=(dialog.input_dialog, Qt.Key_Enter)
##        )
##        thread3.start()
##        thread3.join()
##        
##        self.assertTrue(dialog.input_dialog.isShown())
#        
#        self.fail("test is not implemented yet")

    def test_add_type_toolButton_pops_up_a_QInputDialog_for_asset(self):
        """testing if hitting the add_type_toolButton pops up a QInputDialog
        with a comboBox filled with all the suitable version types for the
        current asset
        """
        
        proj1 = Project("TEST_PROJECT")
        proj1.create()
        
        # create assets
        asset1 = Asset(proj1, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(proj1, "Test Asset 2")
        asset2.save()
        
        # sequences
        seq1 = Sequence(proj1, "Test Sequence 1")
        seq2 = Sequence(proj1, "Test Sequence 2")
        
        seq1.save()
        seq2.save()
        
        # shots
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        
        shot4 = Shot(seq2, 4)
        shot5 = Shot(seq2, 5)
        shot6 = Shot(seq2, 6)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        shot5.save()
        shot6.save()
        
        # new user
        user1 = User(
            name="User1",
            initials="u1",
            email="user1@test.com"
        )
        
        # create a couple of versions
        asset_vtypes =\
            VersionType.query().filter_by(type_for="Asset").all()
        
        vers1 = Version(
            asset1,
            asset1.name,
            asset_vtypes[0],
            user1,
            take_name="Main",
            note="test note"
        )
        vers1.save()
        
        dialog = version_creator.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        pass
    
    def test_add_type_will_not_add_the_same_type_more_than_once(self):
        """testing if using the add_type will not add the same type to the list
        over and over again
        """
        
        proj = Project("TEST_PROJECT1")
        proj.create()
        
        # create an asset
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        # get types for assets and shots
        asset_vtypes = \
            VersionType.query().filter_by(type_for="Asset").all()
        shot_vtypes = \
            VersionType.query().filter_by(type_for="Shot").all()
        
        # create the dialog
        dialog = version_creator.MainDialog()
        
        # set the tabWidget to asset
        dialog.tabWidget.setCurrentIndex(0)
        
        # check if the version_type_comboBox has no item
        self.assertEqual(dialog.version_types_listWidget.count(), 0)
        
        # try to add a asset type for the asset
        dialog.add_type(asset_vtypes[0])
        
        # check if the version_type_comboBox has one item
        self.assertEqual(dialog.version_types_listWidget.count(), 1)
        
        # try to add the same thing for a second time
        dialog.add_type(asset_vtypes[0])
        
        # check if the version_type_comboBox has one item
        self.assertEqual(dialog.version_types_listWidget.count(), 1)
    
    def test_add_type_will_not_add_inappropriate_type_for_the_current_versionable(self):
        """testing if add_type will not add will not add the given type to the
        list if it is not appropriate for the current versionable object, that
        is it will not add a new version type if it is not suitable for Shots
        or for Assets depending to the current tab
        """
        
        proj = Project("TEST_PROJECT1")
        proj.create()
        
        # create an asset
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        # get types for assets and shots
        asset_vtypes = VersionType.query().filter_by(type_for="Asset").all()
        shot_vtypes = VersionType.query().filter_by(type_for="Shot").all()
        
        # create the dialog
        dialog = version_creator.MainDialog()
        
        # set the tabWidget to asset
        dialog.tabWidget.setCurrentIndex(0)
        
        # try to add a shot type for the asset
        self.assertRaises(TypeError, dialog.add_type, shot_vtypes[0])
        
        # check if the version_type_comboBox still has no items
        self.assertEqual(dialog.version_types_listWidget.count(), 0)
    
    def test_add_type_will_add_the_name_of_the_version_type(self):
        """testing if using the add_type will add the name of the given
        VersionType to the list
        """
        
        proj = Project("TEST_PROJECT1")
        proj.create()
        
        # create an asset
        asset1 = Asset(proj, "TEST_ASSET")
        asset1.save()
        
        # get types for assets and shots
        asset_vtypes = VersionType.query().filter_by(type_for="Asset").all()
        shot_vtypes = VersionType.query().filter_by(type_for="Shot").all()
        
        # create the dialog
        dialog = version_creator.MainDialog()
        
        # set the tabWidget to asset
        dialog.tabWidget.setCurrentIndex(0)
        
        # check if the version_type_comboBox has no item
        self.assertEqual(dialog.version_types_listWidget.count(), 0)
        
        # try to add a asset type for the asset
        dialog.add_type(asset_vtypes[0])
        
        # check if the version_type_comboBox has one item
        self.assertEqual(
            dialog.version_types_listWidget.currentItem().text(),
            asset_vtypes[0].name
        )
    
    def test_add_type_will_work_with_VersionType_instances_only(self):
        """testing if the add_type method work only with VersionType instances
        """
        
        proj = Project("TEST_PROJECT")
        proj.create()
        
        dialog = version_creator.MainDialog()
        
        self.assertRaises(
            TypeError, dialog.add_type, 13212
        )
    
    def test_get_versionable_returns_the_correct_versionable_instance(self):
        """testing if the get_versionable method is returning the correct
        versionable from the UI
        """
        
        proj1 = Project("TEST_PROJECT1")
        proj1.create()
        
        # Assets
        asset1 = Asset(proj1, "Test Asset1", type='Default')
        asset1.save()
        
        asset2 = Asset(proj1, "Test Asset2", type='Default')
        asset2.save()
        
        asset3 = Asset(proj1, "Test Asset3", type='Default')
        asset3.save()
        
        # sequences
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        seq1.save()
        seq2.save()
        
        # Shots
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq1, 3)
        shot4 = Shot(seq1, 4)
        
        shot1.save()
        shot2.save()
        shot3.save()
        shot4.save()
        
        dialog = version_creator.MainDialog()
        
        # set the tabWidget to 0
        dialog.tabWidget.setCurrentIndex(0)
        
        logger.debug(dialog.assets_tableWidget.assets)
        
        # set to the first asset
        dialog.assets_tableWidget.selectRow(0)
        
        # get the current versionable and expect it to be the asset1
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, asset1)
        
        # set to the second asset
        dialog.assets_tableWidget.selectRow(1)
        
        #dialog.show()
        #self.app.exec_()
        #self.app.connect(
        #    self.app,
        #    QtCore.SIGNAL("lastWindowClosed()"),
        #    self.app,
        #    QtCore.SLOT("quit()")
        #)
        
        # get the current versionable and expect it to be the asset2
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, asset2)
        
        # switch to shot tab
        dialog.tabWidget.setCurrentIndex(1)
        
        # set to the first sequence
        dialog.sequences_comboBox.setCurrentIndex(0)
        
        # set to the first shot
        dialog.shots_listWidget.setCurrentRow(0)
        
        # get the versionable and expect it to be shot1
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, shot1)
        
        # set it to the second shot
        dialog.shots_listWidget.setCurrentRow(1)
        
        # get the versionable and expect it to be shot2
        versionable = dialog.get_versionable()
        
        self.assertEqual(versionable, shot2)

    # TODO: update this test
#    def test_add_take_toolButton_pops_up_a_QInputDialog_with_input_field(self):
#        """testing if the add_take_toolButton pops up a QInputDialog with an
#        input text field
#        """
#        self.fail("test is not implemented yet")
    
    def test_setup_defaults_will_setup_the_db(self):
        """testing if the database also will be setup
        """
        
        self.assertTrue(db.session is None)
        dialog = version_creator.MainDialog()
        self.assertTrue(db.session is not None)
    
    def test_restore_ui_works_properly(self):
        """testing if restore_ui method is restoring the environment with the
        given version instance
        """
        
        proj1 = Project(name="Test Project 1")
        proj1.create()
        
        proj2 = Project(name="Test Project 2")
        proj2.create()
        
        # sequences
        
        # for proj1
        seq1 = Sequence(proj1, "Seq1")
        seq1.save()
        
        seq2 = Sequence(proj1, "Seq2")
        seq2.save()

        # for proj2
        seq3 = Sequence(proj2, "Seq3")
        seq3.save()

        seq4 = Sequence(proj2, "Seq4")
        seq4.save()
        
        # shots

        # for seq1
        shot1 = Shot(seq1, 1)
        shot1.save()

        shot2 = Shot(seq1, 2)
        shot2.save()

        # for seq2
        shot3 = Shot(seq2, 3)
        shot3.save()

        shot4 = Shot(seq2, 4)
        shot4.save()

        # for seq3
        shot5 = Shot(seq3, 5)
        shot5.save()

        shot6 = Shot(seq3, 6)
        shot6.save()

        # for seq4
        shot7 = Shot(seq4, 7)
        shot7.save()

        shot8 = Shot(seq4, 8)
        shot8.save()
        
        # create assets
        asset1 = Asset(proj1, name="Test Asset 1")
        asset1.save()
        
        asset2 = Asset(proj1, name="Test Asset 2")
        asset2.save()

        asset3 = Asset(proj2, name="Test Asset 3")
        asset3.save()

        asset4 = Asset(proj2, name="Test Asset 4")
        asset4.save()

        # user
        user1 = User(name="Test User 1", initials="TU1")
        user2 = User(name="Test User 2", initials="TU2")
        
        # create versions
        asset_vTypes = VersionType.query()\
            .filter(VersionType.type_for=="Asset")\
            .all()
        
        shot_vTypes = VersionType.query()\
            .filter(VersionType.type_for=="Shot")\
            .all()

        # for asset1
        vers1 = Version(
            asset1, asset1.code, asset_vTypes[0], user1, take_name="Take1"
        )
        vers1.save()

        vers2 = Version(
            asset1, asset1.code, asset_vTypes[0], user1, take_name="Take1"
        )
        vers2.save()

        vers3 = Version(
            asset1, asset1.code, asset_vTypes[0], user1, take_name="Take2"
        )
        vers3.save()

        # for asset2
        vers4 = Version(
            asset2, asset2.code, asset_vTypes[1], user2, take_name="Take3"
        )
        vers4.save()

        vers5 = Version(
            asset2, asset2.code, asset_vTypes[1], user2, take_name="Take4"
        )
        vers5.save()

        vers6 = Version(
            asset2, asset2.code, asset_vTypes[2], user1, take_name="Take4"
        )
        vers6.save()

        # for asset3
        vers7 = Version(
            asset3, asset3.code, asset_vTypes[2], user1, take_name="Take5"
        )
        vers7.save()

        vers8 = Version(
            asset3, asset3.code, asset_vTypes[2], user1, take_name="Take6"
        )
        vers8.save()

        vers9 = Version(
            asset3, asset3.code, asset_vTypes[3], user2, take_name="Take7"
        )
        vers9.save()

        # for asset4
        vers10 = Version(
            asset4, asset4.code, asset_vTypes[5], user1, take_name="Take8A",
            note="This is a test note"
        )
        vers10.save()

        vers11 = Version(
            asset4, asset4.code, asset_vTypes[5], user2, take_name="Take8"
        )
        vers11.save()
        
        vers12 = Version(
            asset4, asset4.code, asset_vTypes[4], user2, take_name="Take8"
        )
        vers12.save()

        # for shot1
        vers13 = Version(
            shot1, shot1.code, shot_vTypes[0], user1, take_name="Take10"
        )
        vers13.save()

        vers14 = Version(
            shot1, shot1.code, shot_vTypes[0], user1, take_name="Take10"
        )
        vers14.save()

        # for shot2
        vers15 = Version(
            shot2, shot2.code, shot_vTypes[0], user2, take_name="Take11"
        )
        vers15.save()

        vers16 = Version(
            shot2, shot2.code, shot_vTypes[0], user2, take_name="Take11"
        )
        vers16.save()

        # for shot3
        vers17 = Version(
            shot3, shot3.code, shot_vTypes[1], user1, take_name="Take12"
        )
        vers17.save()

        vers18 = Version(
            shot3, shot3.code, shot_vTypes[1], user1, take_name="Take12"
        )
        vers18.save()

        # for shot4
        vers19 = Version(
            shot4, shot4.code, shot_vTypes[1], user1, take_name="Take13"
        )
        vers19.save()

        vers20 = Version(
            shot4, shot4.code, shot_vTypes[1], user1, take_name="Take13"
        )
        vers20.save()

        # for shot5
        vers21 = Version(
            shot5, shot5.code, shot_vTypes[2], user1, take_name="Take14"
        )
        vers21.save()

        vers22 = Version(
            shot5, shot5.code, shot_vTypes[2], user1, take_name="Take14"
        )
        vers22.save()

        # for shot6
        vers23 = Version(
            shot6, shot6.code, shot_vTypes[2], user1, take_name="Take15"
        )
        vers23.save()

        vers24 = Version(
            shot6, shot6.code, shot_vTypes[2], user1, take_name="Take15"
        )
        vers24.save()

        # for shot7
        vers25 = Version(
            shot7, shot7.code, shot_vTypes[3], user1, take_name="Take16"
        )
        vers25.save()

        vers26 = Version(
            shot7, shot7.code, shot_vTypes[3], user1, take_name="Take16"
        )
        vers26.save()

        # for shot8
        vers27 = Version(
            shot8, shot8.code, shot_vTypes[4], user1, take_name="Take17"
        )
        vers27.save()

        vers28 = Version(
            shot8, shot8.code, shot_vTypes[4], user1, take_name="Take17"
        )
        vers28.save()

        dialog = version_creator.MainDialog()
        
        # try to restore the ui with version10
        dialog.restore_ui(vers10)
        
        # check for an asset
        # check if the fields show data from version10
        self.assertEqual(
            vers10.project.name,
            dialog.projects_comboBox.currentText(),
        )
        
        self.assertEqual(
            dialog.tabWidget.currentIndex(), 0
        )
        
        index = dialog.assets_tableWidget.currentRow()
        item_text = dialog.assets_tableWidget.item(index, 0).text()
        self.assertEqual(
            item_text,
            vers10.version_of.type
        )
        
        index = dialog.assets_tableWidget.currentRow()
        item_text = dialog.assets_tableWidget.item(index, 1).text()
        self.assertEqual(
            vers10.version_of.name,
            item_text
        )
        
        self.assertEqual(
            vers10.type.name,
            dialog.version_types_listWidget.currentItem().text()
        )
        
        self.assertEqual(
            vers10.take_name,
            dialog.takes_listWidget.currentItem().text(),
        )
        
        # check for a shot
        dialog.restore_ui(vers28)
        
        self.assertEqual(
            dialog.projects_comboBox.currentText(),
            vers28.project.name
        )
        
        self.assertEqual(
            dialog.tabWidget.currentIndex(), 1
        )
        
        self.assertEqual(
            dialog.sequences_comboBox.currentText(),
            vers28.version_of.sequence.name
        )
        
        self.assertEqual(
            dialog.shots_listWidget.currentItem().text(),
            vers28.version_of.code
        )
        
        self.assertEqual(
            dialog.version_types_listWidget.currentItem().text(),
            vers28.type.name
        )
        
        self.assertEqual(
            dialog.takes_listWidget.currentItem().text(),
            vers28.take_name
        )
    
    def test_users_comboBox_shows_the_last_user_from_conf(self):
        """testing if the users_comboBox shows the last user from the previous
        session
        """
        
        project = Project("Test Project")
        project.save()
        
        asset = Asset(project, "Test Asset")
        asset.save()
        
        asset_v_types = VersionType.query().\
            filter(VersionType.type_for=="Asset").all()
        
        user1 = User("User1")
        user2 = User("User2")
        user3 = User("User3")
        
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        dialog = version_creator.MainDialog()
        
        # select asset1
        dialog.tabWidget.setCurrentIndex(0)
        
        # set type to asset_v_types[0]
        dialog.version_types_listWidget.addItem(asset_v_types[0].name)
        
        # set the user to user2
        index = dialog.users_comboBox.findText(user2.name)
        dialog.users_comboBox.setCurrentIndex(index)
        
        # hit save
        QTest.mouseClick(dialog.save_as_pushButton, Qt.LeftButton)
        
        # close the dialog
        dialog.close()
        
        # re-open the dialog
        dialog = version_creator.MainDialog()
        
        # check if the users_comboBox is set to user2
        self.assertEqual(
            dialog.users_comboBox.currentText(),
            user2.name
        )
    
    def test_get_new_version_with_publish_checkBox_is_checked_creates_published_Version(self):
        """testing if checking the publish_checkbox will create a published
        Version instance
        """

        proj1 = Project("Test Project")
        proj1.save()

        asset1 = Asset(proj1, "Test Asset")
        asset1.save()

        asset_vtypes = VersionType.query().filter_by(type_for="Asset").all()

        user = User("Test User")
        db.session.add(user)
        db.session.commit()

        # create a new version
        vers1 = Version(asset1, asset1.code, asset_vtypes[0], user)
        vers1.save()
        
        dialog = version_creator.MainDialog()
        
        # set the tab to assets
        dialog.tabWidget.setCurrentIndex(0)

        # check the publish checkbox
        dialog.publish_checkBox.setChecked(True)
        
        vers_new = dialog.get_new_version()
        
        # is_published should be True
        self.assertTrue(vers_new.is_published==True)
    
    def test_previous_version_tableWidget_shows_published_Versions_in_bold(self):
        """testing if the previous_version_tableWidget is showing published
        Versions in bold
        """
        
        proj1 = Project("Test Project")
        proj1.save()
        
        asset = Asset(proj1, "Test Asset 1")
        asset.save()
        
        asset_types = VersionType.query().filter_by(type_for="Asset").all()
        
        user = User("Test User")
        user.save()

        vers1 = Version(asset, asset.code, asset_types[0], user)
        vers1.save()
        
        vers2 = Version(asset, asset.code, asset_types[0], user)
        vers2.save()
        
        vers3 = Version(asset, asset.code, asset_types[0], user, is_published=True)
        vers3.save()
        
        vers4 = Version(asset, asset.code, asset_types[0], user)
        vers4.save()
        
        vers5 = Version(asset, asset.code, asset_types[0], user, is_published=True)
        vers5.save()
        
        dialog = version_creator.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )
        
        # check if ver3 and vers5 is written with bold font
        self.assertEqual(
            dialog.previous_versions_tableWidget.item(0, 0).font().bold(),
            False
        )

        self.assertEqual(
            dialog.previous_versions_tableWidget.item(1, 0).font().bold(),
            False
        )
        
        self.assertEqual(
            dialog.previous_versions_tableWidget.item(2, 0).font().bold(),
            True
        )

        self.assertEqual(
            dialog.previous_versions_tableWidget.item(3, 0).font().bold(),
            False
        )
        
        self.assertEqual(
            dialog.previous_versions_tableWidget.item(4, 0).font().bold(),
            True
        )
    
    def test_previous_versions_tableWidget_shows_only_published_versions_if_show_published_only_checkBox(self):
        """testing if previous_versions_tableWidget shows only published
        versions if show_published_only_checkBox is checked
        """
        project = Project("Test Project")
        project.save()
        
        asset1 = Asset(project, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(project, "Test Asset 2")
        asset2.save()
        
        aTypes = VersionType.query().filter_by(type_for="Asset").all()
        
        user = User("Test User")
        
        vers1 = Version(
            asset1,
            asset1.code,
            aTypes[0],
            user,
            is_published=False
        )
        vers1.save()

        vers2 = Version(
            asset1,
            asset1.code,
            aTypes[0],
            user,
            is_published=False
        )
        vers2.save()

        vers3 = Version(
            asset1,
            asset1.code,
            aTypes[0],
            user,
            is_published=True
        )
        vers3.save()

        vers4 = Version(
            asset1,
            asset1.code,
            aTypes[0],
            user,
            is_published=True
        )
        vers4.save()

        dialog = version_creator.MainDialog()
        self.show_dialog(dialog)
        
        # set to assets
        dialog.tabWidget.setCurrentIndex(0)
        
        # select Asset
        
        dialog.assets_tableWidget.selectRow(0)
        
        # test there is 4 versions in the list
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            4
        )
        
        # now check the shot_published_only_checkBox
        dialog.show_published_only_checkBox.setChecked(True)
        
        # check if only 2 items are shown
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            2
        )
        
        # and the versions are vers3 and vers4
        all_vers = dialog.previous_versions_tableWidget.versions
        self.assertTrue(vers1 not in all_vers)
        self.assertTrue(vers2 not in all_vers)
        self.assertTrue(vers3 in all_vers)
        self.assertTrue(vers4 in all_vers)
    
    def test_previous_versions_tableWidget_shows_only_defined_amount_of_item_with_version_count_spinBox(self):
        """testing if the previous_versions_tableWidget is only showing the
        number of items defined in the version_count_spinBox
        """
        
        project = Project("Test Project")
        project.save()

        asset1 = Asset(project, "Test Asset 1")
        asset1.save()

        asset2 = Asset(project, "Test Asset 2")
        asset2.save()

        aTypes = VersionType.query().filter_by(type_for="Asset").all()

        user = User("Test User")
        
        versions = []
        
        for i in range(20):
            vers = Version(
                asset1,
                asset1.code,
                aTypes[0],
                user,
                is_published=False
            )
            vers.save()
            versions.append(vers)

        versions[0].is_published = True
        versions[0].save()

        versions[1].is_published = True
        versions[1].save()
        
        versions[-1].is_published = True
        versions[-1].save()
        
        dialog = version_creator.MainDialog()
#        dialog.show()
#        self.app.exec_()
#        self.app.connect(
#            self.app,
#            QtCore.SIGNAL("lastWindowClosed()"),
#            self.app,
#            QtCore.SLOT("quit()")
#        )

        # set to assets
        dialog.tabWidget.setCurrentIndex(0)

        # select Asset
        dialog.assets_tableWidget.selectRow(0)
        
        # set the version_count_spinBox to 10
        dialog.version_count_spinBox.setValue(10)
        
        # now check if all the versions are visible
        
        # test there is 8 versions in the list
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            10
        )
        
        # set the version_count_spinBox to 3
        dialog.version_count_spinBox.setValue(3)
        
        # check if only the last 5 are visible
        self.assertEqual(
            dialog.previous_versions_tableWidget.rowCount(),
            3
        )

        self.assertTrue(
            versions[-1] in dialog.previous_versions_tableWidget.versions
        )

        self.assertTrue(
            versions[-2] in dialog.previous_versions_tableWidget.versions
        )
        
        self.assertTrue(
            versions[-3] in dialog.previous_versions_tableWidget.versions
        )
    
    def test_shots_listWidgets_gets_empty_for_a_new_project_without_sequence(self):
        """testing if shots_listWidget becomes empty when switched from a
        project with sequences to a project without sequences
        """
        
        proj1 = Project("Test Project 1")
        proj1.save()
        
        proj2 = Project("Test Project 2")
        proj2.save()
        
        seq1 = Sequence(proj1, "Test Seq 1")
        seq1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        shot2 = Shot(seq1, 2)
        shot2.save()
        
        shot3 = Shot(seq1, 3)
        shot3.save()
        
        shot4 = Shot(seq1, 4)
        shot4.save()
        
        dialog = version_creator.MainDialog()
        #dialog.show()
        #self.app.exec_()
        #self.app.connect(
        #    self.app,
        #    QtCore.SIGNAL("lastWindowClosed()"),
        #    self.app,
        #    QtCore.SLOT("quit()")
        #)
        
        # set the tab to shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # select seq1
        index = dialog.sequences_comboBox.findText(seq1.name)
        dialog.sequences_comboBox.setCurrentIndex(index)
        
        # check if the shots_listWidget has only 4 elements
        self.assertTrue(dialog.shots_listWidget.count()==4)
        
        # now switch to proj2
        index = dialog.projects_comboBox.findText(proj2.name)
        dialog.projects_comboBox.setCurrentIndex(index)
        
        # check if the shots_listWidget has no elemens
        self.assertTrue(dialog.shots_listWidget.count()==0)
    
    def test_restore_ui_will_work_correctly_for_versions_belonging_to_non_active_projects(self):
        """testing if the restore_ui will work properly for Version instances
        retrieved from the environment where the Project of the Version is not
        active thus not listed in the projects_comboBox
        """
        
        proj1 = Project("Test Project 1")
        proj1.active = False
        proj1.save()
        
        proj2 = Project("Test Project 2")
        proj2.save()
        
        asset_vtypes = VersionType.query()\
            .filter(VersionType.type_for=="Asset").all()
        
        asset1 = Asset(proj1, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(proj2, "Test Asset 2")
        asset2.save()
        
        user = User("Test User")
        user.save()
        
        vers1 = Version(asset1, asset1.code, asset_vtypes[0], user)
        vers1.save()
        
        # now initialize the ui and call restore with vers1
        dialog = version_creator.MainDialog()
        dialog.restore_ui(vers1)
        
        # there should be no errors raised
        # and the project_comboBox should be set to proj2
        self.assertEqual(dialog.projects_comboBox.currentText(), proj2.name)
    
    def test_frame_info_spinBoxes_are_correctly_filled(self):
        """testing if the frame info spinBoxes are correctly filled
        """
        
        proj = Project("Test Project")
        proj.save()
        
        seq = Sequence(proj, "Test Sequence")
        seq.save()
        
        shot1 = Shot(seq, 1)
        start_frame = 23
        end_frame = 100
        handle_at_start = 10
        handle_at_end = 7
        
        shot1.start_frame = start_frame
        shot1.end_frame = end_frame
        shot1.handle_at_start = handle_at_start
        shot1.handle_at_end = handle_at_end
        shot1.save()
        
        dialog = version_creator.MainDialog()
        
        # set the tab to shots
        dialog.tabWidget.setCurrentIndex(1)
        
        # the first shot should have been selected
        # check the frame info
        self.assertEqual(dialog.start_frame_spinBox.value(), start_frame)
        self.assertEqual(dialog.end_frame_spinBox.value(), end_frame)
        self.assertEqual(dialog.handle_at_start_spinBox.value(),
            handle_at_start)
        self.assertEqual(dialog.handle_at_end_spinBox.value(), handle_at_end)
    
    def test_frame_info_updated_to_the_shot_when_hit_to_update(self):
        """testing if the frame info of the shot is updated with the update
        button
        """
        
        proj = Project("Test Project")
        proj.save()
        
        seq = Sequence(proj, "Test Sequence")
        seq.save()
        
        seq2 = Sequence(proj, "Test Sequence 2")
        seq2.save()
        
        shot1 = Shot(seq, 1)
       
        shot1.start_frame = 1
        shot1.end_frame = 100
        shot1.handle_at_start = 10
        shot1.handle_at_end = 10
        shot1.save()
        
        dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
        
        # set the tab to shots
        dialog.tabWidget.setCurrentIndex(1)
        
        
        # update the fields
        start_frame = 23
        end_frame = 100
        handle_at_start = 10
        handle_at_end = 7
        
        dialog.start_frame_spinBox.setValue(start_frame)
        dialog.end_frame_spinBox.setValue(end_frame)
        dialog.handle_at_start_spinBox.setValue(handle_at_start)
        dialog.handle_at_end_spinBox.setValue(handle_at_end)
        
        # hit update
        QTest.mouseClick(
            dialog.shot_info_update_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # now check if the info is updated to the shot
        self.assertEqual(shot1.start_frame, start_frame)
        self.assertEqual(shot1.end_frame, end_frame)
        self.assertEqual(shot1.handle_at_start, handle_at_start)
        self.assertEqual(shot1.handle_at_end, handle_at_end)
    
    def test_update_thumbnail_clears_the_graphic_view_for_no_thumbnail(self):
        """testing if the update_gview_with_image_file method clears the graphic view for
        no thumbnail
        """
        self.fail("test is not implemented yet")
    
    def test_upload_thumbnail_overwrites_to_old_thumbnail_without_any_problem(self):
        """testing if upload_thumbnail method can overwrite to previous
        thumbnails
        """
        self.fail("test is not implemented yet")
    
    def test_update_thumbnail_works_correctly_switching_from_asset_to_shots(self):
        """testing if update_gview_with_image_file works correctly when switching from
        asset to shots
        """
        self.fail("test is not implemented yet")
    
    def test_upload_thumbnail_can_upload_different_formats(self):
        """testing if the upload_thumbnail method can upload different formats
        """
        self.fail("test is not implemented yet")
   
    def test_statuses_comboBox_is_filled_with_status_list(self):
        """testing if the status_comboBox is filled with default statuses
        """
        dialog = version_creator.MainDialog()
        item_count = dialog.statuses_comboBox.count()
        self.assertEqual(item_count, len(conf.status_list))
        
        item_texts = []
        for i in range(item_count):
            self.assertEqual(
                conf.status_list_long_names[i],
                dialog.statuses_comboBox.itemText(i)
            )
    
    def test_status_of_version_will_be_picked_from_statuses_comboBox(self):
        """testing if the status of the created version will be picked from the
        statuses_comboBox
        """
        
        new_project = Project('Test Project')
        new_project.save()
        
        new_asset = Asset(new_project, 'Test Asset')
        new_asset.save()
        
        admin = User.query().first()
        
        asset_vtypes = VersionType.query()\
            .filter(VersionType.type_for=='Asset')\
            .all()
        
        # create a new version
        new_version = Version(
            version_of=new_asset,
            base_name=new_asset.code,
            type=asset_vtypes[0],
            created_by=admin,
            status=conf.status_list[3]
        )
        new_version.save()
        
        dialog = version_creator.MainDialog()
        
        ## first check if the status comes correctly from the version
        #current_long_status = dialog.statuses_comboBox.currentText()
        #index = conf.status_list_long_names.index(current_long_status)
        #short_status = conf.status_list[index]
        #
        #self.assertEqual(
        #    new_version.status,
        #    short_status
        #)
        
        # now create a new version with different status
        dialog.statuses_comboBox.setCurrentIndex(4)
        
        QTest.mouseClick(
            dialog.save_as_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # get the new version
        newest_version = Version.query()\
            .filter(Version.version_of==new_asset)\
            .filter(Version.base_name==new_asset.code)\
            .filter(Version.type==asset_vtypes[0])\
            .filter(Version.version_number==new_version.version_number+1)\
            .first()
        
        self.assertEqual(
            conf.status_list[4],
            newest_version.status
        )
        
        #dialog = version_creator.MainDialog()
        #self.show_dialog(dialog)
    
    def test_statuses_comboBox_is_restored_with_the_most_recent_versions_status(self):
        """testing if the statuses_comboBox is  restored with the most recent
        versions status
        """
        
        db.setup()
        
        user = User.query().first()
        
        proj1 = Project('Test_Project')
        proj1.save()
        
        avtypes = VersionType.query()\
            .filter(VersionType.type_for=='Asset')\
            .all()
        
        asset1 = Asset(proj1, 'Test Asset 1', type='Character')
        asset1.save()
        
        asset2 = Asset(proj1, 'Test Asset 2', type='Environment')
        asset2.save()
        
        # create a couple of versions
        
        # for asset1
        vers_kwargs = {
            'version_of': asset1,
            'base_name': asset1.code,
            'type': avtypes[0],
            'created_by': user,
            'status': 'WIP'
        }
        
        vers1 = Version(**vers_kwargs)
        vers1.save()
        
        vers_kwargs['status'] = 'REV'
        vers2 = Version(**vers_kwargs)
        vers2.save()
        
        # for asset2
        vers_kwargs = {
            'version_of': asset2,
            'base_name': asset2.code,
            'type': avtypes[1],
            'created_by': user,
            'status': 'CMP'
        }
        
        vers3 = Version(**vers_kwargs)
        vers3.save()
        
        vers_kwargs['status'] = 'APP'
        vers4 = Version(**vers_kwargs)
        vers4.save()
        
        # now bring up the UI
        dialog = version_creator.MainDialog()
        
        # select the asset1
        dialog.tabWidget.setCurrentIndex(0)
        item = dialog.assets_tableWidget.findItems(
            asset1.name,
            QtCore.Qt.MatchExactly
        )[0]
        dialog.assets_tableWidget.setCurrentItem(item)
        
        # and test if the statuses_comboBox is set to the last status of the
        # version
        
        index = conf.status_list.index(vers2.status)
        long_name = conf.status_list_long_names[index]
        
        self.assertEqual(
            long_name,
            dialog.statuses_comboBox.currentText()
        )
        
        # now set it to asset 2
        item = dialog.assets_tableWidget.findItems(
            asset2.name,
            QtCore.Qt.MatchExactly
        )[0]
        dialog.assets_tableWidget.setCurrentItem(item)
        
        # and test if the statuses_comboBox is set to the last status of the
        # version
        index = conf.status_list.index(vers4.status)
        long_name = conf.status_list_long_names[index]
        
        self.assertEqual(
            long_name,
            dialog.statuses_comboBox.currentText()
        )
        
        #self.show_dialog(dialog)

class VersionCreator_Environment_Relation_Tester(unittest.TestCase):
    """tests the interaction of the UI with the given environment
    """
    
    def setUp(self):
        """setup the test
        """
        # -----------------------------------------------------------------
        # start of the setUp
        conf.database_url = "sqlite://"
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        db.setup()
        
        self.app = QtGui.QApplication(sys.argv)
        
        # create the necessary data
        
        # project
        self.test_project1 = Project("TEST_PROJECT1")
        self.test_project1.create()
        
        self.test_project2 = Project("TEST_PROJECT2")
        self.test_project2.create()
        
        # sequence
        self.test_sequence1 = Sequence(self.test_project1, "TEST_SEQUENCE_1")
        self.test_sequence2 = Sequence(self.test_project1, "TEST_SEQUENCE_2")
        self.test_sequence3 = Sequence(self.test_project1, "TEST_SEQUENCE_3")
        
        self.test_sequence4 = Sequence(self.test_project2, "TEST_SEQUENCE_4")
        self.test_sequence5 = Sequence(self.test_project2, "TEST_SEQUENCE_5")
        self.test_sequence6 = Sequence(self.test_project2, "TEST_SEQUENCE_6")
        
        # shots for sequence1
        self.test_shot1 = Shot(self.test_sequence1, 1)
        self.test_shot2 = Shot(self.test_sequence1, 2)
        self.test_shot3 = Shot(self.test_sequence1, 3)
        
        # shots for sequence2
        self.test_shot4 = Shot(self.test_sequence2, 4)
        self.test_shot5 = Shot(self.test_sequence2, 5)
        self.test_shot6 = Shot(self.test_sequence2, 6)

        # shots for sequence3
        self.test_shot7 = Shot(self.test_sequence3, 7)
        self.test_shot8 = Shot(self.test_sequence3, 8)
        self.test_shot9 = Shot(self.test_sequence3, 9)
        
        # shots for sequence4
        self.test_shot10 = Shot(self.test_sequence4, 10)
        self.test_shot11 = Shot(self.test_sequence4, 11)
        self.test_shot12 = Shot(self.test_sequence4, 12)

        # shots for sequence5
        self.test_shot13 = Shot(self.test_sequence5, 13)
        self.test_shot14 = Shot(self.test_sequence5, 14)
        self.test_shot15 = Shot(self.test_sequence5, 15)

        # shots for sequence6
        self.test_shot16 = Shot(self.test_sequence6, 16)
        self.test_shot17 = Shot(self.test_sequence6, 17)
        self.test_shot18 = Shot(self.test_sequence6, 18)
        
        # assets for project1
        self.test_asset1 = Asset(self.test_project1, "Test Asset 1")
        self.test_asset2 = Asset(self.test_project1, "Test Asset 2")
        self.test_asset3 = Asset(self.test_project1, "Test Asset 3")
        
        # assets for project2
        self.test_asset4 = Asset(self.test_project2, "Test Asset 4")
        self.test_asset5 = Asset(self.test_project2, "Test Asset 5")
        self.test_asset6 = Asset(self.test_project2, "Test Asset 6")
        
        self.test_user = User.query().first()
        
        self.test_asset_versionTypes_for_project1 = \
            VersionType.query().\
            filter(VersionType.type_for=="Asset").\
            all()
        
        # add the asset version to TestEnv
        for vtype in self.test_asset_versionTypes_for_project1:
            vtype.environments = ["TestEnv"]
        
        db.session.commit()
        
        # version for asset1
        self.test_version1 = Version(
            self.test_asset1,
            self.test_asset1.code,
            self.test_asset_versionTypes_for_project1[0],
            self.test_user
        )
        self.test_version1.is_published = True
        self.test_version1.save()
        
        db.session.add_all([
            self.test_shot1,
            self.test_shot2,
            self.test_shot3,
            self.test_shot4,
            self.test_shot5,
            self.test_shot6,
            self.test_shot7,
            self.test_shot8,
            self.test_shot9,
            self.test_asset1,
            self.test_asset2,
            self.test_asset3,
            self.test_shot10,
            self.test_shot11,
            self.test_shot12,
            self.test_shot13,
            self.test_shot14,
            self.test_shot15,
            self.test_shot16,
            self.test_shot17,
            self.test_shot18,
            self.test_asset4,
            self.test_asset5,
            self.test_asset6
        ])
        
        db.session.commit()
        
        self.test_environment = TestEnvironment()
        
        # the dialog
        self.test_dialog = \
            version_creator.MainDialog(self.test_environment)
        
        #        self.test_dialog.show()
        #        self.app.exec_()
        #        self.app.connect(
        #            self.app,
        #            QtCore.SIGNAL("lastWindowClosed()"),
        #            self.app,
        #            QtCore.SLOT("quit()")
        #        )
    
    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def show_dialog(self, dialog):
        """show the given dialog
        """
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
    
    def test_get_version_type_returns_VersionType_instance_from_the_UI(self):
        """testing if the get_version_type method returns the correct
        VersionType instance from the UI
        """
        
        # set the project to project1
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # and to asset1
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # the versionType to the first one
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # now try to get the version type
        version_type_from_UI = self.test_dialog.get_version_type()
        
        self.assertEqual(
            version_type_from_UI.name,
            self.test_asset_versionTypes_for_project1[0].name
        )
        
        self.assertEqual(
            version_type_from_UI.type_for,
            self.test_asset_versionTypes_for_project1[0].type_for
        )
    
    def test_get_version_type_returns_None_for_no_version_type_name(self):
        """testing if the get_version_type method returns None when there is
        no entry in the version_types_listWidget
        """
        # set the project to project1
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # and to asset2
        self.test_dialog.assets_tableWidget.selectRow(1)
        
        # be sure that there is no version type name in comboBox
        self.assertEqual(self.test_dialog.version_types_listWidget.count(), 0)
        
        # now try to get the version type
        version_type_from_UI = self.test_dialog.get_version_type()
        
        # check if it is None
        self.assertEqual(
            version_type_from_UI,
            None
        )
    
    def test_get_new_version_returns_correct_Version_instance(self):
        """testing if the get_new_version method returns the correct version
        from the interface
        """
        
        # set the project to project1
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # and to asset1
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # the versionType to the first one
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # take to the first one
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # expect the version to be
        expected_version = Version(
            self.test_asset1, self.test_asset1.code,
            self.test_asset_versionTypes_for_project1[0], self.test_user)
        
        self.assertEqual(
            expected_version,
            self.test_dialog.get_new_version()
        )
    
    def test_get_user_returns_a_proper_User_instance(self):
        """testing if the get_user method returns a proper user from the UI
        """
        self.assertEqual(
            self.test_dialog.get_user(),
            self.test_user
        )
    
    def test_get_old_version_returns_correct_Version_instance(self):
        """testing if the get_previous_version method returns the correct version
        from the previous_versions_tableWidget
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the assets tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # get the first version from the previous_versions_tableWidget
        version = self.test_dialog.previous_versions_tableWidget.versions[0]
        
        # get it by using the UI
        version_from_UI = self.test_dialog.get_previous_version()
        
        # check if they are equal
        self.assertTrue(version, version_from_UI)
    
    def test_export_as_pushButton_calls_environments_export_as_method(self):
        """testing if the export_as_pushButton calls the environments export_as
        method with the correct version given  to it
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the Asset tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first Asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # set the note to a known one
        test_note = "test note"
        self.test_dialog.note_textEdit.setText(test_note)
        
        # check if the run_count of export_as is 0
        self.assertEqual(
            self.test_environment.test_data["export_as"]["call count"], 0)
        self.assertTrue(
            self.test_environment.test_data["export_as"]["data"] is None)
        
        # hit to the export_as_pushButton
        QTest.mouseClick(
            self.test_dialog.export_as_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the run_count of export_as is raised to 1
        self.assertEqual(
            self.test_environment.test_data["export_as"]["call count"], 1)
        
        version_instance = self.test_environment.test_data["export_as"]["data"]
        
        self.assertTrue(isinstance(version_instance, Version))
        self.assertEqual(version_instance.version_of, self.test_asset1)
        self.assertEqual(
            version_instance.type.name,
            self.test_dialog.version_types_listWidget.currentItem().text()
        )
        self.assertEqual(
            version_instance.take_name,
            self.test_dialog.takes_listWidget.currentItem().text()
        )
        self.assertEqual(version_instance.note, test_note)
    
    def test_save_as_pushButton_calls_environments_save_as_method(self):
        """testing if the save_as_pushButton calls the environments save_as
        method with the correct version given  to it
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the Asset tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first Asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # set the note to a known one
        test_note = "test note"
        self.test_dialog.note_textEdit.setText(test_note)
        
        # check if the run_count of save_as is 0
        self.assertEqual(
            self.test_environment.test_data["save_as"]["call count"], 0)
        self.assertTrue(
            self.test_environment.test_data["save_as"]["data"] is None)
        
        # hit to the export_as_pushButton
        QTest.mouseClick(
            self.test_dialog.save_as_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the run_count of save_as is raised to 1
        self.assertEqual(
            self.test_environment.test_data["save_as"]["call count"], 1)
        
        version_instance = self.test_environment.test_data["save_as"]["data"]
        
        self.assertTrue(isinstance(version_instance, Version))
        self.assertEqual(version_instance.version_of, self.test_asset1)
        self.assertEqual(
            version_instance.type.name,
            self.test_dialog.version_types_listWidget.currentItem().text()
        )
        self.assertEqual(
            version_instance.take_name,
            self.test_dialog.takes_listWidget.currentItem().text()
        )
        self.assertEqual(version_instance.note, test_note)
    
    def test_open_pushButton_calls_environments_open_method(self):
        """testing if the open_pushButton calls the environments open method
        with the correct version given to it
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the Asset tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first Asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # check if the run_count of open_ is 0
        self.assertEqual(
            self.test_environment.test_data["open_"]["call count"], 0)
        self.assertTrue(
            self.test_environment.test_data["open_"]["data"] is None)
        
        # hit to the open_pushButton
        QTest.mouseClick(
            self.test_dialog.open_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the run_count of open_ is raised to 1
        self.assertEqual(
            self.test_environment.test_data["open_"]["call count"], 1)
        
        version_instance = self.test_environment.test_data["open_"]["data"]
        
        self.assertTrue(isinstance(version_instance, Version))
        self.assertEqual(version_instance.version_of, self.test_asset1)
        self.assertEqual(
            version_instance.type.name,
            self.test_dialog.version_types_listWidget.currentItem().text()
        )
        self.assertEqual(
            version_instance.take_name,
            self.test_dialog.takes_listWidget.currentItem().text()
        )
    
    def test_open_pushButton_closes_the_interface_after_successful_open(self):
        """testing if the interface will be closed after open_pushButton is
        clicked and a successful open action has been made
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the Asset tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first Asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # check if the interface is still open
        # show the dialog on purpose
        self.test_dialog.show()
        self.assertTrue(self.test_dialog.isVisible())
        
        # hit to the open_pushButton
        QTest.mouseClick(
            self.test_dialog.open_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the interface has been closed
        self.assertFalse(self.test_dialog.isVisible())
    
    def test_reference_pushButton_calls_environments_reference_method(self):
        """testing if the reference_pushButton calls the environments reference
        method with the correct version given to it
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the Asset tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first Asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # check if the run_count of reference is 0
        self.assertEqual(
            self.test_environment.test_data["reference"]["call count"], 0)
        self.assertTrue(
            self.test_environment.test_data["reference"]["data"] is None)
        
        # hit to the reference_pushButton
        QTest.mouseClick(
            self.test_dialog.reference_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the run_count of reference is raised to 1
        self.assertEqual(
            self.test_environment.test_data["reference"]["call count"], 1)
        
        version_instance = self.test_environment.test_data["reference"]["data"]
        
        self.assertTrue(isinstance(version_instance, Version))
        self.assertEqual(version_instance.version_of, self.test_asset1)
        self.assertEqual(
            version_instance.type.name,
            self.test_dialog.version_types_listWidget.currentItem().text()
        )
        self.assertEqual(
            version_instance.take_name,
            self.test_dialog.takes_listWidget.currentItem().text()
        )
    
    def test_import_pushButton_calls_environments_import_method(self):
        """testing if the import_pushButton calls the environments import
        method with the correct version given to it
        """
        
        # set to the first project
        self.test_dialog.projects_comboBox.setCurrentIndex(0)
        
        # set to the Asset tab
        self.test_dialog.tabWidget.setCurrentIndex(0)
        
        # set to the first Asset
        self.test_dialog.assets_tableWidget.selectRow(0)
        
        # set to the first version type
        self.test_dialog.version_types_listWidget.setCurrentRow(0)
        
        # set to the first take name
        self.test_dialog.takes_listWidget.setCurrentRow(0)
        
        # check if the run_count of import_ is 0
        self.assertEqual(
            self.test_environment.test_data["import_"]["call count"], 0)
        self.assertTrue(
            self.test_environment.test_data["import_"]["data"] is None)
        
        # hit to the import_pushButton
        QTest.mouseClick(
            self.test_dialog.import_pushButton,
            QtCore.Qt.LeftButton
        )
        
        # check if the run_count of import is raised to 1
        self.assertEqual(
            self.test_environment.test_data["import_"]["call count"], 1)
        
        version_instance = self.test_environment.test_data["import_"]["data"]
        
        self.assertTrue(isinstance(version_instance, Version))
        self.assertEqual(version_instance.version_of, self.test_asset1)
        self.assertEqual(
            version_instance.type.name,
            self.test_dialog.version_types_listWidget.currentItem().text()
        )
        self.assertEqual(
            version_instance.take_name,
            self.test_dialog.takes_listWidget.currentItem().text()
        )

    def test_no_environment_given_export_selection_as_pushButton_is_hidden(self):
        """testing if no environment instance is given the
        export_selection_as_pushButton is hidden
        """
        new_vc_dialog = version_creator.MainDialog()
        new_vc_dialog.show()
        self.assertFalse(new_vc_dialog.export_as_pushButton.isVisible())
    
    def test_no_environment_given_save_as_pushButton_is_still_visible(self):
        """testing if no environment instance is given the save_as_pushButton
        is still visible
        """
        new_vc_dialog = version_creator.MainDialog()
        new_vc_dialog.show()
        self.assertTrue(new_vc_dialog.save_as_pushButton.isVisible())
    
    def test_no_environment_given_open_pushButton_is_hidden(self):
        """testing if no environment instance is given the open_pushButton is
        hidden
        """
        new_vc_dialog = version_creator.MainDialog()
        new_vc_dialog.show()
        #self.show_dialog(new_vc_dialog)
        self.assertFalse(new_vc_dialog.open_pushButton.isVisible())
    
    def test_no_environment_given_reference_pushButton_is_hidden(self):
        """testing if no environment instance is given the reference_pushButton
        is hidden
        """
        new_vc_dialog = version_creator.MainDialog()
        new_vc_dialog.show()
        self.assertFalse(new_vc_dialog.reference_pushButton.isVisible())
    
    def test_no_environment_given_import_pushButton_is_hidden(self):
        """testing if no environment instance is given the import_pushButton is
        hidden
        """
        new_vc_dialog = version_creator.MainDialog()
        new_vc_dialog.show()
        self.assertFalse(new_vc_dialog.import_pushButton.isVisible())
    
    def test_mode_is_one_will_hide_some_elements(self):
        """testing if the mode is set to 1 will hide the read_write elements
        """
        vc_dialog = version_creator.MainDialog(mode=1)
        vc_dialog.show()
        self.assertFalse(vc_dialog.create_asset_pushButton.isVisible())
        self.assertFalse(vc_dialog.add_type_toolButton.isVisible())
        self.assertFalse(vc_dialog.add_take_toolButton.isVisible())
        self.assertFalse(vc_dialog.note_label.isVisible())
        self.assertFalse(vc_dialog.note_textEdit.isVisible())
        self.assertFalse(vc_dialog.statuses_comboBox.isVisible())
        self.assertFalse(vc_dialog.publish_checkBox.isVisible())
        self.assertFalse(vc_dialog.update_paths_checkBox.isVisible())
        self.assertFalse(vc_dialog.export_as_pushButton.isVisible())
        self.assertFalse(vc_dialog.save_as_pushButton.isVisible())
        self.assertFalse(vc_dialog.open_pushButton.isVisible())
        self.assertFalse(vc_dialog.reference_pushButton.isVisible())
        self.assertFalse(vc_dialog.import_pushButton.isVisible())
        self.assertFalse(vc_dialog.upload_thumbnail_pushButton.isVisible())
        self.assertFalse(vc_dialog.users_comboBox.isVisible())
        self.assertFalse(vc_dialog.user_label.isVisible())
        self.assertTrue(vc_dialog.chose_pushButton.isVisible())
        
        # set the shots tab
        vc_dialog.tabWidget.setCurrentIndex(1)
        
        self.assertFalse(vc_dialog.shot_info_update_pushButton.isVisible())
    
    
