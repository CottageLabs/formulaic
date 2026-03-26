from formulaic.coerce.coerce import Unicode, Integer
from formulaic.core import Field, Structure, OPTIONAL, SINGLE, REQUIRED, REPEATABLE
from formulaic.serialise.form.core import FormFieldCapability, CompoundFieldCapability, FieldsetCapability, \
    FormCapability, FormSerialiser, FormDataParser
from formulaic.serialise.form.render import DebugFormHTML, DebugFieldHTML, DebugControlHTML, DebugListHTML
from formulaic.test.example.forms.validate import RequiredValueDOAJ, JournalURLInPublicDOAJ, ISSNInPublicDOAJ, \
    CurrentISOLanguage, CurrentISOCurrency
from formulaic.test.example.validate import IsISSN
from formulaic.validate.validate import RequiredValue, IsURL, NoScriptTag, OptionalIf, DifferentTo, StopWords, MaxLen, \
    RequiredIf, OnlyIfExists
from formulaic.serialise.form.controls import Radio, TextInput, Select, NumberInput, URLInput, Checkbox


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
    list_render_class = DebugListHTML

class DOAJFormCapability(FormCapability):
    render_class = DebugFormHTML
    list_render_class = DebugListHTML

class DOAJFieldsetCapability(FieldsetCapability):
    list_render_class = DebugListHTML

class DOAJCompoundFieldCapability(CompoundFieldCapability):
    list_render_class = DebugListHTML

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
        options = [
            {"value": "y", "label": "Yes"},
            {"value": "n", "label": "No"}
        ]

        long_help = ["Publication fees are sometimes called "
                     "article processing charges (APCs). You should answer"
                     " Yes if any fee is required from the author for "
                     "publishing their paper."]
        doaj_criteria = "You must tell us about any APCs"

        control_class = Radio

    capabilities = (APCFormCapability(),)

## APC Currency Field
class APCCurrency(Field):
    class APCCurrencyFormCapability(DOAJFormFieldCapability):
        label = "What is the currency of the APC?"
        placeholder = "Currency"

        options = lambda x: currency_list(x)
        default = ""

        control_class = Select

        js = ["select"]

    name = "apc_currency"
    coerce = [Unicode()]
    validate = [RequiredIf("apc", "y"), CurrentISOCurrency]
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
    validate = [RequiredIf("apc", "y")]
    capabilities = (APCMaxFormCapability(),)

class APCURL(Field):
    class APCURLCapability(DOAJFormFieldCapability):
        label = "Where can we find this information?"
        short_help = ["Link to the page where this is stated. The page "
                     "must declare <b>whether or not</b> there is a fee "
                     "to publish an article in the journal."]
        doaj_criteria = "You must provide a URL"
        placeholder = "https://www.my-journal.com/about#apc"

        control_class = TextInput

        js = [
            "trim_whitespace",
            "clickable_url"
        ]

    name = "apc_url"
    validators = [IsURL()]

## APC Compound Field Container

class APCCharges(Structure):
    class APCChargesCapability(CompoundFieldCapability):
        label = "APC"
        repeatable_label = "Highest fee charged"
        long_help = [" If the journal charges a range of fees for "
                          "the publication of an article, enter the highest fee. "
                          "If the fee can be paid in more than one currency, "
                          "you may list them here."]

        repeatable_initial = 5
        repeatable_minimum = 1

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
## Copyright Author Retains

class CopyrightAuthorRetains(Field):
    class CopyrightAuthorRetainsCapability(DOAJFormFieldCapability):
        label = ("For all the licenses you have indicated above, do authors retain the copyright "
                 "<b>and</b> full publishing rights without restrictions?")

        long_help = ["Answer <strong>No</strong> if authors transfer "
                          "copyright or assign exclusive rights to the publisher"
                          " (including commercial rights). <br/><br/> Answer "
                          "<strong>Yes</strong> only if authors publishing "
                          "under any license allowed by the journal "
                          "retain all rights."]

        options = [
            {"label": "Yes", "value": "y"},
            {"label": "No", "value": "n"}
        ]
        control_class = Radio

    name = "copyright_author_retains"
    coerce = [Unicode()]
    capabilities = (CopyrightAuthorRetainsCapability(),)

