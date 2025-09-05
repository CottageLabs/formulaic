from formulaic.core import Field, Coerce
from formulaic.coerce import Unicode, Integer, LowerCase, UpperCaseUnicode
from formulaic.fields import BasicUnicode, BasicBoolean, DateField, UTCDateTimeField, IntegerField
from formulaic.schema.es7x import ES7xStorableField
from formulaic.validate import IsURL
from formulaic.test.example.validate import IsISSN

############################################
# Custom coerce functions

class ISOLang2LetterLax(Coerce):
    def coerce(self, val, field):
        pass

class CurrencyCodeLax(Coerce):
    def coerce(self, val, field):
        pass

class CountryCode(Coerce):
    def coerce(self, val, field):
        pass

class ISSNCoerce(UpperCaseUnicode):
    def coerce(self, val, field):
        # force unicode uppercase
        val = super().coerce(val, field)

        if len(val) > 9 or val == '':
            raise ValueError("Unable to normalise {x} to valid ISSN".format(x=val))

        if len(val) == 9:
            return val

        if len(val) == 8:
            if "-" in val:
                return "0" + val
            else:
                return val[:4] + "-" + val[4:]

        if len(val) < 8:
            if "-" in val:
                return ("0" * (9 - len(val))) + val
            else:
                issn = ("0" * (8 - len(val))) + val
                return issn[:4] + "-" + issn[4:]

############################################
# Custom base fields

class ISSN(Field):
    coerce = [ISSNCoerce]
    allow_coerce_failure = True

class URL(Field):
    name = "url"
    coerce = [Unicode]
    validators = [IsURL]

class ES7xKeywordField(ES7xStorableField):
    es_keyword_field = True
    es_keyword_ignore_above = 0 # no limit

class ES7xDateOptionalTime(ES7xStorableField):
    es_type = "date"
    es_format = "date_optional_time"

class ES7xBoolean(ES7xStorableField):
    es_type = "boolean"

class ES7xInteger(ES7xStorableField):
    es_type="long"

class ES7xYear(ES7xStorableField):
    es_type = "date"
    es_format = "year"

class ES7xNotIndexed(ES7xStorableField):
    es_index = False

#############################################
## Common reusable fields

class ID(BasicUnicode, ES7xKeywordField):
    name = "id"

class CreatedDate(UTCDateTimeField, ES7xDateOptionalTime):
    name = "created_date"

class LastUpdated(UTCDateTimeField, ES7xDateOptionalTime):
    name = "last_updated"

class Scheme(BasicUnicode, ES7xKeywordField):
    name = "scheme"

class Value(BasicUnicode, ES7xKeywordField):
    name = "value"

class Name(BasicUnicode, ES7xKeywordField):
    name = "name"

class Country(ES7xKeywordField, Field):
    name = "country"
    coerce = [CountryCode]
    allow_coerce_failure = True

class ESType(BasicUnicode, ES7xKeywordField):
    name = "es_type"

############################################
# Field elements

class AlternativeTitle(BasicUnicode, ES7xKeywordField):
    name = "alternative_title"

class BOAI(BasicBoolean, ES7xBoolean):
    name = "boai"

class EISSN(ISSN, ES7xKeywordField):
    name = "eissn"

class PISSN(ISSN, ES7xKeywordField):
    name = "pissn"

class DiscontinuedDate(DateField, ES7xDateOptionalTime):
    name = "discontinued_date"

class PublicationTimeWeeks(IntegerField, ES7xInteger):
    name = "publication_tile_weeks"

class Title(BasicUnicode, ES7xKeywordField):
    name = "title"

class OAStart(IntegerField, ES7xInteger):
    name = "oa_start"

class IsReplacedBy(ISSN, ES7xKeywordField):
    name = "is_replaced_by"
    allow_coerce_failure = True

class Keywords(ES7xKeywordField, Field):
    name = "keywords"
    corece = [Unicode, LowerCase],

class Language(ES7xKeywordField, Field):
    name = "language"
    coerce = [ISOLang2LetterLax]

class Replaces(ISSN, ES7xKeywordField):
    name = "replaces"
    allow_coerce_failure = True

class Labels(BasicUnicode, ES7xKeywordField):
    name = "labels"
    allowed_values = ["s2o"]

class HasAPC(BasicBoolean, ES7xBoolean):
    name = "has_apc"

