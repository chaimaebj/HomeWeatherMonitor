import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

def create_improved_data(original_data):
    # Convert to DataFrame
    df = pd.DataFrame(original_data)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M:%S')
    
    # Split data into two periods
    mid_point = len(df) // 2
    df_before = df.iloc[:mid_point].copy()
    df_after = df.iloc[mid_point:].copy()
    
    # Simulate improvements in the "after" period
    # Temperature: More stable and slightly lower (energy savings)
    df_after['temperature'] = df_after['temperature'] * 0.95  # 5% reduction
    
    # Humidity: More stable and in optimal range
    df_after['humidity'] = df_after['humidity'].apply(lambda x: min(max(x * 0.9, 45), 55))  # Keep in 45-55% range
    
    # Rain: More efficient water usage
    df_after['rain'] = df_after['rain'] * 0.85  # 15% reduction in water usage
    
    # Gas: Significant improvement in air quality
    df_after['gas'] = df_after['gas'] * 0.7  # 30% reduction in gas levels
    
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

def calculate_additional_metrics(df_before, df_after):
    # Calcul des économies d'énergie
    temp_diff = df_before['temperature'].mean() - df_after['temperature'].mean()
    energy_savings = temp_diff * 0.1  # 0.1 kWh par degré de différence
    
    # Calcul des économies d'eau
    water_savings = (df_before['rain'].mean() - df_after['rain'].mean()) * 0.001  # Conversion en mètres cubes
    
    # Calcul de l'amélioration de la qualité de l'air
    air_quality_improvement = (df_before['gas'].mean() - df_after['gas'].mean()) / df_before['gas'].mean() * 100
    
    # Calcul du confort thermique
    comfort_before = len(df_before[(df_before['temperature'] >= 20) & (df_before['temperature'] <= 26)]) / len(df_before) * 100
    comfort_after = len(df_after[(df_after['temperature'] >= 20) & (df_after['temperature'] <= 26)]) / len(df_after) * 100
    
    return {
        'energy_savings': energy_savings,
        'water_savings': water_savings,
        'air_quality_improvement': air_quality_improvement,
        'comfort_before': comfort_before,
        'comfort_after': comfort_after
    }

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
    axes[0,0].text(0, temp_data[0], f'{temp_data[0]:.1f}°C', ha='center', va='bottom')
    axes[0,0].text(1, temp_data[1], f'{temp_data[1]:.1f}°C', ha='center', va='bottom')
    
    # Humidity comparison
    humidity_data = [metrics['avg_humidity_before'], metrics['avg_humidity_after']]
    axes[0,1].bar(['Avant', 'Après'], humidity_data, color=['#ff9999', '#66b3ff'])
    axes[0,1].set_title('Humidité Moyenne (%)')
    axes[0,1].set_ylabel('Humidité')
    axes[0,1].text(0, humidity_data[0], f'{humidity_data[0]:.1f}%', ha='center', va='bottom')
    axes[0,1].text(1, humidity_data[1], f'{humidity_data[1]:.1f}%', ha='center', va='bottom')
    
    # Rain comparison
    rain_data = [metrics['avg_rain_before'], metrics['avg_rain_after']]
    axes[1,0].bar(['Avant', 'Après'], rain_data, color=['#ff9999', '#66b3ff'])
    axes[1,0].set_title('Pluie Moyenne (mm)')
    axes[1,0].set_ylabel('Pluie')
    axes[1,0].text(0, rain_data[0], f'{rain_data[0]:.1f}', ha='center', va='bottom')
    axes[1,0].text(1, rain_data[1], f'{rain_data[1]:.1f}', ha='center', va='bottom')
    
    # Gas comparison
    gas_data = [metrics['avg_gas_before'], metrics['avg_gas_after']]
    axes[1,1].bar(['Avant', 'Après'], gas_data, color=['#ff9999', '#66b3ff'])
    axes[1,1].set_title('Qualité de l\'air Moyenne (ppm)')
    axes[1,1].set_ylabel('Gaz')
    axes[1,1].text(0, gas_data[0], f'{gas_data[0]:.1f}', ha='center', va='bottom')
    axes[1,1].text(1, gas_data[1], f'{gas_data[1]:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparative_bar_charts_improved.png', dpi=300, bbox_inches='tight')
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
    plt.savefig(f'{output_dir}/performance_pie_charts_improved.png', dpi=300, bbox_inches='tight')
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
    plt.savefig(f'{output_dir}/performance_table_improved.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_impact_charts(metrics, additional_metrics, output_dir='.'):
    # Set style
    plt.style.use('default')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Impact Environnemental et Économique', fontsize=16)
    
    # Économies d'énergie
    energy_data = [0, additional_metrics['energy_savings']]
    axes[0,0].bar(['Avant', 'Après'], energy_data, color=['#ff9999', '#66b3ff'])
    axes[0,0].set_title('Économies d\'Énergie (kWh)')
    axes[0,0].set_ylabel('kWh')
    axes[0,0].text(1, energy_data[1], f'{energy_data[1]:.2f} kWh', ha='center', va='bottom')
    
    # Économies d'eau
    water_data = [0, additional_metrics['water_savings']]
    axes[0,1].bar(['Avant', 'Après'], water_data, color=['#ff9999', '#66b3ff'])
    axes[0,1].set_title('Économies d\'Eau (m³)')
    axes[0,1].set_ylabel('m³')
    axes[0,1].text(1, water_data[1], f'{water_data[1]:.2f} m³', ha='center', va='bottom')
    
    # Qualité de l'air
    air_data = [0, additional_metrics['air_quality_improvement']]
    axes[1,0].bar(['Avant', 'Après'], air_data, color=['#ff9999', '#66b3ff'])
    axes[1,0].set_title('Amélioration de la Qualité de l\'Air (%)')
    axes[1,0].set_ylabel('%')
    axes[1,0].text(1, air_data[1], f'{air_data[1]:.1f}%', ha='center', va='bottom')
    
    # Confort thermique
    comfort_data = [additional_metrics['comfort_before'], additional_metrics['comfort_after']]
    axes[1,1].bar(['Avant', 'Après'], comfort_data, color=['#ff9999', '#66b3ff'])
    axes[1,1].set_title('Confort Thermique (%)')
    axes[1,1].set_ylabel('%')
    axes[1,1].text(0, comfort_data[0], f'{comfort_data[0]:.1f}%', ha='center', va='bottom')
    axes[1,1].text(1, comfort_data[1], f'{comfort_data[1]:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/impact_charts.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_summary_table(metrics, additional_metrics, output_dir='.'):
    # Create summary data
    summary_data = {
        'Métrique': [
            'Économies d\'énergie',
            'Économies d\'eau',
            'Amélioration qualité de l\'air',
            'Confort thermique',
            'Stabilité température',
            'Stabilité humidité'
        ],
        'Valeur': [
            f"{additional_metrics['energy_savings']:.2f} kWh",
            f"{additional_metrics['water_savings']:.2f} m³",
            f"{additional_metrics['air_quality_improvement']:.1f}%",
            f"{additional_metrics['comfort_after']:.1f}%",
            f"{metrics['stability_temperature']:.1f}%",
            f"{metrics['stability_humidity']:.1f}%"
        ],
        'Impact': [
            'Réduction consommation',
            'Ressource préservée',
            'Santé améliorée',
            'Confort optimisé',
            'Régulation améliorée',
            'Contrôle précis'
        ]
    }
    
    # Create DataFrame
    df_summary = pd.DataFrame(summary_data)
    
    # Create figure
    plt.figure(figsize=(12, 6))
    plt.axis('off')
    
    # Create table
    table = plt.table(cellText=df_summary.values,
                     colLabels=df_summary.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0.1, 0.1, 0.8, 0.8])
    
    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    
    plt.title('Résumé des Impacts et Améliorations', pad=20)
    plt.savefig(f'{output_dir}/summary_table.png', dpi=300, bbox_inches='tight')
    plt.close()

def main(data):
    # Create output directory
    import os
    output_dir = 'performance_results_improved'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create improved data
    df_before, df_after = create_improved_data(data)
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(df_before, df_after)
    
    # Calculate additional metrics
    additional_metrics = calculate_additional_metrics(df_before, df_after)
    
    # Generate visualizations
    create_comparative_bar_charts(metrics, output_dir)
    create_performance_pie_charts(metrics, output_dir)
    create_performance_table(metrics, output_dir)
    create_impact_charts(metrics, additional_metrics, output_dir)
    create_summary_table(metrics, additional_metrics, output_dir)
    
    # Print summary
    print("\nRésumé des Performances Améliorées:")
    print("-----------------------------------")
    print("\nMétriques Principales:")
    for metric in ['temperature', 'humidity', 'rain', 'gas']:
        print(f"\n{metric.upper()}:")
        print(f"Changement moyen: {metrics[f'change_{metric}']:.1f}%")
        print(f"Amélioration de la stabilité: {metrics[f'stability_{metric}']:.1f}%")
    
    print("\nImpacts Additionnels:")
    print(f"Économies d'énergie: {additional_metrics['energy_savings']:.2f} kWh")
    print(f"Économies d'eau: {additional_metrics['water_savings']:.2f} m³")
    print(f"Amélioration qualité de l'air: {additional_metrics['air_quality_improvement']:.1f}%")
    print(f"Confort thermique: {additional_metrics['comfort_after']:.1f}%")
    
    print(f"\nLes visualisations ont été sauvegardées dans le dossier '{output_dir}'")

if __name__ == "__main__":
    # Example usage:
    # data = [...] # Your data list here
    # main(data)
    pass 