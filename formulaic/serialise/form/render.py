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

"""
Form rendering is done via a set of renderer classes which represent each
part of the hierarchical nature of the form.  The form structure is as
follows

FORM
    |-- FIELD
        |-- FORM CONTROL
    |-- COMPOUND
        |-- FIELD (as above)
        |-- COMPOUND (ad infinitum)
        |-- LIST (as below)
    |-- FIELDSET
        |-- FIELD (as above)
        |-- COMPOUND (as above)
        |-- FIELDSET (ad infinitum)
        |-- LIST (as below)
    |-- LIST
        |-- FIELD (as above)
        |-- COMPOUND (as above)
        |-- FIELDSET (as above)

Therefore we define renderers for each layer in the hierarchy, and a renderer is responsible
for calling those lower down the hierarchy than them.

* FORM: FormHTML
    * Responsible for rendering the <form> tag and calling each fieldset renderer
* FIELDSET: FieldsetHTML
    * Responsible for rendering the <fieldset> tag and calling each field and group renderer
* LIST: ElementListHTML
    * Responsible for rendering the containers for lists of other elements
* COMPOUND: CompoundHTML
    * Responsible for rendering a group of fields (or sub groups).  This may include a container, label etc.  This
    would also then render the individual fields (using a FieldHTML) or sub groups (using a CompoundHTML)
* FIELD: FieldHTML
    * Responsible for rendering the field container (not the form control itself).  This would include
        any information about the field as a while, such as error messages, help text etc.
* FORM CONTROL: ControlHTML
    * Responsible for rendering the actual HTML form control(s) for a field.  This will include the actual raw
    form control and label, but may also include container and layout for a single form (e.g. placing labels in 
    front of controls, or wrapping each control/label pair in a div/span)
"""

class FormHTML(HTMLGenerator):
    # def __init__(self, context:ContextualForm):
    #     self._context = context

    def draw(self, representation):
        raise NotImplementedError("Subclasses must implement this method.")


class FieldsetHTML(HTMLGenerator):
    # def __init__(self, context:ContextualForm, fieldset:Fieldset.__class__):
    #     self._fieldset = fieldset
    #     self._context = context

    def draw(self, representation):
        raise NotImplementedError("Subclasses must implement this method.")

class ElementListHMTL(HTMLGenerator):
    def draw(self, representation):
        raise NotImplementedError("Subclasses must implement this method.")

class CompoundHTML(HTMLGenerator):
    # def __init__(self, context:ContextualForm, group:FormGroup):
    #     self._context = context
    #     self._group = group

    def draw(self, representation):
        raise NotImplementedError("Subclasses must implement this method.")

class FieldHTML(HTMLGenerator):
    # def __init__(self, context:ContextualForm, field:FormField):
    #     self._context = context
    #     self._field = field

    def draw(self, representation):
        raise NotImplementedError("Subclasses must implement this method.")


class ControlHTML(HTMLGenerator):
    # def __init__(self, context:ContextualForm, field:FormField):
    #     self._context = context
    #     self._field = field

    def draw(self, representation):
        raise NotImplementedError("Subclasses must implement this method.")


###################################################
## Default implementations

class DefaultFormHTML(FormHTML):
    def draw(self, representation):
        element_frags = []
        for element in representation.get("elements"):
            match element.get("type"):
                case "fieldset":
                    fs_capability = element.get("ref")
                    fs_render = fs_capability.get_renderer()
                    element_frags.append(fs_render.draw(element))
                case "compound":
                    c_capability = element.get("ref")
                    c_render = c_capability.get_renderer()
                    element_frags.append(c_render.draw(element))
                case "field":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_renderer()
                    element_frags.append(f_render.draw(element))
                case "list":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_list_renderer()
                    element_frags.append(f_render.draw(element))

        elements_frag = "\n" + "\n".join(element_frags) + "\n"

        ctx = representation.get("ref")
        attrs = ctx.attributes
        attrs["id"] = ctx.struct_ref.name
        attrs["action"] = ctx.action
        attrs["method"] = ctx.method
        html = self._make_tag('form',
                       content=elements_frag,
                       attributes=attrs
                    )

        return html

class DefaultFieldsetHTML(FieldsetHTML):
    def draw(self, representation):
        element_frags = [
            self._make_tag('legend', content=representation.get("ref").label)
        ]
        for element in representation.get("elements"):
            match element.get("type"):
                case "fieldset":
                    fs_capability = element.get("ref")
                    fs_render = fs_capability.get_renderer()
                    element_frags.append(fs_render.draw(element))
                case "compound":
                    c_capability = element.get("ref")
                    c_render = c_capability.get_renderer()
                    element_frags.append(c_render.draw(element))
                case "field":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_renderer()
                    element_frags.append(f_render.draw(element))
                case "list":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_list_renderer()
                    element_frags.append(f_render.draw(element))

        elements_frag = "\n" + "\n".join(element_frags) + "\n"

        ctx = representation.get("ref")
        attrs = ctx.attributes
        attrs["id"] = ctx.struct_ref.name
        html = self._make_tag('fieldset',
                              content=elements_frag,
                              attributes=attrs
                              )

        return html

