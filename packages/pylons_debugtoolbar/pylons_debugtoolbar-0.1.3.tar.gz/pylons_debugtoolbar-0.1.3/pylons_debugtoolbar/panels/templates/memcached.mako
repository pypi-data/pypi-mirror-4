<table>
	<thead>
		<tr>
            <th>Time&nbsp;(ms)</th>
            <th>Func</th>
            <th>Hits</th>
            <th>Args</th>
            <th>Return</th>
		</tr>
	</thead>
	<tbody>
		% for i, call in enumerate(calls):
			<tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
                <td>${round(call['duration'], 2)|h}</td>
                <td>${call['function']|h}</td>
                <td>${call.get('hits', '')|h}</td>
                <td>${call['args']|h}</td>
                <td>${call['ret']|h}</td>
			</tr>
		% endfor
	</tbody>
</table>
