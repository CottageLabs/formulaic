from typing import Union, Any

from formulaic.core import Structure
from formulaic.objects import FormulaicObject, FormulaicMixin


class Serialiser:
    def __init__(self, *args, **kwargs):
        pass

    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        """
        Convert data from the internal formulaic format to a serialisation-specific representation.

        This gives the serialiser the opportunity to have an intermediate, non-string representation of the data.

        For example, converting a formulaic object to an XML document, an intermediate representation might be an
        ElementTree Element, which can then be serialised to a string if desired

        :param data:
        :param struct:
        :param kwargs:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def representation_to_string(self, representation, **kwargs):
        """
        Take the intermediate representation and convert it to a string.

        :param representation:
        :param kwargs:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def data_to_string(self, data: Union[dict, FormulaicObject, FormulaicMixin], struct: Structure = None, **kwargs):
        """
        Convert data from the internal formulaic format to a string representation.

        By default, this method will call to_representation and then serialise the result

        :param data:
        :param struct:
        :param kwargs:
        :return:
        """
        repr = self.data_to_representation(data, struct, **kwargs)
        return self.representation_to_string(repr, **kwargs)

    def representation_to_data(self, representation, struct:Structure, **kwargs) -> Union[dict, FormulaicObject, FormulaicMixin]:
        """
        Take the intermediate representation and convert it back to the internal formulaic format.

        :param representation:
        :param struct:
        :param kwargs:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def string_to_representation(self, string:str, struct:Structure, **kwargs) -> Any:
        """
        Take a string representation of the data and convert it to the intermediate representation.

        :param string:
        :param struct:
        :param kwargs:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def string_to_data(self, string:str, struct:Structure, **kwargs) -> Union[dict, FormulaicObject, FormulaicMixin]:
        """
        Convert a string representation of the data back to the internal formulaic format.

        :param string:
        :param struct:
        :param kwargs:
        :return:
        """
        repr = self.string_to_representation(string, struct, **kwargs)
        return self.representation_to_data(repr, struct, **kwargs)