import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import math
import glob

def load_participant_data(data_dir="data"):
    """Load all participant CSV files and combine them."""
    all_files = glob.glob(os.path.join(data_dir, "fitts_law_*.csv"))
    
    if not all_files:
        print("No data files found in the 'data' directory.")
        return None
    
    # Combine all files into a single DataFrame
    dfs = []
    for filename in all_files:
        participant_id = os.path.basename(filename).split('_')[2].split('.')[0]
        df = pd.read_csv(filename)
        df['participant_id'] = participant_id
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

def remove_outliers(df, column='time_ms', z_threshold=3):
    """Remove outliers from the dataset based on z-score."""
    # Group data by configuration
    grouped = df.groupby(['size', 'distance', 'direction'])
    
    # Function to remove outliers within each group
    def filter_outliers(group):
        z_scores = np.abs(stats.zscore(group[column]))
        return group[z_scores < z_threshold]
    
    # Apply the filter to each group
    filtered_df = grouped.apply(filter_outliers).reset_index(drop=True)
    
    # Calculate how many rows were removed
    removed_count = len(df) - len(filtered_df)
    print(f"Removed {removed_count} outliers ({removed_count/len(df)*100:.1f}% of data).")
    
    return filtered_df

def calculate_fitts_metrics(df):
    """Calculate ID and IP for Fitts' Law analysis."""
    # Group by configuration and calculate means
    grouped_means = df.groupby(['size', 'distance', 'direction']).agg({
        'time_ms': 'mean',
        'errors': 'mean',
        'distance_traveled': 'mean'
    }).reset_index()
    
    # Calculate standard deviations
    grouped_std = df.groupby(['size', 'distance', 'direction']).agg({
        'time_ms': 'std',
        'errors': 'std',
        'distance_traveled': 'std'
    }).reset_index()
    
    # Merge means and standard deviations
    grouped = pd.merge(grouped_means, grouped_std, 
                       on=['size', 'distance', 'direction'],
                       suffixes=('_mean', '_std'))
    
    # Calculate Index of Difficulty (ID) using Shannon formulation
    # ID = log2(A/W + 1) where A is distance and W is width
    grouped['ID'] = np.log2(grouped['distance'] / grouped['size'] + 1)
    
    # Calculate Index of Performance (IP) in bits per second
    # IP = ID / MT where MT is movement time in seconds
    grouped['IP'] = grouped['ID'] / (grouped['time_ms_mean'] / 1000)
    
    return grouped

