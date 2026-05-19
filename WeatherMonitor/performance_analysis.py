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
    
    # Split data into two periods (before/after)
    mid_point = len(df) // 2
    df_before = df.iloc[:mid_point]
    df_after = df.iloc[mid_point:]
    
    return df_before, df_after

def calculate_performance_metrics(df_before, df_after):
    metrics = {}
    
    # Calculate average values
    for metric in ['temperature', 'humidity', 'rain', 'gas']:
        metrics[f'avg_{metric}_before'] = df_before[metric].mean()
        metrics[f'avg_{metric}_after'] = df_after[metric].mean()
        
        # Calculate percentage change
        metrics[f'change_{metric}'] = ((df_after[metric].mean() - df_before[metric].mean()) / 
                                     df_before[metric].mean() * 100)
    
    # Calculate stability metrics (standard deviation)
    for metric in ['temperature', 'humidity', 'rain', 'gas']:
        metrics[f'std_{metric}_before'] = df_before[metric].std()
        metrics[f'std_{metric}_after'] = df_after[metric].std()
        
        # Calculate stability improvement
        metrics[f'stability_{metric}'] = ((df_before[metric].std() - df_after[metric].std()) / 
                                        df_before[metric].std() * 100)
    
    return metrics

def create_comparative_bar_charts(metrics, output_dir='.'):
    # Set style
    plt.style.use('default')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Comparaison des Mesures Avant/Après', fontsize=16)
    
    # Temperature comparison
    temp_data = [metrics['avg_temperature_before'], metrics['avg_temperature_after']]
    axes[0,0].bar(['Avant', 'Après'], temp_data, color=['#ff9999', '#66b3ff'])
    axes[0,0].set_title('Température Moyenne (°C)')
    axes[0,0].set_ylabel('Température')
    
    # Humidity comparison
    humidity_data = [metrics['avg_humidity_before'], metrics['avg_humidity_after']]
    axes[0,1].bar(['Avant', 'Après'], humidity_data, color=['#ff9999', '#66b3ff'])
    axes[0,1].set_title('Humidité Moyenne (%)')
    axes[0,1].set_ylabel('Humidité')
    
    # Rain comparison
    rain_data = [metrics['avg_rain_before'], metrics['avg_rain_after']]
    axes[1,0].bar(['Avant', 'Après'], rain_data, color=['#ff9999', '#66b3ff'])
    axes[1,0].set_title('Pluie Moyenne (mm)')
    axes[1,0].set_ylabel('Pluie')
    
    # Gas comparison
    gas_data = [metrics['avg_gas_before'], metrics['avg_gas_after']]
    axes[1,1].bar(['Avant', 'Après'], gas_data, color=['#ff9999', '#66b3ff'])
    axes[1,1].set_title('Qualité de l\'air Moyenne (ppm)')
    axes[1,1].set_ylabel('Gaz')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparative_bar_charts.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_pie_charts(metrics, output_dir='.'):
    # Set style
    plt.style.use('default')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Amélioration des Performances', fontsize=16)
    
    # Temperature stability
    temp_stability = [abs(metrics['stability_temperature']), 100 - abs(metrics['stability_temperature'])]
    axes[0,0].pie(temp_stability, labels=['Amélioration', 'Reste'], autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'])
    axes[0,0].set_title('Stabilité de la Température')
    
    # Humidity stability
    humidity_stability = [abs(metrics['stability_humidity']), 100 - abs(metrics['stability_humidity'])]
    axes[0,1].pie(humidity_stability, labels=['Amélioration', 'Reste'], autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'])
    axes[0,1].set_title('Stabilité de l\'Humidité')
    
    # Rain stability
    rain_stability = [abs(metrics['stability_rain']), 100 - abs(metrics['stability_rain'])]
    axes[1,0].pie(rain_stability, labels=['Amélioration', 'Reste'], autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'])
    axes[1,0].set_title('Stabilité de la Pluie')
    
    # Gas stability
    gas_stability = [abs(metrics['stability_gas']), 100 - abs(metrics['stability_gas'])]
    axes[1,1].pie(gas_stability, labels=['Amélioration', 'Reste'], autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'])
    axes[1,1].set_title('Stabilité de la Qualité de l\'air')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/performance_pie_charts.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_table(metrics, output_dir='.'):
    # Create performance summary
    performance_data = {
        'Métrique': ['Température', 'Humidité', 'Pluie', 'Qualité de l\'air'],
        'Changement (%)': [
            f"{metrics['change_temperature']:.1f}%",
            f"{metrics['change_humidity']:.1f}%",
            f"{metrics['change_rain']:.1f}%",
            f"{metrics['change_gas']:.1f}%"
        ],
        'Amélioration de la Stabilité (%)': [
            f"{metrics['stability_temperature']:.1f}%",
            f"{metrics['stability_humidity']:.1f}%",
            f"{metrics['stability_rain']:.1f}%",
            f"{metrics['stability_gas']:.1f}%"
        ]
    }
    
    # Create DataFrame
    df_performance = pd.DataFrame(performance_data)
    
    # Create figure
    plt.figure(figsize=(10, 4))
    plt.axis('off')
    
    # Create table
    table = plt.table(cellText=df_performance.values,
                     colLabels=df_performance.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0.1, 0.1, 0.8, 0.8])
    
    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    
    plt.title('Tableau de Performance', pad=20)
    plt.savefig(f'{output_dir}/performance_table.png', dpi=300, bbox_inches='tight')
    plt.close()

def main(data):
    # Create output directory
    import os
    output_dir = 'performance_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and prepare data
    df_before, df_after = load_and_prepare_data(data)
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(df_before, df_after)
    
    # Generate visualizations
    create_comparative_bar_charts(metrics, output_dir)
    create_performance_pie_charts(metrics, output_dir)
    create_performance_table(metrics, output_dir)
    
    # Print summary
    print("\nRésumé des Performances:")
    print("------------------------")
    for metric in ['temperature', 'humidity', 'rain', 'gas']:
        print(f"\n{metric.upper()}:")
        print(f"Changement moyen: {metrics[f'change_{metric}']:.1f}%")
        print(f"Amélioration de la stabilité: {metrics[f'stability_{metric}']:.1f}%")
    
    print(f"\nLes visualisations ont été sauvegardées dans le dossier '{output_dir}'")

if __name__ == "__main__":
    # Example usage:
    # data = [...] # Your data list here
    # main(data)
    pass 