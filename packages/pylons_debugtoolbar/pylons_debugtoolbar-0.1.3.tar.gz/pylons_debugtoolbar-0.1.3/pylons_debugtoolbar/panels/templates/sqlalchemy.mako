<%def name="result_table(result, headers, id)">
    % if result:
  		<table class="SqlSelectExplain" id="table-${id}" style="display: none;">
  			<thead>
  				<tr>
  					% for h in headers:
  						<th>${h.upper()}</th>
  					% endfor
  				</tr>
  			</thead>
  			<tbody>
  				% for i, row in enumerate(result):
  				    <tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
  						% for column in row:
  						<td>${db_to_unicode(column)[:max_length]|h}</td>
  						% endfor
  					</tr>
  				% endfor
  			</tbody>
  		</table>
    % else:
  		<p>Empty set</p>
    % endif
</%def>


<table id="pSqlaTable">
	<thead>
		<tr>
			<th>Time&nbsp;(ms)</th>
			<th>Query</th>
		</tr>
	</thead>
	<tbody>
	% for i, query in enumerate(queries):
		<tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
			<td>
                <strong>${query['duration']}</strong><br />
                % if query['result']:
                    <span class="js-click" id="${i}">Result</span>
                % endif
            </td>
			<td>${query['sql']|n}</td>
		</tr>
        % if query['result']:
            <tr class="${i%2 and 'pDebugEven' or 'pDebugOdd'}">
                <td></td>
                <td>
                    ${result_table(query['result'], query['headers'], i)}
                </td>
            </tr>
        % endif
	% endfor
	</tbody>
</table>

<script type="text/javascript">
    jQuery(document).ready( function() {
        (function($){
            $(".js-click").click( function() {
                var id = $(this).attr("id");
                var $table = $("#table-" + id);

                if ($table.css("display") === "none") {
                    $table.show();
                } else {
                    $table.hide();
                }
            });
        })(jQuery);
    });
</script>