## / Copyright Author Retains
#############################

#############################
## Copyright URL

class CopyrightURL(Field):
    class CopyrightURLCapability(DOAJFormFieldCapability):
        label = "Where can we find this information?"
        diff_table_context = "Copyright terms"
        short_help = "Link to the journal’s copyright terms"
        placeholder = "https://www.my-journal.com/about#licensing"

        control_class = TextInput

        js = [
            "trim_whitespace",
            "clickable_url"
        ]

    name = "copyright_url"
    coerce = [Unicode()]
    validators = [IsURL()]
    capabilities = (CopyrightURLCapability(),)

## Copyright URL
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
## Institution Country

class InstitutionCountryCapability(DOAJFormFieldCapability):
    label = "Other organisation's country"
    short_help = "The country in which the other organisation is based"
    doaj_criteria = "You must provide a publisher country"
    placeholder = "Type or select the country"

    options = lambda x: iso_country_list(x)
    default = ""
    control_class = Select

    js = [
        {"select": {"allow_clear": True}}
    ]

class InstitutionCountry(Field):
    name = "institution_country"
    coerce = [Unicode()]
    capabilities = (InstitutionCountryCapability(),)

class InstitutionCountryPublisher(InstitutionCountry):
    validators = [OnlyIfExists()]

## / Institution Country
#############################

#############################
## Institution Name

class InstitutionNameCapability(DOAJFormFieldCapability):
    label = "Other organisation's name"
    placeholder = "Type or select the other organisation's name"
    short_help = "Any other organisation associated with the journal"
    long_help = [
                "The journal may be owned, funded, sponsored, or supported by another organisation that is not "
                "the publisher. If your journal is linked to "
                "a second organisation, enter its name here."]

    control_class = TextInput

    js = [
        "trim_whitespace",
        {"autocomplete": {"type": "journal", "field": "bibjson.institution.name.exact"}},
        "full_contents"
    ]

class InstitutionName(Field):
    name = "institution_name"
    coerce = [Unicode()]

    capabilities = (InstitutionNameCapability(),)

class IntitutionNameEditorial(InstitutionName):
    class InstitutionNameEditorialCapability(InstitutionNameCapability):
        js = [
            "trim_whitespace",
            {"autocomplete": {"type": "journal", "field": "bibjson.institution.name.exact"}},
            "click_to_copy"
        ]

    capabilities = (InstitutionNameEditorialCapability(),)

class InstitionalNamePublisher(InstitutionName):
    validators = [DifferentTo("publisher_name")]

## / Institution Name
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
        label = "Language"
        placeholder = "Type or select the language"
        repeatable_label = "Languages in which the journal accepts manuscripts"

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
## License

