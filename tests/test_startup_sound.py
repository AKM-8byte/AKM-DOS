import struct
import tempfile
import unittest
import wave
from pathlib import Path

from tools.generate_startup_sound import generate, DURATION, RATE


class SoundAssetTests(unittest.TestCase):
    def test_generated_asset_matches_source_and_is_unclipped(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            regenerated = Path(directory) / 'sound.wav'
            generate(regenerated)
            self.assertEqual(regenerated.read_bytes(), (root / 'assets/audio/akm_horizon.wav').read_bytes())
        with wave.open(str(root / 'assets/audio/akm_horizon.wav'), 'rb') as stream:
            self.assertEqual((stream.getnchannels(), stream.getsampwidth(), stream.getframerate()), (1, 2, RATE))
            self.assertAlmostEqual(stream.getnframes() / RATE, DURATION)
            samples = struct.unpack('<' + 'h' * stream.getnframes(), stream.readframes(stream.getnframes()))
            self.assertGreater(max(samples), 1000)
            self.assertLess(max(abs(value) for value in samples), 32767)
            self.assertEqual(samples[-1], 0)
