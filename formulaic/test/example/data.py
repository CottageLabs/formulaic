JOURNAL_LIKE_BIBJSON = {
    "alternative_title": "Alternative Title",
    "apc": {
        "max": [
            {"currency": "GBP", "price": 2}
        ],
        "url": "http://apc.com",
        "has_apc": True
    },
    "article": {
        "license_display": ["Embed"],
        "license_display_example_url": "http://licence.embedded"
    },
    "boai": True,
    "copyright": {
        "author_retains": True,
        "url": "http://copyright.com"
    },
    "deposit_policy": {
        "has_policy" : True,
        "service": ["Open Policy Finder", "Store it"],
        "url": "http://deposit.policy"
    },
    "discontinued_date": "2001-01-01",
    "editorial": {
        "review_process": ["Open peer review", "some bloke checks it out"],
        "review_url": "http://review.process",
        "board_url": "http://editorial.board"
    },
    "eissn": "9876-5432",
    "is_replaced_by": ["2222-2222"],
    "institution": {
        "name": "Society Institution",
        "country": "US"
    },
    "keywords": ["word", "key"],
    "labels": ["s2o"],
    "language": ["EN", "FR"],
    "license": [
        {
            "type": "Publisher's own license",
            "BY": True,
            "NC": True,
            "ND": False,
            "SA": False,
            "url": "http://licence.url"
        }
    ],
    "oa_start": 2012,
    "other_charges": {
        "has_other_charges" : True,
        "url": "http://other.charges"
    },
    "pid_scheme": {
        "has_pid_scheme" : True,
        "scheme": ["DOI", "ARK", "PURL", "PIDMachine"],
    },
    "pissn": "1234-5678",
    "plagiarism": {
        "detection": True,
        "url": "http://plagiarism.screening"
    },
    "preservation": {
        "has_preservation" : True,
        "service": ["LOCKSS", "CLOCKSS", "A safe place"],
        "national_library": ["Trinity", "Imperial"],
        "url": "http://digital.archiving.policy"
    },
    "publication_time_weeks": 8,
    "publisher": {
        "name": "The Publisher",
        "country": "US"
    },
    "ref": {
        "oa_statement": "http://oa.statement",
        "journal": "http://journal.url",
        "aims_scope": "http://aims.scope",
        "author_instructions": "http://author.instructions.com",
        "license_terms": "http://licence.url"
    },
    "replaces": ["1111-1111"],
    "subject": [
        {"scheme": "LCC", "term": "Economic theory. Demography",
         "code": "HB1-3840"},
        {"scheme": "LCC", "term": "Social Sciences", "code": "H"},
        {"scheme": "LCC", "term": "Veterinary medicine", "code": "SF600-1100"}
    ],
    "title": "The Title",
    "waiver": {
        "has_waiver" : True,
        "url": "http://waiver.policy"
    }
}

JOURNAL_SOURCE = {
    "id": "abcdefghijk_journal",
    "created_date": "2000-01-01T00:00:00Z",
    "last_manual_update": "2001-01-01T00:00:00Z",
    "last_updated": "2002-01-01T00:00:00Z",
    "admin": {
        "current_application": "qwertyuiop",
        "editor_group": "editorgroup",
        "editor": "associate",
        "in_doaj": False,
        "notes": [
            {"note": "Second Note", "date": "2014-05-22T00:00:00Z", "id": "1234",
             "author_id": "fake_account_id__b"},
            {"note": "First Note", "date": "2014-05-21T14:02:45Z", "id": "abcd",
             "author_id": "fake_account_id__a"},
        ],
        "owner": "publisher",
        "related_applications": [
            {"application_id": "asdfghjkl", "date_accepted": "2018-01-01T00:00:00Z"},
            {"application_id": "zxcvbnm"}
        ],
        "ticked": True
    },
    "bibjson": JOURNAL_LIKE_BIBJSON
}

JOURNAL_FORM = {
    "basic_compliance": {
        "boai": "y",
        "oa_statement_url": "https://cottagelabs.com/"
    },
    "about_the_journal": {
        "language": ["FRE", "ESP"]
    },
    "apc": {
        "apc": "y",
        "apc_charges": [
            {
                "apc_currency": "GBP",
                "apc_max": 1000
            }
        ]
    }
}

JOURNAL_BROWSER_FORM = {
    "boai": "y",
    "oa_statement_url": "https://cottagelabs.com/",
    "title": "",
    "alternative_title": "",
    "journal_url": "",
    "pissn": "",
    "eissn": "",
    "keywords": "",
    "language-0": "FRE",
    "language-1": "ESP",
    "language-2": "",
    "language-3": "",
    "language-4": "",
    "publisher_name": "",
    "publisher_country": "",
    "institution_name": "",
    "institution_country": "",
    "license_terms_url": "",
    "license_display_example_url": "",
    "apc": "y",
    "apc_charges-0-apc_currency": "GBP",
    "apc_charges-0-apc_max": "1000",
    "apc_charges-1-apc_currency": "",
    "apc_charges-1-apc_max": "",
    "apc_charges-2-apc_currency": "",
    "apc_charges-2-apc_max": "",
    "apc_charges-3-apc_currency": "",
    "apc_charges-3-apc_max": "",
    "apc_charges-4-apc_currency": "",
    "apc_charges-4-apc_max": ""
}

if __name__ == "__main__":
    from formulaic.test.example.structs import JournalStructure
    from formulaic.serialise.json.json import JSONSerialiser

    struct = JournalStructure()
    serialiser = JSONSerialiser()
    out = serialiser.data_to_string(JOURNAL_SOURCE, struct, indent=3, sort_keys=True)
    print(out)