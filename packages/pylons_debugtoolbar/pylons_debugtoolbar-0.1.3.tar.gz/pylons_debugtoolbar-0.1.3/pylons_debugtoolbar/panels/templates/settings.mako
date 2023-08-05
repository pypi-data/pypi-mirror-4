<table>
	<thead>
		<tr>
			<th>Key</th>
			<th>Value</th>
		</tr>
	</thead>
	<tbody>
		% for i, (key, value) in enumerate(settings):
			<tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
				<td>${key|h}</td>
                <%
                    try:
                        if isinstance(value, basestring):
                            if value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                        value = asbool(value)
                    except ValueError:
                        pass
                %>
				<td>${value|h}</td>
			</tr>
		% endfor
	</tbody>
</table>
