# pylint: disable=C,R
import subprocess


def get_tango_host(ns: str) -> str:
    cmd = (
        f"kubectl -n {ns}"
        + " get svc databaseds-tango-base --output jsonpath='{.status.loadBalancer.ingress[0].ip}'"
    )
    res = subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=False)
    ip = res.stdout.decode().replace("'", "")
    tango_host = f"{ip}:10000"
    return tango_host
