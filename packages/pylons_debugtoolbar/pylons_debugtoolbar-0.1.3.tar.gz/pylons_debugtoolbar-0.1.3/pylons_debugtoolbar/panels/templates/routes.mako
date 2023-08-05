<table>
	<thead>
		<tr>
			<th>Route Pattern</th>
            <th>Route Name</th>
            <th>Controller</th>
			<th>Action</th>
			<th>Requirements</th>
		</tr>
	</thead>
	<tbody>
		% for i, route_info in enumerate(result):
			<tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
                <td>${route_info['route']|h}</td>
                <td>${route_info['name']|h}</td>
				<td>${route_info['controller']}</td>
				<td>${route_info['action']}</td>
				<td>${route_info['requirements']}</td>
			</tr>
		% endfor
	</tbody>
</table>
