# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile
import unittest
from oyProjectManager import (conf, db, Project, Sequence, Shot, Version, User,
                              VersionType)

class ShotTester(unittest.TestCase):
    """tests the Shot class
    """
    
    def setUp(self):
        """setup the test settings with environment variables
        """
        # -----------------------------------------------------------------
        # start of the setUp
        conf.database_url = "sqlite://"
        
        # create the environment variable and point it to a temp directory
        self.temp_config_folder = tempfile.mkdtemp()
        self.temp_projects_folder = tempfile.mkdtemp()
        
        os.environ["OYPROJECTMANAGER_PATH"] = self.temp_config_folder
        os.environ[conf.repository_env_key] = self.temp_projects_folder
        
        self.test_proj = Project("TEST_PROJ1")
        self.test_proj.create()
        
        self.test_seq = Sequence(self.test_proj, "TEST_SEQ")
        self.test_seq.save()
        self.test_seq.create()
        
        self.kwargs = {
            "sequence": self.test_seq,
            "number": 1,
            "start_frame": 1,
            "end_frame": 100,
            "description": "Test shot"
        }
        
        self.test_shot = Shot(**self.kwargs)
        
        self._number_test_values = [
            (23, "23"),
            ("24", "24"),
            ("324ASF", "324ASF"),
            ("AD43", "AD43"),
            ("AS43A", "AS43A"),
            ("afasfas fasf    asdf67", "AFASFAS_FASF_ASDF67"),
            ("45a", "45A"),
            ("45acafs","45ACAFS"),
            ("45'^+'^+b", "45B"),
            ("45asf78wr", "45ASF78WR"),
            ("'^+'afsd2342'^+'asdFGH", "AFSD2342ASDFGH"),
            ("46B-3-B", "46B-3-B"),
            ("XB58P-4-C", "XB58P-4-C"),
            ("A143AN-04-D", "A143AN-04-D"),
            ("xb58q-2-d", "XB58Q-2-D"),
            ("underscores_are_allowed", "UNDERSCORES_ARE_ALLOWED"),
            ("304_sb_0403_0040", "304_SB_0403_0040"),
            #("0001", "1"),
        ]
    
    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.session = None
        
        # delete the temp folder
        shutil.rmtree(self.temp_config_folder)
        shutil.rmtree(self.temp_projects_folder)
    
    def test_number_argument_is_skipped(self):
        """testing if a TypeError will be raised when the number argument is
        skipped
        """
        self.kwargs.pop("number")
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_number_argument_is_None(self):
        """testing if a TypeError will be raised when the number argument is
        None
        """
        self.kwargs["number"] = None
        self.assertRaises(TypeError, Shot, **self.kwargs)

    def test_number_attribute_is_None(self):
        """testing if a TypeError will be raised when the number attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "number", None)
    
    def test_number_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the number argument is
        an empty string
        """
        self.kwargs["number"] = ""
        self.assertRaises(ValueError, Shot, **self.kwargs)
    
    def test_number_attribute_is_set_to_empty_string(self):
        """testing if a ValueError will be raised when the number attribute is
        set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_shot, "number", "")
    
    def test_number_argument_is_not_a_string_or_integer(self):
        """testing if a TypeError will be raised when the number argument is
        not a string or integer
        """
        self.kwargs["number"] = [123]
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_number_attribute_is_not_a_string_integer(self):
        """testing if a TypeError will be raised when the number attribute is
        not a string or integer
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "number", [])
    
    def test_number_argument_formatted_correctly(self):
        """testing if the number attribute is formatted correctly when the class
        is initialized
        """
        for test_value in self._number_test_values:
            self.kwargs["number"] = test_value[0]
            new_shot = Shot(**self.kwargs)
            self.assertEqual(test_value[1], new_shot.number)
            
    
