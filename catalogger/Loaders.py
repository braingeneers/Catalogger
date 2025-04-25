import os
from braingeneers.analysis import SpikeData, load_spike_data
from braingeneers import analysis
from braingeneers.data import datasets_electrophysiology as ephys
from spikedata.spikedata import SpikeData
import json
import zipfile
import numpy as np
import pandas as pd
from pathlib import Path


class AcqmLoader:
    """
    Loader for regular acqm files. Supports loading from full path or from catalog.
    Also provides catalog update and spike data extraction utilities.
    """
    def __init__(self, basepath=None, catalog=None):
        """
        Initialize AcqmLoader.
        
        Parameters:
        basepath (str): Base directory where data is stored.
        catalog (pd.DataFrame): Catalog DataFrame containing experiment metadata.
        """
        self.basepath = basepath
        self.catalog = catalog

    @staticmethod
    def load_curation(qm_path):
        """
        Load spike data from a curation zip file (acqm).
        
        Parameters:
        qm_path (str): Path to the .zip file containing spike data.
        
        Returns:
        tuple: (train, neuron_data, config, fs)
            train (list): List of spike times arrays (seconds).
            neuron_data (dict): Neuron metadata.
            config (dict or None): Configuration dictionary if present.
            fs (float): Sampling frequency.
        """
        with zipfile.ZipFile(qm_path, 'r') as f_zip:
            qm = f_zip.open("qm.npz")
            data = np.load(qm, allow_pickle=True)
            spike_times = data["train"].item()
            fs = data["fs"]
            train = [times / fs for _, times in spike_times.items()]
            config = data["config"].item() if "config" in data else None
            neuron_data = data["neuron_data"].item()
        return train, neuron_data, config, fs

    def load_from_path(self, qm_path):
        """
        Load spike data from a given file path.
        
        Parameters:
        qm_path (str): Path to the .zip file containing spike data.
        
        Returns:
        tuple: (train, neuron_data, config, fs)
        """
        return self.load_curation(qm_path)

    def load_from_path_using_cat(self, exp_name, suffix='_params_params_low_ISI_acqm.zip'):
        """
        Load spike data for a single experiment using the catalog. This will load using the full path.
        
        Parameters:
        exp_name (str): Name of the experiment to load.
        suffix (str): Suffix for the acqm zip file. Default is '_params_params_low_ISI_acqm.zip'.
        
        Returns:
        tuple: (train, neuron_data, config, fs)
        """
        if self.basepath is None or self.catalog is None:
            raise ValueError("basepath and catalog must be set for this operation.")
        row = self.catalog.loc[self.catalog['experiment_name'] == exp_name]
        if row.empty:
            raise ValueError(f"Experiment {exp_name} not found in catalog.")
        qm_path = os.path.join(self.basepath, row['uuids'].values[0], exp_name + suffix)
        return self.load_from_path(qm_path)

    def get_spike_data_from_catalog(self, recording_name):
        """
        Retrieve the SpikeData object from the catalog for a given recording name if data is loaded into catalog.
        
        Parameters:
        recording_name (str): Name of the recording/experiment.
        
        Returns:
        SpikeData: The spike data object stored in the catalog.
        """
        if self.catalog is None:
            raise ValueError("catalog must be set for this operation.")
        return self.catalog.loc[self.catalog['experiment_name'] == recording_name, 'data_obj'].values[0]

    @staticmethod
    def update_catalog_with_spike_data(catalog, basepath, gen_metrics=False, min_units=None):
        """
        Update the catalog with spike data and metrics.
        
        Parameters:
        catalog (pd.DataFrame): The catalog DataFrame to update.
        basepath (str): The base path for the data.
        gen_metrics (bool): Whether to generate metrics for the spike data.
        min_units (int, optional): Minimum number of units required to include a recording. 
                                  If None, all recordings are included.
        
        Returns: 
        pd.DataFrame: The updated catalog DataFrame with filtered entries if min_units is specified.
        """
        # First convert the org_age column to days
        catalog['org_age'] = catalog['org_age'].apply(lambda x: int(str(x).split('days')[0].strip()) if pd.notna(x) else None)
        
        for idx, row in catalog.iterrows():
            uuid = row['uuids']
            exp = row['experiment_name']
            exp_path = os.path.join(basepath, uuid, exp + '_params_params_low_ISI_acqm.zip')
            if os.path.exists(exp_path):
                print(f"Processing: {exp_path}")
                try:
                    train, neuron_data, _, _ = AcqmLoader.load_curation(exp_path)
                    train = [t*1000 for t in train]
                    sd = analysis.SpikeData(train, neuron_data={0: neuron_data})

                    num_units = len(train)
                    catalog.at[idx, 'num_units'] = num_units
                    
                    # Only proceed with full processing if the recording meets unit threshold
                    if min_units is None or num_units >= min_units:
                        if gen_metrics:
                            rec_len = sd.length
                            firing_rates = [(len(t)/rec_len) * 1000 for t in train]
                            burstiness = sd.burstiness_index()

                            # Update catalog with new information
                            catalog.at[idx, 'burstiness'] = json.dumps(burstiness.tolist() if isinstance(burstiness, np.ndarray) else burstiness)
                            catalog.at[idx, 'mean_firing_rate'] = np.mean(firing_rates) if firing_rates else None
                            catalog.at[idx, 'firing_rates'] = json.dumps(firing_rates)  # Store as JSON string
                            catalog.at[idx, 'median_firing_rate'] = np.median(firing_rates) if firing_rates else None

                        catalog.at[idx, 'data_obj'] = sd
                        catalog.at[idx, 'processed'] = True
                        catalog.at[idx, 'error'] = None
                    else:
                        catalog.at[idx, 'processed'] = False
                        catalog.at[idx, 'error'] = f'Insufficient units: {num_units} (minimum: {min_units})'
                        catalog.at[idx, 'data_obj'] = None  # Clear data object to save memory
                        
                except Exception as e:
                    print(f"Error processing {exp}: {str(e)}")
                    catalog.at[idx, 'processed'] = False
                    catalog.at[idx, 'error'] = str(e)
            else:
                print(f"File not found: {exp_path}")
                catalog.at[idx, 'processed'] = False
                catalog.at[idx, 'error'] = 'File not found'
        
        # Filter the catalog if min_units was specified
        if min_units is not None:
            filtered_catalog = catalog[catalog['processed'] == True].copy()
            print(f"Filtered from {len(catalog)} to {len(filtered_catalog)} recordings with at least {min_units} units")
            return filtered_catalog
        
        return catalog

    def update_catalog(self, gen_metrics=False, min_units=None):
        """
        Update the loader's catalog with spike data and metrics.
        
        Parameters:
        gen_metrics (bool): Whether to generate metrics for the spike data.
        min_units (int, optional): Minimum number of units required to include a recording.
        
        Returns:
        pd.DataFrame: The updated catalog DataFrame.
        """
        if self.catalog is None or self.basepath is None:
            raise ValueError("basepath and catalog must be set for this operation.")
        updated = AcqmLoader.update_catalog_with_spike_data(self.catalog, self.basepath, gen_metrics, min_units)
        self.catalog = updated
        return updated

    def get_spike_data(self, recording_name):
        """
        Retrieve the SpikeData object for a given recording name from a loaded catalog.
        
        Parameters:
        recording_name (str): Name of the recording/experiment.
        
        Returns:
        SpikeData: The spike data object stored in the catalog.
        """
        return self.get_spike_data_from_catalog(recording_name)


