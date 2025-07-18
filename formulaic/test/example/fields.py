from formulaic.core import Field, Coerce
from formulaic.coerce import Unicode, Integer, LowerCase, UpperCaseUnicode
from formulaic.fields import BasicUnicode, BasicBoolean, DateField, UTCDateTimeField, IntegerField
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

#############################################
## Common reusable fields

class ID(BasicUnicode):
    name = "id"

class CreatedDate(UTCDateTimeField):
    name = "created_date"

class LastUpdated(UTCDateTimeField):
    name = "last_updated"

class Scheme(BasicUnicode):
    name = "scheme"

class Value(BasicUnicode):
    name = "value"

class Name(BasicUnicode):
    name = "name"

class Country(Field):
    name = "country"
    coerce = [CountryCode]
    allow_coerce_failure = True

class ESType(BasicUnicode):
    name = "es_type"

############################################
# Field elements

class AlternativeTitle(BasicUnicode):
    name = "alternative_title"

class BOAI(BasicBoolean):
    name = "boai"

class EISSN(ISSN):
    name = "eissn"

class PISSN(ISSN):
    name = "pissn"

class DiscontinuedDate(DateField):
    name = "discontinued_date"

class PublicationTimeWeeks(IntegerField):
    name = "publication_tile_weeks"

class Title(BasicUnicode):
    name = "title"

class OAStart(IntegerField):
    name = "oa_start"

class IsReplacedBy(ISSN):
    name = "is_replaced_by"
    allow_coerce_failure = True

class Keywords(Field):
    name = "keywords"
    corece = [Unicode, LowerCase],

class Language(Field):
    name = "language"
    coerce = [ISOLang2LetterLax]

class Replaces(ISSN):
    name = "replaces"
    allow_coerce_failure = True

class Labels(BasicUnicode):
    name = "labels"
    allowed_values = ["s2o"]

class HasAPC(BasicBoolean):
    name = "has_apc"

class Currency(Field):
    name = "currency"
    coerce = [CurrencyCodeLax]

class Price(Field):
    name = "price"
    coerce = [Integer]

class LicenceDisplayExampleURL(URL):
    name = "license_display_example_url"

class LicenceDisplay(BasicUnicode):
    name = "license_display"
    allowed_values = ["Embed", "Display", "No"]

class AuthorRetainsCopyright(BasicBoolean):
    name = "author_retains"

class HasPolicy(BasicBoolean):
    name = "has_policy"

class IsRegistered(BasicBoolean):
    name = "is_registered"

class DepositPolicyService(BasicUnicode):
    name = "service"

class ReviewURL(URL):
    name = "review_url"

class BoardURL(URL):
    name = "board_url"

class ReviewProcess(BasicUnicode):
    name = "review_process"

class Type(BasicUnicode):
    name = "type"

class BY(BasicBoolean):
    name = "BY"

class NC(BasicBoolean):
    name = "NC"

class ND(BasicBoolean):
    name = "ND"

class SA(BasicBoolean):
    name = "SA"

class HasOtherCharges(BasicBoolean):
    name = "has_other_charges"

class HasPIDScheme(BasicBoolean):
    name = "has_pid_scheme"

class PlagiarismDetection(BasicBoolean):
    name = "detection"

class HasPreservation(BasicBoolean):
    name = "has_preservation"

class NationalLibrary(BasicUnicode):
    name = "national_library"

class PreservationService(BasicUnicode):
    name = "service"

class OAStatement(URL):
    name = "oa_statement"

class Journal(URL):
    name = "journal"

class AimsScope(URL):
    name = "aims_scope"

class AuthorInstructions(URL):
    name = "author_instructions"

class LicenseTerms(URL):
    name = "license_terms"

class Code(BasicUnicode):
    name = "code"

class Term(BasicUnicode):
    name = "term"

class HasWaiver(BasicBoolean):
    name = "has_waiver"

class LastManualUpdate(UTCDateTimeField):
    name = "last_manual_update"

class Owner(BasicUnicode):
    name = "owner"

class EditorGroup(BasicUnicode):
    name = "editor_group"

class Editor(BasicUnicode):
    name = "editor"

class Note(BasicUnicode):
    name = "note"

class Date(UTCDateTimeField):
    name = "date"

class AuthorID(BasicUnicode):
    name = "author_id"

###############################################
# Journal specific fields

class InDOAJ(BasicBoolean):
    name = "in_doaj"

class Ticked(BasicBoolean):
    name = "ticked"

class CurrentApplication(BasicUnicode):
    name = "current_application"

class ApplicationID(BasicUnicode):
    name = "application_id"

class DateAccepted(UTCDateTimeField):
    name = "date_accepted"

class RelatedApplicationStatus(BasicUnicode):
    name = "status"

###############################################
## Application specific fields

class CurrentJournal(BasicUnicode):
    name = "current_journal"

class RelatedJournal(BasicUnicode):
    name = "related_journal"

class ApplicationStatus(BasicUnicode):
    name = "application_status"

class DateApplication(UTCDateTimeField):
    name = "date_applied"

class ApplicationType(BasicUnicode):
    name = "application_type"

###############################################
## Index fields

# TODO