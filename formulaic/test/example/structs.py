from formulaic.core import Structure, REQUIRED, OPTIONAL, REPEATABLE, SINGLE, StructRef

from formulaic.test.example import fields

#################################################
## Bibjson structures

## APC ####################

class MaxAPC(Structure):
    _name = "max"

    price = fields.Price(REQUIRED, SINGLE)
    currency = fields.Currency(OPTIONAL, SINGLE)

class APC(Structure):
    _name = "apc"

    has_apc = fields.HasAPC(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)
    max = MaxAPC(OPTIONAL, SINGLE)

############################

class Article(Structure):
    _name = "article"

    license_display = fields.LicenceDisplay(OPTIONAL, SINGLE)
    license_display_example_url = fields.LicenceDisplayExampleURL(OPTIONAL, SINGLE)

class Copyright(Structure):
    _name = "copyright"

    author_retains_copyright = fields.AuthorRetainsCopyright(OPTIONAL, SINGLE)
    url = fields.URL(REQUIRED, SINGLE)

class DepositPolicy(Structure):
    _name = "deposit_policy"

    has_policy = fields.HasPolicy(OPTIONAL, SINGLE)
    is_registered = fields.IsRegistered(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)
    service = fields.DepositPolicyService(OPTIONAL, REPEATABLE)

class Editorial(Structure):
    _name = "editorial"

    review_url = fields.URL(OPTIONAL, SINGLE)
    board_url = fields.URL(OPTIONAL, SINGLE)
    review_process = fields.ReviewProcess(OPTIONAL, REPEATABLE)

class Institution(Structure):
    _name = "institution"

    name = fields.Name(OPTIONAL, SINGLE)
    country = fields.Country(OPTIONAL, SINGLE)

class License(Structure):
    _name = "license"

    type = fields.Type(OPTIONAL, SINGLE)
    by = fields.BY(OPTIONAL, SINGLE)
    nc = fields.NC(OPTIONAL, SINGLE)
    nd = fields.ND(OPTIONAL, SINGLE)
    sa = fields.SA(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)

class OtherCharges(Structure):
    _name = "other_charges"

    has_other_charges = fields.HasOtherCharges(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)

class PIDScheme(Structure):
    _name = "pid_scheme"

    has_pid_scheme = fields.HasPIDScheme(OPTIONAL, SINGLE)
    scheme = fields.Scheme(OPTIONAL, REPEATABLE)

class Plagiarism(Structure):
    _name = "plagiarism"

    detection = fields.PlagiarismDetection(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)

class Preseravation(Structure):
    _name = "preservation"

    has_preservation = fields.HasPreservation(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)
    national_library = fields.NationalLibrary(OPTIONAL, REPEATABLE)
    service = fields.PreservationService(OPTIONAL, REPEATABLE)

class Publisher(Structure):
    _name = "publisher"

    name = fields.Name(OPTIONAL, SINGLE)
    country = fields.Country(OPTIONAL, SINGLE)

class Ref(Structure):
    _name = "ref"

    oa_statement = fields.OAStatement(OPTIONAL, SINGLE)
    journal = fields.Journal(OPTIONAL, SINGLE)
    aims_scope = fields.AimsScope(OPTIONAL, SINGLE)
    author_instructions = fields.AuthorInstructions(OPTIONAL, SINGLE)
    license_terms = fields.LicenseTerms(OPTIONAL, SINGLE)

class Subject(Structure):
    _name = "subject"

    code = fields.Code(OPTIONAL, SINGLE)
    scheme = fields.Scheme(OPTIONAL, SINGLE)
    term = fields.Term(OPTIONAL, SINGLE)

class Waiver(Structure):
    _name = "waiver"

    has_waiver = fields.HasWaiver(OPTIONAL, SINGLE)
    url = fields.URL(OPTIONAL, SINGLE)

###############################################

