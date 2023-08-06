<%namespace name="tw" module="tw.core.mako_util"/>\
<%
    attrs = context.get('attrs')
%>\
<div style="float:left; padding-right:10px;"><select ${tw.attrs(
    [('name', name),
     ('class', css_class),
     ('id', context.get('id'))],
    attrs=attrs
)}>
    % for group, options in grouped_options:
    % if group:
    <optgroup ${tw.attrs([('label', group)])}>
    % endif
        % for value, desc, attrs in options:
        <option ${tw.attrs(
            [('value', value)],
            attrs=attrs
        )}>${tw.content(desc)}</option>
        % endfor
    % if group:
    </optgroup>
    % endif
    % endfor
</select>
</div>
<div class="fielderror" id="${context.get('id',)}_error"></div>
<div style="clear:both;">
    <div>
      <div style="float:left">Add a new ${model_name}:</div>
      <div id="${subform_id}_opener" class="subform-opener subform-opener-closed" onclick="javascript:toggleSubForm('${subform_id}');"></div>
    </div>
    <div style="clear:both;"></div>
    <div style="float:left; clear:both; display:none" id="${subform_id}_wrapper">
       ${add_form(id=subform_id) |n }
       ${subform_js()}
     </div>
</div>