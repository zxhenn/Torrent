# This file helps open Windows Firewall ports for tracker and peer connections.
"""Windows Firewall helpers for ChunkShare LAN demos."""

from __future__ import annotations

import base64
import os
import subprocess

TRACKER_PORT_RANGE = "8000-8099"
PEER_PORT_RANGE = "9000-9100"
FIREWALL_PROFILE = "Any"


# This function returns firewall information for the dashboard.
def firewall_summary() -> dict:
    """Return dashboard-friendly firewall setup information."""
    return {
        "supported": os.name == "nt",
        "requires_admin": True,
        "tracker_ports": TRACKER_PORT_RANGE,
        "peer_ports": PEER_PORT_RANGE,
        "profile": FIREWALL_PROFILE,
        "message": (
            "Click Firewall once on Windows if other laptops cannot reach this app."
            if os.name == "nt"
            else "Firewall setup is only automated for Windows."
        ),
    }


# This function asks Windows to add firewall rules for ChunkShare.
def request_windows_firewall_rules() -> dict:
    """Ask Windows for admin permission and add ChunkShare inbound TCP rules."""
    if os.name != "nt":
        return {
            "ok": False,
            "supported": False,
            "message": "Automatic firewall setup is only available on Windows.",
        }

    encoded_script = _encode_powershell(_firewall_rule_script())
    launch_command = (
        "$process = Start-Process -FilePath powershell "
        "-ArgumentList "
        f"'-NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded_script}' "
        "-Verb RunAs -WindowStyle Hidden -PassThru -Wait; "
        "exit $process.ExitCode"
    )

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                launch_command,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "supported": True,
            "message": "Firewall permission timed out. Try again and approve the Windows prompt.",
        }

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        return {
            "ok": False,
            "supported": True,
            "message": detail or "Firewall setup was cancelled or blocked by Windows.",
        }

    return {
        "ok": True,
        "supported": True,
        "tracker_ports": TRACKER_PORT_RANGE,
        "peer_ports": PEER_PORT_RANGE,
        "message": (
            "Firewall rules requested. If you approved the Windows prompt, "
            "other laptops can use tracker ports 8000-8099 and peer ports 9000-9100."
        ),
    }


# This function encodes a PowerShell script so Windows can run it safely.
def _encode_powershell(script: str) -> str:
    """Encode a PowerShell script for the -EncodedCommand argument."""
    return base64.b64encode(script.encode("utf-16le")).decode("ascii")


# This function builds the PowerShell commands that create firewall rules.
def _firewall_rule_script() -> str:
    """Return the elevated PowerShell script that creates firewall rules."""
    return f"""
$ErrorActionPreference = "Stop"
$rules = @(
    @{{ Name = "ChunkShare Tracker TCP"; Ports = "{TRACKER_PORT_RANGE}" }},
    @{{ Name = "ChunkShare Peer TCP"; Ports = "{PEER_PORT_RANGE}" }}
)

foreach ($rule in $rules) {{
    Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue |
        Remove-NetFirewallRule
    New-NetFirewallRule `
        -DisplayName $rule.Name `
        -Direction Inbound `
        -Action Allow `
        -Protocol TCP `
        -LocalPort $rule.Ports `
        -Profile {FIREWALL_PROFILE} | Out-Null
}}
"""
