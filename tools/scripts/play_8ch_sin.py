import time, math
import numpy as np
import sounddevice as sd

DEVICE_NAME_SUBSTR = "XAudio A2B"
CHANNELS = 8
DURATION_SEC = 60.0
LEVEL = 0.8
FREQ_HZ = 440.0
SAMPLERATE = 48000
FORMAT = "int32"

def find_wdmks_device(name_substr, min_ch):
    name_substr = (name_substr or "").lower()
    hostapis = sd.query_hostapis()
    wdmks_idx = next((i for i, h in enumerate(hostapis) if "WDM-KS" in h["name"].upper()), None)
    if wdmks_idx is None:
        raise SystemExit("WDM-KS host API not found.")
    for i, d in enumerate(sd.query_devices()):
        if d["hostapi"] == wdmks_idx and d["max_output_channels"] >= min_ch:
            if not name_substr or name_substr in d["name"].lower():
                return i, d
    raise SystemExit(f"No WDM-KS output device with >= {min_ch} ch matching '{name_substr}'.")

def make_callback(sr):
    phase = 0.0
    omega = 2.0 * math.pi * FREQ_HZ / sr
    
    dtype = np.dtype(FORMAT)
    peak = int(np.iinfo(dtype).max * LEVEL)

    def cb(outdata, frames, timeinfo, status):
        nonlocal phase
        if status:
            print(status)
        t = phase + omega * np.arange(frames, dtype=np.float64)
        mono = (np.sin(t) * peak).round().astype(dtype).reshape(-1, 1)
        outdata[:] = np.repeat(mono, CHANNELS, axis=1)
        phase = (phase + omega * frames) % (2 * math.pi)
    return cb

def main():
    dev_index, dev = find_wdmks_device(DEVICE_NAME_SUBSTR, CHANNELS)
    print(f"Using WDM-KS device [{dev_index}]: {dev['name']} (max_out={dev['max_output_channels']})")

    try:
        print(f"Audio: {SAMPLERATE} Hz, dtype={FORMAT}")
        cb = make_callback(SAMPLERATE)
        with sd.OutputStream(
            device=dev_index,
            samplerate=SAMPLERATE,
            channels=CHANNELS,
            dtype=FORMAT,
            callback=cb,
            blocksize=0,
            latency=None
        ):
            time.sleep(DURATION_SEC)
        print("SUCCESS ✅")
        return
    except Exception as e:
        print(f"  failed: {e}")

if __name__ == "__main__":
    main()