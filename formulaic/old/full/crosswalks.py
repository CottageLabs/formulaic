class APCCharges(Transformer):
    def transform(self, max_apc_data):
        res = []
        for apc_charge in max_apc_data:
             res.append(str(apc_charge.get("apc_max")) + " " + apc_charge.get("apc_currency"))
        return res

class PreservationService(Transformer):
    def transform(self, preservation_data):
        dap = deepcopy(preservation_data.get("service", []))
        if "national_library" in dap: dap.remove("national_library")
        if "other" in dap:
            dap.remove("other")
            # dap.append(forminfo.get("preservation_service_other"))
        if "none" in dap: dap.remove("none")
        return ", ".join(dap)

class JournalCSVCrosswalk(Transform):
    source = JournalStruct
    target = JournalCSVStruct

    mapping = [
        (source.AlternativeTitle, target.AlternativeTitle, None),
        (source.JournalBibJSON.APC.MaxAPC, target.get("apc_charges"), APCCharges),
        (source.JournalBibJSON.APC.URL, target.get("apc_url"), None)
        (source.JournalBibJSON.Preservation, target.get("preservation_service"), preservation_service)
    ]