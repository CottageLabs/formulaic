from formulaic.form import Fieldset, FormField, Radio, TextInput, FormGroupInfo, FormGroup, Select, NumberInput, \
    FormContext
from formulaic.coerce import Boolean, Unicode, Integer
from formulaic.validate import RequiredValue, IsURL, RequiredIf
from formulaic.core import Structure, REQUIRED, OPTIONAL, SINGLE, REPEATABLE
# from portality.forms.validate import CurrentISOCurrency

###############################
## localisations for our specific type of form


class DOAJFormField(FormField):
    long_help = None
    short_help = None
    doaj_criteria = None
    hint = None
    diff_table_context = None

class RequiredValueDOAJ(RequiredValue):
    def html_attrs(self, attrs):
        attrs["data-parsley-requiredvalue"] = self.required_value

class IsURLDOAJ(IsURL):
    msg = "<p><small>" + "Please enter a valid URL. It should start with http or https" + "</p></small>"

    def html_attrs(self, attrs):
        super(IsURLDOAJ, self).html_attrs(attrs)
        attrs["data-parsley-pattern"] = self.HTTP_URL
        attrs["data-parsley-pattern-message"] = self.msg
        return attrs

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

######################################
## Form Fields

class BOAI(DOAJFormField):
    name = "boai"
    coerce = [Unicode()]
    allow_none = False
    validate = [RequiredValueDOAJ("y")]

    label = "Does the journal have a BOAI-compliant open access policy?"
    control = Radio
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

class AdminBOAI(BOAI):
    validators = []

class EditorBOAI(BOAI):
    validators = []
    disabled = True

class AssEdBOAI(BOAI):
    validators = []
    disabled = True


class OAStatementURL(DOAJFormField):
    name = "oa_statement_url"
    coerce = [Unicode()]
    validate = [IsURL()]

    label = "The journal website must display its open access statement. Where can we find this information?"
    control = TextInput
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
    short_help =  "Link to the journal’s open access statement",


class APC(FormField):
    name = "apc"
    coerce = [Unicode()]
    allow_none = False

    label = "Does the journal charge fees for publishing an article (APCs)?"
    control = Radio
    options = [
        {"value": "y", "label": "Yes"},
        {"value": "n", "label": "No"}
    ]

    long_help = ["Publication fees are sometimes called "
                          "article processing charges (APCs). You should answer"
                          " Yes if any fee is required from the author for "
                          "publishing their paper."]
    doaj_criteria = "You must tell us about any APCs"


class APCCurrency(DOAJFormField):
    name = "apc_currency"
    coerce = [Unicode()]
    validate = [RequiredIf("apc", "y")], #CurrentISOCurrency

    label = "What is the currency of the APC?"
    control = Select
    options = lambda x: currency_list()
    placeholder = "Currency"
    default = ""
    js = ["select"]
    attributes = {
        "class": "input-xlarge"
    }

class APCMax(DOAJFormField):
    name = "apc_max"
    coerce = [Integer()]
    validate = [RequiredIf("apc", "y")]

    label = "What is the maximum APC charged by this journal?"
    control = NumberInput
    attributes = {
        "min": "1"
    }

class APCCharges(FormGroup):
    class APCChargesFormInfo(FormGroupInfo):
        label = "Highest fee charged"
        repeatable = {
            "minimum": 1,
            "initial": 5
        }
        conditional = [
            {"field": "apc", "value": "y"}
        ]
        js = ["multiple_field"]

    _name = "apc_charges"
    _form = APCChargesFormInfo

    apc_currency = APCCurrency(OPTIONAL, SINGLE)
    apc_max = APCMax(OPTIONAL, SINGLE)


########################################
## Fieldsets

class BasicCompliance(Fieldset):
    name = "basic_compliance"
    label = "Open access compliance"

class APCFieldset(Fieldset):
    name = "apc"
    label = "Publication fees"

#########################################
## Full form definitions

class PublicApplicationForm(FormGroup):
    class PublicApplicationFormInfo(FormGroupInfo):
        label = "Public Application Form"

    _name = "public_application_form"

    ###################################
    ## Individual Fields

    boai = BOAI(REQUIRED, SINGLE, fieldset=BasicCompliance, fs_pos=1)
    oa_statement_url = OAStatementURL(REQUIRED, SINGLE, fieldset=BasicCompliance, fs_pos=2)
    apc = APC(REQUIRED, SINGLE, fieldset=APCFieldset, fs_pos=1)

    ###################################
    ## Field Groups

    apc_charges = APCCharges(OPTIONAL, REPEATABLE, fieldset=APCFieldset, fs_pos=2)

class PublicApplicationFormContext(FormContext):
    name = "public_application_form_context"
    form = PublicApplicationForm()
    action = "/application"
    method = "POST"
    fieldset_ordering = [
        BasicCompliance,
        APCFieldset
    ]

# pafc = PublicApplicationFormContext()
# print(pafc.draw())