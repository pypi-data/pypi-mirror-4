<h4>Resource usage</h4>
<table>
	<colgroup>
		<col style="width: 20%"/>
		<col/>
	</colgroup>
	<thead>
		<tr>
			<th>Resource</th>
			<th>Value</th>
		</tr>
	</thead>
	<tbody>
		% for i, (key, value) in enumerate(rows):
			<tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
				<td>${key|h}</td>
				<td>${value|h}</td>
			</tr>
		% endfor
	</tbody>
</table>
