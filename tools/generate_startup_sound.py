"""Reproducible original AKM cue; no recordings or third-party samples."""
import math
from pathlib import Path
import struct
import wave

RATE = 44100
DURATION = 3.6


def generate(path: Path):
    samples = []
    notes = [(0.0, 0.09, 880, 0.13), (0.16, 0.09, 1320, 0.10),
             (0.42, 2.9, 261.6256, 0.15), (0.68, 2.65, 329.6276, 0.13),
             (0.94, 2.38, 391.9954, 0.12), (1.20, 2.12, 523.2511, 0.10)]
    for index in range(round(RATE * DURATION)):
        t = index / RATE
        value = 0.0
        for onset, length, frequency, gain in notes:
            age = t - onset
            if 0 <= age < length:
                envelope = min(age / 0.025, 1.0) * min((length - age) / 0.65, 1.0)
                envelope *= math.exp(-age * 0.65)
                phase = 2 * math.pi * frequency * age
                value += gain * envelope * (math.sin(phase) + 0.18 * math.sin(2 * phase))
        samples.append(struct.pack('<h', round(max(-1, min(1, value)) * 32767)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as stream:
        stream.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        stream.writeframes(b''.join(samples))


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1] / 'assets/audio/akm_horizon.wav')
