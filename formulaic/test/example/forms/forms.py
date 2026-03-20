from formulaic.coerce.coerce import Unicode
from formulaic.core import Field, Structure, OPTIONAL, SINGLE, REQUIRED, REPEATABLE
from formulaic.serialise.form.core import FormFieldCapability, CompoundFieldCapability, FieldsetCapability, \
    FormCapability, FormSerialiser
from formulaic.serialise.form.render import DebugFormHTML, DebugFieldHTML, DebugControlHTML
from formulaic.test.example.forms.validate import RequiredValueDOAJ, JournalURLInPublicDOAJ, ISSNInPublicDOAJ, \
    CurrentISOLanguage
from formulaic.test.example.validate import IsISSN
from formulaic.validate.validate import RequiredValue, IsURL, NoScriptTag, OptionalIf, DifferentTo, StopWords, MaxLen
from formulaic.serialise.form.controls import Radio, TextInput, Select, NumberInput, URLInput


####################################
## DOAJ-specific form field capabilities

class DOAJFormFieldCapability(FormFieldCapability):
    long_help = None
    short_help = None
    doaj_criteria = None
    hint = None
    diff_table_context = None
    render_class = DebugFieldHTML
    control_render_class = DebugControlHTML

#######################################
#### FIELD DEFINITIONS
#######################################

# Presented in alphabetical order

#############################
## Alternative Title

class AlternativeTitleCapability(DOAJFormFieldCapability):
    label = "Alternative title (including translation of the title)"
    placeholder = "Ma revue"
    control_class = TextInput

    js = [
        "trim_whitespace",
        {"full_contents": {"empty_disabled": "[The journal has no alternative title]"}}
    ]

class AlternativeTitle(Field):
    name = "alternative_title"
    coerce = [Unicode()]
    validators = [NoScriptTag()]
    capabilities = (AlternativeTitleCapability(),)

# Context variations

class AlternativeTitleEditorial(AlternativeTitle):
    class AlternativeTitleEditorialCapability(AlternativeTitleCapability):
        js = [
            "trim_whitespace",
            "click_to_copy"
        ]

class AlternativeTitleUpdateRequest(AlternativeTitle):
    class AlternativeTitleUpdateRequestCapability(AlternativeTitleCapability):
        disabled = True

## / Alternative Title
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
        options = lambda x: currency_list(x)
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

###########################
## BOAI

class BOAIFormCapability(DOAJFormFieldCapability):
    label = "Does the journal have a BOAI-compliant open access policy?"
    control_class = Radio
    options = [
        {"value": "y", "label": "Yes"},
        {"value": "n", "label": "No"}
    ]

    long_help = ["See <a href='https://blog.doaj.org/2020/11/17/"
                  "what-does-doaj-define-as-open-access/' "
                  "target='_blank' rel='noopener'>"
                  "DOAJ’s definition of open access explained "
                  "in full</a>."],

    doaj_criteria = "You must answer 'Yes'"

class BOAI(Field):
    name = "boai"
    coerce = [Unicode()]
    allow_none = False
    # Note that a field being "required" at all is a property of the field in the form
    # and doesn't need to be listed explicitly here
    validators = [RequiredValueDOAJ("y")]
    capabilities = (BOAIFormCapability(),)

# Context-specific variations on BOAI

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
## EISSN

class EISSNCapability(DOAJFormFieldCapability):
    label = "ISSN (online)"
    long_help = ["Must be a valid ISSN, fully registered and confirmed at the "
                  "<a href='https://portal.issn.org/' target='_blank' rel='noopener'> ISSN Portal</a>.",
                  "Use the link under the ISSN you provided to check it.",
                  "The ISSN must match what is given on the journal website."]
    short_help = "For example, 0378-5955",
    doaj_criteria = "ISSN must be provided"

    control_class = TextInput

    js = [
        "trim_whitespace",
        "full_contents",
        "issn_link"
    ]

class EISSN(Field):
    name = "eissn"
    coerce = [Unicode()]
    validators = [OptionalIf("pissn"), IsISSN(), DifferentTo("pissn")]
    capabilities = (EISSNCapability(),)

class EISSNPublic(EISSN):
    validators = [OptionalIf("pissn"), IsISSN(), DifferentTo("pissn"), ISSNInPublicDOAJ()]

class EISSNUpdateRequest(EISSN):
    class EISSNUpdateRequestCapability(EISSNCapability):
        disabled = True
    capabilities = (EISSNUpdateRequestCapability(),)

class EISSNEditorialCapability(EISSNCapability):
    long_help = ["Must be a valid ISSN, fully registered and confirmed at the "
                  "<a href='https://portal.issn.org/' target='_blank' rel='noopener'> ISSN Portal</a>.",
                  "The ISSN must match what is given on the journal website."]
    disabled = True

class EISSNEditorial(EISSN):
    capabilities = (EISSNEditorialCapability(),)