class License(Field):
    class LicenseCapability(DOAJFormFieldCapability):
        label = "License(s) permitted by the journal"
        long_help = ["The journal must use some form of licensing to be considered for indexing in DOAJ. ",
                          "If Creative Commons licensing is not used, then select <em>Publisher's own license</em> and enter "
                          "more details below.",
                          "More information on CC licenses: <br/>"
                          "<a href='https://creativecommons.org/licenses/by/4.0/"
                          "' target='_blank' 'rel='noopener'>CC BY</a> <br/>"
                          "<a href='https://creativecommons.org/licenses/by-sa/4.0/"
                          "' target='_blank' 'rel='noopener'>CC BY-SA</a> <br/>"
                          "<a href='https://creativecommons.org/licenses/by-nd/4.0/"
                          "' target='_blank' 'rel='noopener'>CC BY-ND</a> <br/>"
                          "<a href='https://creativecommons.org/licenses/by-nc/4.0/"
                          "' target='_blank' 'rel='noopener'>CC BY-NC</a> <br/>"
                          "<a href='https://creativecommons.org/licenses/by-nc-sa/4.0/"
                          "' target='_blank' 'rel='noopener'>CC BY-NC-SA</a> <br/>"
                          "<a href='https://creativecommons.org/licenses/by-nc-nd/4.0/"
                          "' target='_blank' 'rel='noopener'>CC BY-NC-ND</a>",
                          "<a href='https://wiki.creativecommons.org/wiki/CC0_"
                          "FAQ#What_is_the_difference_between_CC0_and_the_Publ"
                          "ic_Domain_Mark_.28.22PDM.22.29.3F' target='_blank' "
                          "rel='noopener'>What is the difference between CC0 "
                          "and the Public Domain Mark (\"PDM\")?</a>"]
        doaj_criteria = "Content must be licensed"

        multiple = True
        options = [
            {"label": "CC BY", "value": "CC BY"},
            {"label": "CC BY-SA", "value": "CC BY-SA"},
            {"label": "CC BY-ND", "value": "CC BY-ND"},
            {"label": "CC BY-NC", "value": "CC BY-NC"},
            {"label": "CC BY-NC-SA", "value": "CC BY-NC-SA"},
            {"label": "CC BY-NC-ND", "value": "CC BY-NC-ND"},
            {"label": "CC0", "value": "CC0"},
            {"label": "Public domain", "value": "Public domain"},
            {"label": "Publisher's own license", "value": "Publisher's own license"},
        ]
        control_class = Checkbox

    name = "license"
    coerce = [Unicode()]
    capabilities = (LicenseCapability(),)

## / License
#############################

#############################
## License Attributes

class LicenseAttributes(Field):
    class LicenseAttributesCapability(DOAJFormFieldCapability):
        label = "Select all the attributes that your license has"
        doaj_criteria = "Content must be licensed"

        options = [
            {"label": "Attribution", "value": "BY"},
            {"label": "Share Alike", "value": "SA"},
            {"label": "No Derivatives", "value": "ND"},
            {"label": "No Commercial Usage", "value": "NC"}
        ]
        multiple = True
        control_class = Checkbox

        display_conditional = [{"field": "license", "value": "Publisher's own license"}]
        js = [
            {"conditional": {"field": "license", "value": "Publisher's own license"}}
        ]

    name = "license_attributes"
    coerce = [Unicode()]
    capabilities = (LicenseAttributesCapability(),)

## / License Attributes
#############################

#############################
## License Terms URL

class LicenseTermsURL(Field):
    class LicenseTermsURLCapability(DOAJFormFieldCapability):
        label = "Where can we find this information?"
        diff_table_context = "License terms"
        short_help = "Link to the page where the license terms are stated on your site."
        doaj_criteria = "You must provide a link to your license terms"
        placeholder = "https://www.my-journal.com/about#licensing"

        control_class = TextInput

        display_conditional = [{"field": "license", "value": "Publisher's own license"}]
        js = [
            {"conditional": {"field": "license", "value": "Publisher's own license"}}
        ]

    name = "license_terms_url"
    coerce = [Unicode()]
    validators = [IsURL()]
    capabilities = (LicenseTermsURLCapability(),)

    js = [
        "trim_whitespace",
        "clickable_url"
    ]

## / License Terms URL
#############################

#############################
## License Display

class LicenseDisplay(Field):
    class LicenseDisplayCapability(DOAJFormFieldCapability):
        label = "Does the journal embed and/or display licensing information in its articles?"
        long_help = ["It is recommended that licensing information is included in full-text articles "
                          "but it is not required for inclusion. "
                          "Answer <strong>Yes</strong> if licensing is displayed or "
                          "embedded in all versions of each article."]

        options = [
            {"label": "Yes", "value": "y"},
            {"label": "No", "value": "n"}
        ]
        control_class = Radio

        display_conditional = [{"field": "license", "value": "Publisher's own license"}]
        js = [
            {"conditional": {"field": "license", "value": "Publisher's own license"}}
        ]

    name = "license_display"
    coerce = [Unicode()]
    capabilities = (LicenseDisplayCapability(),)

    js = [
        "trim_whitespace",
        "clickable_url"
    ]


