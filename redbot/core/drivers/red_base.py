from typing import Tuple

__all__ = ["BaseDriver", "IdentifierData"]


class IdentifierData:
    def __init__(self, uuid: str, category: str, primary_key: Tuple[str], identifiers: Tuple[str]):
        self._uuid = uuid
        self._category = category
        self._primary_key = primary_key
        self._identifiers = identifiers

    @property
    def uuid(self):
        return self._uuid

    @property
    def category(self):
        return self._category

    @property
    def primary_key(self):
        return self._primary_key

    @property
    def identifiers(self):
        return self._identifiers

    def __repr__(self):
        return (
            f"<IdentifierData uuid={self.uuid} category={self.category} primary_key={self.primary_key}"
            f" identifiers={self.identifiers}>"
        )

    def add_identifier(self, *identifier: str) -> "IdentifierData":
        if not all(isinstance(i, str) for i in identifier):
            raise ValueError("Identifiers must be strings.")

        return IdentifierData(
            self.uuid, self.category, self.primary_key, self.identifiers + identifier
        )

    def to_tuple(self):
        return tuple(
            item
            for item in (self.uuid, self.category, *self.primary_key, *self.identifiers)
            if len(item) > 0
        )


class BaseDriver:
    def __init__(self, cog_name, identifier):
        self.cog_name = cog_name
        self.unique_cog_identifier = identifier

    async def get(self, identifier_data: IdentifierData):
        """
        Finds the value indicate by the given identifiers.

        Parameters
        ----------
        identifier_data

        Returns
        -------
        Any
            Stored value.
        """
        raise NotImplementedError

    def get_config_details(self):
        """
        Asks users for additional configuration information necessary
        to use this config driver.

        Returns
        -------
            Dict of configuration details.
        """
        raise NotImplementedError

    async def set(self, identifier_data: IdentifierData, value=None):
        """
        Sets the value of the key indicated by the given identifiers.

        Parameters
        ----------
        identifier_data
        value
            Any JSON serializable python object.
        """
        raise NotImplementedError

    async def clear(self, identifier_data: IdentifierData):
        """
        Clears out the value specified by the given identifiers.

        Equivalent to using ``del`` on a dict.

        Parameters
        ----------
        identifier_data
        """
        raise NotImplementedError
