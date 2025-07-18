run_app:
	python3 pf_macro.py & sleep 30

	wget -r http://127.0.0.1:8050/
	wget -r http://127.0.0.1:8050/_dash-layout 
	wget -r http://127.0.0.1:8050/_dash-dependencies

	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dcc/async-graph.js
	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dcc/async-highlight.js
	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dcc/async-markdown.js
	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dcc/async-datepicker.js
	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dcc/async-dropdown.js

	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dash_table/async-table.js
	wget -r http://127.0.0.1:8050/_dash-component-suites/dash/dash_table/async-highlight.js

	wget -r http://127.0.0.1:8050/_dash-component-suites/plotly/package_data/plotly.min.js

	# Move scraped files
	mv 127.0.0.1:8050 pages_files

	# Copy assets folder into the deployment folder
	mkdir -p pages_files/assets
	cp -R assets/* pages_files/assets/

	find pages_files -exec sed -i.bak 's|_dash-component-suites|macro\\/_dash-component-suites|g' {} \;
	find pages_files -exec sed -i.bak 's|_dash-layout|macro/_dash-layout.json|g' {} \;
	find pages_files -exec sed -i.bak 's|_dash-dependencies|macro/_dash-dependencies.json|g' {} \;
	find pages_files -exec sed -i.bak 's|_reload-hash|macro/_reload-hash|g' {} \;
	find pages_files -exec sed -i.bak 's|_dash-update-component|macro/_dash-update-component|g' {} \;
	find pages_files -exec sed -i.bak 's|assets|macro/assets|g' {} \;

	mv pages_files/_dash-layout pages_files/_dash-layout.json
	mv pages_files/_dash-dependencies pages_files/_dash-dependencies.json

	ps | grep python | awk '{print $$1}' | xargs kill -9	

clean_dirs:
	ls
	rm -rf 127.0.0.1:8050/
