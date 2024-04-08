import os
from typing import Literal, TypedDict

from tango import DeviceProxy


class Env(TypedDict):
    namespace: str
    telescope: str | None
    database_name: str
    ingress_name: str
    tango_host: str
    cluster_domain: str


env = Env(
    namespace="",
    telescope="",
    database_name="",
    ingress_name="",
    tango_host="",
    cluster_domain="",
)


def smoke_test_cluster() -> int:
    """Smoke test cluster by pinging Database"""
    return DeviceProxy("sys/database/2").ping()


def set_cluster(
    namespace: str = "staging",
    telescope: str | None = "mid",
    database_name: str = "tango-databaseds",
    facility: Literal["stfc", "itf"] = "itf",
    db_port: int | None = 10000,
    polling: bool = False,
) -> int:
    """
    Set the cluster environment variables
    :param job_id: job id
    :param namespace: namespace
    :param telescope: telescope
    :param database_name: database name
    :param facility: facility
    :param db_port: database port
    :param polling: use polling
    :return: result of smoke test
    """
    cluster_domain = {
        "stfc": "cluster.local",
        "itf": "miditf.internal.skao.int",
    }.get(facility)
    assert cluster_domain
    ingress_name = f"k8s.{cluster_domain}"
    env["database_name"] = database_name
    env["namespace"] = namespace
    env["telescope"] = telescope
    env["cluster_domain"] = cluster_domain
    env["ingress_name"] = ingress_name
    env["tango_host"] = (
        f"{database_name}.{namespace}.svc.{cluster_domain}:{db_port}"
    )
    os.environ["TANGO_HOST"] = env["tango_host"]
    if polling:
        os.environ["USE_POLLING"] = "True"
    return smoke_test_cluster()
