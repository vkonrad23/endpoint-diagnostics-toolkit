import hashlib
import platform
import socket
import time
from datetime import datetime, timezone
import psutil


def _metric(name, fn):
    started = time.perf_counter()
    try:
        return {
            "name": name,
            "status": "OK",
            "value": fn(),
            "error": None,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "name": name,
            "status": "Unsupported",
            "value": None,
            "error": str(exc)[:200],
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def collect_system(show_hostname=True):
    host = socket.gethostname()
    metrics = [
        _metric("cpu_percent", lambda: psutil.cpu_percent(interval=0.05)),
        _metric(
            "memory",
            lambda: {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
            },
        ),
        _metric(
            "disks",
            lambda: [
                {
                    "mountpoint": p.mountpoint,
                    "total_bytes": psutil.disk_usage(p.mountpoint).total,
                    "free_bytes": psutil.disk_usage(p.mountpoint).free,
                }
                for p in psutil.disk_partitions(all=False)
            ],
        ),
    ]
    vals = {m["name"]: m["value"] for m in metrics}
    mem = vals.get("memory") or {}
    return {
        "device_id": hashlib.sha256(host.encode()).hexdigest()[:16],
        "hostname": host if show_hostname else None,
        "os_name": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "uptime_seconds": max(0, int(time.time() - psutil.boot_time())),
        "cpu_percent": vals.get("cpu_percent"),
        "memory_total_bytes": mem.get("total"),
        "memory_available_bytes": mem.get("available"),
        "disks": vals.get("disks"),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "results": metrics,
    }


def demo_system():
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
        "disks": [{"mountpoint": "/", "total_bytes": 536870912000, "free_bytes": 322122547200}],
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "results": [
            {
                "name": "demo",
                "status": "OK",
                "value": "sample",
                "error": None,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "duration_ms": 0.1,
            }
        ],
    }
