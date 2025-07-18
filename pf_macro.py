from dash import Dash, html, dcc, Output, Input, State
import pandas as pd
import dash_bootstrap_components as dbc
import dash_daq as daq
import json

external_stylesheets = [dbc.themes.CERULEAN, 
                        #dbc.themes.BOOTSTRAP,
                        dbc.icons.FONT_AWESOME,
                        dbc.icons.BOOTSTRAP]

style_heading={'color':'slategray', 'font-weight':'bold'}

base_prc = 1000
date_format = '%Y-%m-%d'

# load data
file = 'macro_indicators_250617.csv'
path = 'assets'
#df_macro = pd.read_csv(f'{path}/{file}', parse_dates=[0], index_col=0).rename_axis('date')
df_macro = pd.read_csv(file, parse_dates=[0], index_col=0).rename_axis('date')

# category & dropdown options
file = 'macro_indicator_category_250617.csv'
path = 'assets'
#df = pd.read_csv(f'{path}/{file}', index_col=0)
df = pd.read_csv(file, index_col=0)
data_category = df['category'].to_dict()
indicator_desc = df['title'].to_dict()

## sample data
freq = 'W' #'M' #'Q'
df = df_macro.stack().swaplevel().rename_axis(['ticker', 'date']).sort_index()
grouped = df.groupby([df.index.get_level_values('ticker'),
                     df.index.get_level_values('date').to_period(freq)])

### Get the index (MultiIndex) of the max/min per group
idx1 = grouped.idxmax()
idx2 = grouped.idxmin()
idx = pd.concat([idx1, idx2]).drop_duplicates()

df = df.loc[idx].unstack('ticker').sort_index()
df_macro = df.reindex(df.index.strftime(date_format))

# convert to json
data_macro = {}
for col in df_macro.columns:
    data_macro[col] = df_macro[col].dropna().to_dict()
data_macro_json = json.dumps(data_macro)

data_category_json = json.dumps(data_category)

# dropdown options
indicator_options = [{'label':x, 'value':x, 'title':indicator_desc[x]} for x in df_macro.columns]
indicator_options = [{'label':'All', 'value':'All'}] + indicator_options
#indicator_default = ['All']
#indicator_default = ['FEDFUNDS', 'DXY', 'GOLD', 'S&P500']
#indicator_default = ['DXY', 'GOLD']
indicator_default = ['USREC', 'DXY', 'GOLD']



app = Dash(__name__, title="Markets",
           external_stylesheets=external_stylesheets)

