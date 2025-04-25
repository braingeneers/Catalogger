# Catalogger

Catalogger is a Python package for loading, cataloging, and analyzing data from high-density microelectrode array (HD-MEA) recordings, with a focus on experiments involving organoids and mouse brain slices. It leverages cataloged metadata to streamline data access and analysis.

## Features

- Load and update experiment catalogs from metadata and CSV files.
- Extract and process spike data from HD-MEA recordings.
- Annotate catalogs with computed metrics (e.g., firing rates, burstiness).
- Support for filtering experiments based on quality metrics.
- Utilities for handling large-scale electrophysiology datasets.

## Installation

First, install the SpikeData dependency:

```bash
pip install git+https://github.com/braingeneers/SpikeData
```

Then install Catalogger:

```bash
pip install git+https://github.com/hschweiger15/Catalogger.git
```

Or clone the repository and install locally:

```bash
git clone https://github.com/hschweiger15/Catalogger.git
cd Catalogger
pip install .
```

## Requirements

- Python >= 3.8
- See `setup.py` for a full list of dependencies, including: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `h5py`, `tqdm`, `joblib`, `boto3`, `pyarrow`, `tables`, `nptyping`, `pyqt5`, `xarray`, and more.

## Usage

### Loading a Catalog

```python
from Catalogger.Loaders import AcqmLoader
import pandas as pd

# Load a catalog CSV
catalog = pd.read_csv('catalog_baseline.csv')

# Initialize loader
loader = AcqmLoader(basepath='/path/to/data', catalog=catalog)
```

### Updating Catalog with Spike Data

```python
updated_catalog = loader.update_catalog(gen_metrics=True, min_units=5)
```

### Accessing Spike Data

```python
spike_data = loader.get_spike_data('Trace_20240619_12_24_17_20174a_day46_ventral_c57')
```

## Data Structure

- `catalog_baseline.csv`: Main experiment catalog, with columns for UUID, experiment name, date, sample type, species, cell line, media, drug, chip number, etc.
- `metadata.json`: Detailed metadata for each experiment, including hardware, sample info, and data file paths.

## Example Catalog Entry

| uuids                        | experiment_name                                 | experiment_date      | sample_type | species   | cell_line | agg_date   | plating_date | org_age         | media  | patterning | drug     | chip_number |
|------------------------------|-------------------------------------------------|---------------------|-------------|-----------|-----------|------------|--------------|-----------------|--------|------------|----------|-------------|
| 2024-05-04-e-sakura-day22and24 | Trace_20240504_13_26_11_21985_day22_ventral_e14 | 2024-05-04 13:27:00 | organoid    | organoid  | E14       | 2024-04-11 | 2024-04-29   | 23 days 13:27:00| sakura | ventral    |          | 21985e      |

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## License

MIT License

## Author

Hunter Schweiger (hschweig@ucsc.edu)

## Plotting and Visualization

Catalogger provides a utility function for visualizing spike data as a styled raster plot with population firing rate overlay.

### plot_styled_raster

```python
def plot_styled_raster(spike_data, title=None, time_window=None, y_lim=None, 
                      styler=None, width_pt=None, height_pt=None, save_path=None, filename=None,
                      smoothing_window=100, sort_by_fr=False, time_unit='seconds',
                      pop_rate_unit='Hz'):
    """
    Plot a styled raster plot with population firing rate.
    
    Parameters:
        spike_data (SpikeData): SpikeData object containing spike times and neuron data
        title (str, optional): Title for the plot
        time_window (tuple, optional): Time window to display in time units specified by time_unit
        y_lim (tuple, optional): Y-axis limits for population rate (min, max)
        styler (Styler, optional): Styler object for plot formatting
        width_pt (float, optional): Width of the figure in points
        height_pt (float, optional): Height of the figure in points
        save_path (str, optional): Path to save the figure
        smoothing_window (float, optional): Bin size in ms for population rate calculation
        sort_by_fr (bool, optional): Whether to sort neuron IDs by firing rate
        time_unit (str, optional): Unit for x-axis, either 'seconds' or 'minutes'
        pop_rate_unit (str, optional): Unit for population rate, either 'Hz' or 'kHz'
    Returns:
        tuple: (fig, (ax1, ax2)) where ax2 is None if no spikes are present
    """
    # ...see examples/ex_usage.py for full implementation...
```

#### Example Usage

```python
import pandas as pd
import matplotlib.pyplot as plt
from catalogger.Loaders import AcqmLoader

# Load the catalog
catalog = pd.read_csv('catalog_baseline.csv')

# Set your basepath
basepath = '/path/to/data'  # Update to your actual data path

# Instantiate the loader
loader = AcqmLoader(basepath=basepath, catalog=catalog)

# Update the catalog with spike data (optional)
loader.update_catalog(gen_metrics=True, min_units=5)

# Select a recording name
recording_name = loader.catalog['experiment_name'].iloc[0]

# Get the SpikeData object for the recording
sd = loader.get_spike_data(recording_name)

# Plot the raster
fig, (ax, ax2) = plot_styled_raster(
    sd,
    title=f"Raster for {recording_name}",
    sort_by_fr=True
)
plt.show()
```

- Set `sort_by_fr=True` to sort neurons by firing rate (highest at bottom).
- The function supports custom time windows, population rate units, and saving plots to file.
- For advanced styling, pass a `Styler` object (see `cell_styler.py`).
