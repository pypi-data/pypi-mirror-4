# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
import sys
import os
import shutil
import tempfile
import unittest

#from PySide import QtGui, QtCore
#from PySide.QtCore import Qt
#from PySide.QtTest import QTest
import sip
from oyProjectManager.models.auth import Client
from oyProjectManager.models.project import Project

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from oyProjectManager import conf, db
from oyProjectManager.ui import project_properties

logger = logging.getLogger("oyProjectManager.ui.project_properties")
logger.setLevel(logging.DEBUG)

class ProjectPropertiesTester(unittest.TestCase):
    """tests the project_properties UI
    """

    def setUp(self):
        """setup the test
        """
        # create an in memory database
        conf.database_url = "sqlite://"
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
    
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        #        os.environ["OYPROJECTMANAGER_PATH"] = ""
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        # re-parse the settings
        #        conf._parse_settings()

        # for PySide
#        if QtGui.qApp is None:
#            print "qApp is None"
#            self.app = QtGui.QApplication(sys.argv)
#        else:
#            print "qApp is OK"
#            self.app = QtGui.qApp
        
        # for PyQt4
        self.app = QtGui.QApplication(sys.argv)

    
    def tearDown(self):
        """clean up the test
        """
        # for PySide
#        self.app.quit()
#        del self.app
    
        # set the db.session to None
        db.session = None
    
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def show_dialog(self, dialog):
        """shows the given dialog
        """
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )
    
    def test_resolution_comboBox_is_filled_with_resolutions_from_the_config(self):
        """testing if the resolution_comboBox is filled with predefined values
        from the oyProjectManager.conf
        """
        
        dialog = project_properties.MainDialog()
        
        resolutions_from_conf = conf.resolution_presets.keys()
        resolutions_from_ui = []
        
        for i in range(dialog.resolution_comboBox.count()):
            resolutions_from_ui.append(dialog.resolution_comboBox.itemText(i))
        
        for preset in resolutions_from_conf:
            self.assertTrue(preset in resolutions_from_ui)
    
    def test_passing_a_Project_instance_will_fill_the_interface_with_the_project(self):
        """testing if passing a Project instance will fill the interface with
        the data coming from the given Project instance
        """
        
        new_client = Client(name='Client Agency 1', code='CA1')
        new_client.save()
        
        new_project = Project("Test Project")
        new_project.client = new_client
        new_project.width = 720
        new_project.height = 576
        new_project.pixel_aspect = 1.067
        new_project.fps = 30
        new_project.active = True

        dialog = project_properties.MainDialog(project=new_project)
       
        # now check if the interface is filled properly
        self.assertEqual(
            dialog.name_lineEdit.text(), new_project.name
        )
        
        self.assertEqual(
            dialog.code_lineEdit.text(), new_project.code
        )

        # preset name
        preset_name = dialog.resolution_comboBox.currentText()

        self.assertEqual(
            conf.resolution_presets[preset_name][0],
            new_project.width
        )

        self.assertEqual(
            conf.resolution_presets[preset_name][1],
            new_project.height
        )

        self.assertEqual(
            conf.resolution_presets[preset_name][2],
            new_project.pixel_aspect
        )

        self.assertEqual(
            dialog.fps_spinBox.value(), new_project.fps
        )

        self.assertEqual(
            dialog.active_checkBox.isChecked(), True
        )
        
        # Advanced settings
        self.assertEqual(
            dialog.shot_number_prefix_lineEdit.text(),
            new_project.shot_number_prefix
        )
        
        self.assertEqual(
            dialog.shot_number_padding_spinBox.value(),
            new_project.shot_number_padding
        )
        
#        self.assertEqual(
#            dialog.revision_number_prefix_lineEdit.text(),
#            new_project.rev_number_prefix
#        )
        
#        self.assertEqual(
#            dialog.revision_number_padding_spinBox.value(),
#            new_project.rev_number_padding
#        )
        
#        self.assertEqual(
#            dialog.version_number_prefix_lineEdit.text(),
#            new_project.ver_number_prefix
#        )
        
