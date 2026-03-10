from typing import Union, Optional, Set

from formulaic.core import Field, StructRef, Structure, SINGLE, REPEATABLE, UNIQUE, DUPLICABLE, OPTIONAL, REQUIRED
from formulaic.lib import unity
from formulaic.objects import FormulaicObject


class HTMLGenerator:
    def _make_tag(self, tag_name, attributes=None, close=True, content=None):
        """
        Create an HTML tag with the given name and attributes.
        """
        if content is None:
            content = ''

        attrs = ""
        if attributes is not None:
            attrs = ' '.join(f'{key}="{value}"' for key, value in attributes.items())
            attrs = " " + attrs if attrs else ""

        if close:
            return f'<{tag_name}{attrs}>{content}</{tag_name}>'
        else:
            return f'<{tag_name}{attrs} />'

#######################################
## Form structures

class FormField(Field):
    label = "_label"
    control_class = None
    options = []
    default = None
    placeholder = None
    js = []
    attributes = {}
    disabled = False
    multivalue = False
    repeatable = None
    conditional = False
    field_render_class = None
    control_render_class = None

    def __init__(self, need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=UNIQUE,
                 parent=None,
                 check_coherence=False,
                 fieldset=None,
                 fs_pos=0):
        """
        Initialize the field with its properties.

        :param need: Is the field required or optional? Use REQUIRED or OPTIONAL.
        :param multiplicity: Is the field single or repeatable? Use SINGLE or REPEATABLE.
        :param duplicability: Is the field unique or duplicable? Use UNIQUE or DUPLICABLE. Applies to repeatable fields only, ignored in other cases.
        :param parent: The containing Structure.  May be left as None, and will be populated when the structure is initialized.
        :param check_coherence: Should the properties of the field be checked for coherence? If True, then the field will check that the properties are coherent with each other.  Useful for testing, not recommended for general usage.
        """
        self._fieldset = fieldset if fieldset is not None else DefaultFieldset
        self._fs_pos = fs_pos
        super(FormField, self).__init__(need=need, multiplicity=multiplicity, duplicability=duplicability, parent=parent, check_coherence=check_coherence)

    def get_options(self):
        if isinstance(self.options, list):
            return self.options
        elif callable(self.options):
            return self.options()
        return []

    def get_control(self):
        if self.control_class is None:
            raise ValueError("Field control not defined")
        return self.control_class(self)

    def get_field_renderer(self, context:"ContextualForm"):
        if self.field_render_class is not None:
            return self.field_render_class(context, self)
        else:
            from formulaic.forms.renderers import DefaultFieldRenderer
            return DefaultFieldRenderer(context, self)

    def get_control_renderer(self, context:"ContextualForm"):
        if self.control_render_class is not None:
            return self.control_render_class(context, self)
        else:
            from formulaic.forms.renderers import DefaultFormControlRenderer
            return DefaultFormControlRenderer(context, self)

    @property
    def fieldset(self):
        """
        Returns the fieldset associated with this field.
        """
        return self._fieldset

    @property
    def fs_pos(self):
        return self._fs_pos

    def clone(self):
        """
        Clone the field, returning a new instance with the same properties.
        """
        return self.__class__(need=self.need,
                              multiplicity=self.multiplicity,
                              duplicability=self.duplicability,
                              parent=self.parent,
                              fieldset=self.fieldset,
                              fs_pos=self.fs_pos)


#######################################
## Form Structure elements.  Consists of 3 cooperating classes
## 1. The FormGroup, a Structure subclass, which defines the structure
## 2. The FormStructRef, a StructRef subclass, which defines the reference to the structure, and all the operational methods
## 3. The FormGroupInfo class, which defines the rendering and other information about the form, which is attached to the FormGroup Structure class

