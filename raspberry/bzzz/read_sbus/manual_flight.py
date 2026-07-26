import time
import os
import datetime
import threading
import queue

from bzzz.read_sbus.radio_receiver import RC
from bzzz.read_sbus.radioData import RadioData
from bzzz.read_sbus.esp_bridge import EspBridge

LOOP_RATE_HZ = 125
LOOP_PERIOD = 1.0 / LOOP_RATE_HZ

N_VALUES = 29

LOG_DIR = os.path.expanduser("~/flight_logs")
os.makedirs(LOG_DIR, exist_ok=True)

HEADER = (
    "t_pi,qw,qx,qy,qz,wx,wy,wz,"
    "FL,FR,BL,BR,ML,MR,"
    "J0,J1,J2,J3,J4,J5,J6,"
    "best,inject,dt,"
    "pitchRef,rollRef,yawRateRef,"
    "uRoll,uPitch,uYaw\n"
)


class LogWriter:
    """Owns the actual file handle. All file I/O happens on this
    background thread, so a slow SD card write can never block the
    real-time control loop."""

    def __init__(self):
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        f = None
        while True:
            kind, payload = self.q.get()
            if kind == "open":
                f = open(payload, "w", buffering=8192)
            elif kind == "write":
                if f:
                    f.write(payload)
            elif kind == "close":
                if f:
                    f.close()
                    f = None

    def open(self, path):
        self.q.put(("open", path))

    def write(self, line):
        self.q.put(("write", line))

    def close(self):
        self.q.put(("close", None))


class FlightState:
    def __init__(self, log_writer):
        self.log_writer = log_writer
        self.is_recording = False
        self.session = -1
        self.n_seen = 0
        self.n_bad_fd = 0
        self.n_bad_len = 0
        self.n_sentinel = 0
        self.n_written = 0
        self.radio_max_ms = 0.0
        self.radio_total_ms = 0.0
        self.loop_max_ms = 0.0
        self.loop_total_ms = 0.0
        self.send_max_ms = 0.0
        self.send_total_ms = 0.0
        self.recv_max_ms = 0.0
        self.recv_total_ms = 0.0
        self.write_max_ms = 0.0
        self.write_total_ms = 0.0
        self.n_loops = 0

    def start_log(self):
        self.session += 1
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = os.path.join(LOG_DIR, f"flight_{stamp}_{self.session:02d}.csv")
        self.log_writer.open(name)
        self.log_writer.write(HEADER)
        self.is_recording = True

    def stop_log(self):
        avg_radio = self.radio_total_ms / max(self.n_loops, 1)
        avg_loop = self.loop_total_ms / max(self.n_loops, 1)
        avg_send = self.send_total_ms / max(self.n_loops, 1)
        avg_recv = self.recv_total_ms / max(self.n_loops, 1)
        avg_write = self.write_total_ms / max(self.n_loops, 1)
        print(f"seen={self.n_seen} bad_fd={self.n_bad_fd} "
              f"bad_len={self.n_bad_len} sentinel={self.n_sentinel} "
              f"written={self.n_written} "
              f"radio_max_ms={self.radio_max_ms:.1f} radio_avg_ms={avg_radio:.1f} "
              f"send_max_ms={self.send_max_ms:.1f} send_avg_ms={avg_send:.1f} "
              f"recv_max_ms={self.recv_max_ms:.1f} recv_avg_ms={avg_recv:.1f} "
              f"write_max_ms={self.write_max_ms:.1f} write_avg_ms={avg_write:.1f} "
              f"loop_max_ms={self.loop_max_ms:.1f} loop_avg_ms={avg_loop:.1f}")
        self.log_writer.close()
        self.is_recording = False
        self.n_seen = self.n_bad_fd = self.n_bad_len = 0
        self.n_sentinel = self.n_written = 0
        self.radio_max_ms = self.radio_total_ms = 0.0
        self.loop_max_ms = self.loop_total_ms = 0.0
        self.send_max_ms = self.send_total_ms = 0.0
        self.recv_max_ms = self.recv_total_ms = 0.0
        self.write_max_ms = self.write_total_ms = 0.0
        self.n_loops = 0


def handle_telemetry_lines(lines, state, recording):
    for line in lines:
        state.n_seen += 1
        i = line.find("FD: ")
        if i < 0:
            state.n_bad_fd += 1
            continue

        vals = line[i + 4:].split()

        if len(vals) != N_VALUES:
            state.n_bad_len += 1
            continue

        if vals[0] == "-1.0000":
            state.n_sentinel += 1
            continue

        if recording:
            state.n_written += 1
            state.log_writer.write(f"{time.time():.4f}," + ",".join(vals) + "\n")