class BibJSON(Structure):
    _name = "bibjson"

    # single fields
    alternative_title = fields.AlternativeTitle(OPTIONAL, SINGLE)
    boai = fields.BOAI(OPTIONAL, SINGLE)
    eissn = fields.EISSN(OPTIONAL, SINGLE)
    pissn = fields.PISSN(OPTIONAL, SINGLE)
    discontinued_date = fields.DiscontinuedDate(OPTIONAL, SINGLE)
    publication_time_weeks = fields.PublicationTimeWeeks(OPTIONAL, SINGLE)
    title = fields.Title(OPTIONAL, SINGLE)
    oa_start = fields.OAStart(OPTIONAL, SINGLE)

    # single structures
    apc = APC(OPTIONAL, SINGLE)
    article = Article(OPTIONAL, SINGLE)
    copyright = Copyright(OPTIONAL, SINGLE)
    deposit_policy = DepositPolicy(OPTIONAL, SINGLE)
    editorial = Editorial(OPTIONAL, SINGLE)
    institution = Institution(OPTIONAL, SINGLE)
    other_charges = OtherCharges(OPTIONAL, SINGLE)
    pid_scheme = PIDScheme(OPTIONAL, SINGLE)
    plagiarism = Plagiarism(OPTIONAL, SINGLE)
    preservation = Preseravation(OPTIONAL, SINGLE)
    publisher = Publisher(OPTIONAL, SINGLE)
    ref = Ref(OPTIONAL, SINGLE)
    waiver = Waiver(OPTIONAL, SINGLE)

    # repeatable fields
    is_replaced_by = fields.IsReplacedBy(OPTIONAL, REPEATABLE)
    keywords = fields.Keywords(OPTIONAL, REPEATABLE)
    language = fields.Language(OPTIONAL, REPEATABLE)
    replaces = fields.Replaces(OPTIONAL, REPEATABLE)
    labels = fields.Labels(OPTIONAL, REPEATABLE)

    # repeatable structures
    license = License(OPTIONAL, REPEATABLE)
    subject = Subject(OPTIONAL, REPEATABLE)


####################################################
## Admin structures

class RelatedApplications(Structure):
    _name = "related_applications"

    application_id = fields.ApplicationID(OPTIONAL, SINGLE)
    date_accepted = fields.DateAccepted(OPTIONAL, SINGLE)
    status = fields.ApplicationStatus(OPTIONAL, SINGLE)

class Notes(Structure):
    _name = "notes"

    id = fields.ID(OPTIONAL, SINGLE)
    note = fields.Note(OPTIONAL, SINGLE)
    date = fields.Date(OPTIONAL, SINGLE)
    author_id = fields.AuthorID(OPTIONAL, SINGLE)

class SharedAdmin(Structure):
    _name = "shared_admin"

    # single fields
    owner = fields.Owner(OPTIONAL, SINGLE)
    editor_group = fields.EditorGroup(OPTIONAL, SINGLE)
    editor = fields.Editor(OPTIONAL, SINGLE)

    # repeated structures
    notes = Notes(OPTIONAL, REPEATABLE)

################################################
## Journal Structures

class JournalLike(Structure):
    _name = "journal_like"

    # single fields
    id = fields.ID(OPTIONAL, SINGLE)
    created_date = fields.CreatedDate(OPTIONAL, SINGLE)
    last_updated = fields.LastUpdated(OPTIONAL, SINGLE)
    last_manual_update = fields.LastManualUpdate(OPTIONAL, SINGLE)
    es_type = fields.ESType(OPTIONAL, SINGLE)

    # single structures
    admin = SharedAdmin(OPTIONAL, SINGLE)
    bibjson = BibJSON(OPTIONAL, SINGLE)

class JournalAdmin(SharedAdmin):
    _name = "admin"

    # single fields
    in_doaj = fields.InDOAJ(OPTIONAL, SINGLE)
    ticked = fields.Ticked(OPTIONAL, SINGLE)
    current_application = fields.CurrentApplication(OPTIONAL, SINGLE)

    # repeated structures
    related_applications = RelatedApplications(OPTIONAL, REPEATABLE)

class Journal(JournalLike):
    _name = "journal"

    admin = JournalAdmin(OPTIONAL, SINGLE)