class FormGroupStructRef(StructRef):
    def __init__(self, struct: Union["Structure", "Structure.__class__"],
                 need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None,
                 fieldset:"Fieldset"=None,
                 fs_pos:int=0):
        self._fieldset:"Fieldset" = fieldset
        self._fs_pos:int = fs_pos

        super(FormGroupStructRef, self).__init__(struct=struct,
                                                 need=need,
                                                 multiplicity=multiplicity,
                                                 duplicability=duplicability,
                                                 parent=parent)

    @property
    def fieldset(self) -> "Fieldset":
        """
        Returns the fieldset associated with this structure reference.
        """
        return self._fieldset

    @property
    def fs_pos(self) -> int:
        return self._fs_pos

    @property
    def fieldsets(self):
        known_fieldsets: Set[Fieldset] = set()
        subs = self.struct.ref_.all
        for sub in subs:
            fs = unity.get_prop(sub, "fieldset")
            known_fieldsets.add(fs)

        # assemble all fieldsets listed with ordering in the correct order
        ordered = []
        for fs in self.struct._form_group_info.fieldset_ordering:
            if fs in known_fieldsets:
                ordered.append(fs)
                known_fieldsets.remove(fs)

        # all remaining fieldsets that were not ordered
        ordered.extend(known_fieldsets)

        return ordered

    def get_fieldset_fields(self, fieldset: "Fieldset"):
        subs = self.struct.ref_.all
        fields = []
        for sub in subs:
            fs = unity.get_prop(sub, "fieldset")
            if fs == fieldset:
                fields.append(sub)

        sorted_fields = sorted(fields, key=lambda f: unity.get_prop(f, "fs_pos") or 0)
        return sorted_fields

    def draw(self, context:"ContextualForm"):
        r = self.get_renderer(context)
        return r.draw()

    def get_renderer(self, context:"ContextualForm"):
        if self._struct._form_group_info.render_class is not None:
            return self._struct._form_group_info.render_class(context, self._struct)
        else:
            from formulaic.forms.renderers import DefaultGroupRenderer
            return DefaultGroupRenderer(context, self._struct)


    def clone(self):
        """
        Clone the structure reference, returning a new instance with the same properties.
        """
        return self.struct.__class__(need=self.need,
                              multiplicity=self.multiplicity,
                              duplicability=self.duplicability,
                              parent=self.parent,
                              fieldset=self.fieldset,
                              fs_pos=self.fs_pos)

class FormGroup(Structure):
    _form_group_info:"FormGroupInfo" = None
    ref_class_:FormGroupStructRef = FormGroupStructRef
    # ref_:FormGroupStructRef

    def __init__(self, need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None,
                 fieldset=None,
                 fs_pos=0):
        super().__init__(need=need,
                         multiplicity=multiplicity,
                         duplicability=duplicability,
                         parent=parent,
                         fieldset=fieldset,
                         fs_pos=fs_pos)

class FormGroupInfo:
    label = "_label"
    js = []
    repeatable = None
    conditional = False
    render_class = None
    fieldset_ordering: list["Fieldset"] = []


class FormStructRef(StructRef):
    def __init__(self, struct: Union["Structure", "Structure.__class__"],
                 need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None):
        super(FormStructRef, self).__init__(struct=struct,
                                                 need=need,
                                                 multiplicity=multiplicity,
                                                 duplicability=duplicability,
                                                 parent=parent)

    def draw(self, context:"ContextualForm"):
        r = self.get_renderer(context)
        return r.draw()

    def get_renderer(self, context:"ContextualForm"):
        if self.struct._form_info.render_class is not None:
            return self._struct._form_info.render_class(context, self._struct)
        else:
            from formulaic.forms.renderers import DefaultFormRenderer
            return DefaultFormRenderer(context, self._struct)

    @property
    def fieldsets(self):
        known_fieldsets: Set[Fieldset] = set()
        subs = self.struct.ref_.all
        for sub in subs:
            fs = unity.get_prop(sub, "fieldset")
            known_fieldsets.add(fs)

        # assemble all fieldsets listed with ordering in the correct order
        ordered = []
        for fs in self.struct._form_info.fieldset_ordering:
            if fs in known_fieldsets:
                ordered.append(fs)
                known_fieldsets.remove(fs)

        # all remaining fieldsets that were not ordered
        ordered.extend(known_fieldsets)

        return ordered

    def get_fieldset_fields(self, fieldset:"Fieldset"):
        subs = self.struct.ref_.all
        fields = []
        for sub in subs:
            fs = unity.get_prop(sub, "fieldset")
            if fs == fieldset:
                fields.append(sub)

        sorted_fields = sorted(fields, key=lambda f: unity.get_prop(f, "fs_pos") or 0)
        return sorted_fields


