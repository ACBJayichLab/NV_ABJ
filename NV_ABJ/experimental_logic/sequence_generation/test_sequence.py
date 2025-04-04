import unittest
from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import *

DeviceConfigurationUnderTest = SequenceDeviceConfiguration
SequenceDeviceUnderTest = SequenceDevice
SequenceSubsetUnderTest = SequenceSubset
SequenceUnderTest = Sequence


class TestSequenceDevice(unittest.TestCase):

    def test_device_properties(self):
        """There isn't traditionally functionality to a sequence device it is meant to be a dataclass however we 
        want to make sure we keep the same functionality for each iteration of the devices 
        """

        # Checking a hashable device configuration
        dev_config_annotations = DeviceConfigurationUnderTest.__annotations__
        config_labels = {"address":int, "device_label":str, "delayed_to_on_ns":int}

        for label in config_labels:
            self.assertEqual(config_labels[label],dev_config_annotations[label])
        
        # Checking a overall class labels
        dev_mut_annotations = SequenceDeviceUnderTest.__annotations__
        dev_mut_labels = {"device_status":bool, "config":DeviceConfigurationUnderTest}

        for label in dev_mut_labels:
            self.assertEqual(dev_mut_labels[label],dev_mut_annotations[label])
    
    def test_device_assignments(self):
        """This checks we can assign a device certain properties it should be redundant to properties 
        """
        dev0 = SequenceDeviceUnderTest(config={"address":10,"device_label":"10","delayed_to_on_ns":10},device_status=True)

        self.assertEqual(10,dev0.config.address)
        self.assertEqual("10",dev0.config.device_label)
        self.assertEqual(10,dev0.config.delayed_to_on_ns)
        self.assertEqual(True,dev0.device_status)
    
    def test_device_sorting_by_configuration_delay(self):
        """This tests that the devices configuration which has to be hashable will sort correctly based on the delayed_time_ns 
        """
        dev0 = SequenceDeviceUnderTest(config={"address":0,"device_label":"0","delayed_to_on_ns":10},device_status=True)
        dev1 = SequenceDeviceUnderTest(config={"address":1,"device_label":"1","delayed_to_on_ns":5},device_status=True)
        dev2 = SequenceDeviceUnderTest(config={"address":2,"device_label":"2","delayed_to_on_ns":2},device_status=True)

        # Adding a list of devices in the reversed order we want
        devices = [dev0.config,dev1.config,dev2.config]
        sorted_devices = sorted(devices)
        expected = [dev2.config,dev1.config,dev0.config]

        self.assertEqual(sorted_devices,expected)





