import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hab_owned_record_validator", HERE / "validate_records.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class Records(unittest.TestCase):
    def test_six_samples(self):
        files = list((HERE.parent / "formats").glob("sample.*"))
        self.assertEqual(len(files), 6)
        for p in files:
            with self.subTest(extension=p.suffix):
                result = validator.validate_bytes(p.read_bytes(), p.suffix)
                self.assertEqual(result["status"], "STRUCTURE_VALID_ONLY")
                self.assertFalse(result["authorization_granted"])
                self.assertFalse(result["ownership_verified"])

    def test_invalid_inputs(self):
        valid = {"schema_version": "1", "id": "example", "payload": {}}
        for data, ext in [
            (b"not json", ".habflow"), (json.dumps(valid).encode(), ".exe"),
            (b"x" * 65537, ".habflow"), (b'{"x":1}', ".habflow"),
            (json.dumps({**valid, "id": "../unsafe"}).encode(), ".habflow"),
            (json.dumps({**valid, "payload": []}).encode(), ".habflow"),
            (json.dumps({**valid, "payload": {"privateKey": "synthetic"}}).encode(), ".habflow"),
            (json.dumps({**valid, "schema_version": "2"}).encode(), ".habflow"),
            (b'{"schema_version":"1","id":"x","payload":{"n":NaN}}', ".habflow"),
            (b'{"schema_version":"1","id":"x","payload":{"n":1e309}}', ".habflow"),
            (b'{"schema_version":"1","id":"x","id":"y","payload":{}}', ".habflow"),
        ]:
            with self.subTest(extension=ext, bytes=len(data)):
                with self.assertRaises(ValueError):
                    validator.validate_bytes(data, ext)

    def test_depth_limit(self):
        payload = {}
        for _ in range(34):
            payload = {"nested": payload}
        with self.assertRaises(ValueError):
            validator.validate_bytes(json.dumps({"schema_version": "1", "id": "x", "payload": payload}).encode(), ".habflow")


if __name__ == "__main__":
    unittest.main()
