structures = [
    Top,
    Form
]

crosswalks = [
    ObjectToForm,
    FormToObject
]

ojects = [
    MyDataObject,
    MyForm
]

def document(structures, crosswalks, objects):
    pass

## output

documentation = {
    "<field>" : {
        "definition": "<mod path>",
        "parents": [
            ["<parent>", "<parent>"],
            ["<parent>", "<parent>"]
        ],
        "children": [
            "<child>",
            "<child>"
        ],
        "coerce": ["<coerce>"],
        "validate": ["<validate>"],
        "crosswalks": {
            "<crosswalk>": {
                "mapping": [
                    {"to": "<to>", "transform": "<transform>"}
                ],
                "errors": [
                    {"code": "<code>", "to": "<to>", "transform": "<transform>"}
                ]
            }
        },
        "objects": ["<object>"]
    }
}