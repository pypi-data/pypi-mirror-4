import devpath
import unittest

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_accessors(self):

        from pyjsbsim import FGFDMExec
        fdm = FGFDMExec()
        
        root_dir = "/usr/local/share/JSBSim/"
        fdm.set_root_dir(root_dir)
        assert (root_dir == fdm.get_root_dir())

        engine_path = "engine"
        fdm.set_engine_path(engine_path)
        assert (root_dir+engine_path == fdm.get_engine_path())

        aircraft_path = "aircraft"
        fdm.set_aircraft_path(aircraft_path)
        assert (root_dir+aircraft_path == fdm.get_aircraft_path())

        systems_path = "systems"
        fdm.set_systems_path(systems_path)
        assert (root_dir+systems_path == fdm.get_systems_path())

        model = "f16"
        fdm.load_model(model)
        assert (model == fdm.get_model_name())

if __name__ == '__main__':
    unittest.main()
