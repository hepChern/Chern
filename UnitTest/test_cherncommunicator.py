import os
import unittest
from colored import Fore, Style
import Chern.kernel.vobject as vobj
from Chern.kernel.chern_cache import ChernCache
import prepare

CHERN_CACHE = ChernCache.instance()

import unittest
from io import BytesIO
from unittest.mock import patch, mock_open, MagicMock
from Chern.kernel.chern_communicator import ChernCommunicator  # Replace with your actual module name
import tarfile

class TestChernCommunicator(unittest.TestCase):

    @patch("Chern.kernel.chern_communicator.requests.get")  # Patch at the location where it's used
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


    @patch("Chern.kernel.chern_communicator.requests.get")
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


    @patch("Chern.kernel.chern_communicator.requests.get")
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


    @patch("Chern.kernel.chern_communicator.requests.get")
    def get_file(self, mock_get):
        print(Fore.BLUE + "Testing Get File..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Mock the response for get_file
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.text = "file content"
        mock_get.return_value = mock_response

        result = self.comm.get_file("xyz", "output1.out", machine="local")

        mock_get.assert_called_once_with(
            "http://localhost:8080/get_file/xyz/output1.out/local", timeout=10
        )
        self.assertEqual(result, "file content")

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()



    @patch("Chern.kernel.chern_communicator.requests.get")
    @patch("Chern.kernel.chern_communicator.requests.post")
    @patch("Chern.kernel.chern_communicator.open", new_callable=mock_open, read_data=b"filedata")
    @patch("Chern.kernel.chern_communicator.tarfile.open")
    def test_deposit_with_data(
        self, mock_tarfile_open, mock_open_fn, mock_post, mock_get
    ):
        print(Fore.BLUE + "Testing Deposit With Data..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        # Setup mock impression
        class FakeImpression:
            uuid = "abc123"
            tarfile = "/path/to/impression.tar"
            path = "/path/to/impression"

        impression = FakeImpression()

        # Create fake tarfile members
        fake_member = tarfile.TarInfo(name="file1.txt")
        fake_tar = MagicMock()
        fake_tar.getmembers.return_value = [fake_member]
        fake_tar.extractfile.return_value = BytesIO(b"content")

        # tarfile.open is called twice: once to read, once to write
        mock_tarfile_open.side_effect = [fake_tar, MagicMock()]

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")
        self.comm.timeout = 5

        self.comm.deposit_with_data(impression, path="/some/raw/data")


        # Check tarfile opening: read and write
        self.assertEqual(mock_tarfile_open.call_count, 2)
        mock_tarfile_open.assert_any_call("/path/to/impression.tar", "r")
        mock_tarfile_open.assert_any_call("/tmp/abc123.tar.gz", "w:gz")

        # Check file reading (tar.gz and config.json)
        expected_open_calls = [
            unittest.mock.call("/tmp/abc123.tar.gz", "rb"),
            unittest.mock.call("/path/to/impression/config.json", "rb")
        ]
        mock_open_fn.assert_has_calls(expected_open_calls, any_order=True)

        # Check HTTP post
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("http://localhost:8080/upload", args[0])
        self.assertEqual(kwargs["timeout"], 5)
        self.assertIn("files", kwargs)
        self.assertEqual(
            sorted(kwargs["data"].keys()), ["config", "tarname"]
        )

        # Check HTTP get
        mock_get.assert_called_once_with(
            "http://localhost:8080/setjobstatus/abc123/archived",
            timeout=5
        )
        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()

    """
    def export(self, impression, filename, output):
        url = self.serverurl()
        r = requests.get(
                f"http://{url}/export/{impression.uuid}/{filename}",
                timeout=self.timeout
        )
        with open(output, "wb") as f:
            f.write(r.content)
    """
    @patch("Chern.kernel.chern_communicator.requests.get")
    def test_export(self, mock_get):
        print(Fore.BLUE + "Testing Export..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Setup mock impression
        class FakeImpression:
            uuid = "abc123"
            tarfile = "/path/to/impression.tar"
            path = "/path/to/impression"

        impression = FakeImpression()

        # Mock the response for export
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.content = b"exported content"
        mock_get.return_value = mock_response

        # Call the export method
        self.comm.export(impression, "file.txt", "output.txt")

        mock_get.assert_called_once_with(
            "http://localhost:8080/export/abc123/file.txt", timeout=10
        )

        # Check if the output file was created correctly
        with open("output.txt", "rb") as f:
            content = f.read()
            self.assertEqual(content, b"exported content")

        os.remove("output.txt")
        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()

    @patch("Chern.kernel.chern_communicator.requests.get")
    def test_status(self, mock_get):
        print(Fore.BLUE + "Testing Status..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Setup mock impression
        class FakeImpression:
            uuid = "abc123"
            tarfile = "/path/to/impression.tar"
            path = "/path/to/impression"

        impression = FakeImpression()

        # Mock the response for status
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_get.return_value = mock_response

        # Call the status method
        status = self.comm.status(impression)

        mock_get.assert_called_once_with(
            "http://localhost:8080/status/abc123", timeout=10
        )
        self.assertEqual(status, "ok")

        # Simulate unconnected status
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection error")
        status = self.comm.status(impression)

        mock_get.assert_called_once_with(
            "http://localhost:8080/status/abc123", timeout=10
        )
        self.assertEqual(status, "unconnected")

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()

    @patch("Chern.kernel.chern_communicator.requests.get")
    def test_run_status(self, mock_get):
        print(Fore.BLUE + "Testing Run Status..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Setup mock impression
        class FakeImpression:
            uuid = "abc123"
            tarfile = "/path/to/impression.tar"
            path = "/path/to/impression"

        impression = FakeImpression()

        # Mock the response for run status
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.text = "running"
        mock_get.return_value = mock_response

        # Call the run_status method
        status = self.comm.run_status(impression, machine="local")

        mock_get.assert_called_once_with(
            "http://localhost:8080/runstatus/abc123/local", timeout=10
        )
        self.assertEqual(status, "running")

        # Simulate unconnected status
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection error")
        status = self.comm.run_status(impression, machine="local")

        mock_get.assert_called_once_with(
            "http://localhost:8080/runstatus/abc123/local", timeout=10
        )
        self.assertEqual(status, "unconnected")

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()

    @patch("Chern.kernel.chern_communicator.requests.get")
    def test_collect(self, mock_get):
        print(Fore.BLUE + "Testing Collect..." + Style.RESET)
        prepare.create_chern_project("demo_genfit_new")
        os.chdir("demo_genfit_new")
        obj_gen = vobj.VObject("Gen")
        obj_genTask = vobj.VObject("GenTask")
        obj_fit = vobj.VObject("Fit")
        obj_fitTask = vobj.VObject("FitTask")

        self.comm = ChernCommunicator()
        self.comm.serverurl = MagicMock(return_value="localhost:8080")

        # Setup mock impression
        class FakeImpression:
            uuid = "abc123"
            tarfile = "/path/to/impression.tar"
            path = "/path/to/impression"

        impression = FakeImpression()

        # Mock the response for collect
        mock_get.reset_mock()
        mock_response = MagicMock()
        mock_response.text = "collected"
        mock_get.return_value = mock_response

        # Call the collect method
        result = self.comm.collect(impression)

        mock_get.assert_called_once_with(
            "http://localhost:8080/collect/abc123", timeout=10
        )
        self.assertEqual(result, "collected")

        os.chdir("..")
        prepare.remove_chern_project("demo_genfit_new")
        CHERN_CACHE.__init__()

if __name__ == "__main__":
    unittest.main(verbosity=2)
