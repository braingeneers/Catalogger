# Catalogger

Catalogger is a Python package for loading, cataloging, and analyzing data from high-density microelectrode array (HD-MEA) recordings, with a focus on experiments involving organoids and mouse brain slices. It leverages cataloged metadata to streamline data access and analysis.

## Features

- Load and update experiment catalogs from metadata and CSV files.
- Extract and process spike data from HD-MEA recordings.
- Annotate catalogs with computed metrics (e.g., firing rates, burstiness).
- Support for filtering experiments based on quality metrics.
- Utilities for handling large-scale electrophysiology datasets.

## Installation

```bash
pip install git+ssh://git@github.com:hschweiger15/Catalogger.git
```

Or clone the repository and install locally:

```bash
git clone git@github.com:hschweiger15/Catalogger.git
cd Catalogger
pip install .
```

## Requirements

- Python >= 3.8
- See `setup.py` for a full list of dependencies, including: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `h5py`, `scikit-learn`, `statsmodels`, `tqdm`, `joblib`, `boto3`, `pyarrow`, `tables`, `umap-learn`, `nptyping`, `numba`, `pyqt5`, `xarray`, and more.

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
