<input name="${field.name}"\
% if field.raw_value:
value="${field.raw_value}"
% endif
data-dojo-type="anthrax.AnthraxDateBox"
data-dojo-props="${h.render_date_box_constraints(field)}"
/>

