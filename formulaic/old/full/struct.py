from formulaic.core import Field, Structure, Unicode, Boolean, BigEndDate

class BasicUnicode(Field):
    coerce = [Unicode]

class ISSN(Field):
    coerce = [
        {"coerce": Unicode, "allow_coerce_failure": True}
    ]
    validators = [
        IsISSN
    ]

class BasicBoolean(Field):
    coerce = [Boolean]

class DateField(Field):
    coerce = [BigEndDate]

##################################################

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

class PublicationTimeWeeks(Field):
    name = "publication_tile_weeks"
    coerce = [Integer]

class Title(BasicUnicode):
    name = "title"

class OAStart(Field):
    name = "oa_start"
    coerce = [Integer]

class IsReplacecBy(ISSN):
    name = "is_replaced_by"

class Keywords(Field):
    name = "keywords"
    corece = [Unicode, LowerCase],

class Language(Field):
    name = "language"
    coerce = [ISOLang2LetterLax]

class Replaces(ISSN):
    name = "replaces"

class Scheme(BasicUnicode):
    name = "scheme"

class Value(BasicUnicode):
    name = "value"

class HasAPC(BasicBoolean):
    name = "has_apc"

class URL(Field):
    name = "url"
    coerce = [
        {"coerce": URL, "allow_corece_failure": True}
    ]

class Currency(Field):
    name = "currency"
    coerce = [CurrencyCodeLax]

class Price(Field):
    name = "price"
    coerce = [Integer]

class MaxAPC(Structure):
    name = "max"
    fields = [
        Currency,
        Price
    ]

class LicenceDisplayExampleURL(URL):
    name = "license_display_example_url"

class ORCID(BasicBoolean):
    name = "orcid"

class I4OC(BasicBoolean):
    name = "i4oc_open_citations"

class LicenceDisplay(BasicUnicode):
    allowed_values = ["Embed", "Display", "No"]

class AuthorRetainsCopyright(BasicBoolean):
    name = "author_retains"

class HasPolicy(BasicBoolean):
    name = "has_policy"

class IsRegistered(BasicBoolean):
    name = "is_registered"

class Service(BasicUnicode):
    name = "service"

class ReviewURL(URL):
    name = "review_url"

class BoardURL(URL):
    name = "board_url"

class ReviewProcess(BasicUnicode):
    name = "review_process"

class Name(BasicUnicode):
    name = "name"

class Country(Field):
    name = "country"
    coerce = [
        {"coerce": CountryCode, "allow_coerce_failure": True}
    ]

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

class PIDSchemeValue(BasicUnicode):
    name = "scheme"

class Detection(BasicBoolean):
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

class ID(BasicUnicode):
    name = "id"

class CreatedDate(UTCDateTime):
    name = "created_date"

class LastUpdated(UTCDateTime):
    name = "last_updated"

class LastManualUpdate(UTCDateTime):
    name = "last_manual_update"

class ESType(BasicUnicode):
    name = "es_type"

class Seal(BasicBoolean):
    name = "seal"

class Owner(BasicUnicode):
    name = "owner"

class EditorGroup(BasicUnicode):
    name = "editor_group"

class Editor(BasicUnicode):
    name = "editor"

class Note(BasicUnicode):
    name = "note"

class Date(UTCDateTime):
    name = "date"

class AuthorID(BasicUnicode):
    name = "author_id"

class InDOAJ(BasicBoolean):
    name = "in_doaj"

class Ticked(BasicBoolean):
    name = "ticked"

class CurrentApplication(BasicUnicode):
    name = "current_application"

##################################################

class APC(Structure):
    name = "apc"
    fields = [
        HasAPC,
        URL
    ]
    lists = [
        MaxAPC
    ]

class Article(Structure):
    name = "article"
    fields = [
        LicenceDisplayExampleURL,
        ORCID,
        I4OC
    ]
    lists = [
        LicenceDisplay
    ]

class Copyright(Structure):
    name = "copyright"
    fields = [
        AuthorRetainsCopyright,
        URL
    ]

class DeppsitPolicy(Structure):
    name = "deposit_policy"
    fields = [
        HasPolicy,
        IsRegistered,
        URL
    ]
    lists = [
        Service
    ]

class Editorial(Structure):
    name = "editorial"
    fields = [
        ReviewURL,
        BoardURL
    ]
    lists = [
        ReviewProcess
    ]

class Institution(Structure):
    name = "institution"
    fields = [
        Name,
        Country
    ]