class Form(Structure):
    _form_info: "FormInfo" = None
    ref_class_: FormStructRef = FormStructRef
    # ref_: FormStructRef

    def __init__(self, need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None):
        super().__init__(need=need,
                         multiplicity=multiplicity,
                         duplicability=duplicability,
                         parent=parent)

class FormInfo:
    render_class: "FormRenderer" = None
    action: Optional[str] = None
    method: str = "post"
    fieldset_ordering: list["Fieldset"] = []

###########################################
## Representation of the fieldset

class Fieldset:
    name = "_fieldset"
    label = "_label"
    render_class = None

    @classmethod
    def draw(cls, context:"ContextualForm"):
        r = cls.get_renderer(context)
        return r.draw()

    @classmethod
    def get_renderer(cls, context:"ContextualForm"):
        if cls.render_class is not None:
            return cls.render_class(context, cls)
        else:
            from formulaic.forms.renderers import DefaultFieldsetRenderer
            return DefaultFieldsetRenderer(context, cls)


class DefaultFieldset(Fieldset):
    name = "default_fieldset"
    label = "Default"

#############################################
## The Contextual Form, which pulls together the specific
## form structure and its presentation in this particular context

class ContextualForm(FormulaicObject):
    def draw(self):
        r = self.get_renderer()
        return r.draw()

    def get_renderer(self):
        klazz = self.struct.ref_.get_renderer(self)
        if klazz is not None:
            return klazz(self)
        else:
            from formulaic.forms.renderers import DefaultFormRenderer
            return DefaultFormRenderer(self)

# class ContextualForm:
#     name:str = "_form_context"
#     form_structure: Structure = None
#     render_class:"FormRenderer" = None
#     action:Optional[str] = None
#     method:str = "post"
#     fieldset_ordering:list[Fieldset] = []
#
#     def draw(self):
#         r = self.get_renderer()
#         return r.draw()
#
#     def get_renderer(self):
#         if self.render_class is not None:
#             return self.render_class(self)
#         else:
#             from formulaic.forms.renderers import DefaultFormRenderer
#             return DefaultFormRenderer(self)
#
#     @property
#     def fieldsets(self):
#         known_fieldsets: Set[Fieldset] = set()
#         subs = self.form_structure.ref_.all
#         for sub in subs:
#             fs = unity.get_prop(sub, "fieldset")
#             known_fieldsets.add(fs)
#
#         # assemble all fieldsets listed with ordering in the correct order
#         ordered = []
#         for fs in self.fieldset_ordering:
#             if fs in known_fieldsets:
#                 ordered.append(fs)
#                 known_fieldsets.remove(fs)
#
#         # all remaining fieldsets that were not ordered
#         ordered.extend(known_fieldsets)
#
#         return ordered
#
#     def get_fieldset_fields(self, fieldset:Fieldset):
#         subs = self.form_structure.ref_.all
#         fields = []
#         for sub in subs:
#             fs = unity.get_prop(sub, "fieldset")
#             if fs == fieldset:
#                 fields.append(sub)
#
#         sorted_fields = sorted(fields, key=lambda f: unity.get_prop(f, "fs_pos") or 0)
#         return sorted_fields