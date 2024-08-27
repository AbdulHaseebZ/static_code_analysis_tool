import dash
import dash_cytoscape as cyto
from dash import html, dcc, Input, Output, State
import joern_data_extraction as jde

# Define the create_elements function before it is used
def create_elements(data, parent_id=None):
    elements = []
    if isinstance(data, dict):
        for node_id, children in data.items():
            unique_node_id = f"{parent_id}->{node_id}" if parent_id else node_id
            elements.append({"data": {"id": unique_node_id, "label": node_id}})
            if parent_id is not None:
                elements.append({"data": {"source": parent_id, "target": unique_node_id}})
            elements += create_elements(children, parent_id=unique_node_id)
    elif isinstance(data, list):
        for child in data:
            elements += create_elements(child, parent_id=parent_id)
    
    return elements

# Initialize the Dash app
app = dash.Dash(__name__)

# Initial graph data from Joern
hierarchy_data = jde.initialization()
elements = create_elements(hierarchy_data)

app.layout = html.Div([
    dcc.Input(id='variable-input', type='text', placeholder='Enter variable name'),
    html.Button('Search', id='search-button', n_clicks=0),
    cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        layout={'name': 'cose', 'padding': 100, 'nodeDimensionsIncludeLabels': True},
        style={'width': '100vw', 'height': '90vh', 'background-color': 'black'},
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    'background-color': '#0074D9',
                    'color': 'yellow',
                    'font-size': '14px',
                }
            },
            {
                'selector': 'node[id = "bpf_struct_ops_map_update_elem"]',
                'style': {
                    'shape': 'octagon',
                    'background-color': 'green',
                    'color': 'yellow',
                    'font-size': '20px',
                    'width': '80px',
                    'height': '80px',
                }
            },
            {
                'selector': 'edge',
                'style': {'line-color': '#0074D9', 'width': 2},
            },
        ]
    )
])

# Store the selected node
selected_node = None

# Callback to capture the clicked node
@app.callback(
    Output('cytoscape', 'tapNodeData'),
    Input('cytoscape', 'tapNodeData')
)
def store_selected_node(node_data):
    global selected_node
    if node_data:
        selected_node = node_data['id']
    return node_data

# Callback to highlight nodes using the searched variable
@app.callback(
    Output('cytoscape', 'stylesheet'),
    Input('search-button', 'n_clicks'),
    State('variable-input', 'value')
)
def highlight_nodes(n_clicks, variable_name):
    if n_clicks > 0 and selected_node and variable_name:
        # Extract the function name from the selected node ID
        function_name = selected_node.split('->')[-1]
        highlighted_functions = jde.variable_search(function_name, variable_name)

        # Create a new stylesheet to highlight nodes
        new_stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    'background-color': '#0074D9',
                    'color': 'yellow',
                    'font-size': '14px',
                }
            },
            {
                'selector': f'node[id = "bpf_struct_ops_map_update_elem"]',
                'style': {
                    'shape': 'octagon',
                    'background-color': 'green',
                    'color': 'yellow',
                    'font-size': '20px',
                    'width': '80px',
                    'height': '80px',
                }
            },
            {
                'selector': 'edge',
                'style': {'line-color': '#0074D9', 'width': 2},
            },
        ]

        # Add red color to the nodes containing the variable
        for func in highlighted_functions:
            node_id = f'{selected_node}->{func}'
            new_stylesheet.append({
                'selector': f'node[id = "{node_id}"]',
                'style': {
                    'background-color': 'red',
                }
            })

        return new_stylesheet
    
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)