#        self.assertEqual(
#            dialog.version_number_padding_spinBox.value(),
#            new_project.ver_number_padding
#        )
        
        self.assertEqual(
            dialog.structure_textEdit.toPlainText(),
            new_project.structure
        )
    

    def test_UI_will_edit_the_given_Project_instance(self):
        """testing if a Project instance is passed the interface will allow the
        given Project instance to be edited
        """
        
        new_client = Client(name='Test Client 1')
        new_client.save()
        
        new_project = Project("Test Project")
        new_project.create()
        
        dialog = project_properties.MainDialog(project=new_project)
        
        # now edit the project from the UI
        new_name = "Test Project New Name"
        new_fps = 50
        dialog.name_lineEdit.setText(new_name)
        new_client_2_name = 'Test Client 2'
        dialog.clients_comboBox.lineEdit().setText(new_client_2_name)
        dialog.fps_spinBox.setValue(new_fps)
        dialog.resolution_comboBox.setCurrentIndex(3)
        preset_name = dialog.resolution_comboBox.currentText()
        resolution_data = conf.resolution_presets[preset_name]
        dialog.active_checkBox.setChecked(False)
        dialog.shot_number_prefix_lineEdit.setText("PL")
        dialog.shot_number_padding_spinBox.setValue(5)
        dialog.revision_number_prefix_lineEdit.setText("rev")
        dialog.revision_number_padding_spinBox.setValue(3)
        dialog.version_number_prefix_lineEdit.setText("ver")
        dialog.version_number_padding_spinBox.setValue(5)
        new_structure = "This is the new structure\nwith three lines\n" + \
                        "and this is the third line"
        dialog.structure_textEdit.setText(new_structure)
        
        # hit ok
        QTest.mouseClick(dialog.buttonBox.buttons()[0], Qt.LeftButton)

        # now check the data
        self.assertEqual(new_project.name, new_name)
        self.assertEqual(new_project.client.name, new_client_2_name)
        # check if a client is created with that name
        
        new_client_2 = Client.query().filter(Client.name==new_client_2_name).first()
        self.assertIsInstance(new_client_2, Client)
        
        self.assertEqual(new_project.fps, new_fps)
        self.assertEqual(new_project.width, resolution_data[0])
        self.assertEqual(new_project.height, resolution_data[1])
        self.assertEqual(new_project.pixel_aspect, resolution_data[2])
        self.assertEqual(new_project.active, False)
        self.assertEqual(new_project.shot_number_padding, 5)
        self.assertEqual(new_project.shot_number_prefix, "PL")
        self.assertEqual(new_project.rev_number_padding, 3)
        self.assertEqual(new_project.rev_number_prefix, "rev")
        self.assertEqual(new_project.ver_number_padding, 5)
        self.assertEqual(new_project.ver_number_prefix, "ver")
        self.assertEqual(new_project.structure, new_structure)
    
    def test_UI_will_not_allow_new_projects_with_no_code(self):
        """testing if the UI will warn the user if no code is supplied
        """
        dialog = project_properties.MainDialog()
        
        # now edit the project from the UI
        new_name = "Test Project New Name"
        new_code = "test"
        new_fps = 50
        dialog.name_lineEdit.setText(new_name)
        dialog.code_lineEdit.setText(new_code)
        new_client_name = 'Test Client 1'
        dialog.clients_comboBox.lineEdit().setText(new_client_name)
        dialog.fps_spinBox.setValue(new_fps)
        dialog.resolution_comboBox.setCurrentIndex(3)
        preset_name = dialog.resolution_comboBox.currentText()
        resolution_data = conf.resolution_presets[preset_name]
        dialog.active_checkBox.setChecked(False)
        
        #self.show_dialog(dialog)
        
        # hit ok
        # this will raise a dialog asking the user to set a proper code value
        QTest.mouseClick(dialog.buttonBox.buttons()[0], Qt.LeftButton)
        
        self.fail('test can not be implemented')
   
    def test_UI_will_create_a_new_Project_instance_if_it_is_not_passed_any(self):
        """testing if no Project instance is passed the interface will create
        a new Project instance with the values
        """

        dialog = project_properties.MainDialog()

        # now edit the project from the UI
        new_name = "Test Project New Name"
        new_fps = 50
        dialog.name_lineEdit.setText(new_name)
        new_client_name = 'Test Client 1'
        dialog.clients_comboBox.lineEdit().setText(new_client_name)
        dialog.fps_spinBox.setValue(new_fps)
        dialog.resolution_comboBox.setCurrentIndex(3)
        preset_name = dialog.resolution_comboBox.currentText()
        resolution_data = conf.resolution_presets[preset_name]
        dialog.active_checkBox.setChecked(False)

        # hit ok
        QTest.mouseClick(dialog.buttonBox.buttons()[0], Qt.LeftButton)
        
        # get the project
        new_project = dialog.project
        
        # now check the data
        self.assertEqual(new_project.name, new_name)
        self.assertEqual(new_project.client.name, new_client_name)
        self.assertEqual(new_project.fps, new_fps)
        self.assertEqual(new_project.width, resolution_data[0])
        self.assertEqual(new_project.height, resolution_data[1])
        self.assertEqual(new_project.pixel_aspect, resolution_data[2])
        self.assertEqual(new_project.active, False)
    
