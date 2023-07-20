import nbformat
from nbconvert import HTMLExporter
from utils.config import START_TIME, END_TIME
from utils.template import get_readable_date_from_timestamp
from nbconvert.preprocessors import ExecutePreprocessor

html_exporter = HTMLExporter(template_name='templates/sidebar')

notebooks = [
    { 'notebook_file': 'wearables_sales_volume.ipynb', 'html_file': 'index.html', 'title': 'Volume', 'section': 'Wearables' },
    { 'notebook_file': 'wearables_prices.ipynb', 'html_file': 'wearables-prices.html', 'title': 'Prices', 'section': 'Wearables' },
    { 'notebook_file': 'wearables_supply.ipynb', 'html_file': 'wearables-supply.html', 'title': 'Supply', 'section': 'Wearables' },
    { 'notebook_file': 'wearables_market_cap.ipynb', 'html_file': 'wearables-market-cap.html', 'title': 'Market Cap', 'section': 'Wearables' },
    { 'notebook_file': 'wearables_core_supply.ipynb', 'html_file': 'core-supply.html', 'title': 'Cores', 'section': 'Wearables' },
    { 'notebook_file': 'wearables_equipped.ipynb', 'html_file': 'wearables-equipped.html', 'title': 'Usage', 'section': 'Wearables' },
    
    { 'notebook_file': 'forge_activity.ipynb', 'html_file': 'forge-activity.html', 'title': 'Usage', 'section': 'Forge' },
    { 'notebook_file': 'forge_smithing_skill.ipynb', 'html_file': 'smithing-skill.html', 'title': 'Smithing Skill', 'section': 'Forge' },
    { 'notebook_file': 'forge_sales_volume.ipynb', 'html_file': 'forge-volume.html', 'title': 'Volume', 'section': 'Forge' },
    { 'notebook_file': 'forge_prices.ipynb', 'html_file': 'forge-prices.html', 'title': 'Prices', 'section': 'Forge' },
    
    { 'notebook_file': 'schematic_trait_selection.ipynb', 'html_file': 'trait-selection.html', 'title': 'Selection', 'section': 'Traits' },
    { 'notebook_file': 'schematic_trait_selection_simulation.ipynb', 'html_file': 'trait-simulation.html', 'title': 'Simulation', 'section': 'Traits' },
]

navigation_sections = {}

navigation_icons = {
    'Wearables': 'fa-solid fa-shirt',
    'Forge': 'fa-solid fa-hammer',
    'Traits': 'fa-solid fa-image-portrait',
}

for nb in notebooks:
    if nb['section'] not in navigation_sections:
        navigation_sections[nb['section']] = []
    navigation_sections[nb['section']].append(nb)

for i, nb in enumerate(notebooks):
    print('Processing {nb_file}...'.format(nb_file=nb['notebook_file']))
    notebook = nbformat.read(nb['notebook_file'], as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(notebook)
    resources = { 
        'data_window_start': get_readable_date_from_timestamp(START_TIME),
        'data_window_end': get_readable_date_from_timestamp(END_TIME - 1),
        'notebook_index': i, 
        'notebooks': notebooks,
        'navigation_sections': navigation_sections,
        'navigation_icons': navigation_icons
    }
    (body, resources) = html_exporter.from_notebook_node(notebook, resources=resources)
    with open('public/' + nb['html_file'], 'w') as f:
        f.write(body)

print('Processing complete.')

