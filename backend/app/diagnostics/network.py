import ipaddress
import re
import socket
import time

from pydantic import BaseModel, Field, field_validator

HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
)


class NetworkRequest(BaseModel):
    hostname: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)
    timeout_seconds: float = Field(default=3, gt=0, le=10)

    @field_validator("hostname")
    @classmethod
    def host_valid(cls, v):
        v = v.strip()
        try:
            ipaddress.ip_address(v)
        except ValueError:
            if not HOST_RE.fullmatch(v):
                raise ValueError("Invalid hostname")
        return v


def _result(stage, start, ok, detail, next_step):
    return {
        "stage": stage,
        "status": "OK" if ok else "Error",
        "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        "detail": detail[:250],
        "next_step": next_step,
    }


def run_network(req: NetworkRequest):
    results = []
    addresses = []
    start = time.perf_counter()
    try:
        addresses = sorted(
            {x[4][0] for x in socket.getaddrinfo(req.hostname, None, type=socket.SOCK_STREAM)}
        )
        results.append(
            _result(
                "DNS",
                start,
                True,
                f"Resolved {len(addresses)} address(es)",
                "Continue with TCP check",
            )
        )
    except OSError as e:
        results.append(
            _result(
                "DNS", start, False, f"Resolution failed: {e}", "Verify hostname and DNS settings"
            )
        )
    start = time.perf_counter()
    try:
        with socket.create_connection((req.hostname, req.port), timeout=req.timeout_seconds):
            pass
        results.append(
            _result(
                "TCP",
                start,
                True,
                f"Connected to {req.hostname}:{req.port}",
                "Service is reachable",
            )
        )
    except OSError as e:
        results.append(
            _result(
                "TCP",
                start,
                False,
                f"Connection failed: {e}",
                "Verify port, firewall, route, and service status",
            )
        )
    return {"hostname": req.hostname, "port": req.port, "addresses": addresses, "results": results}


def demo_network(req):
    return {
        "hostname": req.hostname,
        "port": req.port,
        "addresses": ["203.0.113.10"],
        "results": [
            {
                "stage": "DNS",
                "status": "OK",
                "duration_ms": 2.1,
                "detail": "Demo resolution succeeded",
                "next_step": "Continue with TCP check",
            },
            {
                "stage": "TCP",
                "status": "OK",
                "duration_ms": 12.4,
                "detail": "Demo connection succeeded",
                "next_step": "Service is reachable",
            },
        ],
    }
