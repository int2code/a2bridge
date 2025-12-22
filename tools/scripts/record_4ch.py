import sounddevice as sd
import sys
import matplotlib.pyplot as plt

SAMPLERATE = 48000
DURATION = 30
CHANNELS = 4
HOSTAPI = "WDM-KS"
DEVICE = "Mikrofon (XAudio A2B Interface)"
FORMAT = "int32"

def list_devices(hostapi_index: int | None = None, inputs_only: bool = False):
    devs = sd.query_devices()
    title = "Input devices" if inputs_only else "Devices (all types)"
    if hostapi_index is None:
        print(f"=== {title} — all host APIs ===")
        for i, d in enumerate(devs):
            if inputs_only and d['max_input_channels'] == 0:
                continue
            han = sd.query_hostapis()[d['hostapi']]['name']
            print(f"[{i}] {d['name']}  (host:{han}, in:{d['max_input_channels']}, out:{d['max_output_channels']})")
        print("================================\n")
        return
    print(f"=== {title} — Host API [{hostapi_index}]: {sd.query_hostapis()[hostapi_index]['name']} ===")
    for i, d in enumerate(devs):
        if d["hostapi"] != hostapi_index:
            continue
        if inputs_only and d['max_input_channels'] == 0:
            continue
        han = sd.query_hostapis()[d['hostapi']]['name']
        print(f"[{i}] {d['name']}  (host:{han}, in:{d['max_input_channels']}, out:{d['max_output_channels']})")
    print("=========================================================\n")
def resolve_hostapi():
    for i, ha in enumerate(sd.query_hostapis()):
        if HOSTAPI.lower() in ha["name"].lower():
            return i, ha["name"]
    return None, None

def find_device(device_spec: str, hostapi_index: int | None, require_input: bool = True, channels: int = 2):
    # Numeric index?
    try:
        idx = int(device_spec)
        info = sd.query_devices(idx)
        if (hostapi_index is None or info["hostapi"] == hostapi_index) and (not require_input or info["max_input_channels"] > 0):
            return idx, info
        return None, None
    except ValueError:
        pass
    # Substring search
    wanted = (device_spec or "").lower()
    for i, d in enumerate(sd.query_devices()):
        if hostapi_index is not None and d["hostapi"] != hostapi_index:
            continue
        if require_input and d["max_input_channels"] == 0:
            continue
        if wanted in d["name"].lower() and d["max_input_channels"] == channels:
            return i, d
    return None, None

def main():
    ha_index, ha_name = resolve_hostapi()
    dev_index, devinfo = find_device(DEVICE, ha_index, require_input=True, channels=CHANNELS)
    if dev_index is None:
        print(f"Input device '{DEVICE}' not found under selected host API.")
        list_devices(ha_index, inputs_only=True); sys.exit(1)
    frames = int(SAMPLERATE * DURATION)

    # Simple path
    data = sd.rec(frames, samplerate=SAMPLERATE, channels=CHANNELS, dtype=FORMAT, device=dev_index)
    sd.wait()
    channel_1 = [sample[0] for sample in data]
    # Create x-axis (sample index)
    x = range(len(channel_1))
    
     # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(x, channel_1)
    plt.title("Audio Channel 1")
    plt.xlabel("Sample index")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    main()