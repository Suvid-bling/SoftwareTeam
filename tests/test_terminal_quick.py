"""Quick test to verify the terminal fix works."""
import asyncio
import os
import sys
from asyncio.subprocess import PIPE, STDOUT

END_MARKER_VALUE = "\x18\x19\x1B\x18\n"

async def test():
    process = await asyncio.create_subprocess_exec(
        "bash", "--norc", "--noprofile",
        stdin=PIPE, stdout=PIPE, stderr=STDOUT,
        executable="bash", cwd=os.getcwd(),
    )
    
    # Send pwd + marker
    cmd = "pwd"
    process.stdin.write((cmd + "\n").encode())
    process.stdin.write((f"echo {END_MARKER_VALUE}" + "\n").encode())
    await process.stdin.drain()
    
    # Fixed read logic
    tmp = b""
    marker_bytes = END_MARKER_VALUE.rstrip("\n").encode()
    cmd_output = []
    
    try:
        while True:
            output = tmp + await asyncio.wait_for(process.stdout.read(1), timeout=5)
            if not output:
                continue
            if marker_bytes in output:
                decoded = output.decode(errors="ignore")
                ix = decoded.find(marker_bytes.decode())
                before = decoded[:ix]
                if before.strip():
                    cmd_output.append(before)
                print(f"MARKER FOUND! Output: {''.join(cmd_output)!r}")
                process.stdin.close()
                return
            *lines, tmp = output.splitlines(True)
            for line in lines:
                line = line.decode(errors="ignore")
                cmd_output.append(line)
                print(f"Line: {line!r}")
    except asyncio.TimeoutError:
        print(f"TIMEOUT! tmp={tmp!r}")
    
    process.stdin.close()

asyncio.run(test())
