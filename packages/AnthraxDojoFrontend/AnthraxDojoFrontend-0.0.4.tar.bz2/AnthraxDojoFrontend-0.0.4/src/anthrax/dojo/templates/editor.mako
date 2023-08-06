<% error = form.__errors__[field.name] %>
% if error:
<div class="error">${error.message}</div>
% endif
<input type="hidden" name="${field.name}" id="${field.id}-value" />
<div id="${field.id}-editor" onChange="dojo.byId('${field.id}-value').value = this.getValue();"
data-dojo-type="dijit.Editor"
>
% if field.raw_value:
${field.raw_value}
% endif
</div>
<script type="text/javascript">
require(['dojo/dom-attr'], function (domAttr) {
    domAttr.set(dojo.byId('${field.id}-value'), 'value',
        dojo.byId('${field.id}-editor').innerHTML);
});
</script>

