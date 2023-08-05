<div style="margin-bottom: 20px;">
    <h4>Global template vars</h4>
    % for key in result['global_keys']:
        <strong>${key}</strong>&nbsp;&nbsp;&nbsp;
    % endfor
</div>

<h4>Template inheritance tree</h4>
% for i, tmpl in enumerate(result['tmpl_inherits']):
    ${'&nbsp;' * i*6|n} ${tmpl}<br />
% endfor

<h4>Template vars</h4>
% if result['tmpl_vars']:
    <table>
        <thead>
            <tr>
                <th>Key</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            % for i, (k, v) in enumerate(result['tmpl_vars']):
                <tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
                    <td>${k|h}</td>
                    <td>${unicode(v)|h}</td>
                </tr>
            % endfor
        </tbody>
    </table>
% else:
    <p>No vars were returned in current rendering.</p>
% endif