class Licence(Structure):
    name = "license"
    fields = [
        Type,
        BY,
        NC,
        ND,
        SA,
        URL
    ]

class OtherCharges(Structure):
    name = "other_charges"
    fields = [
        HasOtherCharges,
        URL
    ]

class PIDScheme(Structure):
    name = "pid_scheme"
    fields = [
        HasPIDScheme,
    ]
    lists = [
        PIDSchemeValue
    ]

class Plagiarism(Structure):
    name = "plagiarism"
    fields = [
        Detection,
        URL
    ]

class Preservation(Structure):
    name = "preservation"
    fields = [
        HasPreservation,
        URL
    ],
    lists = [
        NationalLibrary,
        PreservationService
    ]

class Publisher(Structure):
    name = "publisher"
    fields = [
        Name,
        Country
    ]

class Ref(Structure):
    name = "ref"
    fields = [
        OAStatement,
        Journal,
        AimsScope,
        AuthorInstructions,
        LicenseTerms
    ]

class Subject(Structure):
    name = "subject"
    fields = [
        Code,
        Scheme,
        Term
    ]

class Waiver(Structure):
    name = "waiver"
    fields = [
        HasWaiver,
        URL
    ]

class Notes(Structure):
    name = "notes"
    fields = [
        ID,
        Note,
        Date,
        AuthorID
    ]

class RelatedApplications(Structure):
    name = "related_applications"
    fields = [
        BasicUnicode.make("application_id"),
        DateField.make("date_accepted"),
        BasicUnicode.make("status")
    ]

class JournalLikeAdmin(Structure):
    name = "admin"
    fields = [
        Seal,
        Owner,
        EditorGroup,
        Editor
    ]
    lists = [
        Notes
    ]

class JournalAdmin(Structure):
    name = "admin"
    fields = JournalLikeAdmin.fields + [
        InDOAJ,
        Ticked,
        CurrentApplication
    ]
    lists = JournalLikeAdmin.lists + [
        RelatedApplications
    ]

class JournalLikeIndex(Structure):
    name = "index"
    fields = [
        CountryIndex,
        HasAPCIndex,
        HasSealIndex,
        UnpuncTitle,
        AsciiUnpuncTitle,
        Continued,
        HasEditorGroup,
        HasEditor
    ]
    lists = [
        ISSNIndex,
        TitleIndex,
        SubjectIndex,
        ClassificationIndex,
        LanguageIndex,
        LicenseIndex,
        ClassificationPaths,
        SchemaCode,
        SchemaCodesTree
    ]

class JournalIndex(Structure):
    name = "index"
    fields = JournalLikeIndex.fields + [
        PublisherAC,
        InstitutionAC
    ]

##################################################

class JournalBibJSON(Structure):
    name = "bibjson"
    fields = [
        AlternativeTitle,
        BOAI,
        EISSN,
        PISSN,
        DiscontinuedDate,
        PublicationTimeWeeks,
        Title,
        OAStart
    ]
    lists = [
        IsReplacedBy,
        Keywords,
        Language,
        License,
        Replaces,
        Subject
    ]
    objects = [
        APC,
        Article,
        Copyright,
        DepositPolicy,
        Editorial,
        Institution,
        OtherCharges,
        PIDScheme,
        Plagiarism,
        Preservation,
        Publisher,
        Ref,
        Waiver
    ]

###################################################

class JournalCommon(Structure):
    fields = [
        ID,
        CreatedDate,
        LastUpdated,
        LastManualUpdate,
        ESType
    ],
    objects = [
        JournalLikeAdmin,
        JournalLikeIndex
    ]

class JournalStruct(Structure):
    name = "journal"
    # InDOAJ = InDOAJ()
    fields = JournalCommon.fields + [
        InDOAJ,
        Ticked,
        CurrentApplication
    ]
    lists = [
        RelatedApplications
    ]
    objects = [
        JournalIndex,
        JournalAdmin,
        JournalBibJSON
    ]
    validators = []



class JournalCSVStruct(Structure):
    name = "journal_csv",
    fields = [
        AlternativeTitle,
        BasicUnicode.make("apc_charges"),
        URL.make("apc_url"),
        BasicUnicode.make("preservation_service"),
        BasicUnicode.make("preservation_service_library"),
        URL.make("preservation_service_url"),
        BasicUnicode.make("copyright_author_retains"),
        URL.make("copyright_url"),
        Country.make("publisher_country"),
        BasicUnicode.make("deposit_policy"),
        BasicUnicode.make("review_process")
    ]
