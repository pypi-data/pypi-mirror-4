<div id="pDebug" style="display:none;">
    <script type="text/javascript">
      var DEBUG_TOOLBAR_STATIC_PATH = '/debugtoolbar_static/';
    </script>

    <script data-main="/debugtoolbar_static/js/toolbar"
            src="/debugtoolbar_static/js/require.js"></script>

    <div style="display: none;" id="pDebugToolbar">
        <ol id="pDebugPanelList">
            % if panels:
			<li>
              <a id="pHideToolBarButton" href="#"
                 title="Hide Toolbar">Hide &raquo;</a></li>
			% else:
			<li id="pDebugButton">DEBUG</li>
			% endif
			% for panel in panels:
                <%
                    # Need to do this to get tmpl_vars len on nav_subtitle
                    if panel.name == "Mako":
                        panel.content()
                %>
				<li id="${panel.dom_id()}">
					% if panel.has_content:
						<a href="#"
                           title="${panel.title()}"
                           class="${panel.dom_id()}">
					% else:
					    <div class="contentless">
					% endif

					${panel.nav_title()}

					% if panel.nav_subtitle():
                        <br /><small>${panel.nav_subtitle()}</small>
                    % endif

					% if panel.has_content:
						</a>
					% else:
					    </div>
					% endif

                    % if panel.user_activate:
                    <span class="switch ${'active' if panel.is_active else 'inactive'}"
                          title="Enable or disable the panel"></span>
                    % endif
				</li>
			% endfor
        </ol>
    </div>
    <div style="display:none; ${button_style}" id="pDebugToolbarHandle">
		<a title="Show Toolbar" id="pShowToolBarButton" href="#">&laquo;</a>
	</div>
	% for panel in panels:
		% if panel.has_content:
			<div id="${panel.dom_id()}-content" class="panelContent">
				<div class="pDebugPanelTitle">
					<a href="" class="pDebugClose">Close</a>
					<h3>${panel.title()}</h3>
				</div>
				<div class="pDebugPanelContent">
				    <div class="scroll">
				        ${panel.content()|n}
				    </div>
				</div>
			</div>
		% endif
	% endfor
    <div id="pDebugWindow" class="panelContent"></div>
</div>