## / License Display
#############################

#############################
## License Display Example URL

class LicenseDisplayExampleURL(Field):
    class LicenseDisplayExampleURLCapability(DOAJFormFieldCapability):
        label = "Recent article displaying or embedding a license in the full text"
        short_help = "Link to an example article"
        placeholder = "https://www.my-journal.com/articles/article-page"

        control_class = TextInput

        display_conditional = [{"field": "license_display", "value": "y"}]
        js = [
            {"conditional": {"field": "license_display", "value": "y"}}
        ]

    name = "license_display_example_url"
    coerce = [Unicode()]
    validators = [RequiredIf("license_display", "y"), IsURL()]
    capabilities = (LicenseDisplayExampleURLCapability(),)

    js = [
        "trim_whitespace",
        "clickable_url"
    ]


## / License Display Example URL
#############################

#############################
## OA Start

class OAStart(Field):
    class OAStartCapability(DOAJFormFieldCapability):
        label = "When did the journal start to publish all content using an open license?"
        long_help = [
                "Please enter the year that the journal started to publish all content as true open access, according to DOAJ's <a href='https://blog.doaj.org/2020/11/17/what-does-doaj-define-as-open-access/' target='_blank' rel='nofollow'>definition</a>.",
                "For journals that have flipped to open access, enter the year that the journal flipped, not the original launch date of the journal.",
                "For journals that have made digitised backfiles freely available, enter the year that the journal started publishing as a fully open access title, not the date of the earliest free content."]

        control_class = NumberInput

    name = "oa_start"
    coerce = [Integer()]
    allowed_range = (1900, 2026)
    capabilities = (OAStartCapability(),)

## / OA Start
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
## Publisher Country

class PublisherCountryCapability(DOAJFormFieldCapability):
    label = "Publisher's country"
    long_help = "The country where the publisher carries out its business operations and is registered."
    doaj_criteria = "You must provide a publisher country"
    placeholder = "Type or select the country"

    options = lambda x: iso_country_list(x)
    default = ""
    control_class = Select

    js = [
        "select"
    ]

class PublisherCountry(Field):
    name = "publisher_country"
    coerce = [Unicode()]
    capabilities = (PublisherCountryCapability(),)

class PublisherCountryAssEd(PublisherCountry):
    class PublisherCountryAssEdCapability(PublisherCountryCapability):
        disabled = True

    capabilities = (PublisherCountryCapability(),)

## / Publisher Country
#############################

#############################
## Publisher Name

class PublisherNameCapability(DOAJFormFieldCapability):
    label = "Publisher's name"
    placeholder = "Type or select the publisher's name"

    control_class = TextInput

    js = [
        "trim_whitespace",
        {"autocomplete": {"type": "journal", "field": "bibjson.publisher.name.exact"}},
        "full_contents"
    ]

class PublisherName(Field):
    name = "publisher_name"
    coerce = [Unicode()]

    capabilities = (PublisherNameCapability(),)

class PublisherNameEditorial(PublisherName):
    class PublisherNameEditorialCapability(PublisherNameCapability):
        js = [
            "trim_whitespace",
            {"autocomplete": {"type": "journal", "field": "bibjson.publisher.name.exact"}},
            "click_to_copy"
        ]

    capabilities = (PublisherNameEditorialCapability(),)

class PublisherNamePublisher(PublisherName):
    validators = [DifferentTo("institution_name")]

## / Publisher Name
#############################

#############################
## Review Process