class DefaultElementListHTML(ElementListHMTL):
    def draw(self, representation):
        label = representation.get("ref").repeatable_label
        if not label:
            label = representation.get("ref").label

        element_frags = [
            self._make_tag('legend', content=label)
        ]

        for element in representation.get("elements"):
            match element.get("type"):
                case "fieldset":
                    fs_capability = element.get("ref")
                    fs_render = fs_capability.get_renderer()
                    element_frags.append(fs_render.draw(element))
                case "compound":
                    c_capability = element.get("ref")
                    c_render = c_capability.get_renderer()
                    element_frags.append(c_render.draw(element))
                case "field":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_renderer()
                    element_frags.append(f_render.draw(element))

        elements_frag = "\n" + "\n".join(element_frags) + "\n"
        html = self._make_tag('fieldset',
                              content=elements_frag
                              )

        return html

class DefaultCompoundHTML(CompoundHTML):
    def draw(self, representation):
        label = representation.get("ref").label
        element_frags = [
            self._make_tag('legend', content=label)
        ]
        for element in representation.get("elements"):
            match element.get("type"):
                case "compound":
                    c_capability = element.get("ref")
                    c_render = c_capability.get_renderer()
                    element_frags.append(c_render.draw(element))
                case "field":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_renderer()
                    element_frags.append(f_render.draw(element))
                case "list":
                    f_capabiltiy = element.get("ref")
                    f_render = f_capabiltiy.get_list_renderer()
                    element_frags.append(f_render.draw(element))

        elements_frag = "\n" + "\n".join(element_frags) + "\n"

        ctx = representation.get("ref")
        attrs = ctx.attributes
        attrs["id"] = ctx.struct_ref.name
        html = self._make_tag('fieldset',
                              content=elements_frag,
                              attributes=attrs
                              )

        return html

class DefaultFieldHTML(FieldHTML):
    def draw(self, representation):
        ctx = representation.get("ref")
        ctrl = representation.get("control")
        c_renderer = ctx.get_control_renderer()

        html = c_renderer.draw(ctrl)
        if len(ctrl) > 1:
            legend = self._make_tag("legend", content=ctx.label)
            html = self._make_tag("fieldset", content="\n" + legend + "\n" + html + "\n")
        html = self._make_tag("div", content="\n" + html + "\n")

        return html

class DefaultControlHTML(ControlHTML):
    def draw(self, representation):
        inl_frags = []
        for control in representation:
            label = control.get("label")
            input = control.get("control")

            label_html = self._make_tag(
                label.get("tag", "label"),
                label.get("attrs", {}),
                close=label.get("close", True),
                content=label.get("content")
            )


            def render_content(content_list):
                if isinstance(content_list, str):
                    return content_list

                if isinstance(content_list, list):
                    contents = []
                    for ic in input_content:
                        ic_content = ic.get("content")
                        rendered_content = render_content(ic_content)
                        contents.append(self._make_tag(ic.get("tag"), ic.get("attrs", {}), close=ic.get("close", True), content=rendered_content))
                    return "\n".join(contents)

                return content_list

            input_content = input.get("content")
            content = render_content(input_content)
            input_html = self._make_tag(input.get("tag"), input.get("attrs", {}), close=input.get("close", True), content=content)

            inl_frags.append(f"{label_html}\n{input_html}")

        html = "\n" + "\n".join(inl_frags) + "\n"
        return html

###########################################
## Debug implementations

class DebugFormHTML(DefaultFormHTML):
    def draw(self, representation):
        html = super().draw(representation)

        ref = representation.get("ref")
        prefix = representation.get("prefix")

        debug_info = []
        debug_info.append(self._make_tag("li", content="Capability: " + repr(ref)))
        debug_info.append(self._make_tag("li", content="Prefix: " + repr(prefix)))
        ul = self._make_tag("ul", attributes={"style": "color: #888888"}, content="\n".join(debug_info))
        html = ul + html

        return html

class DebugListHTML(DefaultElementListHTML):
    def draw(self, representation):
        html = super().draw(representation)

        ref = representation.get("ref")
        prefix = representation.get("prefix")

        debug_info = []
        debug_info.append(self._make_tag("li", content="Capability: " + repr(ref)))
        debug_info.append(self._make_tag("li", content="Prefix: " + repr(prefix)))
        ul = self._make_tag("ul", attributes={"style": "color: #888888"}, content="\n".join(debug_info))
        html = ul + html

        return html

class DebugFieldHTML(DefaultFieldHTML):
    def draw(self, representation):
        html = super().draw(representation)

        ref = representation.get("ref")
        prefix = representation.get("prefix")

        debug_info = []
        debug_info.append(self._make_tag("li", content="Capability: " + repr(ref)))
        debug_info.append(self._make_tag("li", content="Prefix: " + repr(prefix)))
        ul = self._make_tag("ul", attributes={"style": "color: #888888"}, content="\n".join(debug_info))
        html = ul + html

        return html

class DebugControlHTML(DefaultControlHTML):
    def draw(self, representation):
        html = super().draw(representation)

        uls = []
        for control in representation:
            attrs = control.get("control").get("attrs", {})
            lis = []
            for k,v in attrs.items():
                lis.append(self._make_tag("li", content=f"{k}: {v}"))
            uls.append(self._make_tag("ul", attributes={"style": "color: #888888"}, content="\n".join(lis)))

        html = "\n".join(uls) + html
        return html