<input name="${field.name}"\
% if field.raw_value:
value="${field.raw_value}"
% endif
data-dojo-type="dijit.form.NumberSpinner"
% if field.min is not None or field.max is not None:
data-dojo-props="constraints: {${h.render_spinner_constraints(field)}}"
% endif
/>

