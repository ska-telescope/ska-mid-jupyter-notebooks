import time
from typing import Any

from tango import DeviceProxy

from ska_mid_jupyter_notebooks.cluster.cluster import TangoCluster


class TangoDishCluster(TangoCluster):
    def __init__(
        self,
        dish_id: str,
        branch_name: str,
        dev_mode: bool,
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ):
        self.dish_id = dish_id
        namespace = get_dish_namespace(dish_id, branch_name, dev_mode)
        super().__init__(namespace, database_name, cluster_domain, db_port)

    def reset_dish(self):
        dish_proxy = self.device_manager_dp()
        print("aborting dish operation")
        dish_proxy.AbortCommands()
        while (str(dish_proxy.dishMode) != "dishMode.ABORTING") and (
            (str(dish_proxy.dishMode) != "dishMode.OPERATE")
        ):
            time.sleep(1)
        print("stowing dish")
        dish_proxy.SetStowMode()
        while str(dish_proxy.dishMode) != "dishMode.STOW":
            time.sleep(1)
        print("setting standbyLP mode")
        dish_proxy.SetStandbyLPMode()
        print(f"ska{self.dish_id}: {dish_proxy.Status()}")

    def device_manager_dp(self) -> Any:
        return DeviceProxy(f"{self.tango_host()}/mid-dish/dish-manager/{self.dish_id}")

    def print_component_states(self):
        d = self.device_manager_dp()
        print(f"{self.dish_id} ComponentStates: {d.GetComponentStates()}")
        print(f"{self.dish_id} DishMode: {d.dishMode}")


def get_dish_namespace(dish_id: str, branch_name: str, dev_mode: bool) -> str:
    if dev_mode:
        return f"ci-dish-lmc-{dish_id}-{branch_name}"
    return f"dish-lmc-{dish_id}"