def control_loop(radio_receiver, bridge, state):
    loop_t0 = time.time()

    t0 = time.time()
    connection_lost, channel_data = radio_receiver.get_radio_data()
    radio_ms = (time.time() - t0) * 1000.0
    state.radio_max_ms = max(state.radio_max_ms, radio_ms)
    state.radio_total_ms += radio_ms
    state.n_loops += 1

    if connection_lost:
        time.sleep(0.1)
        return True

    radio = RadioData(channel_data)

    t0 = time.time()
    bridge.send_to_esp(radio)
    send_ms = (time.time() - t0) * 1000.0
    state.send_max_ms = max(state.send_max_ms, send_ms)
    state.send_total_ms += send_ms

    recording = radio.switch_B() and not radio.switch_D()

    if recording and not state.is_recording:
        state.start_log()

    if not recording and state.is_recording:
        state.stop_log()

    t0 = time.time()
    lines = bridge.receive_from_esp()
    recv_ms = (time.time() - t0) * 1000.0
    state.recv_max_ms = max(state.recv_max_ms, recv_ms)
    state.recv_total_ms += recv_ms

    t0 = time.time()
    handle_telemetry_lines(lines, state, recording)
    write_ms = (time.time() - t0) * 1000.0
    state.write_max_ms = max(state.write_max_ms, write_ms)
    state.write_total_ms += write_ms

    loop_ms = (time.time() - loop_t0) * 1000.0
    state.loop_max_ms = max(state.loop_max_ms, loop_ms)
    state.loop_total_ms += loop_ms

    return True


def main():
    radio_receiver = RC()
    bridge = EspBridge(serial_path="/dev/ttyUSB0", baud=500000)
    log_writer = LogWriter()
    state = FlightState(log_writer)

    keep_running = True
    while keep_running:
        loop_start = time.time()

        keep_running = control_loop(radio_receiver, bridge, state)

        elapsed = time.time() - loop_start
        sleep_time = LOOP_PERIOD - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)


main()

# import time
# import os
# import datetime

# from bzzz.read_sbus.radio_receiver import RC
# from bzzz.read_sbus.radioData import RadioData
# from bzzz.read_sbus.esp_bridge import EspBridge

# LOOP_RATE_HZ = 125
# LOOP_PERIOD = 1.0 / LOOP_RATE_HZ

# N_VALUES = 22

# LOG_DIR = os.path.expanduser("~/flight_logs")
# os.makedirs(LOG_DIR, exist_ok=True)

# HEADER = ("t_pi,qw,qx,qy,qz,wx,wy,wz,FL,FR,BL,BR,ML,MR,"
#           "J0,J1,J2,J3,J4,J5,J6,best,inject\n")

# def main():
#     radio_receiver = RC()
#     bridge = EspBridge(serial_path="/dev/ttyUSB0", baud=500000)

#     log_file = None
#     session = -1
#     n_seen = n_bad_fd = n_bad_len = n_sentinel = n_written = 0
#     t_radio_max = 0.0
#     t_radio_total = 0.0
#     n_radio_calls = 0

#     while True:
#         loop_start = time.time()

#         t0 = time.time()
#         connection_lost, channel_data = radio_receiver.get_radio_data()
#         t_radio = time.time() - t0
#         t_radio_max = max(t_radio_max, t_radio)
#         t_radio_total += t_radio
#         n_radio_calls += 1

#         if connection_lost:
#             time.sleep(0.1)
#             continue

#         radio = RadioData(channel_data)
#         bridge.send_to_esp(radio)

#         recording = radio.switch_B() and not radio.switch_D()

#         if recording and log_file is None:
#             session += 1
#             stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#             name = os.path.join(
#                 LOG_DIR,
#                 f"flight_{stamp}_{session:02d}.csv"
#             )
#             log_file = open(name, "w", buffering=1)
#             log_file.write(HEADER)

#         if not recording and log_file is not None:
#             print(f"seen={n_seen} bad_fd={n_bad_fd} bad_len={n_bad_len} "
#                   f"sentinel={n_sentinel} written={n_written} "
#                   f"radio_max_ms={t_radio_max*1000:.1f} "
#                   f"radio_avg_ms={(t_radio_total/max(n_radio_calls,1))*1000:.1f}")
#             log_file.close()
#             log_file = None
#             n_seen = n_bad_fd = n_bad_len = n_sentinel = n_written = 0
#             t_radio_max = 0.0
#             t_radio_total = 0.0
#             n_radio_calls = 0

#         lines = bridge.receive_from_esp()

#         for line in lines:
#             n_seen += 1
#             i = line.find("FD: ")
#             if i < 0:
#                 n_bad_fd += 1
#                 continue

#             vals = line[i + 4:].split()

#             if len(vals) != N_VALUES:
#                 n_bad_len += 1
#                 continue

#             if vals[0] == "-1.0000":
#                 n_sentinel += 1
#                 continue

#             if recording and log_file:
#                 n_written += 1
#                 log_file.write(
#                     f"{time.time():.4f}," + ",".join(vals) + "\n"
#                 )

#         elapsed = time.time() - loop_start
#         sleep_time = LOOP_PERIOD - elapsed
#         if sleep_time > 0:
#             time.sleep(sleep_time)


# main()