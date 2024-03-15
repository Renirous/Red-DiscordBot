from typing import Tuple

__all__ = ["BaseDriver"]


class BaseDriver:
    def __init__(self, cog_name):
        self.cog_name = cog_name
        self.unique_cog_identifier = None  # This is set by Config's init method

    async def get(self, *identifiers: Tuple[str]):
        """
        Finds the value indicate by the given identifiers.

        :param identifiers:
            A list of identifiers that correspond to nested dict accesses.
        :return:
            Stored value.
        """
        raise NotImplementedError

    def get_config_details(self):
        """
        Asks users for additional configuration information necessary
        to use this config driver.

        :return:
            Dict of configuration details.
        """
        raise NotImplementedError

    async def set(self, *identifiers: Tuple[str], value=None):
        """
        Sets the value of the key indicated by the given identifiers.

        :param identifiers:
            A list of identifiers that correspond to nested dict accesses.
        :param value:
            Any JSON serializable python object.
        """
        raise NotImplementedError
