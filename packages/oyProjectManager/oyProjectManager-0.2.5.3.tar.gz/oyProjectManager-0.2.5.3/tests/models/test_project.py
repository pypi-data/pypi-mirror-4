# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile
import unittest

from oyProjectManager import (db, conf, Asset, Client, Project, Sequence,
                              VersionType, Shot)

class Project_DB_Tester(unittest.TestCase):
    """Tests the design of the Projects after v0.2.0
    """
    
    def setUp(self):
        """set up the test
        """
        conf.database_url = "sqlite://"
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
    
    def tearDown(self):
        """clean up the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folders
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)

    def test_project_initialization_with_database(self):
        """testing the project initialization occurs without any problem
        """

        test_value = "TEST_PROJECT"
        new_proj = Project(test_value)
        self.assertEqual(new_proj.name, test_value)

    def test_project_creation_for_new_project(self):
        """testing if the project creation occurs without any problem
        """
        
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        
        # now check if the folder is created
        self.assertTrue(os.path.exists(new_proj.full_path))

    def test_project_stored_and_retrieved_correctly(self):
        """testing if the project is stored and retrieved correctly
        """

        new_proj = Project(name="TEST_PROJECT")
        new_proj.create()

        name = new_proj.name
        path = new_proj.path
        full_path = new_proj.full_path

        del new_proj

        new_proj_DB = Project.query().first()

        self.assertEqual(new_proj_DB.name, name)
        self.assertEqual(new_proj_DB.path, path)
        self.assertEqual(new_proj_DB.full_path, full_path)

    def test_project_restores_from_database_1(self):
        """testing if a project restores it self from the database with all its
        connections
        """

        # we need to create a new project and a sequence
        new_proj = Project("TEST_PROJECT")
        new_proj.create()

        test_description = "test description"
        new_proj.description = test_description
        new_proj.save()

        del new_proj

        # now retrieve the project by recreating it
        new_proj2 = Project("TEST_PROJECT")

        self.assertEqual(new_proj2.description, test_description)

    def test_project_restores_from_database_2(self):
        """testing if a project restores it self from the database with all its
        connections
        """

        # we need to create a new project and a sequence
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ")
        new_seq.save()
        new_seq.create()
        
        db.session.add(new_proj)
        db.session.commit()

        del new_proj
        del new_seq

        # now retrieve the project by recreating it
        new_proj2 = Project(name="TEST_PROJECT")

        self.assertEqual(new_proj2.sequences[0].name, "TEST_SEQ")

    def test_calling_create_over_and_over_again_will_not_cause_any_problem(self):
        """testing if calling the create over and over again will not create a
        problem
        """

        # we need to create a new project and a sequence
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        new_proj.create()
        new_proj.create()
        new_proj.create()
        new_proj.create()
        new_proj.create()

    def test_creating_two_different_projects_and_calling_create_in_mixed_order(self):
        """testing no error will be raised when creating two Project instances
        and calling their create method in mixed order
        """

        new_proj1 = Project("TEST_PROJECT1")
        new_proj2 = Project("TEST_PROJECT2")

        new_proj1.create()
        new_proj2.create()

    #    def test_creating_two_different_projects_with_same_name_and_calling_create_in_mixed_order(self):
    #        """testing no error will be raised when creating two Project instances
    #        and calling their create method in mixed order
    #        """
    #        
    #        new_proj1 = Project("TEST_PROJECT1")
    #        new_proj2 = Project("TEST_PROJECT1")
    #        
    #        new_proj1.create()
    #        self.assertRaises(IntegrityError, new_proj2.create)

    def test_calling_commit_multiple_times(self):
        """testing if there is no problem of calling Project.save() multiple
        times
        """

        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        new_proj.save()
        new_proj.save()

    def test_calling_create_on_a_project_which_is_retrieved_from_db(self):
        """testing if there will be no error messages generated when the new
        project is retrieved from the database and the create method of this
        project is called
        """

        project_name = "TEST_PROJECT1"
        new_proj1 = Project(project_name)
        new_proj1.create()

        new_proj2 = Project(project_name)
        new_proj2.create()
    
    def test_deleting_a_project_deletes_the_related_assets(self):
        """testing if deleting a project also deletes all Assets related to it
        """
        proj1 = Project("Test Project1")
        proj1.save()
        
        proj2 = Project("Test Project2")
        proj2.save()
        
        asset1 = Asset(proj1, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(proj1, "Test Asset 2")
        asset2.save()
        
        asset3 = Asset(proj2, "Test Asset 3")
        asset3.save()
        
        # confirm assets are in session
        self.assertIn(asset1, db.session)
        self.assertIn(asset2, db.session)
        
        db.session.delete(proj1)
        db.session.commit()
        
        # now check if asset1 and asset2 are also deleted
        assets = db.session.query(Asset).all()
        self.assertNotIn(asset1, assets)
        self.assertNotIn(asset2, assets)
        self.assertNotIn(asset1, db.session)
        self.assertNotIn(asset2, db.session)
        
        # check if proj2 and asset3 are  still there
        self.assertIn(proj2, db.session)
        self.assertIn(asset3, db.session)
    
    def test_deleting_a_project_deletes_the_related_sequences(self):
        """testing if deleting a project will also delete the related sequences
        """
        proj1 = Project("Test Project 1")
        proj1.save()
        
        proj2 = Project("Test Project 2")
        proj2.save()
        
        seq1 = Sequence(proj1, "Test Sequence 1")
        seq1.save()
        
        seq2 = Sequence(proj1, "Test Sequence 2")
        seq2.save()
        
        seq3 = Sequence(proj2, "Test Sequence 3")
        seq3.save()
        
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(seq2, db.session)
        
        db.session.delete(proj1)
        db.session.commit()
        
        self.assertNotIn(proj1, db.session)
        self.assertNotIn(seq1, db.session)
        self.assertNotIn(seq2, db.session)
        
        self.assertIn(proj2, db.session)
        self.assertIn(seq3, db.session)
    
    def test_deleting_a_project_will_delete_the_related_shots(self):
        """testing if deleting a project will also delete the related shots
        """
        proj1 = Project("Test Project 1")
        proj1.save()
        
        proj2 = Project("Test Project 2")
        proj2.save()
        
        seq1 = Sequence(proj1, "Sequence 1")
        seq1.save()
        
        seq2 = Sequence(proj2, "Sequence 2")
        seq2.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        shot2 = Shot(seq1, 2)
        shot2.save()
        
        shot3 = Shot(seq2, 1)
        shot3.save()
        
        shot4 = Shot(seq2, 2)
        shot4.save()
        
        # check all are in session
        self.assertIn(proj1, db.session)
        self.assertIn(proj2, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(seq2, db.session)
        self.assertIn(shot1, db.session)
        self.assertIn(shot2, db.session)
        self.assertIn(shot3, db.session)
        self.assertIn(shot4, db.session)
        
        # delete the project
        db.session.delete(proj1)
        db.session.commit()
        
        self.assertNotIn(proj1, db.session)
        self.assertNotIn(seq1, db.session)
        self.assertNotIn(shot1, db.session)
        self.assertNotIn(shot2, db.session)
        
        self.assertIn(proj2, db.session)
        self.assertIn(seq2, db.session)
        self.assertIn(shot3, db.session)
        self.assertIn(shot4, db.session)
        

class ProjectTester(unittest.TestCase):
    """tests the Project class
    """

    def setUp(self):
        """testing the settings path from the environment variable
        """
        
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self._name_test_values = [
            # (input, name, code)
            ("test project", "test project", "test_project"),
            ("123 test project", "123 test project", "123_test_project"),
            ("£#$£#$test£#$£#$project", "testproject", "testproject"),
            ("_123test project", "_123test project", "_123test_project"),
            ("CamelCase", "CamelCase", "CamelCase"),
            ("234CamelCase", "234CamelCase", "234CamelCase"),
            ("camelCase", "camelCase", "camelCase"),
            ("CamelCase", "CamelCase", "CamelCase"),
            ("minus-sign", "minus-sign", "minus-sign"),
            ("123432!+!'^+Test_PRoject323^+'^%&+%&324", "123432Test_PRoject323324",
             "123432Test_PRoject323324"),
            ("    ---test 9s_project", "test 9s_project", "test_9s_project"),
            ("    ---test 9s-project", "test 9s-project", "test_9s-project"),
            (" multiple     spaces are    converted to under     scores",
             "multiple     spaces are    converted to under     scores",
             "multiple_spaces_are_converted_to_under_scores"),
            ("_Project_Setup_", "_Project_Setup_", "_Project_Setup_"),
            ("_PROJECT_SETUP_", "_PROJECT_SETUP_", "_PROJECT_SETUP_"),
            ("FUL_3D", "FUL_3D", "FUL_3D"),
        ]

    def tearDown(self):
        """cleanup the test
        """
        
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)

    def test_name_argument_formatting(self):
        """testing if the name will be formatted correctly when creating a
        new project.
        """
        for test_value in self._name_test_values:
            project_name = test_value[0]
            expected_project_name = test_value[1]

            new_project = Project(project_name)

            self.assertEqual(new_project.name, expected_project_name)

    def test_name_attribute_formatting(self):
        """testing if the name property will be formatted correctly.
        """
        new_project = Project("TEST_NAME")

        for test_value in self._name_test_values:
            new_project.name = test_value[0]
            expected_project_name = test_value[1]

            self.assertEqual(new_project.name, expected_project_name)

    def test_name_argument_is_None(self):
        """testing if a TypeError will be raised when the name argument is
        None.
        """
        self.assertRaises(TypeError, Project, None)

    def test_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the name property is
        tried to be set to None
        """
        proj = Project("TEST_PROJECT")
        self.assertRaises(TypeError, setattr, proj, "name", None)

    def test_name_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the name arugment is
        an empty string
        """
        self.assertRaises(ValueError, Project, "")

    def test_name_attribute_is_set_to_empty_string(self):
        """testing if a ValueError will be raised when the name property is
        tried to be set to empty string
        """
        proj = Project("TEST_PROJECT")
        self.assertRaises(ValueError, setattr, proj, "name", "")

    def test_name_argument_is_empty_string_after_validation(self):
        """testing if a ValueError will be raised when the name argument is not
        None nor empty string but an empty string after validation
        """

        # this is obviously not a valid name for a project
        test_name = "+++++^^^"
        self.assertRaises(ValueError, Project, test_name)

    def test_name_attribute_is_empty_string_after_validation(self):
        """testing if a ValueError will be raised when the name property is
        an empty string after validation
        """

        # this is again not a valid name for a project
        test_names = [
            "^^+'^+'%^+%",
            "",
            ]

        proj = Project("TEST_PROJECT")

        for test_name in test_names:
            self.assertRaises(ValueError, setattr, proj, "name", test_name)

    def test_name_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the name argument is not
        a string instance
        """
        self.assertRaises(TypeError, Project, name=12314)

    def test_name_attribute_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the name attribute is not
        a string instance
        """
        new_proj = Project(name="TEST_PROJ1")
        self.assertRaises(TypeError, setattr, new_proj, "name", 12312)

    def test_full_path_attribute_is_calculated_from_the_project_code(self):
        """testing if the full_path attribute is calculated from the project
        code
        """
        new_proj = Project(name="Test Project 1", code="TEST_PROJECT_1")
        self.assertEqual(
            new_proj.full_path,
            os.path.join(
                os.environ["REPO"],
                new_proj.code
            )
        )

    def test_full_path_attribute_does_not_change_when_the_name_of_the_project_is_changed(self):
        """testing if the full_path attribute will be the same even the name of
        the proejct is changed
        """
        new_proj = Project(name="TEST_PROJ1")
        full_path = new_proj.full_path
        
        # change the name
        new_proj.name = "TEST_PROJ1_NEW_NAME"
        
        # now check if the full_path is still the same
        self.assertEqual(new_proj.full_path, full_path)

    def test_full_path_attribute_is_read_only(self):
        """testing if the full_path attribute is read-only
        """
        new_proj = Project("TEST_PROJ1")
        self.assertRaises(AttributeError, setattr, new_proj, "full_path",
                          "TEST")

    def test_path_attribute_is_equal_to_server_path(self):
        """testing if the path attribute is equal to the $REPO env variable
        """
        new_proj = Project(name="TEST_PROJ1")
        self.assertEqual(
            new_proj.path,
            os.environ[conf.repository_env_key]
        )

    def test_path_attribute_does_not_change_when_the_name_of_the_project_is_changed(self):
        """testing if the path attribute will be the same even the name of
        the proejct is changed
        """
        new_proj = Project(name="TEST_PROJ1")
        path = new_proj.path
        
        # change the name
        new_proj.name = "TEST_PROJ1_NEW_NAME"
        
        # now check if the path is still the same
        self.assertEqual(new_proj.path, path)

    def test_path_attribute_is_read_only(self):
        """testing if the path attribute is read-only
        """
        new_proj = Project("TEST_PROJ1")
        self.assertRaises(AttributeError, setattr, new_proj, "path", "TEST")

    def test___eq__operator(self):
        """testing the __eq__ (equal) operator
        """

        # create two projects
        proj1 = Project(name="TEST_PROJ1")
        proj2 = Project(name="TEST_PROJ1")

        self.assertEqual(proj1, proj2)

    def test_shot_number_prefix_attribute_initialization(self):
        """testing the shot_number_prefix attribute is initialized correctly
        for a newly created Project instance
        """
        new_proj = Project("TEST_PROJECT")
        new_proj.create()
        
        self.assertEqual(new_proj.shot_number_prefix, conf.shot_number_prefix)

    def test_shot_number_prefix_attribute_initialization_from_DB(self):
        """testing if the shot_number_prefix attribute is initialized correctly
        for a Project which is already in the database
        """
        new_proj = Project("TEST_PROJECT")
        new_proj.shot_number_prefix = "PL"
        new_proj.create()
        new_proj.save()

        # now get it back from db
        new_proj = Project("TEST_PROJECT")
        self.assertEqual(new_proj.shot_number_prefix, "PL")

    def test_version_types_attribute_initialization_for_a_new_Project_instance(self):
        """testing if the version_types attribute initializes from the config
        correctly for a new Project instance
        """

        new_proj = Project("TEST_PROJECT")
        new_proj.create()

        # now check if the project has all the version types defined in the
        # config file

        for version_type in conf.version_types:
            version_type_name = version_type["name"]
            vtype_from_proj =\
                VersionType.query().\
                filter_by(name=version_type_name).\
                first()
            
            self.assertTrue(vtype_from_proj is not None)

#    def test_version_types_attribute_initialization_for_a_Project_created_from_db(self):
#        """testing if the version_types attribute will be initialized correctly
#        for a previously created Project instance
#        """
#
#        new_proj = Project("TEST_PROJECT")
#        new_proj.create()
#
#        # remove all the version_types from the project
#        for vtype in new_proj.version_types:
#            db.session.delete(vtype)
#        
#        new_proj.save()
#
#        # now check if all the version types are removed from the db
#        self.assertEqual(VersionType.query().all(), [])
#
#        # now add a new asset type with known name
#        vtype = VersionType(
#            project=new_proj,
#            name="Test Version Type",
#            code="TVT",
#            path="this is the path",
#            filename="this is the filename",
#            output_path="this is the output path",
#            extra_folders="this is the extra folder",
#            environments=["RANDOM ENV NAME1"],
#            type_for="Asset",
#            )
#
#        new_proj.version_types.append(vtype)
#        new_proj.save()
#
#        # now delete the project and create it again
#        del new_proj
#
#        new_proj = Project("TEST_PROJECT")
#
#        # first check if there is only one version type
#        self.assertEqual(len(new_proj.version_types), 1)
#
#        # now check attributes
#        vtype_db = new_proj.version_types[0]
#        self.assertEqual(vtype.name, vtype_db.name)
#        self.assertEqual(vtype.code, vtype_db.code)
#        self.assertEqual(vtype.filename, vtype_db.filename)
#        self.assertEqual(vtype.path, vtype_db.path)
#        self.assertEqual(vtype.output_path,vtype_db.output_path)
#        self.assertEqual(vtype.extra_folders, vtype_db.extra_folders)
#        self.assertEqual(vtype.environments, vtype_db.environments)

    def test_code_argument_is_skipped(self):
        """testing if the code attribute will be generated from the name
        attribute if the code argument is skipped
        """
        new_proj = Project(name="TEST_PROJ")
        self.assertEqual(new_proj.name, new_proj.code)

    def test_code_argument_is_None(self):
        """testing if the code attribute will be generated from the name
        attribute if the code argument is None
        """
        new_proj = Project(name="TEST_PROJ", code=None)
        self.assertEqual(new_proj.name, new_proj.code)

#    def test_code_attribute_is_None(self):
#        """testing if the code attribute will be generated from the name if it
#        is set to None
#        """
#        new_proj = Project(name="TEST_PROJ", code="TP")
#        new_proj.code = None
#        self.assertEqual(new_proj.code, new_proj.name)

    def test_code_argument_is_empty_string(self):
        """testing if a ValueError will be raised if the code argument is an
        empty string
        """
        self.assertRaises(ValueError, Project, name="TEST_PROJ", code="")

#    def test_code_attribute_is_empty_string(self):
#        """testing if a ValueError will be raised when the code attribute is
#        set to an empty string
#        """
#        new_proj = Project(name="TEST_PROJ", code="TP")
#        self.assertRaises(ValueError, setattr, new_proj, "code", "")

    def test_code_argument_is_not_a_string_instance(self):
        """testing if a TypeError will be raised when the code argument is not
        a string or unicode instance
        """
        self.assertRaises(TypeError, Project, name="TEST_PROJECt", code=123124)

#    def test_code_attribute_is_not_a_string_instance(self):
#        """testing if a TypeError will be raised when the code attribute is set
#        to a value which is not a string or unicode
#        """
#        new_proj = Project(name="TEST_PROJECT")
#        self.assertRaises(TypeError, setattr, new_proj, "code", 12314)

    def test_code_argument_is_working_properly(self):
        """testing if the code attribute is initialized correctly
        """
        test_code = "TST"
        new_proj = Project(name="TEST_PROJECT", code=test_code)
        self.assertEqual(new_proj.code, test_code)

#    def test_code_attribute_is_working_properly(self):
#        """testing if the code attribute is working properly
#        """
#        test_code = "TST"
#        new_proj = Project(name="TEST_PROJ1")
#        new_proj.code = test_code
#        self.assertEqual(new_proj.code, test_code)

    def test_code_argument_is_formatted_correctly(self):
        """testing if the code attribute is formatted correctly on Project
        instance creation
        """
        for test_value in self._name_test_values:
            project_code = test_value[0]
            expected_project_code = test_value[2]
            
            new_project = Project(name="TEST_PROJ1", code=project_code)
            
            self.assertEqual(new_project.code, expected_project_code)

#    def test_code_attribute_is_formatted_correctly(self):
#        """testing if the code attribute is formatted correctly
#        """
#
#        new_proj = Project(name="TEST_PROJECT")
#
#        for test_value in self._name_test_values:
#            project_code = test_value[0]
#            expected_project_code = test_value[2]
#
#            new_proj.code = project_code
#
#            self.assertEqual(new_proj.code, expected_project_code)

    def test_code_argument_is_empty_string_after_formatting(self):
        """testing if a ValueError will be raised when the code argument
        becomes an empty string after formatting
        """
        test_value = "'^+'^+"
        self.assertRaises(ValueError, Project, name="TEST_PROJ1",
                          code=test_value)

#    def test_code_attribute_is_empty_string_after_formatting(self):
#        """testing if a ValueError will be raised when the code attribute is an
#        empty string after formatting
#        """
#        test_value = "12'^+'^+"
#        new_proj = Project(name="TEST_PROJ1", code="TP1")
#        self.assertRaises(ValueError, setattr, new_proj, "code", test_value)
    
    def test_code_attribute_is_read_only(self):
        """testing if the code attribute is read only
        """
        new_project = Project("Test Project")
        self.assertRaises(AttributeError, setattr, new_project, "code",
            "New Code")
   
    def test_client_argument_is_skipped(self):
        """testing if skipping the client argument will set the client
        attribute to None
        """
        new_proj = Project(name="Test Project")
        self.assertEqual(None, new_proj.client)
    
    def test_client_argument_is_None(self):
        """testing if the client argument can be None
        """
        new_proj = Project(name="Test Project", client=None)
        self.assertEqual(None, new_proj.client)
    
    def test_client_attribute_is_None(self):
        """testing if the client attribute is set to None will not cause any
        error
        """
        new_client = Client(name="Test Client")
        new_proj = Project(name="Test Project", client=new_client)
        new_proj.client = None
        self.assertEqual(None, new_proj.client)
    
    def test_client_argument_is_not_a_Client_instance(self):
        """testing if a TypeError will be raised when the client argument is
        not a Client instance
        """
        self.assertRaises(TypeError, Project, name="Test Project",
            client="a client")
    
    def test_client_attribute_is_not_a_Client_instance(self):
        """testing if a TypeError will be raised when the client attribute is
        not set to a Client instance
        """
        new_client = Client(name='Test Client')
        new_proj = Project(name='Test Project', client=new_client)
        self.assertRaises(TypeError, setattr, new_proj, 'client', 'a client')
    
    def test_client_argument_is_working_properly(self):
        """testing if the client argument properly sets the client attribute
        """
        new_client = Client(name='Test Client')
        new_proj = Project(name='Test Project', client=new_client)
        self.assertEqual(new_client, new_proj.client)
    
    def test_client_attribute_is_working_properly(self):
        """testing if the client attribute is working properly
        """
        new_client1 = Client(name='Test Client 1')
        new_client2 = Client(name='Test Client 2')
        new_proj = Project(name='Test Project', client=new_client1)
        self.assertNotEqual(new_client2, new_proj.client)
        new_proj.client = new_client2
        self.assertEqual(new_client2, new_proj.client)
    
    def test_asset_attribute_is_read_only(self):
        """testing if the asset attribute is read-only
        """
        new_proj = Project("Test Project for Asset Relation")
        self.assertRaises(AttributeError, setattr, new_proj, "assets", [])
    
    def test_asset_attribute_returns_a_list_of_assets_related_to_this_project(self):
        """testing if the asset attribute returns a list of assets which are
        related to this project
        """
        new_proj1 = Project("Test Project 1")
        new_proj1.create()
        
        new_proj2 = Project("Test Project 2")
        new_proj2.create()
        
        new_proj3 = Project("Test Project 3")
        new_proj3.create()
        
        asset1 = Asset(new_proj1, "Asset 1")
        asset1.save()
        
        asset2 = Asset(new_proj1, "Asset 2")
        asset2.save()
        
        asset3 = Asset(new_proj2, "Asset 3")
        asset3.save()
        
        asset4 = Asset(new_proj2, "Asset 4")
        asset4.save()
        
        self.assertItemsEqual(new_proj1.assets, [asset1, asset2])
        self.assertItemsEqual(new_proj2.assets, [asset3, asset4])
        self.assertItemsEqual(new_proj3.assets, [])
