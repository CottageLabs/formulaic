class DOAJFormField(FormField):
    long_help = None
    short_help = None
    doaj_criteria = None
    widgets = []

class RequiredValueNotSet(ValidationError):
    id = "required_value_not_set"

    def __init__(self, got, expected):
        self.got = got
        self.expected = expected


class RequiredValue(Validator):
    def __init__(self, required_value):
        self.required_value = required_value

    def validate(self, val, field=None, formulaic_object=None):
        if val != self.required_value:
            raise RequiredValueNotSet(val, self.required_value)

    def html_attrs(self):
        pass

###################################
class BOAI(DOAJFormField):
    name = "boai"
    label = "Does the journal adhere to DOAJ’s definition of open access?"
    control = Radio
    options = [
        ("y", "Yes"),
        ("n", "No")
    ]
    long_help = ["See <a href='https://blog.doaj.org/2020/11/17/"
                          "what-does-doaj-define-as-open-access/' "
                          "target='_blank' rel='noopener'>"
                          "DOAJ’s definition of open access explained "
                          "in full</a>."]
    doaj_criteria = "You must answer 'Yes'"
    coerce = []
    validators = [
        RequiredValue("y")
    ]

class AdminBOAI(BOAI):
    validators = []

class EditorBOAI(BOAI):
    validators = []
    disabled = True

#######################################

class OAStatmentURL(DOAJFormField):
    name = "oa_statement_url"
    label = "The journal website must display its open access statement. Where can we find this information?"
    input = None
    long_help = "etc"
    short_help = "short",
    placeholder = "https://www.my-journal.com/open-access"
    validators = [
        IsURL
    ]
    widgets = [
        "trim_witespace",
        "clickable_url"
    ]

###################################

class PublicJournalFormStructure(Structure):
    name = "public_journal_form"
    fields = [
        {"field": BOAI, "required": True},
        {"field": OAStatmentURL, "required": True}
    ]
    lists = [

    ]

class AdminJournalFormStructure(Structure):
    name = "admin_journal_form"
    fields = [
        AdminBOAI,
        {"field": OAStatmentURL, "required": True}
    ]
    lists = []

class EditorJournalFormStructure(Structure):
    name = "editor_journal_form"
    fields = [
        EditorBOAI,
        {"field": OAStatmentURL, "required": True}
    ]
    lists = []

class AssedJournalFormStructure(Structure):
    name = "assed_journal_form"
    fields = [
        EditorBOAI
    ]
    lists = []

class PublicJournalForm(FormulaicObject):
    struct = PublicJournalFormStructure