#    def test_number_attribute_formatted_correctly(self):
#        """testing if the number attribute is formatted correctly
#        """
#        for test_value in self._number_test_values:
#            self.kwargs["number"] = test_value[0]
#            new_shot = Shot(**self.kwargs)
#            self.assertEqual(test_value[1], new_shot.number)
    
    def test_number_is_already_defined_in_the_sequence(self):
        """testing if a ValueError will be raised when the shot number is
        already defined in the given Sequence
        """
        self.kwargs["number"] = 101
        new_shot1 = Shot(**self.kwargs)
        self.assertRaises(
            ValueError,
            Shot,
            **self.kwargs
        )
    
    def test_number_is_already_defined_in_the_sequence_for_an_already_created_one(self):
        """testing if a ValueError will be raised when the number is already
        defined for a Shot in the same Sequence instance
        """
        self.kwargs["number"] = 101
        new_shot1 = Shot(**self.kwargs)
        new_shot1.save()
        
        self.assertRaises(ValueError, Shot, **self.kwargs)
    
    def test_number_argument_is_string_or_integer(self):
        """testing if both strings and integers are ok to pass to the number
        argument
        """
        self.kwargs["number"] = 10
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.number, "10")
        
        self.kwargs["number"] = "11A"
        new_shot2 = Shot(**self.kwargs)
        self.assertEqual(new_shot2.number, "11A")
    
    def test_code_attribute_is_calculated_from_the_number_argument(self):
        """testing if the code attribute is calculated from the number
        argument
        """
        
        self.kwargs["number"] = 10
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, "SH010")
        
        self.kwargs["number"] = "10A"
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, "SH010A")
        
        self.kwargs["number"] = "A143AN-04-D"
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, "SHA143AN-04-D")
        
        self.kwargs["number"] = "A143AN-04-DB"
        self.test_proj.shot_number_prefix = ""
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, "A143AN-04-DB")
        
        self.kwargs['number'] = '304_sb_0403_0040'
        self.test_proj.shot_number_prefix = ""
        new_shot1 = Shot(**self.kwargs)
        self.assertEqual(new_shot1.code, '304_SB_0403_0040')
    
    def test_code_attribute_is_calculated_from_the_number_attribute(self):
        """testing if the code attribute is calculated from the number
        attribute
        """
        
        self.test_shot.number = 10
        self.assertEqual(self.test_shot.code, "SH010")
        
        self.test_shot.number = "10A"
        self.assertEqual(self.test_shot.code, "SH010A")
    
    def test_code_attribute_is_read_only(self):
        """testing if the code attribute is read_only
        """
        self.assertRaises(AttributeError, setattr, self.test_shot, "code",
                          "SH010A")
    