class TestSequenceSubset(unittest.TestCase):

    def setUp(self):
        self.dev0 = SequenceDeviceUnderTest(config={"address":0,"device_label":"0","delayed_to_on_ns":0},device_status=False)
        self.dev1 = SequenceDeviceUnderTest(config={"address":1,"device_label":"1","delayed_to_on_ns":0},device_status=False)
        self.dev2 = SequenceDeviceUnderTest(config={"address":2,"device_label":"2","delayed_to_on_ns":0},device_status=False)
        self.dev_none = SequenceDeviceUnderTest(config={"address":None,"device_label":"000","delayed_to_on_ns":0},device_status=False)

    
    def tearDown(self):
        pass

    def test_add_step_normal(self):
        """Checks a normal entry has the formatting of a list with tuples (duration_ns, set(devices))
        """
        duration = 10
        
        # Adding to the subset
        sub = SequenceSubsetUnderTest()
        sub.add_step(devices=[self.dev0,self.dev1],duration_ns=duration)

        # Checks that the loop when not specified goes to zero 
        loops = sub.loop_steps
        self.assertEqual(loops,0)

        result = sub.steps

        # Expected result 
        devices_set = set([self.dev1.config,self.dev0.config])
        expected = [(duration,devices_set)]

        self.assertEqual(result,expected)

    def test_add_step_with_no_devices(self):
        """Checks we can add a step that has no devices and a duration greater than zero
        """
        duration = 10
        
        # Adding to the subset
        sub = SequenceSubsetUnderTest()
        sub.add_step(devices=[],duration_ns=duration)

        # Checks that the loop when not specified goes to zero 
        loops = sub.loop_steps
        self.assertEqual(loops,0)

        result = sub.steps

        # Expected result 
        devices_set = set()
        expected = [(duration,devices_set)]

        self.assertEqual(result,expected)

    def test_add_step_with_a_none_address(self):
        """Checks that a none address will be removed from the list 
        """
        duration = 10
        
        # Adding to the subset
        sub = SequenceSubsetUnderTest()
        sub.add_step(devices=[self.dev0,self.dev1,self.dev_none],duration_ns=duration)

        # Checks that the loop when not specified goes to zero 
        loops = sub.loop_steps
        self.assertEqual(loops,0)

        result = sub.steps

        # Expected result 
        devices_set = set([self.dev1.config,self.dev0.config])
        expected = [(duration,devices_set)]

        self.assertEqual(result,expected)

    def test_add_step_with_no_duration(self):
        """Checks that when we enter a duration of 0 the step will be ignored from the sequence 
        """
        duration = 0
        
        # Adding to the subset
        sub = SequenceSubsetUnderTest()
        sub.add_step(devices=[self.dev0,self.dev1,self.dev_none],duration_ns=duration)

        # Checks that the loop when not specified goes to zero 
        loops = sub.loop_steps
        self.assertEqual(loops,0)

        result = sub.steps

        # Expected result 
        expected = []

        self.assertEqual(result,expected)

    def test_add_sequence_loops(self):
        sub = SequenceSubsetUnderTest()
        sub.loop_steps = 10

        loops = sub.loop_steps
        self.assertEqual(loops,10)


    
    def test_adding_multiple_steps(self):
        """This tests that multiple steps can be added and we won't have an issue as a result
        """

        sub = SequenceSubsetUnderTest()
        sub.add_step(devices = [], duration_ns=2)
        sub.add_step(devices=[self.dev0,self.dev1],duration_ns=10)
        sub.add_step(devices=[self.dev0,self.dev2],duration_ns=5)
        sub.add_step(devices=[self.dev0,self.dev1,self.dev_none],duration_ns=12)
        sub.add_step(devices = [], duration_ns=0)

        loops = 10
        sub.loop_steps = loops
        self.assertEqual(loops,sub.loop_steps)

        result = sub.steps


        expected = [
        (2, set()),
        (10,set([self.dev1.config,self.dev0.config])),
        (5,set([self.dev2.config,self.dev0.config])),
        (12,set([self.dev1.config,self.dev0.config])),
        ]
        self.assertEqual(result,expected)


    def test_devices_set(self):
        """This checks that the overall devices set will be equal to the added devices 

        here we should see no none address and no device 2 because its step has zero duration
        """

        sub = SequenceSubsetUnderTest()
        sub.add_step(devices = [], duration_ns=2)
        sub.add_step(devices=[self.dev0,self.dev1],duration_ns=10)
        sub.add_step(devices=[self.dev0,self.dev2],duration_ns=0)
        sub.add_step(devices=[self.dev0,self.dev1,self.dev_none],duration_ns=12)
        sub.add_step(devices = [], duration_ns=0)

        loops = 10
        sub.loop_steps = loops
        self.assertEqual(loops,sub.loop_steps)

        result = sub.devices
        expected = set([self.dev0.config,self.dev1.config])
        self.assertEqual(result,expected)


    def test_less_than_zero_duration_error(self):
        sub = SequenceSubsetUnderTest()
        with self.assertRaises(ValueError):
            sub.add_step(devices=[], duration_ns=-10)
    
