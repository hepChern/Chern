import os
import unittest
from colored import Fore, Style
import Chern.kernel.vobject as vobj
from Chern.kernel.chern_cache import ChernCache
import prepare

CHERN_CACHE = ChernCache.instance()

import unittest
from unittest.mock import patch, MagicMock
from Chern.kernel.chern_communicator import ChernCommunicator  # Replace with your actual module name

class TestChernCommunicator(unittest.TestCase):

    @patch("requests.get")  # Patch at the location where it's used
    def test_dite_status(self, mock_get):
        print(Fore.BLUE + "Testing Dite Status..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Connect successfully
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_get.return_value = mock_response

        status = self.comm.dite_status()
        mock_get.assert_called_once_with("http://localhost:8080/ditestatus", timeout=10)
        self.assertEqual(status, "ok")

        # Simulate unconnected status due to response
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection error")
        status = self.comm.dite_status()
        mock_get.assert_called_once_with("http://localhost:8080/ditestatus", timeout=10)
        self.assertEqual(status, "unconnected")

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()


    @patch("requests.get")
    def test_dite_info(self, mock_get):
        print(Fore.BLUE + "Testing Dite Info..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Mock the response for Dite info
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_get.return_value = mock_response

        # Call the dite_info method
        info = self.comm.dite_info()
        mock_get.assert_called_once_with("http://localhost:8080/ditestatus", timeout=10)
        self.assertIn("[connected]", info)

        # Simulate unconnected status
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection error")
        info = self.comm.dite_info()
        mock_get.assert_called_once_with("http://localhost:8080/ditestatus", timeout=10)
        self.assertIn("[unconnected]", info)

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()


    @patch("requests.get")
    def test_output_files(self, mock_get):
        print(Fore.BLUE + "Testing Output Files..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")
        # Mock the response for output files

        mock_get.reset_mock()
        mock_get.side_effect = [
            MagicMock(text="machineABC"),             # response to machine_id
            MagicMock(text="output1.out output2.out") # response to outputs
        ]

        result = self.comm.output_files("xyz", machine="local")

        expected_calls = [
            unittest.mock.call("http://localhost:8080/machine_id/local", timeout=10),
            unittest.mock.call("http://localhost:8080/outputs/xyz/machineABC", timeout=10),
        ]
        mock_get.assert_has_calls(expected_calls)
        self.assertEqual(result, ["output1.out", "output2.out"])

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()



    """
    @patch("Chern.kernel.requests.get")
    def test_dite_status_unconnected_due_to_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "not_ok"
        mock_get.return_value = mock_response

        status = self.comm.dite_status()

        self.assertEqual(status, "unconnected")

    @patch("Chern.kernel.requests.get")
    def test_dite_status_unconnected_due_to_exception(self, mock_get):
        mock_get.side_effect = Exception("Connection error")

        status = self.comm.dite_status()

        self.assertEqual(status, "unconnected")
    """


if __name__ == "__main__":
    unittest.main(verbosity=2)