class ReviewProcess(Field):
    class ReviewProcessCapability(DOAJFormFieldCapability):
        label = ("DOAJ only accepts peer-reviewed journals. "
                 "Which type(s) of peer review does this journal use?")
        long_help = ("Enter all types of review used by the journal for "
                          "research articles. Note that editorial review is "
                          "only accepted for <a href='https://doaj.org/apply/guide/#arts-and-humanities-journals' target='_blank' rel='nofollow'>arts and humanities journals</a>."
                          "For a detailed description of the peer review types, "
                          "see <a href='https://docs.google.com/document/d/1ADiVPR7tY8a9JKr2VjFEXbNG7FIpz22nOPDDPfRzJxA/edit?tab=t.0' target='_blank' rel='nofollow'>this summary</a>.")
        doaj_criteria = "Peer review must be carried out"

        options = [
            {"label": "Editorial review", "value": "Editorial review"},
            {"label": "Peer review", "value": "Peer review"},
            {"label": "Anonymous peer review", "value": "Anonymous peer review"},
            {"label": "Double anonymous peer review", "value": "Double anonymous peer review"},
            {"label": "Post-publication peer review", "value": "Post-publication peer review"},
            {"label": "Open peer review", "value": "Open peer review"},
            {"label": "Other", "value": "other"}
        ]
        multiple = True
        control_class = Checkbox

    name = "review_process"
    coerce = [Unicode()]
    capabilities = (ReviewProcessCapability(),)

## / Review Process
#############################

#############################
## Review Process Other

class ReviewProcessOther(Field):
    class ReviewProcessOtherCapability(DOAJFormFieldCapability):
        label = "Other peer review"
        placeholder = "Other peer review"

        control_class = TextInput

        display_conditional = [{"field": "review_process", "value": "other"}]
        js = [
            "trim_whitespace",
        ]

    name = "review_process_other"
    coerce = [Unicode()]
    validators = [RequiredIf("review_process", "other")]
    capabilities = (ReviewProcessOtherCapability(),)

## / Review Process Other
#############################

#############################
## Review URL

class ReviewURL(Field):
    class ReviewURLCapability(DOAJFormFieldCapability):
        label = "Where can we find this information?"
        diff_table_context = "Peer review policy"
        doaj_criteria = "You must provide a URL"
        short_help = "Link to the journal’s peer review policy"

        control_class = TextInput

        js = [
            "trim_whitespace",
            "clickable_url"
        ]

    name = "review_url"
    coerce = [Unicode()]
    validators = [IsURL()]
    capabilities = (ReviewURLCapability(),)

## / Review URL
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
    class AboutTheJournalCapability(DOAJFieldsetCapability):
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
    class APCFieldsetCapability(DOAJFieldsetCapability):
        label = "Publication fees"
        order = ["apc", "apc_charges"]

    name_ = "apc"
    capabilities_ = (APCFieldsetCapability(),)

    apc = APC(REQUIRED, SINGLE)
    apc_charges = APCCharges(OPTIONAL, REPEATABLE)
    apc_url = APCURL(OPTIONAL, SINGLE)

class BasicCompliance(Structure):
    class BasicComplianceCapability(DOAJFieldsetCapability):
        label = "Open access compliance"
        order = ["boai", "oa_statement_url", "oa_start"]

    name_ = "basic_compliance"
    capabilities_ = (BasicComplianceCapability(),)

    boai = BOAI(REQUIRED, SINGLE)
    oa_statement_url = OAStatementURL(REQUIRED, SINGLE)
    oa_start = OAStart(REQUIRED, SINGLE)

class CopyrightFieldset(Structure):
    class CopyrightFieldsetCapability(DOAJFieldsetCapability):
        label = "Copyright"
        order = ["copyright_author_retains", "copyright_url"]

    name_ = "copyright"
    capabilities_ = (CopyrightFieldsetCapability(),)

    copyright_author_retains = CopyrightAuthorRetains(REQUIRED, SINGLE)
    copyright_url = CopyrightURL(REQUIRED, SINGLE)

