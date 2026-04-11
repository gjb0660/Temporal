from __future__ import annotations

import argparse
import csv
import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QCoreApplication

from temporal.app.fake_runtime import fake_app_bridge


def _process_rss_mb() -> float:
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        psapi = ctypes.WinDLL("Psapi.dll")
        kernel32 = ctypes.WinDLL("Kernel32.dll")
        get_process_memory_info = psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
            wintypes.DWORD,
        ]
        get_process_memory_info.restype = wintypes.BOOL
        get_current_process = kernel32.GetCurrentProcess
        get_current_process.restype = wintypes.HANDLE

        counters = PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
        process = get_current_process()
        ok = get_process_memory_info(process, ctypes.byref(counters), counters.cb)
        if not ok:
            return 0.0
        return float(counters.WorkingSetSize) / (1024.0 * 1024.0)
    except Exception:
        return 0.0


def _build_ssl_message(sample: int) -> dict[str, Any]:
    return {
        "timeStamp": sample,
        "src": [
            {"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.92},
            {"x": 0.0, "y": 1.0, "z": 0.0, "E": 0.77},
            {"x": 0.0, "y": 0.0, "z": 1.0, "E": 0.55},
        ],
    }


def _build_audio_chunk() -> bytes:
    return b"\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00"


@dataclass
class SharedState:
    produced_ssl: int = 0
    produced_audio_chunks: int = 0
    producer_errors: int = 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Potential ingress 10-minute stress run")
    parser.add_argument("--duration-sec", type=int, default=600)
    parser.add_argument("--ssl-rate-hz", type=int, default=500)
    parser.add_argument("--log-interval-sec", type=float, default=1.0)
    parser.add_argument("--out-dir", type=Path, default=Path(".tmp/perf"))
    args = parser.parse_args()

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QCoreApplication.instance() or QCoreApplication([])
    bridge = fake_app_bridge()
    bridge.setPotentialsEnabled(True)
    bridge.startStreams()
    bridge._on_sst(
        {
            "timeStamp": 0,
            "src": [
                {"id": 101, "x": 1.0, "y": 0.0, "z": 0.0},
                {"id": 202, "x": 0.0, "y": 1.0, "z": 0.0},
                {"id": 303, "x": -1.0, "y": 0.0, "z": 0.0},
                {"id": 404, "x": 0.0, "y": -1.0, "z": 0.0},
            ],
        }
    )

    start_monotonic = time.monotonic()
    end_monotonic = start_monotonic + float(args.duration_sec)
    shared = SharedState()
    lock = threading.Lock()
    stop_event = threading.Event()
    sample_counter = 1
    audio_chunk = _build_audio_chunk()

    def _producer() -> None:
        nonlocal sample_counter
        target_period = 1.0 / float(max(1, args.ssl_rate_hz))
        next_tick = time.perf_counter()
        audio_toggle = False
        while not stop_event.is_set():
            try:
                current_sample = sample_counter
                sample_counter += 1
                bridge._on_ssl(_build_ssl_message(current_sample))
                if audio_toggle:
                    bridge._on_sep_audio(audio_chunk)
                else:
                    bridge._on_pf_audio(audio_chunk)
                audio_toggle = not audio_toggle
                with lock:
                    shared.produced_ssl += 1
                    shared.produced_audio_chunks += 1
            except Exception:
                with lock:
                    shared.producer_errors += 1

            next_tick += target_period
            sleep_s = next_tick - time.perf_counter()
            if sleep_s > 0:
                time.sleep(sleep_s)
            else:
                next_tick = time.perf_counter()

    producer = threading.Thread(target=_producer, name="ssl-producer", daemon=True)
    producer.start()

    run_tag = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"potential_stress_{run_tag}.csv"
    summary_path = out_dir / f"potential_stress_{run_tag}.summary.json"

    headers = [
        "t_sec",
        "rss_mb",
        "ssl_queue_depth",
        "ssl_blocked_count",
        "ssl_last_batch_size",
        "ssl_last_batch_latency_ms",
        "runtime_last_ssl_sample",
        "potential_positions_count",
        "potential_trail_len",
        "potential_history_len",
        "produced_ssl",
        "produced_audio_chunks",
        "producer_errors",
    ]

    rows: list[dict[str, float | int]] = []
    next_log_at = start_monotonic
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        while time.monotonic() < end_monotonic:
            app.processEvents()
            now = time.monotonic()
            if now >= next_log_at:
                with lock:
                    produced_ssl = int(shared.produced_ssl)
                    produced_audio = int(shared.produced_audio_chunks)
                    producer_errors = int(shared.producer_errors)
                row = {
                    "t_sec": int(now - start_monotonic),
                    "rss_mb": round(_process_rss_mb(), 3),
                    "ssl_queue_depth": int(bridge.sslIngressQueueDepth),  # pyright: ignore[reportArgumentType]
                    "ssl_blocked_count": int(bridge.sslIngressBlockedCount),  # pyright: ignore[reportArgumentType]
                    "ssl_last_batch_size": int(bridge.sslIngressLastBatchSize),  # pyright: ignore[reportArgumentType]
                    "ssl_last_batch_latency_ms": round(
                        float(bridge.sslIngressLastBatchLatencyMs),  # pyright: ignore[reportArgumentType]
                        3,
                    ),
                    "runtime_last_ssl_sample": int(bridge._runtime_last_ssl_sample or 0),
                    "potential_positions_count": int(bridge.potentialPositionsModel.count),
                    "potential_trail_len": int(len(bridge._runtime_potential_trail)),
                    "potential_history_len": int(len(bridge._runtime_potential_history)),
                    "produced_ssl": produced_ssl,
                    "produced_audio_chunks": produced_audio,
                    "producer_errors": producer_errors,
                }
                writer.writerow(row)
                rows.append(row)
                f.flush()
                next_log_at = now + float(args.log_interval_sec)
            time.sleep(0.002)

    rss_values = [float(row["rss_mb"]) for row in rows if float(row["rss_mb"]) > 0.0]
    queue_values = [int(row["ssl_queue_depth"]) for row in rows]
    blocked_values = [int(row["ssl_blocked_count"]) for row in rows]
    batch_latency_values = [float(row["ssl_last_batch_latency_ms"]) for row in rows]
    tail_start = max(0, len(rows) - 120)
    tail = rows[tail_start:] if rows else []
    summary = {
        "duration_sec": int(args.duration_sec),
        "ssl_rate_hz": int(args.ssl_rate_hz),
        "row_count": len(rows),
        "csv_path": str(csv_path),
        "rss_mb_start": rss_values[0] if rss_values else 0.0,
        "rss_mb_peak": max(rss_values) if rss_values else 0.0,
        "rss_mb_end": rss_values[-1] if rss_values else 0.0,
        "rss_mb_tail_min": min(float(row["rss_mb"]) for row in tail) if tail else 0.0,
        "rss_mb_tail_max": max(float(row["rss_mb"]) for row in tail) if tail else 0.0,
        "queue_depth_peak": max(queue_values) if queue_values else 0,
        "queue_depth_end": queue_values[-1] if queue_values else 0,
        "blocked_count_end": blocked_values[-1] if blocked_values else 0,
        "batch_latency_ms_peak": max(batch_latency_values) if batch_latency_values else 0.0,
        "runtime_last_ssl_sample": int(rows[-1]["runtime_last_ssl_sample"]) if rows else 0,
        "produced_ssl_total": int(shared.produced_ssl),
        "produced_audio_chunks_total": int(shared.produced_audio_chunks),
        "producer_errors_total": int(shared.producer_errors),
        "potential_trail_len_end": int(rows[-1]["potential_trail_len"]) if rows else 0,
        "potential_history_len_end": int(rows[-1]["potential_history_len"]) if rows else 0,
        "potential_positions_count_end": int(rows[-1]["potential_positions_count"]) if rows else 0,
    }
    stop_event.set()
    bridge._set_ssl_ingress_accepting(False)
    producer.join(timeout=5.0)
    summary["producer_alive_after_stop"] = producer.is_alive()
    bridge.stopStreams()
    app.processEvents()
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