class Currency(ES7xKeywordField, Field):
    name = "currency"
    coerce = [CurrencyCodeLax]

class Price(ES7xInteger, Field):
    name = "price"
    coerce = [Integer]

class LicenceDisplayExampleURL(URL, ES7xKeywordField):
    name = "license_display_example_url"

class LicenceDisplay(BasicUnicode, ES7xKeywordField):
    name = "license_display"
    allowed_values = ["Embed", "Display", "No"]

class AuthorRetainsCopyright(BasicBoolean, ES7xBoolean):
    name = "author_retains"

class HasPolicy(BasicBoolean, ES7xBoolean):
    name = "has_policy"

class IsRegistered(BasicBoolean, ES7xBoolean):
    name = "is_registered"

class DepositPolicyService(BasicUnicode, ES7xKeywordField):
    name = "service"

class ReviewURL(URL, ES7xKeywordField):
    name = "review_url"

class BoardURL(URL, ES7xKeywordField):
    name = "board_url"

class ReviewProcess(BasicUnicode, ES7xKeywordField):
    name = "review_process"

class Type(BasicUnicode, ES7xKeywordField):
    name = "type"

class BY(BasicBoolean, ES7xBoolean):
    name = "BY"

class NC(BasicBoolean, ES7xBoolean):
    name = "NC"

class ND(BasicBoolean, ES7xBoolean):
    name = "ND"

class SA(BasicBoolean, ES7xBoolean):
    name = "SA"

class HasOtherCharges(BasicBoolean, ES7xBoolean):
    name = "has_other_charges"

class HasPIDScheme(BasicBoolean, ES7xBoolean):
    name = "has_pid_scheme"

class PlagiarismDetection(BasicBoolean, ES7xBoolean):
    name = "detection"

class HasPreservation(BasicBoolean, ES7xBoolean):
    name = "has_preservation"

class NationalLibrary(BasicUnicode, ES7xKeywordField):
    name = "national_library"

class PreservationService(BasicUnicode, ES7xKeywordField):
    name = "service"

class OAStatement(URL, ES7xKeywordField):
    name = "oa_statement"

class Journal(URL, ES7xKeywordField):
    name = "journal"

class AimsScope(URL, ES7xKeywordField):
    name = "aims_scope"

class AuthorInstructions(URL, ES7xKeywordField):
    name = "author_instructions"

class LicenseTerms(URL, ES7xKeywordField):
    name = "license_terms"

class Code(BasicUnicode, ES7xKeywordField):
    name = "code"

class Term(BasicUnicode, ES7xKeywordField):
    name = "term"

class HasWaiver(BasicBoolean, ES7xBoolean):
    name = "has_waiver"

class LastManualUpdate(UTCDateTimeField, ES7xDateOptionalTime):
    name = "last_manual_update"

class Owner(BasicUnicode, ES7xKeywordField):
    name = "owner"

class EditorGroup(BasicUnicode, ES7xKeywordField):
    name = "editor_group"

class Editor(BasicUnicode, ES7xKeywordField):
    name = "editor"

class Note(BasicUnicode, ES7xKeywordField):
    name = "note"

class Date(UTCDateTimeField, ES7xDateOptionalTime):
    name = "date"

class AuthorID(BasicUnicode, ES7xKeywordField):
    name = "author_id"

###############################################
# Journal specific fields

class InDOAJ(BasicBoolean, ES7xBoolean):
    name = "in_doaj"

class Ticked(BasicBoolean, ES7xBoolean):
    name = "ticked"

class CurrentApplication(BasicUnicode, ES7xKeywordField):
    name = "current_application"

class ApplicationID(BasicUnicode, ES7xKeywordField):
    name = "application_id"

class DateAccepted(UTCDateTimeField, ES7xDateOptionalTime):
    name = "date_accepted"

class RelatedApplicationStatus(BasicUnicode, ES7xKeywordField):
    name = "status"

###############################################
## Application specific fields

class CurrentJournal(BasicUnicode, ES7xKeywordField):
    name = "current_journal"

class RelatedJournal(BasicUnicode, ES7xKeywordField):
    name = "related_journal"

class ApplicationStatus(BasicUnicode, ES7xKeywordField):
    name = "application_status"

class DateApplication(UTCDateTimeField, ES7xDateOptionalTime):
    name = "date_applied"

class ApplicationType(BasicUnicode, ES7xKeywordField):
    name = "application_type"

###############################################
## Index fields

# TODO