class EmbeddedLicensing(Structure):
    class EmbeddedLicensingCapability(DOAJFieldsetCapability):
        label = "Embedded licenses"
        order = ["license_display", "license_display_example_url"]

    name_ = "embedded_licensing"
    capabilities_ = (EmbeddedLicensingCapability(),)

    license_display = LicenseDisplay(OPTIONAL, SINGLE)
    license_display_example_url = LicenseDisplayExampleURL(OPTIONAL, SINGLE)

class Licensing(Structure):
    class LicensingCapability(DOAJFieldsetCapability):
        label = "Licensing"
        order = ["license", "license_attributes", "license_terms_url"]

    name_ = "licensing"
    capabilities_ = (LicensingCapability(),)

    license = License(OPTIONAL, SINGLE)
    license_attributes = LicenseAttributes(OPTIONAL, SINGLE)
    license_terms_url = LicenseTermsURL(OPTIONAL, SINGLE)

class OtherOrganisation(Structure):
    class OtherOrganisationCapability(DOAJFieldsetCapability):
        label = "Other organisation, if applicable"
        order = ["institution_name", "institution_country"]

    name_ = "society_or_institution"
    capabilities_ = (OtherOrganisationCapability(),)

    institution_name = InstitutionName(OPTIONAL, SINGLE)
    institution_country = InstitutionCountry(OPTIONAL, SINGLE)

class PeerReview(Structure):
    class PeerReviewCapability(DOAJFieldsetCapability):
        label = "Peer review"
        order = ["review_process", "review_process_other", "review_url"]

    name_ = "peer_review"
    capabilities_ = (PeerReviewCapability(),)

    review_process = ReviewProcess(REQUIRED, SINGLE)
    review_process_other = ReviewProcessOther(OPTIONAL, SINGLE)
    review_url = ReviewURL(REQUIRED, SINGLE)

class Publisher(Structure):
    class PublisherCapability(DOAJFieldsetCapability):
        label = "Publisher"
        order = ["publisher_name", "publisher_country"]

    name_ = "publisher"
    capabilities_ = (PublisherCapability(),)

    publisher_name = PublisherNamePublisher(REQUIRED, SINGLE)
    publisher_country = PublisherCountry(REQUIRED, SINGLE)

#######################################
#### FORM DEFINTIONS
#######################################

class PublicApplicationForm(Structure):
    class PublicApplicationFormCapability(DOAJFormCapability):
        action = "/application"
        method = "POST"
        order = [
            "basic_compliance",
            "about_the_journal",
            "publisher",
            "other_organisation",
            "licensing",
            "embedded_licensing",
            "copyright",
            "peer_review",
            "apcs"
        ]

    name_ = "public_application_form"
    capabilities_ = (PublicApplicationFormCapability(),)

    basic_compliance = BasicCompliance(OPTIONAL, SINGLE)
    about_the_journal = AboutTheJournal(OPTIONAL, SINGLE)
    publisher = Publisher(OPTIONAL, SINGLE)
    other_organisation = OtherOrganisation(OPTIONAL, SINGLE)
    licensing = Licensing(OPTIONAL, SINGLE)
    embedded_licensing = EmbeddedLicensing(OPTIONAL, SINGLE)
    copyright = CopyrightFieldset(OPTIONAL, SINGLE)
    peer_review = PeerReview(OPTIONAL, SINGLE)
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
    # cl = [{"display": " ", "value": ""}]
    # for v, d in language_options:
    #     cl.append({"display": d, "value": v})
    # return cl

def iso_country_list(capability):
    return [
        {"value": "US", "label": "United States"},
        {"value": "CA", "label": "Canada"},
        {"value": "NZ", "label": "New Zealand"},
        {"value": "BG", "label": "Bangladesh"}
    ]

if __name__ == "__main__":
    from formulaic.test.example.data import JOURNAL_FORM, JOURNAL_PARSED_FORM
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

    parser = FormDataParser()
    data = parser.representation_to_data(JOURNAL_PARSED_FORM, PublicApplicationForm())
    print(json.dumps(data, indent=2, default=repr))