def generate_fitts_plots(metrics_df, output_dir="results"):
    """Generate plots for Fitts' Law analysis."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: ID vs MT with linear regression
    plt.figure(figsize=(10, 6))
    
    # Scatter plot for each configuration
    plt.scatter(metrics_df['ID'], metrics_df['time_ms_mean'], 
                s=50, alpha=0.7, c='blue', label='Configurations')
    
    # Add error bars
    plt.errorbar(metrics_df['ID'], metrics_df['time_ms_mean'], 
                yerr=metrics_df['time_ms_std'], fmt='none', 
                ecolor='lightgray', alpha=0.5)
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        metrics_df['ID'], metrics_df['time_ms_mean'])
    
    # Plot regression line
    x_range = np.linspace(metrics_df['ID'].min() - 0.1, metrics_df['ID'].max() + 0.1)
    plt.plot(x_range, intercept + slope * x_range, 'r--', 
             label=f'y = {slope:.2f}x + {intercept:.2f} (R² = {r_value**2:.2f})')
    
    # Add labels and title
    plt.xlabel('Index of Difficulty (bits)')
    plt.ylabel('Movement Time (ms)')
    plt.title("Fitts' Law: Movement Time vs Index of Difficulty")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, 'fitts_law_regression.png'), dpi=300)
    
    # Plot 2: Direction comparison
    plt.figure(figsize=(12, 6))
    
    # Group by ID and direction
    direction_grouped = metrics_df.groupby(['ID', 'direction']).agg({
        'time_ms_mean': 'mean'
    }).reset_index()
    
    # Reshape data for easier plotting
    pivot_df = direction_grouped.pivot(index='ID', columns='direction', values='time_ms_mean')
    
    # Bar plot
    pivot_df.plot(kind='bar', figsize=(12, 6))
    plt.xlabel('Index of Difficulty (bits)')
    plt.ylabel('Movement Time (ms)')
    plt.title('Movement Time Comparison: Left vs Right Direction')
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, 'direction_comparison.png'), dpi=300)
    
    # Plot 3: Error rates by configuration
    plt.figure(figsize=(12, 6))
    
    # Create a bubble chart where size represents error rate
    plt.scatter(metrics_df['distance'], metrics_df['size'], 
                s=metrics_df['errors_mean']*100 + 20, # Scale up for visibility
                alpha=0.6, 
                c=metrics_df['time_ms_mean'], cmap='viridis')
    
    plt.colorbar(label='Movement Time (ms)')
    plt.xlabel('Target Distance (pixels)')
    plt.ylabel('Target Size (pixels)')
    plt.title('Error Rates by Target Configuration')
    plt.grid(True, alpha=0.3)
    
    # Save figure
    plt.savefig(os.path.join(output_dir, 'error_rates.png'), dpi=300)
    
    # Plot 4: Participant comparison
    return os.path.join(output_dir, 'fitts_law_regression.png')

def generate_participant_comparison(df, output_dir="results"):
    """Generate plots comparing participant performance."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate mean stats for each participant
    participant_stats = df.groupby('participant_id').agg({
        'time_ms': 'mean',
        'errors': 'mean',
        'distance_traveled': 'mean'
    }).reset_index()
    
    # Plot comparison
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Movement time comparison
    axes[0].bar(participant_stats['participant_id'], participant_stats['time_ms'], color='skyblue')
    axes[0].set_xlabel('Participant ID')
    axes[0].set_ylabel('Average Movement Time (ms)')
    axes[0].set_title('Movement Time by Participant')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(axis='y', alpha=0.3)
    
    # Error rate comparison
    axes[1].bar(participant_stats['participant_id'], participant_stats['errors'], color='salmon')
    axes[1].set_xlabel('Participant ID')
    axes[1].set_ylabel('Average Errors per Trial')
    axes[1].set_title('Error Rate by Participant')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', alpha=0.3)
    
    # Distance traveled comparison
    axes[2].bar(participant_stats['participant_id'], participant_stats['distance_traveled'], color='lightgreen')
    axes[2].set_xlabel('Participant ID')
    axes[2].set_ylabel('Average Distance Traveled (pixels)')
    axes[2].set_title('Mouse Path Length by Participant')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'participant_comparison.png'), dpi=300)
    return os.path.join(output_dir, 'participant_comparison.png')

