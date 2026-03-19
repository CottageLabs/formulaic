from formulaic.coerce.coerce import Unicode
from formulaic.core import Field, Structure, OPTIONAL, SINGLE, REQUIRED, REPEATABLE
from formulaic.serialise.form.core import FormFieldCapability, CompoundFieldCapability, FieldsetCapability, \
    FormCapability, FormSerialiser, data_to_kv
from formulaic.validate.validate import RequiredValue, IsURL
from formulaic.serialise.form.controls import Radio, TextInput, Select, NumberInput


####################################
## DOAJ-specific form field capabilities

class DOAJFormFieldCapability(FormFieldCapability):
    long_help = None
    short_help = None
    doaj_criteria = None
    hint = None
    diff_table_context = None


#####################################
## DOAJ-specific validators

class RequiredValueDOAJ(RequiredValue):
    def html_attrs(self, attrs):
        attrs["data-parsley-requiredvalue"] = self.required_value


#######################################
#### FIELD DEFINITIONS
#######################################

###########################
## BOAI

class BOAIFormCapability(DOAJFormFieldCapability):
    label = "Does the journal have a BOAI-compliant open access policy?"
    control_class = Radio
    options = [
        {"value": "y", "label": "Yes"},
        {"value": "n", "label": "No"},
        {"value": "u", "label": "Unknown"}
    ]

    long_help = "The journal must have a BOAI-compliant open access policy, which is defined as <a href='https://doaj.org/faq#boai' target='_blank'>here</a>."
    short_help = "The journal must have a BOAI-compliant open access policy, which is defined as <a href='https://doaj.org/faq#boai' target='_blank'>here</a>."
    doaj_criteria = "You must answer 'Yes'"
    hint = "This is a required field.  If you are unsure, please select 'Unknown'.  If you select 'No', then you will be asked to provide an explanation."
    diff_table_context = "This field is required for all journals that are <a href='https://doaj.org/doaj?func=searchAdvanced&mode=full' target='_blank'>in DOAJ</a> and <a href='https://doaj.org/doaj?func=searchAdvanced&mode=full&filter=oa' target='_blank'>in full</a>."

class BOAI(Field):
    name = "boai"
    coerce = [Unicode()]
    allow_none = False
    validators = [RequiredValueDOAJ("y")]
    capabilities = (BOAIFormCapability(),)

class BOAIAdmin(BOAI):
    validators = []

class BOAIEditor(BOAI):
    validators = []

    class BOAIEditorCapability(BOAIFormCapability):
        disabled = True

    capabilities = (BOAIFormCapability(),)

class BOAIAssEd(BOAI):
    validators = []

    class BOAIAssEdCapability(BOAIFormCapability):
        disabled = True

    capabilities = (BOAIFormCapability(),)

## /BOAI
#############################

#############################
## OA Statement URL

class OAStatementURLFormCapability(DOAJFormFieldCapability):
    label = "The journal website must display its open access statement. Where can we find this information?"
    control_class = TextInput
    placeholder = "https://www.my-journal.com/open-access"
    js = [
        "trim_whitespace",
        "clickable_url"
    ]
    attributes = {
        "type": "url"
    }

    long_help = ["Here is an example of a suitable Open Access "
                 "statement that meets our criteria: <blockquote>This"
                 " is an open access journal, which means that all "
                 "content is freely available without charge to the "
                 "user or his/her institution. Users are allowed to "
                 "read, download, copy, distribute, print, search, or"
                 " link to the full texts of the articles, or use "
                 "them for any other lawful purpose, without asking "
                 "prior permission from the publisher or the author. "
                 "This is in accordance with the BOAI definition of "
                 "open access.</blockquote>"]
    short_help = "Link to the journal’s open access statement",

class OAStatementURL(Field):
    name = "oa_statement_url"
    coerce = [Unicode()]
    validators = [IsURL()]
    capabilities = (OAStatementURLFormCapability(),)

## / OA Statement URL
#############################

#################################
## APC Compound Field

