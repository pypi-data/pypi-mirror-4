import devpath
from pyjsbsim import FGFDMExec
import time
import numpy as np
import pickle
from bada import BadaData

class FDM737(FGFDMExec):

    def __init__(self):
        super(FDM737, self).__init__()

        self.set_root_dir("/usr/local/share/JSBSim/")
        self.set_aircraft_path("aircraft")
        self.set_engine_path("engine")
        self.set_systems_path("systems")
        self.load_model("737")

        # solver properties
        self.set_property_value("trim/solver/iterMax", 300)
        self.set_property_value("trim/solver/showConvergence", False)
        self.set_property_value("trim/solver/showSimplex", False)
        self.set_property_value("trim/solver/pause", False)
   
        #for item in self.query_property_catalog("/"):
            #print item

        self.set_property_value("ic/h-agl-ft", 30000.0)
        self.set_property_value("ic/gamma-deg", 0.0)
        
    def setup_bada_trim(self, mode):

        self.set_property_value("trim/solver/aileronGuess",0)
        self.set_property_value("trim/solver/elevatorGuess",0)
        self.set_property_value("trim/solver/rudderGuess",0)
        self.set_property_value("trim/solver/throttleGuess",0.5)
        self.set_property_value("trim/solver/alphaGuess",0)
        self.set_property_value("trim/solver/betaGuess",0)

        self.set_property_value("ic/vc-kts", 250)
        self.set_property_value("ic/lat-gc-deg", 0.0)
        self.set_property_value("ic/lon-gc-deg", 0.0)
        self.set_property_value("ic/lat-gc-deg", 47.0)
        self.set_property_value("ic/lon-gc-deg", 122.0)
        self.set_property_value("ic/phi-deg", 0.0)
        self.set_property_value("ic/theta-deg", 0.0)
        self.set_property_value("ic/psi-deg", 0.0)
        if mode == "low":
            for i_tank in range(3):
                self.set_property_value("propulsion/tank[{}]/contents-lbs".format(i_tank), 1)
        elif mode == "nom":
            for i_tank in range(3):
                self.set_property_value("propulsion/tank[{}]/contents-lbs".format(i_tank), 5000)
        elif mode == "high":
            for i_tank in range(3):
                self.set_property_value("propulsion/tank[{}]/contents-lbs".format(i_tank), 10000)
        else:
            raise IOError("unknown mode")
        for item in ["ic/h-agl-ft","ic/vc-kts","ic/vt-kts"]:
            print "{}\t: {}".format(item,self.get_property_value(item))

file_name = "save.bada_data_737-" + time.strftime("%m_%d_%y__%H_%M")
bada_data_737 = BadaData.from_fdm(
    fdm=FDM737(),
    flight_levels = np.array([
        0, 5, 10, 15, 20, 30, 40, 60, 80, 100,
        120, 140, 160, 180, 200, 220, 240, 260,
        280, 290, 310, 330, 350, 370]),
    file_name=file_name,
    verbose=False)
bada_data_737_loaded = pickle.load(open(file_name,"rb"))

print bada_data_737_loaded