class EISSNAdmin(EISSN):
    class EISSNAdminCapability(EISSNEditorialCapability):
        disabled = False
        js = [
            "trim_whitespace",
            "autocheck",
            "issn_link"
        ]

## / PISSN
#############################

#############################
## Journal URL

class JournalURLCapability(DOAJFormFieldCapability):
    label = "Link to the journal’s homepage"
    placeholder = "https://www.my-journal.com"

    control_class = URLInput

    js = [
        "trim_whitespace",
        "clickable_url"
    ]

class JournalURL(Field):
    name = "journal_url"
    coerce = [Unicode()]
    validators = [IsURL()]
    capabilities = (JournalURLCapability(),)

class JournalURLPublic(JournalURL):
    validators = [IsURL(), JournalURLInPublicDOAJ()]

## / Journal URL
#############################

#############################
## Keywords

STOP_WORDS = [
    "open access",
    "high quality",
    "peer-reviewed",
    "peer-review",
    "peer review",
    "peer reviewed",
    "quality",
    "medical journal",
    "multidisciplinary",
    "multi-disciplinary",
    "multi-disciplinary journal",
    "interdisciplinary",
    "inter disciplinary",
    "inter disciplinary research",
    "international journal",
    "journal",
    "scholarly journal",
    "open science",
    "impact factor",
    "scholarly",
    "research",
    "research journal"
]

class Keywords(Field):
    class KeywordsCapability(DOAJFormFieldCapability):
        label = "Up to 6 subject keywords in English"
        long_help = ["Choose up to 6 keywords that describe the journal's subject matter. "
                          "Keywords must be in English.", "Use single words or short phrases (2 to 3 words) "
                                                          "that describe the journal's main topic.",
                          "Do not add acronyms, abbreviations or descriptive sentences.",
                          "Note that the keywords may be edited by DOAJ editorial staff."]

        control_class = TextInput

        js = [
            {
                "taglist": {
                    "maximumSelectionSize": 6,
                    "stopWords": STOP_WORDS,
                    "field": "bibjson.keywords"
                }
            }
        ]

    name = "keywords"
    validators = [StopWords(STOP_WORDS), MaxLen(6)]
    capabilities = (KeywordsCapability(),)

## / Keywords
#############################

#############################
## Language

class Language(Field):
    class LanguageCapability(DOAJFormFieldCapability):
        label = "Languages in which the journal accepts manuscripts"
        placeholer = "Type or select the language"

        control_class = Select
        default = ""
        options = lambda x : iso_language_list(x)

        repeatable_initial = 5
        repeatable_minimum = 1

        js = [
            "select",
            "multiple_field"
        ]

    name = "language"
    coerce = [Unicode()]
    validators = [CurrentISOLanguage()]
    capabilities = (LanguageCapability(),)

## / Language
#############################

#############################
## OA Statement URL

class OAStatementURLFormCapability(DOAJFormFieldCapability):
    label = "The journal website must display its open access statement. Where can we find this information?"
    placeholder = "https://www.my-journal.com/open-access"
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

    control_class = URLInput
    js = [
        "trim_whitespace",
        "clickable_url"
    ]

class OAStatementURL(Field):
    name = "oa_statement_url"
    coerce = [Unicode()]
    validators = [IsURL()]
    capabilities = (OAStatementURLFormCapability(),)

## / OA Statement URL
#############################

#############################
## PISSN

class PISSNCapability(DOAJFormFieldCapability):
    label = "ISSN (print)"
    long_help = ["Must be a valid ISSN, fully registered and confirmed at the "
                  "<a href='https://portal.issn.org/' target='_blank' rel='noopener'> ISSN Portal</a>.",
                  "Use the link under the ISSN you provided to check it.",
                  "The ISSN must match what is given on the journal website."]
    short_help = "For example, 2049-3630"
    doaj_criteria = "ISSN must be provided"

    control_class = TextInput

    js = [
        "trim_whitespace",
        "full_contents",
        "issn_link"
    ]

class PISSN(Field):
    name = "pissn"
    coerce = [Unicode()]
    validators = [OptionalIf("eissn"), IsISSN(), DifferentTo("eissn")]
    capabilities = (PISSNCapability(),)

class PISSNPublic(PISSN):
    validators = [OptionalIf("eissn"), IsISSN(), DifferentTo("eissn"), ISSNInPublicDOAJ()]

class PISSNUpdateRequest(PISSN):
    class PISSNUpdateRequestCapability(PISSNCapability):
        disabled = True
    capabilities = (PISSNUpdateRequestCapability(),)

class PISSNEditorialCapability(PISSNCapability):
    long_help = ["Must be a valid ISSN, fully registered and confirmed at the "
                  "<a href='https://portal.issn.org/' target='_blank' rel='noopener'> ISSN Portal</a>.",
                  "The ISSN must match what is given on the journal website."]
    placeholder = ""
    doaj_criteria = "ISSN must be provided"

    disabled = True