## APC Yes/No Field
class APC(Field):
    name = "apc"
    coerce = [Unicode()]
    allow_none = False

    class APCFormCapability(DOAJFormFieldCapability):
        label = "Does the journal charge fees for publishing an article (APCs)?"
        control_class = Radio
        options = [
            {"value": "y", "label": "Yes"},
            {"value": "n", "label": "No"}
        ]

        long_help = ["Publication fees are sometimes called "
                     "article processing charges (APCs). You should answer"
                     " Yes if any fee is required from the author for "
                     "publishing their paper."]
        doaj_criteria = "You must tell us about any APCs"

    capabilities = (APCFormCapability(),)

## APC Currency Field
class APCCurrency(Field):
    class APCCurrencyFormCapability(DOAJFormFieldCapability):
        label = "What is the currency of the APC?"
        control_class = Select
        options = lambda x: currency_list()
        placeholder = "Currency"
        default = ""
        js = ["select"]
        attributes = {
            "class": "input-xlarge"
        }

    name = "apc_currency"
    coerce = [Unicode()]
    validate = [] #[RequiredIf("apc", "y")],  # CurrentISOCurrency
    capabilities = (APCCurrencyFormCapability(),)

## APC Max Valuue Field
class APCMax(Field):
    class APCMaxFormCapability(DOAJFormFieldCapability):
        label = "What is the maximum APC charged by this journal?"
        control_class = NumberInput
        attributes = {
            "min": "1"
        }

    name = "apc_max"
    coerce = [int]
    validate = [] #[RequiredIf("apc", "y")]
    capabilities = (APCMaxFormCapability(),)

## APC Compound Field Container

class APCCharges(Structure):
    class APCChargesCapability(CompoundFieldCapability):
        label = "Highest fee charged"
        repeatable = {
            "minimum": 1,
            "initial": 5
        }
        conditional = [
            {"field": "apc", "value": "y"}
        ]
        js = ["multiple_field"]
        order = ["apc_currency", "apc_max"]

    name_ = "apc_charges"
    capabilities_ = (APCChargesCapability(),)

    apc_currency = APCCurrency(OPTIONAL, SINGLE)
    apc_max = APCMax(OPTIONAL, SINGLE)

## /APC Compound Field
##############################

#######################################
#### FIELDSETS
#######################################

class BasicCompliance(Structure):
    class BasicComplianceCapability(FieldsetCapability):
        label = "Open access compliance"
        order = ["boai", "oa_statement_url"]

    name_ = "basic_compliance"
    capabilities_ = (BasicComplianceCapability(),)

    boai = BOAI(REQUIRED, SINGLE)
    oa_statement_url = OAStatementURL(REQUIRED, SINGLE)


class APCFieldset(Structure):
    class APCFieldsetCapability(FieldsetCapability):
        label = "Publication fees"
        order = ["apc", "apc_charges"]

    name_ = "apc"
    capabilities_ = (APCFieldsetCapability(),)

    apc = APC(REQUIRED, SINGLE)
    apc_charges = APCCharges(OPTIONAL, REPEATABLE)

#######################################
#### FORM DEFINTIONS
#######################################

class PublicApplicationForm(Structure):
    class PublicApplicationFormCapability(FormCapability):
        action = "/application"
        method = "POST"
        order = ["basic_compliance", "apcs"]

    name_ = "public_application_form"
    capabilities_ = (PublicApplicationFormCapability(),)

    basic_compliance = BasicCompliance(OPTIONAL, SINGLE)
    apcs = APCFieldset(OPTIONAL, SINGLE)


######################################
## Supporting functions

def currency_list():
    """
    Returns a list of dictionaries containing currency codes and their names.
    This is a placeholder function; in a real application, this would likely
    query a database or an external service to get the current list of currencies.
    """
    return [
        {"value": "USD", "label": "US Dollar"},
        {"value": "EUR", "label": "Euro"},
        {"value": "GBP", "label": "British Pound"},
        {"value": "JPY", "label": "Japanese Yen"},
        # Add more currencies as needed
    ]

if __name__ == "__main__":
    from formulaic.test.example.data import JOURNAL_FORM
    import json

    serialiser = FormSerialiser()
    representation = serialiser.data_to_representation(JOURNAL_FORM, PublicApplicationForm())
    print(json.dumps(representation, indent=2, default=repr))

    html = serialiser.representation_to_string(representation)
    print(html)

    # kvs = data_to_kv(JOURNAL_FORM, PublicApplicationForm())
    # print(kvs)