#### NEED TO TEST #####
class DrugLoader: 
    """
    Loader for drug experiments, handling spike data and windows (stitch points).
    """
    def __init__(self, basepath=None, catalog=None):
        """
        Initialize DrugLoader.
        
        Parameters:
        basepath (str): Base directory where data is stored.
        catalog (pd.DataFrame): Catalog DataFrame containing experiment metadata.
        """
        self.basepath = basepath
        self.catalog = catalog

    def quick_load(self, drug_name, uuid, drug_files):
        """
        Load spike data and stitching points for a drug recording.
        
        Parameters:
        drug_name (str): Name of the drug/experiment.
        uuid (str): Unique identifier for the experiment.
        drug_files (dict): Mapping of drug names to file paths.
        
        Returns:
        tuple: (spike_data, stitch_points)
            spike_data (SpikeData): Loaded spike data object.
            stitch_points (list or None): List of stitching points (if available).
        """
        if self.basepath is None:
            raise ValueError("basepath must be set for this operation.")
        try:
            with open(f'{self.basepath}/{drug_name}_stitch_inds.json', 'r') as f:
                stitch_data = json.load(f)
            stitch_points = [point[1] for point in stitch_data]
        except FileNotFoundError:
            print(f"Warning: Using default windows for {drug_name}")
            stitch_points = None
        spike_data = load_spike_data(
            uuid=uuid,
            full_path=os.path.join(self.basepath, drug_files[drug_name]),
            groups_to_load=["good"]
        )
        return spike_data, stitch_points

    def load_stitch_points(self, drug_name, uuid):
        """
        Load stitching points for a recording.
        
        Parameters:
        drug_name (str): Name of the drug/experiment.
        uuid (str): Unique identifier for the experiment.
        
        Returns:
        list or None: List of stitching points if found, else None.
        """
        if self.basepath is None:
            raise ValueError("basepath must be set for this operation.")
        try:
            stitch_file = os.path.join(self.basepath, uuid, f'{drug_name}_stitch_inds.json')
            with open(stitch_file, 'r') as f:
                stitch_data = json.load(f)
            stitch_points = [point[1] for point in stitch_data]
            return stitch_points
        except FileNotFoundError:
            print(f"Warning: No stitch points found for {drug_name}")
            return None

    def get_phase_spikedata(self, sd, windows, phase):
        """
        Get SpikeData for a specific phase using subtime.
        
        Parameters:
        sd (SpikeData): The spike data object.
        windows (dict): Dictionary of phase names to (start, end) times in ms.
        phase (str): Phase name to extract.
        
        Returns:
        SpikeData: Subset of spike data for the specified phase.
        """
        start_ms, end_ms = windows[phase]
        return sd.subtime(start_ms, end_ms)

    def stitch_windows(self, stitch_points=None):
        """
        Generate time windows for analysis based on stitch points or defaults.
        
        Parameters:
        stitch_points (list, optional): List of stitching points (sample indices).
        
        Returns:
        dict: Dictionary with phase names as keys and (start, end) times in ms as values.
        """
        sampling_rate = 20000
        if stitch_points:
            windows = {
                'baseline': (0, stitch_points[0] / sampling_rate * 1000),
                'initial': (stitch_points[0] / sampling_rate * 1000, stitch_points[1] / sampling_rate * 1000),
                'incubated': (stitch_points[1] / sampling_rate * 1000, stitch_points[2] / sampling_rate * 1000)
            }
        else:
            windows = {
                'baseline': (0, 10 * 60 * 1000),
                'initial': (10 * 60 * 1000, 20 * 60 * 1000),
                'incubated': (20 * 60 * 1000, 30 * 60 * 1000)
            }
        return windows




