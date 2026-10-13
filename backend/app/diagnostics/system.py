import hashlib
import platform
import socket
import time
from datetime import UTC, datetime

import psutil


def _metric(name, function):
    started = time.perf_counter()

    try:
        return {
            "name": name,
            "status": "OK",
            "value": function(),
            "error": None,
            "collected_at": datetime.now(UTC).isoformat(),
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "name": name,
            "status": "Unsupported",
            "value": None,
            "error": str(exc)[:200],
            "collected_at": datetime.now(UTC).isoformat(),
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def _collect_memory():
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "available": memory.available,
    }


def _collect_disks():
    disks = []

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except OSError:
            continue

        disks.append(
            {
                "mountpoint": partition.mountpoint,
                "total_bytes": usage.total,
                "free_bytes": usage.free,
            }
        )

    return disks


def collect_system(show_hostname=True):
    hostname = socket.gethostname()

    metrics = [
        _metric("cpu_percent", lambda: psutil.cpu_percent(interval=0.05)),
        _metric("memory", _collect_memory),
        _metric("disks", _collect_disks),
    ]

    values = {metric["name"]: metric["value"] for metric in metrics}
    memory = values.get("memory") or {}

    return {
        "device_id": hashlib.sha256(hostname.encode("utf-8")).hexdigest()[:16],
        "hostname": hostname if show_hostname else None,
        "os_name": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "uptime_seconds": max(0, int(time.time() - psutil.boot_time())),
        "cpu_percent": values.get("cpu_percent"),
        "memory_total_bytes": memory.get("total"),
        "memory_available_bytes": memory.get("available"),
        "disks": values.get("disks"),
        "collected_at": datetime.now(UTC).isoformat(),
        "results": metrics,
    }


def demo_system():
    collected_at = datetime.now(UTC).isoformat()

    return {
        "device_id": "demo-device",
        "hostname": "demo-workstation",
        "os_name": "Linux",
        "os_version": "Demo",
        "architecture": "x86_64",
        "uptime_seconds": 86400,
        "cpu_percent": 18.5,
        "memory_total_bytes": 17179869184,
        "memory_available_bytes": 9663676416,
        "disks": [
            {
                "mountpoint": "/",
                "total_bytes": 536870912000,
                "free_bytes": 322122547200,
            }
        ],
        "collected_at": collected_at,
        "results": [
            {
                "name": "demo",
                "status": "OK",
                "value": "sample",
                "error": None,
                "collected_at": collected_at,
                "duration_ms": 0.1,
            }
        ],
    }