class TestSequence(unittest.TestCase):

    def setUp(self):
        self.dev0 = SequenceDeviceUnderTest(config={"address":0,"device_label":"0","delayed_to_on_ns":0},device_status=False)
        self.dev1 = SequenceDeviceUnderTest(config={"address":1,"device_label":"1","delayed_to_on_ns":0},device_status=False)
        self.dev2 = SequenceDeviceUnderTest(config={"address":2,"device_label":"2","delayed_to_on_ns":0},device_status=False)
        self.dev_none = SequenceDeviceUnderTest(config={"address":None,"device_label":"000","delayed_to_on_ns":0},device_status=False)

        sub = SequenceSubsetUnderTest()
        sub.add_step(devices = [], duration_ns=2)
        sub.add_step(devices=[self.dev0,self.dev1],duration_ns=10)
        sub.add_step(devices=[self.dev0,self.dev2],duration_ns=0)
        sub.add_step(devices=[self.dev0,self.dev1,self.dev_none],duration_ns=12)
        sub.add_step(devices = [], duration_ns=0)
        sub.loop_steps = 3

        self.sub_sequence = sub


    
    def tearDown(self):
        pass


    def test_adding_singular_step_entered(self):
        """Tests to see that the sequence is entering a singular step correctly
        """
        seq = SequenceUnderTest()
        seq.add_step(devices=[], duration_ns=10)

        result = seq.steps
        expected = [(10, set())]

        self.assertEqual(result,expected)

    def test_adding_singular_step_entered_with_devices(self):
        """Tests to see that the sequence is entering a singular step correctly
        """
        seq = SequenceUnderTest()
        seq.add_step(devices=[self.dev0], duration_ns=10)

        result = seq.steps
        expected = [(10, set([self.dev0.config]))]

        self.assertEqual(result,expected)

        result = seq.devices
        expected = set([self.dev0.config])

        self.assertEqual(result,expected)
    
    def test_adding_a_sub_sequence(self):
        """This tests adding a subsequence which will have loops 
        """
        seq = SequenceUnderTest()
        seq.add_sub_sequence(self.sub_sequence)

        result_steps = seq.steps
        result_devices = seq.devices

        expected_steps = [
        (2, set()),
        (10,set([self.dev1.config,self.dev0.config])),
        (12,set([self.dev1.config,self.dev0.config])),
        (2, set()),
        (10,set([self.dev1.config,self.dev0.config])),
        (12,set([self.dev1.config,self.dev0.config])),
        (2, set()),
        (10,set([self.dev1.config,self.dev0.config])),
        (12,set([self.dev1.config,self.dev0.config])),
        (2, set()),
        (10,set([self.dev1.config,self.dev0.config])),
        (12,set([self.dev1.config,self.dev0.config]))
        ]

        expected_devices = set([self.dev1.config,self.dev0.config])

        self.assertEqual(result_steps,expected_steps)
        self.assertEqual(result_devices,expected_devices)
    
    def test_less_than_zero_duration_error(self):
        seq = SequenceUnderTest()
        with self.assertRaises(ValueError):
            seq.add_step(devices=[], duration_ns=-10)
    
    def test_linear_time_conversion_no_wrapping(self):
        ...





if __name__ == "__main__":
    unittest.main()




# dev0 = SequenceDevice(config={"address":0,"device_label":"0","delayed_to_on_ns":0},device_status=False)
# dev1 = SequenceDevice(config={"address":1,"device_label":"1","delayed_to_on_ns":0},device_status=False)
# dev2 = SequenceDevice(config={"address":2,"device_label":"2","delayed_to_on_ns":0},device_status=False)
# dev_none = SequenceDevice(config={"address":None,"device_label":"000","delayed_to_on_ns":0},device_status=False)

# sub = SequenceSubset()
# # sub.add_step(devices = [], duration_ns=2)
# sub.add_step(devices=[dev0,dev1],duration_ns=10)
# sub.add_step(devices=[dev0],duration_ns=10)
# sub.add_step(devices=[dev0,dev1,dev2],duration_ns=10)
# sub.loop_steps = 5000

# sub2 = SequenceSubset()
# # sub.add_step(devices = [], duration_ns=2)
# sub2.add_step(devices=[dev2,dev1],duration_ns=10)
# sub2.add_step(devices=[dev1],duration_ns=10)
# sub2.add_step(devices=[dev0,dev1,dev2],duration_ns=10)
# sub2.loop_steps = 5000


# seq = Sequence()
# # seq.add_sub_sequence(sub)
# # seq.add_step(devices=[dev0],duration_ns=10)
# # seq.add_step(devices=[dev1],duration_ns=10)
# seq.add_step(devices=[dev0,dev1,dev2],duration_ns=10)
# # seq.add_sub_sequence(sub2)
# # seq.add_step(devices = [], duration_ns=10)

# import time
# start = time.time()
# instructions,sub_routines = seq.instructions(wrapped=True,allow_subroutine=True)
# print(f"Time took:{(time.time()-start)/60}")

# print(sub_routines)

# for inst in instructions:
#     print(instructions[inst])
