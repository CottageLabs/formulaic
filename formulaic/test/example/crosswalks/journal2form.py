from typing import Optional, Any

from formulaic.core import Structure
from formulaic.objects import FormulaicMixin, FormulaicObject
from formulaic.crosswalk.core import Crosswalk, CrosswalkRule
from formulaic.crosswalk.core import BooleanString

from formulaic.test.example.structs import JournalStructure
from formulaic.test.example.forms_old import PublicApplicationForm


class APCChargesCrosswalkRule(CrosswalkRule):
    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        fo:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        if value is None:
            return None

        result = []
        for apc_record in value:
            currency = apc_record.get("currency")
            price = apc_record.get("price")

            result.append({
                "apc_currency": currency,
                "apc_max": price
            })

        return result if len(result) > 0 else None


class Journal2Form(Crosswalk):
    source = JournalStructure()
    target = PublicApplicationForm()

    mapping = [
        (source.bibjson.boai, target.boai, BooleanString(true="y", false="n")),
        (source.bibjson.ref.oa_statement, target.oa_statement_url),
        (source.bibjson.apc.has_apc, target.apc, BooleanString(true="y", false="n")),
        (source.bibjson.apc.max, target.apc_charges, APCChargesCrosswalkRule())
    ]