def export_to_excel(df, metrics_df, output_dir="results"):
    """Export processed data to Excel for further analysis."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create Excel writer
    with pd.ExcelWriter(os.path.join(output_dir, 'fitts_law_analysis.xlsx')) as writer:
        # Raw data sheet
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        # Configuration means sheet
        metrics_df.to_excel(writer, sheet_name='Configuration Metrics', index=False)
        
        # Participant summary
        participant_summary = df.groupby('participant_id').agg({
            'time_ms': ['mean', 'std', 'min', 'max'],
            'errors': ['mean', 'sum'],
            'distance_traveled': ['mean', 'std']
        })
        participant_summary.columns = ['_'.join(col).strip() for col in participant_summary.columns.values]
        participant_summary.reset_index().to_excel(writer, sheet_name='Participant Summary', index=False)
        
        # Linear regression results
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            metrics_df['ID'], metrics_df['time_ms_mean'])
        
        regression_df = pd.DataFrame({
            'Parameter': ['Slope (a)', 'Intercept (b)', 'R-squared', 'p-value', 'Standard Error'],
            'Value': [slope, intercept, r_value**2, p_value, std_err],
            'Description': [
                'Represents reciprocal of throughput (1/IP)',
                'Represents fixed time overhead',
                'Coefficient of determination',
                'Significance of regression',
                'Standard error of the estimate'
            ]
        })
        regression_df.to_excel(writer, sheet_name='Regression Results', index=False)
    
    return os.path.join(output_dir, 'fitts_law_analysis.xlsx')

def main():
    """Main function to run the analysis."""
    print("Loading participant data...")
    df = load_participant_data()
    
    if df is None:
        print("No data found. Please run the experiment first.")
        return
    
    print(f"Loaded data from {df['participant_id'].nunique()} participants with {len(df)} total trials.")
    
    # Remove outliers
    print("\nRemoving outliers...")
    filtered_df = remove_outliers(df)
    
    # Calculate Fitts' Law metrics
    print("\nCalculating Fitts' Law metrics...")
    metrics_df = calculate_fitts_metrics(filtered_df)
    print(f"Generated metrics for {len(metrics_df)} configurations.")
    
    # Generate plots
    print("\nGenerating plots...")
    plot_path = generate_fitts_plots(metrics_df)
    participant_plot_path = generate_participant_comparison(filtered_df)
    
    # Export to Excel
    print("\nExporting data to Excel...")
    excel_path = export_to_excel(filtered_df, metrics_df)
    
    # Generate report data
    print("\nGenerating report data...")
    report_data = generate_report_data(filtered_df, metrics_df)
    
    # Print key findings
    print("\n=== Key Findings ===")
    print(f"Fitts' Law Correlation (R²): {report_data['regression_stats']['r_squared']:.4f}")
    print(f"Throughput: {report_data['regression_stats']['throughput']:.2f} bits/second")
    print(f"Average Movement Time: {report_data['overall_stats']['mean_movement_time']:.1f} ms")
    print(f"Average Error Rate: {report_data['overall_stats']['mean_error_rate']:.2f} errors per trial")
    
    # Direction comparison
    left_time = report_data['direction_stats'].loc['left', 'time_ms']
    right_time = report_data['direction_stats'].loc['right', 'time_ms']
    dir_diff_pct = abs(left_time - right_time) / min(left_time, right_time) * 100
    
    print(f"\nDirection Difference: {dir_diff_pct:.1f}% (Left: {left_time:.1f} ms, Right: {right_time:.1f} ms)")
    
    # Participant variation
    print(f"\nParticipant Variation in Movement Time: {report_data['participant_stats']['time_variation']:.1f}% CV")
    print(f"Participant Variation in Error Rate: {report_data['participant_stats']['error_variation']:.1f}% CV")
    
    print("\nAnalysis complete!")
    print(f"- Excel file saved to: {excel_path}")
    print(f"- Main plot saved to: {plot_path}")
    print(f"- Participant comparison saved to: {participant_plot_path}")

def generate_report_data(df, metrics_df):
    """Generate summary data for the report."""
    # Overall summary statistics
    overall_stats = {
        'total_participants': df['participant_id'].nunique(),
        'total_trials': len(df),
        'mean_movement_time': df['time_ms'].mean(),
        'mean_error_rate': df['errors'].mean(),
        'mean_distance_traveled': df['distance_traveled'].mean()
    }
    
    # Fitts' Law regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        metrics_df['ID'], metrics_df['time_ms_mean'])
    
    regression_stats = {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'throughput': 1000 / slope  # throughput in bits/s
    }
    
    # Direction comparison
    direction_stats = df.groupby('direction').agg({
        'time_ms': 'mean',
        'errors': 'mean'
    })
    
    # Size comparison
    size_stats = df.groupby('size').agg({
        'time_ms': 'mean',
        'errors': 'mean'
    })
    
    # Distance comparison
    distance_stats = df.groupby('distance').agg({
        'time_ms': 'mean',
        'errors': 'mean'
    })
    
    # Participant variability 
    participant_var = df.groupby('participant_id').agg({
        'time_ms': ['mean', 'std'],
        'errors': 'mean',
        'distance_traveled': 'mean'
    })
    
    participant_var.columns = ['_'.join(col).strip() for col in participant_var.columns.values]
    participant_var = participant_var.reset_index()
    
    participant_stats = {
        'fastest_participant': participant_var.loc[participant_var['time_ms_mean'].idxmin()]['participant_id'],
        'slowest_participant': participant_var.loc[participant_var['time_ms_mean'].idxmax()]['participant_id'],
        'most_accurate_participant': participant_var.loc[participant_var['errors_mean'].idxmin()]['participant_id'],
        'least_accurate_participant': participant_var.loc[participant_var['errors_mean'].idxmax()]['participant_id'],
        'time_variation': participant_var['time_ms_mean'].std() / participant_var['time_ms_mean'].mean() * 100, # CV as percentage
        'error_variation': participant_var['errors_mean'].std() / (participant_var['errors_mean'].mean() + 0.001) * 100 # Avoid div by 0
    }
    
    return {
        'overall_stats': overall_stats,
        'regression_stats': regression_stats,
        'direction_stats': direction_stats,
        'size_stats': size_stats,
        'distance_stats': distance_stats,
        'participant_stats': participant_stats
    }