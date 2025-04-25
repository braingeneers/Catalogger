import pandas as pd
import matplotlib.pyplot as plt
from catalogger.Loaders import load_catalog, get_spike_data
# from catalogger.plotting import plot_styled_raster



## Plotting functions
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
    # Validate inputs
    if time_unit not in ['seconds', 'minutes']:
        raise ValueError("time_unit must be either 'seconds' or 'minutes'")
    if pop_rate_unit not in ['Hz', 'kHz']:
        raise ValueError("pop_rate_unit must be either 'Hz' or 'kHz'")
    
    # Get spike times and cluster IDs from spike_data
    cluster_ids, spike_times = spike_data.idces_times()
    
    # Sort by firing rate if requested
    if sort_by_fr:
        # Calculate firing rates
        rates = []
        for i in range(spike_data.N):
            spikes = spike_data.train[i]
            rate = len(spikes) / (spike_data.length / 1000)  # spikes per second
            rates.append(rate)
        
        # Get sorted indices (descending order)
        sort_indices = np.argsort(rates)[::-1]
        
        # Create mapping from original to sorted indices
        id_mapping = {old_id: new_id for new_id, old_id in enumerate(sort_indices)}
        
        # Map original cluster IDs to sorted IDs
        sorted_cluster_ids = np.array([id_mapping[cid] for cid in cluster_ids])
        
        # Use sorted IDs for plotting
        cluster_ids = sorted_cluster_ids
    
    # Create figure with custom dimensions if provided
    if styler is None:
        fig = plt.figure(figsize=(10, 10))
        scale_factor = 1
    else:
        if width_pt and height_pt:
            fig = plt.figure(figsize=styler.get_figure_size(width_pt=width_pt, height_pt=height_pt))
        else:
            fig = plt.figure(figsize=styler.get_figure_size(size_preset='single'))
        
        fig_width, fig_height = fig.get_size_inches()
        scale_factor = np.sqrt(fig_width * fig_height) / np.sqrt(3.346 * 2.51)
    
    ax = fig.add_subplot(111)
    
    # Convert spike times to selected time unit
    time_divisor = 1000  # ms to seconds
    if time_unit == 'minutes':
        time_divisor = 60000  # ms to minutes
        
    normalized_times = spike_times / time_divisor
    
    # Plot raster
    ax.scatter(normalized_times, cluster_ids, 
              s=0.25 * scale_factor,
              marker='|', 
              c='k',
              alpha=0.8)
    
    # Set appropriate axis labels
    ax.set_xlabel(f'Time ({time_unit})')
    
    if sort_by_fr:
        ax.set_ylabel('Neuron ID (sorted by firing rate, highest at bottom)')
    else:
        ax.set_ylabel('Neuron ID')
        
    ax.yaxis.set_major_formatter(plt.ScalarFormatter())
    ax.ticklabel_format(style='plain', axis='y')
    
    if title:
        ax.set_title(title)
    
    # Add population firing rate if spikes are present
    if len(spike_times) > 0:
        ax2 = ax.twinx()
        
        # Calculate population rate using the specified smoothing window
        bin_size = smoothing_window * scale_factor  # ms
        bins = np.arange(spike_times.min(), spike_times.max() + bin_size, bin_size)
        spike_counts, _ = np.histogram(spike_times, bins=bins)
        pop_rate = spike_counts / (bin_size / 1000)  # Convert to Hz
        
        # Convert to kHz if requested
        rate_divisor = 1.0  # Hz
        if pop_rate_unit == 'kHz':
            rate_divisor = 1000.0  # Hz to kHz
            pop_rate = pop_rate / rate_divisor
            
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Convert bin centers to proper time unit
        bin_centers_normalized = bin_centers / time_divisor
        
        # Apply time window if specified
        if time_window is not None:
            # Convert time window to ms based on the specified time unit
            multiplier = 1000 if time_unit == 'seconds' else 60000
            time_window_ms = (time_window[0] * multiplier, time_window[1] * multiplier)
            mask = (bin_centers >= time_window_ms[0]) & (bin_centers <= time_window_ms[1])
            bin_centers_normalized = bin_centers_normalized[mask]
            pop_rate = pop_rate[mask]
        
        # Plot population rate
        pop_rate_color = styler.colors[5] if styler else 'blue'
        ax2.plot(bin_centers_normalized, pop_rate, 
                color=pop_rate_color,
                linewidth=1 * scale_factor)
        
        ax2.set_ylabel(f'Population Firing Rate ({pop_rate_unit})', 
                      color=pop_rate_color)
        ax2.tick_params(axis='y', labelcolor=pop_rate_color)
        
        if y_lim is not None:
            ax2.set_ylim(y_lim)
        
        # Adjust right spine position
        ax.spines['right'].set_position(('outward', 10 * scale_factor))
    else:
        ax2 = None
    
    # Set time window limits if specified
    if time_window is not None:
        ax.set_xlim(time_window)
    
# In your plot_styled_raster function
    if styler is not None:
        if save_path is not None:
            # Use the provided filename or create one from the save_path if none provided
            name_to_use = filename or os.path.splitext(os.path.basename(save_path))[0]
            styler.finish_plot(True, os.path.dirname(save_path), name_to_use)
        else:
            styler.finish_plot(False, None, None)
    else:
        plt.tight_layout()
        if save_path is not None:
            plt.savefig(save_path)
    
    return fig, (ax, ax2)


# Load the catalog (update the path as needed)
catalog = load_catalog('../catalog_baseline.csv')

# Select a recording name (first entry as example)
recording_name = catalog['experiment_name'].iloc[10]

# Get the SpikeData object for the recording
sd = get_spike_data(catalog, recording_name)

# Plot the raster
fig, (ax, ax2) = plot_styled_raster(
    sd,
    title=f"Raster for {recording_name}",
    sort_by_fr=True
)
plt.show()
