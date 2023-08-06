<% requirements = set(['dijit/form/Form', 'dojo/parser', 'dojo/domReady']) %>
<%def name="render_tabular(container)">
% for fname, field in container.__fields__.items():
    % if h.is_container(field):
        ${render_tabular(field)}
    % else:
    <tr>
    <%
require, rendering = field.render(form=form)
if require:
    requirements.add(require)
endif
    %>
    <td>${field.label}</td>
    <td>${rendering}</td>
    <td></td>
    </tr>
    % endif
% endfor
</%def>

<div\
   data-dojo-type='dijit.form.Form'
   % if 'action' in form.kwargs:
   action = "${form.kwargs['action']}"
   % endif
   % if 'method' in form.kwargs:
   method = "${form.kwargs['method']}"
   % endif
   % if form.has_uploads():
   enctype="multipart/form-data"
   % endif
   id="${form.id}"
   data-dojo-props="id: '${form.id}'"
>
    <table>
    <tbody>
    ${render_tabular(form)}
    </tbody>
    </table>
</div>
<script type="text/javascript">
    require([${h.render_requirements(requirements)}]\
    % if form.kwargs.get('do_parsing', False):
    , function () {
        dojo.parser.parse(dojo.byId('${form.id}').parentElement);
    % if form.kwargs.get('ajax_submit', None):
        require(['dojo/request/xhr', 'dojo/dom-form'],
            function (xhr, domForm) {
                dijit.registry.byId('${form.id}').onSubmit = function (ev) {
                    dojo.stopEvent(ev);
                    if (!this.validate()) {
                        return;
                    }
                    xhr(
                        this.action,
                        {data: domForm.toObject(this.id), method: 'POST'}
                    ).then(${form.kwargs['ajax_submit']});
                };
        });
    % endif
    % if form.kwargs.get('iframe_submit', None):
        require(['dojo/request/iframe', 'dojo/dom-form'],
            function (iframe, domForm) {
                dijit.registry.byId('${form.id}').onSubmit = function (ev) {
                    dojo.stopEvent(ev);
                    if (!this.validate()) {
                        return;
                    }
                    iframe(
                        this.action,
                        {form: this.id, method: 'POST'}
                    ).then(${form.kwargs['iframe_submit']});
                };
        });
    % endif
    }
    % endif
);
</script>
