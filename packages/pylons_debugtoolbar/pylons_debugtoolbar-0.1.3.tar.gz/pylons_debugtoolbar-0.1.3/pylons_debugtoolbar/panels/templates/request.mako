<%def name="table(values, join_value=False)">
    <table>
        <colgroup>
            <col style="width: 20%"/>
            <col/>
        </colgroup>
        <thead>
            <tr>
                <th>Key</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            % for i, (key, value) in enumerate(values):
                <tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
                    <td>${key|h}</td>
                    % if join_value:
                        <td>${', '.join(value)|h}</td>
                    % else:
                        <td>${value|h}</td>
                    % endif
                </tr>
            % endfor
        </tbody>
    </table>
</%def>


<h4>Controller info</h4>
${table(controller_vars)}

<h4>Route info</h4>
${table(route_vars)}

<h4>Cookie Variables</h4>
% if cookies:
    ${table(cookies)}
% else:
    <p>No cookie data</p>
% endif

<h4>Session Variables</h4>
% if session:
    ${table(session)}
% else:
    <p>No session data</p>
% endif

<h4>GET Variables</h4>
% if get:
    ${table(get, join_value=True)}
% else:
    <p>No GET data</p>
% endif

<h4>POST Variables</h4>
% if post:
    ${table(post, join_value=True)}
% else:
    <p>No POST data</p>
% endif

<h4>Request attributes</h4>
% if attrs:
    ${table(attrs.items())}
% else:
    <p>No request attributes</p>
% endif

<h4>Request environ</h4>
% if environ:
    ${table(environ.items())}
% else:
    <p>No request environ</p>
% endif

<h4>Request Headers</h4>
${table(request_headers)}

<h4>Response Headers</h4>
${table(response_headers)}