app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        <link rel="icon" type="image/x-icon" href="/assets/favicon.ico">
        <style>
        #styled-numeric-input input:invalid {{
            border-color: #dc3545;
            padding-right: calc(1.5em + 0.75rem);
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right calc(0.375em + 0.1875rem) center;
            background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
            outline: none;
        }}
        </style>
        <script>
            function minAbsScale(data) {{
                // Compute the normalized values with the same structure as the input
                let result = {{}};
                for (let tkr in data) {{
                    result[tkr] = {{}};
                    let maxVal = Math.max(...Object.values(data[tkr]).map(Math.abs));
                    for (let date in data[tkr]) {{
                        result[tkr][date] = data[tkr][date] / maxVal;
                    }}
                }}
                return result;
            }}
            function minMaxScale(data) {{
                // Compute the min-max scaled values with the same structure as the input
                let result = {{}};
                for (let tkr in data) {{
                    result[tkr] = {{}};
                    let values = Object.values(data[tkr]);
                    let minVal = Math.min(...values);
                    let maxVal = Math.max(...values);
                    let range = maxVal - minVal;
        
                    for (let date in data[tkr]) {{
                        // Avoid division by zero if all values are the same
                        result[tkr][date] = (range === 0) ? 0.5 : (data[tkr][date] - minVal) / range;
                    }}
                }}
                return result;
            }}
            function relativeScale(data) {{
                let result = {{}};
                for (let tkr in data) {{
                    result[tkr] = {{}};
                    let startDate = Object.keys(data[tkr])[0];
                    for (let date in data[tkr]) {{
                        result[tkr][date] = data[tkr][date] / data[tkr][startDate];
                    }}
                }}
                return result;
            }}
        </script>
        {{%css%}}
    </head>
    <body>
        <script>
            var dataMacro = {data_macro_json};
            var dataCategory = {data_category_json};
        </script>
        {{%app_entry%}}
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </body>
</html>
"""


app.layout = dbc.Container([
    html.Br(),
    dbc.Stack([
        html.Div(
            #dcc.Input(
            dbc.Input(
                id='start-input', 
                type='number', min=1900, max=2100, step=1,
                size='4',
                placeholder='Start',
                value=2000
            ), 
            #style={'min-width':'10%'}
        ),
        html.Div(
            dbc.Input(
                id='end-input', 
                type='number', min=1900, max=2100, step=1,
                size='4',
                placeholder='End',
                value=2025
            ), 
        ),
        html.Div(
            dcc.Dropdown(
                id='indicator-dropdown',
                options=indicator_options,
                value=indicator_default,
                multi=True,
            ), style={'min-width':'60%'} 
        ),
        daq.BooleanSwitch(
            id='rebase-boolean-switch',
            on=False
        ),
    ],
        direction="horizontal",
        gap=2,
        className="mb-3",
        id="styled-numeric-input",
    ),
    html.Div(
        dcc.Graph(id='macro-plot')
    ),
    html.Br(),
    dbc.Tooltip(
        'Rebase',
        target='rebase-boolean-switch',
        placement='bottom'
    ),
    dcc.Store(id='macro-data'),
    dcc.Location(id="url", refresh=False),  # To initialize the page
])


# update data based on selected indicators
app.clientside_callback(
    """
    function(indicators, start, end) {
        let data = {};

        // Check indicators
        if (!Array.isArray(indicators) || indicators.length === 0 || indicators[indicators.length - 1] === 'All') {
            data = dataMacro;
            indicators = ['All'];

            // reset start & end years
            let years = [];
            for (let tkr in data) {
                for (let dateStr in data[tkr]) {
                    let year = new Date(dateStr).getFullYear();
                    years.push(year);
                }
            }
            start = Math.min(...years);
            end = Math.max(...years);
        
        } else if (indicators.includes('All')) {
            // 'All' is selected but not last → remove it to avoid conflict
            indicators = indicators.filter(group => group !== 'All');
            // Still need to fetch selected indicators
        }

        // Retrieve selected indicators if not already set to all
        if (Object.keys(data).length === 0) {
            for (let tkr in dataMacro) {
                if (indicators.includes(tkr)) {
                    data[tkr] = dataMacro[tkr];
                }
            }
        }

        return [data, indicators, start, end];

    }
    """,
    Output('macro-data', 'assets'),
    Output('indicator-dropdown', 'value'),
    Output('start-input', 'value'),
    Output('end-input', 'value'),
    Input('indicator-dropdown', 'value'),
    State('start-input', 'value'),
    State('end-input', 'value'),
)



# plot indicator history
app.clientside_callback(
    """
    function(start, end, data, rebase) {
        
        // filter by year
        let data_filterd = {};
        if (start < end) {
            for (let tkr in data) {
                data_filterd[tkr] = {};

                for (let dateStr in data[tkr]) {
                    let year = new Date(dateStr).getFullYear();
                    if (year >= start && year <= end) {
                        data_filterd[tkr][dateStr] = data[tkr][dateStr];
                    }
                }
            }
        } else {
            data_filterd = data;
        }

        // scale data
        if (rebase) {
            data_filterd = relativeScale(data_filterd)
        } else {
            data_filterd = minMaxScale(data_filterd)
        }

        // plot indicator history
        let traces = [];
        let lineStyles = {
            'exchange': { width: 1, dash: 'dot' }, 
            'benchmark':{ width: 0.5, dash: 'solid', shape:'hv'}, 
            'yield':    { width: 0.5, dash: 'solid'}, 
            'market':   { width: 1.5}, 
            'commodity':{ width: 1, dash: 'dot' }, 
            'default':  { width: 1}
        };
        let lineFill ={
            'USREC': 'tozeroy'
        }
        for (let tkr in data_filterd) {
            let cat = dataCategory[tkr] ?? 'default';
            let line = lineStyles[cat] ?? 'default'; // Corrected default value for lineStyles
            let fill = lineFill[tkr] ?? 'none';
            
            const customDataForTrace = Object.keys(data_filterd[tkr]).map((key) => {
                const value = dataMacro[tkr][key]; 
                
                let formattedValue;
                if (value >= 100) {
                    formattedValue = value.toFixed(0); // Format as integer (0 decimal places)
                } else {
                    formattedValue = value.toFixed(2); // Round to the second decimal place for values < 100
                }

                return [
                    tkr, 
                    formattedValue // This will now contain the conditionally formatted value
                ];
            });

            traces.push({
                x: Object.keys(data_filterd[tkr]),
                y: Object.values(data_filterd[tkr]).map(val => val), 
                type: 'scatter',
                mode: 'lines',
                line: { ...line},
                fill: fill,
                name: tkr,
                customdata: customDataForTrace, // customdata is now an array of arrays
                hovertemplate: '%{customdata[0]}: %{customdata[1]}<extra></extra>', // Access by index
            });
        }


        let layout = {
            //title: { text: title},
            hovermode: 'x unified',
            //yaxis: { title: '가격' },
            height: 600
        }

        return {
            data: traces,
            layout: layout
        };
    }
    """,
    Output('macro-plot', 'figure'),
    Input('start-input', 'value'),
    Input('end-input', 'value'),
    Input('macro-data', 'assets'),
    Input('rebase-boolean-switch', 'on'),
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