#    def test_given_project_has_custom_resolution(self):
#        """testing if the resolution will be set to Custom if the given project
#        has a non standard resolution
#        """
#        self.fail("test is not implemented yet")
    
    def test_default_resolution_preset_is_correctly_set(self):
        """testing if the default resolution preset from the config file is set
        at the resolution_comboBox
        """
        
        dialog = project_properties.MainDialog()
        self.assertEqual(
            dialog.resolution_comboBox.currentText(),
            conf.default_resolution_preset
        )
    
    def test_advanced_settings_are_set_to_default_values_if_no_project_has_given(self):
        """testing if the advanced settings are set to the default values if no
        Project instance has been given to the interface
        """
        
        dialog = project_properties.MainDialog()
        self.assertEqual(
            dialog.shot_number_padding_spinBox.value(),
            conf.shot_number_padding
        )
        self.assertEqual(
            dialog.shot_number_prefix_lineEdit.text(),
            conf.shot_number_prefix
        )
        self.assertEqual(
            dialog.revision_number_padding_spinBox.value(),
            conf.rev_number_padding
        )
        self.assertEqual(
            dialog.revision_number_prefix_lineEdit.text(),
            conf.rev_number_prefix
        )
        self.assertEqual(
            dialog.version_number_padding_spinBox.value(),
            conf.ver_number_padding
        )
        self.assertEqual(
            dialog.version_number_prefix_lineEdit.text(),
            conf.ver_number_prefix
        )
        self.assertEqual(
            dialog.structure_textEdit.toPlainText(),
            conf.project_structure
        )
    
#    def test_custom_resolution_will_be_set_if_resolution_can_not_be_found_(self):
#        """testing if the given project has a non standard resolution will
#        set the resolution to Custom
#        """
#        new_project = Project("Test Project")
#        new_project.width = 878
#        
#        dialog = project_properties.MainDialog(None, new_project)
#        self.assertEqual(dialog.resolution_comboBox.currentText(), "Custom")
    
#    def test_custom_resolution_will_make_the_custom_resolution_UI_to_be_active(self):
#        """testing if custom resoultion is selected in the UI will activate the
#        width, height, pixel aspect controls
#        """
#        self.fail("test is not implemented yet")
    
    def test_code_lineEdit_is_disabled_when_an_existing_Project_is_passed(self):
        """testing if the code_lineEdit is disabled when an existing Project
        instance is passed to the UI
        """
        new_project = Project("Test Project 1")
        new_project.create()
        
        dialog = project_properties.MainDialog(project=new_project)
        
        self.assertFalse(dialog.code_lineEdit.isEnabled())
    
    def test_code_lineEdit_is_enabled_when_no_Project_is_passed(self):
        """testing if the code_lineEdit is disabled when no Project instance
        is passed
        """
        dialog = project_properties.MainDialog()
        self.assertTrue(dialog.code_lineEdit.isEnabled())
    
    def test_fps_is_set_to_default_fps_from_conf_if_no_project_is_passed(self):
        """testing if the fps_spingBox is set to the conf.default_fps value if
        no project instance is passed
        """
        dialog = project_properties.MainDialog()
        self.assertEqual(dialog.fps_spinBox.value(), conf.default_fps)
    
    def test_active_checkBox_default_value_is_checked(self):
        """testing if the default value for the active_checkBox is checked
        """
        dialog = project_properties.MainDialog()
        self.assertTrue(dialog.active_checkBox.isChecked())
    
    def test_tabWidget_default_tab_is_Basic(self):
        """testing if the default tab is "Basic"
        """
        dialog = project_properties.MainDialog()
        self.assertTrue(dialog.tabWidget.currentIndex()==0)
