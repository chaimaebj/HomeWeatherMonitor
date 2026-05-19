import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

def load_and_prepare_data(data):
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M:%S')
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    return df

def create_time_series_plots(df, output_dir='.'):
    # Set style
    plt.style.use('seaborn')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Évolution des Mesures Environnementales', fontsize=16)
    
    # Temperature plot
    axes[0,0].plot(df['timestamp'], df['temperature'], 'r-', linewidth=2)
    axes[0,0].set_title('Température (°C)')
    axes[0,0].set_xlabel('Temps')
    axes[0,0].set_ylabel('Température')
    axes[0,0].grid(True)
    
    # Humidity plot
    axes[0,1].plot(df['timestamp'], df['humidity'], 'b-', linewidth=2)
    axes[0,1].set_title('Humidité (%)')
    axes[0,1].set_xlabel('Temps')
    axes[0,1].set_ylabel('Humidité')
    axes[0,1].grid(True)
    
    # Rain plot
    axes[1,0].plot(df['timestamp'], df['rain'], 'g-', linewidth=2)
    axes[1,0].set_title('Pluie (mm)')
    axes[1,0].set_xlabel('Temps')
    axes[1,0].set_ylabel('Pluie')
    axes[1,0].grid(True)
    
    # Gas plot
    axes[1,1].plot(df['timestamp'], df['gas'], 'purple', linewidth=2)
    axes[1,1].set_title('Qualité de l\'air (ppm)')
    axes[1,1].set_xlabel('Temps')
    axes[1,1].set_ylabel('Gaz')
    axes[1,1].grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/time_series_plots.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_correlation_heatmap(df, output_dir='.'):
    # Calculate correlation matrix
    corr_matrix = df[['temperature', 'humidity', 'rain', 'gas']].corr()
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Matrice de Corrélation des Mesures')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_statistical_summary(df, output_dir='.'):
    # Calculate statistics
    stats = df[['temperature', 'humidity', 'rain', 'gas']].describe()
    
    # Create figure
    plt.figure(figsize=(12, 6))
    plt.axis('off')
    
    # Create table
    table = plt.table(cellText=stats.values,
                     rowLabels=stats.index,
                     colLabels=stats.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0.1, 0.1, 0.8, 0.8])
    
    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    plt.title('Statistiques Descriptives des Mesures', pad=20)
    plt.savefig(f'{output_dir}/statistical_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_box_plots(df, output_dir='.'):
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Distribution des Mesures', fontsize=16)
    
    # Temperature box plot
    sns.boxplot(y=df['temperature'], ax=axes[0,0], color='red')
    axes[0,0].set_title('Température (°C)')
    
    # Humidity box plot
    sns.boxplot(y=df['humidity'], ax=axes[0,1], color='blue')
    axes[0,1].set_title('Humidité (%)')
    
    # Rain box plot
    sns.boxplot(y=df['rain'], ax=axes[1,0], color='green')
    axes[1,0].set_title('Pluie (mm)')
    
    # Gas box plot
    sns.boxplot(y=df['gas'], ax=axes[1,1], color='purple')
    axes[1,1].set_title('Qualité de l\'air (ppm)')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/box_plots.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_scatter_matrix(df, output_dir='.'):
    # Create scatter matrix
    plt.figure(figsize=(12, 12))
    sns.pairplot(df[['temperature', 'humidity', 'rain', 'gas']], 
                 diag_kind='kde',
                 plot_kws={'alpha': 0.6})
    plt.suptitle('Matrice de Dispersion des Mesures', y=1.02)
    plt.savefig(f'{output_dir}/scatter_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()

def main(data):
    # Create output directory if it doesn't exist
    import os
    output_dir = 'visualization_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and prepare data
    df = load_and_prepare_data(data)
    
    # Generate all visualizations
    create_time_series_plots(df, output_dir)
    create_correlation_heatmap(df, output_dir)
    create_statistical_summary(df, output_dir)
    create_box_plots(df, output_dir)
    create_scatter_matrix(df, output_dir)
    
    print(f"Visualizations have been saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    # Example usage:
    # data = [...] # Your data list here
    # main(data)
    pass 