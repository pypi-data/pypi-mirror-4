#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

from . import (
    Status,
    modsde,
    backlight,
    battery,
)
from .mail import (
    thunderbird,
)

if True:
    status = Status(standalone=True)
else:
    process = subprocess.Popen(["i3status", "-c", "~/.i3/status"], stdout=subprocess.PIPE, universal_newlines=True)
    status = Status(input_stream=process.stdout)
"""
status.register("clock",
    format="%a %-d %b %X",)

status.register("load")

status.register("alsa",
    format="♪{volume}")

status.register("runwatch",
    name="DHCP",
    path="/var/run/dhclient*.pid",)

status.register(backlight,
    format="{brightness}/{max_brightness}",)

status.register("temp",
    format="{temp} °C")

status.register("regex", 
    regex="speed:\s+([0-9]+)\nlevel:\s+([a-zA-Z0-9]+)",
    file="/proc/acpi/ibm/fan",
    format="{0}",)
"""
status.register(battery,
    format="{status}/{consumption:.2f}W {percentage:.2f}% [{percentage_design:.2f}%] {remaining_hm}",
    alert=True,
    alert_percentage=8,)
"""
status.register(False, #"mail",
    backends=[thunderbird.Thunderbird()],
    format="@{unread}",
    format_plural="@{unread}",)

status.register(modsde,
    username="csde_rats",
    password="kifferstyle",
    format="M{unread}",
    offset=636,)

status.register(False, #"disk",
    path="/",
    format="{percentage_used}% → {used}/{total}G ({avail}G avail)",)

status.register("disk",
    path="/",
    format="{used}/{total}G [{avail}G]",)
"""
status.run()
