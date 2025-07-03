import base64
import json
import re


def parse_key(key):
    if key.startswith("ss://"):
        # ...existing code...
        return {"type": "ss", "raw": key}
    if key.startswith("trojan://"):
        # ...existing code...
        return {"type": "trojan", "raw": key}
    if key.startswith("vless://"):
        # ...existing code...
        return {"type": "vless", "raw": key}
    return None


def generate_xray_config(config):
    # Minimal config for xray-core, based on type
    if config["type"] == "ss":
        # ...parse and generate config...
        return json.dumps(
            {
                "inbounds": [
                    {
                        "port": 1080,
                        "protocol": "socks",
                        "settings": {"auth": "noauth"},
                    }
                ],
                "outbounds": [{"protocol": "shadowsocks", "settings": {}}],
            }
        )
    if config["type"] == "trojan":
        # ...parse and generate config...
        return json.dumps(
            {
                "inbounds": [
                    {
                        "port": 1080,
                        "protocol": "socks",
                        "settings": {"auth": "noauth"},
                    }
                ],
                "outbounds": [{"protocol": "trojan", "settings": {}}],
            }
        )
    if config["type"] == "vless":
        # ...parse and generate config...
        return json.dumps(
            {
                "inbounds": [
                    {
                        "port": 1080,
                        "protocol": "socks",
                        "settings": {"auth": "noauth"},
                    }
                ],
                "outbounds": [{"protocol": "vless", "settings": {}}],
            }
        )
    return "{}"