class PISSNEditorial(PISSN):
    capabilities = (PISSNEditorialCapability(),)

class PISSNAdmin(PISSN):
    class PISSNAdminCapability(PISSNEditorialCapability):
        disabled = False
        js = [
            "trim_whitespace",
            "autocheck",
            "issn_link"
        ]

## / PISSN
#############################

#############################
## Title

class TitleCapability(DOAJFormFieldCapability):
    label = "Journal title"
    control_class = TextInput
    placeholder = "Journal title"
    long_help = ["The journal title must match what is displayed on the website and what is registered at the "
                          "<a href='https://portal.issn.org/' target='_blank' rel='noopener'> ISSN Portal</a>.",
                          "For translated titles, you may add the "
                          "translation as an alternative title."]
    doaj_criteria = "Title in application form, title at ISSN and website must all match"

    js = [
        "trim_whitespace",
        "clickable_url"
    ]

class Title(Field):
    name = "title"
    coerce = [Unicode()]
    validators = [NoScriptTag()]
    capabilities = (TitleCapability(),)

# Context variations
class TitleEditorialCapability(TitleCapability):
    js = [
        "trim_whitespace",
        "click_to_copy"
    ]

class TitleEditorial(Title):
    capabilities = (TitleEditorialCapability(),)

class TitleUpdateRequest(Title):
    class TitleUpdateRequestCapability(TitleCapability):
        disabled = True
    capabilities = (TitleUpdateRequestCapability(),)


## / Title
#############################


#######################################
#### FIELDSETS
#######################################

# presented in alphabetical order

class AboutTheJournal(Structure):
    class AboutTheJournalCapability(FieldsetCapability):
        label = "About the journal"
        order = [
            "title",
            "alt_title",
            "journal_url",
            "pissn",
            "eissn",
            "keywords",
            "language"
        ]

    name_ = "about_the_journal"
    capabilities_ = (AboutTheJournalCapability(),)

    title = Title(REQUIRED, SINGLE)
    alt_title = AlternativeTitle(OPTIONAL, SINGLE)
    journal_url = JournalURL(REQUIRED, SINGLE)
    pissn = PISSNPublic(OPTIONAL, SINGLE)
    eissn = EISSN(OPTIONAL, SINGLE)
    keywords = Keywords(OPTIONAL, SINGLE)
    language = Language(OPTIONAL, REPEATABLE)

class APCFieldset(Structure):
    class APCFieldsetCapability(FieldsetCapability):
        label = "Publication fees"
        order = ["apc", "apc_charges"]

    name_ = "apc"
    capabilities_ = (APCFieldsetCapability(),)

    apc = APC(REQUIRED, SINGLE)
    apc_charges = APCCharges(OPTIONAL, REPEATABLE)

class BasicCompliance(Structure):
    class BasicComplianceCapability(FieldsetCapability):
        label = "Open access compliance"
        order = ["boai", "oa_statement_url"]

    name_ = "basic_compliance"
    capabilities_ = (BasicComplianceCapability(),)

    boai = BOAI(REQUIRED, SINGLE)
    oa_statement_url = OAStatementURL(REQUIRED, SINGLE)

#######################################
#### FORM DEFINTIONS
#######################################

class PublicApplicationForm(Structure):
    class PublicApplicationFormCapability(FormCapability):
        action = "/application"
        method = "POST"
        order = [
            "basic_compliance",
            "about_the_journal",
            "apcs"
        ]

        render_class = DebugFormHTML

    name_ = "public_application_form"
    capabilities_ = (PublicApplicationFormCapability(),)

    basic_compliance = BasicCompliance(OPTIONAL, SINGLE)
    about_the_journal = AboutTheJournal(OPTIONAL, SINGLE)
    apcs = APCFieldset(OPTIONAL, SINGLE)


######################################
## Supporting functions

def currency_list(capability):
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

def iso_language_list(capability):
    return [
        {"value": "ENG", "label": "English"},
        {"value": "FRE", "label": "French"},
        {"value": "GER", "label": "German"},
        {"value": "ESP", "label": "Spanish"},
    ]
    cl = [{"display": " ", "value": ""}]
    for v, d in language_options:
        cl.append({"display": d, "value": v})
    return cl

if __name__ == "__main__":
    from formulaic.test.example.data import JOURNAL_FORM
    import json

    serialiser = FormSerialiser()
    representation = serialiser.data_to_representation(JOURNAL_FORM, PublicApplicationForm())
    print(json.dumps(representation, indent=2, default=repr))

    html = serialiser.representation_to_string(representation)
    print(html)

    with open("out.html", "w") as f:
        f.write("<html>\n")
        f.write(html)
        f.write("\n\n<pre>\n" + json.dumps(representation, indent=2, default=repr) + "\n</pre>")
        f.write("\n</html>")