#    def test_code_argument_is_not_in_good_format(self):
#        """testing if a ValueError will be raised when the code argument format
#        is not correct
#        """
#        self.kwargs["code"] = "wrong format"
#        self.assertRaises(ValueError, Shot, **self.kwargs)
#    
#    def test_code_attribute_is_not_in_good_format(self):
#        """testing if a ValueError will be raised when the code attribute
#        format is not correct
#        """
#        self.assertRaises(ValueError, setattr, self.test_shot, "code",
#                          "wrong format")
#    
#    def test_code_argument_is_formatted_correctly(self):
#        """testing if the code argument is formatted correctly
#        """
#        for test_value in self._code_test_values:
#            self.kwargs["code"] = test_value[0]
#            new_shot = Shot(**self.kwargs)
#            self.assertEqual(new_shot.code, test_value[1])
#    
#    def test_code_attribute_is_formatted_correctly(self):
#        """testing if the code attribute is formatted correctly
#        """
#        for test_value in self._code_test_values:
#            self.test_shot.code = test_value[0]
#            self.assertEqual(self.test_shot.code, test_value[1])
    
    def test_sequence_argument_is_skipped(self):
        """testing if a TypeError will be raised when the sequence argument
        is skipped
        """
        self.kwargs.pop("sequence")
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_None(self):
        """testing if a TypeError will be raised when the sequence argument
        is None
        """
        self.kwargs["sequence"] = None
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_not_a_Sequence_instance(self):
        """testing if a TypeError will be raised when the sequence argument is
        not a Sequence instance
        """
        self.kwargs["sequence"] = "not a sequence instance"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_sequence_argument_is_working_properly(self):
        """testing if the sequence argument is working correctly
        """
        self.assertTrue(self.test_shot.sequence is self.test_seq)
    
    def test_sequence_attribute_is_read_only(self):
        """testing if the sequence attribute is read-only
        """
        new_seq = Sequence(self.test_proj, "TEST_SEQ2")
        new_seq.save()
        self.assertRaises(AttributeError, setattr, self.test_shot, "sequence",
                          new_seq)
    
    def test_start_frame_argument_is_skipped(self):
        """testing if the start_frame attribute will be set to the default
        value when the start_frame argument is skipped
        """
        self.kwargs['number'] = '1a'
        self.kwargs.pop("start_frame")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
    
    def test_start_frame_argument_is_None(self):
        """testing if the start_frame attribute will be set to the default
        value when the start_frame argument is skipped
        """
        self.kwargs['number'] = '1a'
        self.kwargs["start_frame"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
    
    def test_start_frame_attribute_is_None(self):
        """testing if the start_frame attribute will be set to the default
        value when it is set to None
        """
        self.test_shot.start_frame = None
        self.assertEqual(self.test_shot.start_frame, 1)
    
    def test_start_frame_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the start_frame argument
        is not an integer
        """
        self.kwargs['number'] = '1a'
        self.kwargs["start_frame"] = "asdfa"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_start_frame_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the start_frame attribute
        is not set to an integer value
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "start_frame",
                          "asdfs")
    
    def test_start_frame_attribute_is_working_properly(self):
        """testing if the start_frame attribute is working properly
        """
        test_value = 10
        self.test_shot.start_frame = test_value
        self.assertEqual(self.test_shot.start_frame, test_value)
    
    def test_start_frame_attribute_updates_the_duration_attribute(self):
        """testing if the start_frame attribute updates the duration attribute
        value
        """
        self.test_shot.start_frame = 10
        self.assertEqual(self.test_shot.end_frame, 100)
        self.assertEqual(self.test_shot.duration, 91)
    
    def test_end_frame_argument_is_skipped(self):
        """testing if the end_frame attribute will be set to the default
        value when the end_frame argument is skipped
        """
        self.kwargs['number'] = '1a'
        self.kwargs.pop("end_frame")
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.end_frame, 1)
    
    def test_end_frame_argument_is_None(self):
        """testing if the end_frame attribute will be set to the default
        value when the end_frame argument is skipped
        """
        self.kwargs['number'] = '1a'
        self.kwargs["end_frame"] = None
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.end_frame, 1)
    
    def test_end_frame_attribute_is_Non(self):
        """testing if the end_frame attribute will be set to the default
        value when it is set to None
        """
        self.test_shot.end_frame = None
        self.assertEqual(self.test_shot.end_frame, 1)
    
    def test_end_frame_argument_is_not_integer(self):
        """testing if a TypeError will be raised when the end_frame argument
        is not an integer
        """
        self.kwargs['number'] = '1a'
        self.kwargs["end_frame"] = "asdfa"
        self.assertRaises(TypeError, Shot, **self.kwargs)
    
    def test_end_frame_attribute_is_not_integer(self):
        """testing if a TypeError will be raised when the end_frame attribute
        is not set to an integer value
        """
        self.assertRaises(TypeError, setattr, self.test_shot, "end_frame",
                          "asdfs")
    
    def test_end_frame_attribute_is_working_properly(self):
        """testing if the end_frame attribute is working properly
        """
        test_value = 10
        self.test_shot.end_frame = test_value
        self.assertEqual(self.test_shot.end_frame, test_value)
    
    def test_end_frame_attribute_updates_the_duration_attribute(self):
        """testing if the end_frame attribute updates the duration attribute
        value
        """
        self.test_shot.end_frame = 200
        self.assertEqual(self.test_shot.start_frame, 1)
        self.assertEqual(self.test_shot.duration, 200)
    
    def test_duration_attribute_is_initialized_correctly(self):
        """testing if the duration attribute is initialized correctly 
        """
        self.assertEqual(
            self.test_shot.duration,
            self.test_shot.end_frame - self.test_shot.start_frame + 1
        ) 
    
    def test_duration_attribute_is_updated_correctly(self):
        """testing if the duration attribute is updated correctly with the
        changing values of start_frame and end_frame values
        """
        self.kwargs['number'] = '1duration'
        new_shot = Shot(**self.kwargs)
        self.assertEqual(new_shot.start_frame, 1)
        self.assertEqual(new_shot.end_frame, 100)
        new_shot.start_frame = 10
        self.assertEqual(new_shot.duration, 91)
        
        new_shot.end_frame = 110
        self.assertEqual(new_shot.duration, 101)
    
    def test_project_attribute_is_initialized_correctly(self):
        """testing if the project attribute is initialized correctly
        """
        self.assertTrue(self.test_shot.project is
                        self.kwargs["sequence"].project)

    def test_shot_is_CRUD_properly_in_the_database(self):
        """testing if the shot instance is created properly in the database
        """
        new_proj = Project("TEST_PROJ_FOR_CRUD")
        new_proj.create()
        
        new_seq = Sequence(new_proj, "TEST_SEQ103")
        new_seq.save()
        
        new_shot = Shot(new_seq, '1a')
        new_shot.save()
        
        # now query the database if it is created and read correctly
        self.assertEqual(
            new_shot,
            Shot.query()
                .filter(Shot.number==new_shot.number)
                .first()
        )
        
        # now update it
        new_shot.start_frame = 100
        new_shot.end_frame = 200
        new_shot.save()
        
        self.assertEqual(
            new_shot.start_frame,
            Shot.query()
                .filter(Shot.number==new_shot.number)
                .first()
                .start_frame
        )
        self.assertEqual(
            new_shot.end_frame,
            Shot.query()
                .filter(Shot.number==new_shot.number)
                .first()
                .end_frame
        )
        
        # now delete it
        db.session.delete(new_shot)
        db.session.commit()
        
        self.assertEqual(len(Shot.query().all()), 1)
    
    def test_equality_of_shots(self):
        """testing if the equality operator is working properly
        """
        proj1 = Project("TEST_EQ_PROJ")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq2, 1)
        
        #shot1a = Shot(seq1, 1)
        shot1a = seq1.shots[0]
        
        self.assertTrue(shot1==shot1a)
        self.assertFalse(shot1==shot2)
        self.assertFalse(shot1a==shot3)
    
    def test_inequality_of_shots(self):
        """testing if the equality operator is working properly
        """
        proj1 = Project("TEST_EQ_PROJ")
        proj1.create()
        
        seq1 = Sequence(proj1, "TEST_SEQ1")
        seq2 = Sequence(proj1, "TEST_SEQ2")
        
        shot1 = Shot(seq1, 1)
        shot2 = Shot(seq1, 2)
        shot3 = Shot(seq2, 1)
        
        #shot1a = Shot(seq1, 1)
        shot1a = seq1.shots[0]
        
        self.assertFalse(shot1!=shot1a)
        self.assertTrue(shot1!=shot2)
        self.assertTrue(shot1a!=shot3)
    
    def test_handle_at_start_attribute_not_an_integer(self):
        """testing if a TypeError will be raised when the handles_at_start
        attribute is set anything other then an integer
        """
        
        self.assertRaises(
            TypeError, setattr, self.test_shot, "handle_at_start",
            "test value"
        )
    
    def test_handle_at_start_defaults_to_zero(self):
        """testing if the default value of handle_at_start is 0
        """
        
        self.assertEqual(self.test_shot.handle_at_start, 0)
    
    def test_handle_at_start_is_negative(self):
        """testing if a ValueError will be raised when the handle_at_start is
        a negative value
        """
        
        self.assertRaises(
            ValueError, setattr, self.test_shot, "handle_at_start", -10
        )
    
    def test_handle_at_start_is_bigger_then_duration_minus_one(self):
       """testing if a ValueError will be raised when the handle_at_start is
       bigger then the duration-1
       """
       
       self.assertRaises(
           ValueError, setattr, self.test_shot, "handle_at_start",
           self.test_shot.duration
       )
    
    def test_handles_together_are_bigger_then_duration_minus_one_while_setting_handle_at_start(self):
       """testing if a ValueError will be raised when the handle_at_start and
       handle_at_end together are greater then duration-1
       """
       
       self.test_shot.start_frame = 1
       self.test_shot.end_frame = 100
       self.test_shot.handle_at_end = 50
       self.assertRaises(
           ValueError, setattr, self.test_shot, "handle_at_start", 50
       )
    
    def test_handle_at_end_attribute_not_an_integer(self):
        """testing if a TypeError will be raised when the handles_at_start
        attribute is set anything other then an integer
        """
        
        self.assertRaises(
            TypeError, setattr, self.test_shot, "handle_at_end",
            "test value"
        )
    
    def test_handle_at_end_defaults_to_zero(self):
        """testing if the default value of handle_at_end is 0
        """
        self.assertEqual(self.test_shot.handle_at_end, 0)
    
    def test_handle_at_end_is_negative(self):
        """testing if a ValueError will be raised when the handle_at_end is
        a negative value
        """
        self.assertRaises(
            ValueError, setattr, self.test_shot, "handle_at_end", -10
        )
    
    def test_handle_at_end_is_bigger_then_duration_minus_one(self):
       """testing if a ValueError will be raised when the handle_at_end is
       bigger then the duration-1
       """
       self.assertRaises(
           ValueError, setattr, self.test_shot, "handle_at_end",
           self.test_shot.duration
       )
    
    def test_handles_together_are_bigger_then_duration_minus_one_while_setting_handle_at_end(self):
       """testing if a ValueError will be raised when the handle_at_start and
       handle_at_end together are greater then duration-1
       """
       
       self.test_shot.start_frame = 1
       self.test_shot.end_frame = 100
       self.test_shot.handle_at_start = 50
       self.assertRaises(
           ValueError, setattr, self.test_shot, "handle_at_end", 50
       )
    
    def test_deleting_a_shot_will_not_delete_the_related_project(self):
        """testing if deleting a shot will not delete the related project
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'test seq 1')
        seq1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        # check if they are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(shot1, db.session)
        
        # delete the shot
        db.session.delete(shot1)
        db.session.commit()
        
        self.assertNotIn(shot1, db.session)
        
        self.assertIn(proj1, db.session)
    
    def test_deleting_a_shot_will_not_delete_the_related_sequence(self):
        """testing if deleting a shot will not delete the related sequence
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'test seq 1')
        seq1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        # check if they are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(shot1, db.session)
        
        # delete the shot
        db.session.delete(shot1)
        db.session.commit()
        
        self.assertNotIn(shot1, db.session)
        self.assertIn(seq1, db.session)
    
    def test_deleting_a_shot_will_not_delete_the_other_shots_in_the_related_sequence(self):
        """testing if deleting a shot will not delete the other shots in the
        sequence
        """
        proj1 = Project('test project 1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'test seq 1')
        seq1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        shot2 = Shot(seq1, 2)
        shot2.save()
        
        # check if they are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(shot1, db.session)
        self.assertIn(shot2, db.session)
        
        # delete the shot
        db.session.delete(shot1)
        db.session.commit()
        
        self.assertNotIn(shot1, db.session)
        self.assertIn(shot2, db.session)
    
    def test_deleting_a_shot_will_delete_the_related_versions(self):
        """testing if deleting a shot will delete the related versions
        """
        
        proj1 = Project('test project 1')
        proj1.save()
        
        seq1 = Sequence(proj1, 'test sequence 1')
        seq1.save()
        
        shot1 = Shot(seq1, 1)
        shot1.save()
        
        shot2 = Shot(seq1, 2)
        shot2.save()
        
        user = User.query().first()
        shot_vtypes = VersionType.query().filter_by(type_for="Shot").all()
        
        # versions for shot1
        vers1 = Version(
            shot1,
            base_name=shot1.code,
            type=shot_vtypes[0],
            created_by=user
        )
        vers1.save()
        
        vers2 = Version(
            shot1,
            base_name=shot1.code,
            type=shot_vtypes[0],
            created_by=user
        )
        vers2.save()
        
        vers3 = Version(
            shot1,
            base_name=shot1.code,
            type=shot_vtypes[0],
            created_by=user
        )
        vers3.save()
        
        # versions for shot2
        vers4 = Version(
            shot2,
            base_name=shot2.code,
            type=shot_vtypes[0],
            created_by=user
        )
        vers4.save()
        
        vers5 = Version(
            shot2,
            base_name=shot2.code,
            type=shot_vtypes[0],
            created_by=user
        )
        vers5.save()
        
        vers6 = Version(
            shot2,
            base_name=shot2.code,
            type=shot_vtypes[0],
            created_by=user
        )
        vers6.save()
        
        # test all are in the session
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(shot1, db.session)
        self.assertIn(shot2, db.session)
        self.assertIn(vers1, db.session)
        self.assertIn(vers2, db.session)
        self.assertIn(vers3, db.session)
        self.assertIn(vers4, db.session)
        self.assertIn(vers5, db.session)
        self.assertIn(vers6, db.session)
        
        # delete shot1
        db.session.delete(shot1)
        db.session.commit()
        
        # check if versions are deleted
        self.assertNotIn(shot1, db.session)
        self.assertNotIn(vers1, db.session)
        self.assertNotIn(vers2, db.session)
        self.assertNotIn(vers3, db.session)
        
        # check if all the others are still there
        self.assertIn(proj1, db.session)
        self.assertIn(seq1, db.session)
        self.assertIn(shot2, db.session)
        self.assertIn(vers4, db.session)
        self.assertIn(vers5, db.session)
        self.assertIn(vers6, db.session)
    
