from typing import Any, Literal, Set, TypedDict

from ska_oso_pdm.entities.dish.dish_configuration import (
    DishConfiguration as sb_dish_configuration,
)
from ska_tmc_cdm.messages.central_node.common import DishAllocation
from ska_tmc_cdm.messages.subarray_node.configure.core import (
    DishConfiguration,
    PointingConfiguration,
)

from ska_mid_jupyter_scripting.obsconfig.target_spec import TargetSpecs

ReceptorName = Literal["SKA001", "SKA002"]


class ResourceConfiguration(TypedDict):
    receptors: list[ReceptorName]


class Dishes(TargetSpecs):
    @property
    def dishes(self) -> list[ReceptorName]:
        """
        Returns list of dishes
        :return: list of dishes
        """
        return list(
            {
                dish
                for target in self.target_specs.values()
                for dish in target.dish_ids
            }
        )

    @property
    def dish_allocation(self):
        """
        Returns dish allocation
        :return: dish allocation object
        """
        adapted_dishes = [dish + "" for dish in self.dishes]
        return DishAllocation(adapted_dishes)

    @property
    def resource_configuration(self):
        """
        Returns resource configuration
        :return: resource configuration
        """
        adapted_receptors = [dish + "" for dish in self.dishes]
        return ResourceConfiguration(receptors=adapted_receptors)

    def get_pointing_configuration(self, target_id: str | None = None):
        """
        Returns pointing configuration
        :param target_id: target id
        :return: pointing configuration
        """
        return PointingConfiguration(self.get_target_spec(target_id).target)

    def get_dish_configuration(self, target_id: str | None = None):
        """
        Returns dish configuration
        :param target_id: target id
        :return: dish configuration object
        """
        return DishConfiguration(self.get_target_spec(target_id).band)

    def get_dish_configuration_sb(self, target_id: str | None = None):
        """
        Returns dish configuration
        :param target_id: target id
        :return: dish configuration object
        """
        return sb_dish_configuration(
            dish_configuration_id="dish config 123",
            receiver_band=self.get_target_spec(target_id).band,
        )
