"""
Generate professional figures for master's thesis
Comparing optimization methods across various scenarios and metrics
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

# Set professional style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Create output directory
OUTPUT_DIR = Path("thesis_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# Color scheme for methods
METHOD_COLORS = {
    'Random Search': '#FF6B6B',
    'Greedy Heuristic': '#4ECDC4',
    'Exact Solver': '#45B7D1',
    'Exact ILP': '#96CEB4',
    'Genetic Algorithm': '#FFEAA7'
}

# ============================================================================
# DATA: Collected from all test runs
# ============================================================================

# Scenario 1: Over-stocked (demand 3350, quantity 5000)
scenario_1 = {
    'name': 'Over-stocked\n(+49% buffer)',
    'demand': 3350,
    'quantity': 5000,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [10694930, 10685990, 10685990, 10403500, 10685990],
    'service': [100, 100, 100, 100, 100],
    'fitness': [0.4669, 0.4670, 0.4670, 0.4695, 0.4670],
    'runtime': [0.008, 0.001, 0.010, 0.031, 0.306]
}

# Scenario 2: Just-in-time (demand 3350, quantity 3350)
scenario_2 = {
    'name': 'Just-in-time\n(exact match)',
    'demand': 3350,
    'quantity': 3350,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [10073500, 10073500, 10073500, 10073500, 10073500],
    'service': [100, 100, 100, 100, 100],
    'fitness': [0.4779, 0.4779, 0.4779, 0.4779, 0.4779],
    'runtime': [0.008, 0.001, 0.009, 0.031, 0.304]
}

# Scenario 3: Under-stocked (demand 3350, quantity 2000)
scenario_3 = {
    'name': 'Under-stocked\n(-40% shortage)',
    'demand': 3350,
    'quantity': 2000,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [9576010, 9572440, 9572440, 9450000, 9572440],
    'service': [60, 60, 60, 45, 60],
    'fitness': [0.2851, 0.2851, 0.2851, 0.2115, 0.2851],
    'runtime': [0.009, 0.001, 0.010, 0.031, 0.318]
}

# Scenario 4: Medium demand + buffer (demand 12000, quantity 15000)
scenario_4 = {
    'name': 'Medium demand\n(+25% buffer)',
    'demand': 12000,
    'quantity': 15000,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [18997000, 18129250, 18997000, 14493000, 14982820],
    'service': [100, 100, 100, 100, 100],
    'fitness': [0.3879, 0.3829, 0.3879, 0.4010, 0.3962],
    'runtime': [0.009, 0.001, 0.010, 0.032, 0.321]
}

# Scenario 5: High demand (demand 40000, quantity 12000)
scenario_5 = {
    'name': 'High demand\n(-70% shortage)',
    'demand': 40000,
    'quantity': 12000,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [16429000, 16143000, 16143000, 12944000, 13759030],
    'service': [31, 31, 31, 30, 30],
    'fitness': [0.0599, 0.0622, 0.0622, 0.0763, 0.0653],
    'runtime': [0.009, 0.001, 0.010, 0.032, 0.312]
}

# Edge Case 1: Unbalanced warehouses (demand 24000, quantity 11000)
edge_1 = {
    'name': 'Edge: Unbalanced\n(-54% shortage)',
    'demand': 24000,
    'quantity': 11000,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [14759420, 15159860, 15159860, 12175000, 13284550],
    'service': [46, 46, 46, 42, 46],
    'fitness': [0.1461, 0.1474, 0.1474, 0.1470, 0.1524],
    'runtime': [0.009, 0.001, 0.008, 0.031, 0.314]
}

# Edge Case 2: Missing region (demand 20000, quantity 10000)
edge_2 = {
    'name': 'Edge: No ouest WH\n(-50% shortage)',
    'demand': 20000,
    'quantity': 10000,
    'methods': ['Random Search', 'Greedy Heuristic', 'Exact Solver', 'Exact ILP', 'Genetic Algorithm'],
    'cost': [10255000, 10255000, 10255000, 8255000, 9260000],
    'service': [50, 50, 50, 42, 45],
    'fitness': [0.1177, 0.1177, 0.1177, 0.1027, 0.1022],
    'runtime': [0.006, 0.000, 0.000, 0.021, 0.171]
}

all_scenarios = [scenario_1, scenario_2, scenario_3, scenario_4, scenario_5, edge_1, edge_2]

# ============================================================================
# FIGURE 1: Total Cost Comparison Across Scenarios
# ============================================================================

def create_cost_comparison():
    """Bar chart comparing total cost across all scenarios"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    scenarios = [s['name'] for s in all_scenarios]
    x = np.arange(len(scenarios))
    width = 0.15
    
    for i, method in enumerate(scenario_1['methods']):
        costs = [s['cost'][i] / 1e6 for s in all_scenarios]  # Convert to millions
        offset = width * (i - 2)
        ax.bar(x + offset, costs, width, label=method, color=METHOD_COLORS[method])
    
    ax.set_xlabel('Scenario', fontweight='bold')
    ax.set_ylabel('Total Cost (Million DZD)', fontweight='bold')
    ax.set_title('Total Cost Comparison Across Different Scenarios', fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=0, ha='center')
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig1_cost_comparison.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig1_cost_comparison.pdf', bbox_inches='tight')
    print("[OK] Generated: fig1_cost_comparison")
    plt.close()

# ============================================================================
# FIGURE 2: Service Level Comparison
# ============================================================================

def create_service_level_comparison():
    """Line plot showing service level across scenarios"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = [s['name'] for s in all_scenarios]
    x = np.arange(len(scenarios))
    
    for i, method in enumerate(scenario_1['methods']):
        service_levels = [s['service'][i] for s in all_scenarios]
        ax.plot(x, service_levels, marker='o', linewidth=2, markersize=8, 
                label=method, color=METHOD_COLORS[method])
    
    ax.set_xlabel('Scenario', fontweight='bold')
    ax.set_ylabel('Service Level (%)', fontweight='bold')
    ax.set_title('Service Level Achievement Across Scenarios', fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=0, ha='center')
    ax.set_ylim([0, 105])
    ax.legend(loc='lower left', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Target (100%)')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig2_service_level.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig2_service_level.pdf', bbox_inches='tight')
    print("[OK] Generated: fig2_service_level")
    plt.close()

# ============================================================================
# FIGURE 3: Runtime Performance
# ============================================================================

def create_runtime_comparison():
    """Log-scale bar chart for runtime"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = [s['name'] for s in all_scenarios]
    x = np.arange(len(scenarios))
    width = 0.15
    
    for i, method in enumerate(scenario_1['methods']):
        runtimes = [s['runtime'][i] * 1000 for s in all_scenarios]  # Convert to ms
        offset = width * (i - 2)
        ax.bar(x + offset, runtimes, width, label=method, color=METHOD_COLORS[method])
    
    ax.set_xlabel('Scenario', fontweight='bold')
    ax.set_ylabel('Runtime (milliseconds, log scale)', fontweight='bold')
    ax.set_title('Computational Performance Comparison', fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=0, ha='center')
    ax.set_yscale('log')
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(axis='y', alpha=0.3, linestyle='--', which='both')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig3_runtime.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig3_runtime.pdf', bbox_inches='tight')
    print("[OK] Generated: fig3_runtime")
    plt.close()

# ============================================================================
# FIGURE 4: Fitness Score Heatmap
# ============================================================================

def create_fitness_heatmap():
    """Heatmap showing fitness scores"""
    data = []
    for scenario in all_scenarios:
        data.append(scenario['fitness'])
    
    df = pd.DataFrame(data, 
                     columns=scenario_1['methods'],
                     index=[s['name'] for s in all_scenarios])
    
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(df, annot=True, fmt='.4f', cmap='RdYlGn', center=0.3,
                cbar_kws={'label': 'Fitness Score'}, ax=ax, linewidths=0.5)
    
    ax.set_title('Fitness Score Comparison Matrix\n(Higher is Better)', 
                 fontweight='bold', pad=20)
    ax.set_xlabel('Optimization Method', fontweight='bold')
    ax.set_ylabel('Scenario', fontweight='bold')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig4_fitness_heatmap.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig4_fitness_heatmap.pdf', bbox_inches='tight')
    print("[OK] Generated: fig4_fitness_heatmap")
    plt.close()

# ============================================================================
# FIGURE 5: Cost Savings by ILP
# ============================================================================

def create_ilp_savings():
    """Bar chart showing ILP cost savings compared to other methods"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = [s['name'] for s in all_scenarios]
    ilp_idx = 3  # Index of ILP in methods list
    
    # Calculate savings vs average of other methods
    savings = []
    for scenario in all_scenarios:
        ilp_cost = scenario['cost'][ilp_idx]
        other_costs = [scenario['cost'][i] for i in range(len(scenario['methods'])) if i != ilp_idx]
        avg_other = np.mean(other_costs)
        savings_pct = ((avg_other - ilp_cost) / avg_other) * 100
        savings.append(savings_pct)
    
    colors = ['green' if s > 0 else 'red' for s in savings]
    bars = ax.bar(scenarios, savings, color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, saving in zip(bars, savings):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{saving:.1f}%', ha='center', va='bottom' if saving > 0 else 'top',
                fontweight='bold')
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Scenario', fontweight='bold')
    ax.set_ylabel('Cost Savings (%)', fontweight='bold')
    ax.set_title('ILP Cost Savings vs Average of Other Methods', fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=0, ha='center')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig5_ilp_savings.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig5_ilp_savings.pdf', bbox_inches='tight')
    print("[OK] Generated: fig5_ilp_savings")
    plt.close()

# ============================================================================
# FIGURE 6: Cost vs Service Level Trade-off
# ============================================================================

def create_cost_service_tradeoff():
    """Scatter plot showing cost-service trade-off"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for i, method in enumerate(scenario_1['methods']):
        costs = [s['cost'][i] / 1e6 for s in all_scenarios]
        services = [s['service'][i] for s in all_scenarios]
        
        ax.scatter(costs, services, s=150, alpha=0.7, 
                  label=method, color=METHOD_COLORS[method],
                  edgecolors='black', linewidth=1)
        
        # Add trend line for each method
        z = np.polyfit(costs, services, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(min(costs), max(costs), 100)
        ax.plot(x_trend, p(x_trend), linestyle='--', alpha=0.3, 
                color=METHOD_COLORS[method], linewidth=1)
    
    ax.set_xlabel('Total Cost (Million DZD)', fontweight='bold')
    ax.set_ylabel('Service Level (%)', fontweight='bold')
    ax.set_title('Cost vs Service Level Trade-off Analysis', fontweight='bold', pad=20)
    ax.legend(loc='lower right', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add Pareto frontier annotation
    ax.text(0.05, 0.95, 'Ideal: High Service, Low Cost ↖', 
            transform=ax.transAxes, fontsize=9, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig6_cost_service_tradeoff.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig6_cost_service_tradeoff.pdf', bbox_inches='tight')
    print("[OK] Generated: fig6_cost_service_tradeoff")
    plt.close()

# ============================================================================
# FIGURE 7: Method Performance Summary (Radar Chart)
# ============================================================================

def create_radar_chart():
    """Radar chart comparing methods on multiple criteria"""
    from math import pi
    
    # Normalize metrics to 0-1 scale for comparison
    categories = ['Cost\nEfficiency', 'Service\nLevel', 'Runtime\nSpeed', 
                  'Fitness\nScore', 'Consistency']
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Calculate scores for each method (higher is better)
    method_scores = {}
    for i, method in enumerate(scenario_1['methods']):
        # Cost efficiency: inverse normalized
        costs = [s['cost'][i] for s in all_scenarios]
        cost_score = 1 - (np.mean(costs) - min([min(s['cost']) for s in all_scenarios])) / \
                     (max([max(s['cost']) for s in all_scenarios]) - min([min(s['cost']) for s in all_scenarios]))
        
        # Service level: normalized
        services = [s['service'][i] for s in all_scenarios]
        service_score = np.mean(services) / 100
        
        # Runtime: inverse normalized (faster is better)
        runtimes = [s['runtime'][i] for s in all_scenarios]
        runtime_score = 1 - (np.mean(runtimes) - min([min(s['runtime']) for s in all_scenarios])) / \
                        (max([max(s['runtime']) for s in all_scenarios]) - min([min(s['runtime']) for s in all_scenarios]))
        
        # Fitness: normalized
        fitnesses = [s['fitness'][i] for s in all_scenarios]
        fitness_score = (np.mean(fitnesses) - min([min(s['fitness']) for s in all_scenarios])) / \
                       (max([max(s['fitness']) for s in all_scenarios]) - min([min(s['fitness']) for s in all_scenarios]))
        
        # Consistency: inverse of std deviation
        all_metrics = costs + services + [r*1000 for r in runtimes]
        consistency_score = 1 - (np.std(all_metrics) / np.mean(all_metrics)) if np.mean(all_metrics) > 0 else 0
        consistency_score = max(0, min(1, consistency_score))
        
        method_scores[method] = [cost_score, service_score, runtime_score, fitness_score, consistency_score]
    
    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]
    
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=8)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    for method, scores in method_scores.items():
        scores_plot = scores + scores[:1]
        ax.plot(angles, scores_plot, linewidth=2, label=method, color=METHOD_COLORS[method])
        ax.fill(angles, scores_plot, alpha=0.15, color=METHOD_COLORS[method])
    
    ax.set_title('Multi-Criteria Performance Comparison\n(Normalized Scores)', 
                 fontweight='bold', pad=30, size=12)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=True, shadow=True)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig7_radar_comparison.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig7_radar_comparison.pdf', bbox_inches='tight')
    print("[OK] Generated: fig7_radar_comparison")
    plt.close()

# ============================================================================
# FIGURE 8: Scenario Difficulty Analysis
# ============================================================================

def create_difficulty_analysis():
    """Show how scenario difficulty affects method performance"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Calculate difficulty metric: (demand - quantity) / demand
    difficulties = [(s['demand'] - s['quantity']) / s['demand'] * 100 for s in all_scenarios]
    scenario_names = [s['name'] for s in all_scenarios]
    
    # Left plot: Cost variation with difficulty
    for i, method in enumerate(scenario_1['methods']):
        costs = [s['cost'][i] / 1e6 for s in all_scenarios]
        ax1.scatter(difficulties, costs, s=100, label=method, 
                   color=METHOD_COLORS[method], alpha=0.7, edgecolors='black')
    
    ax1.set_xlabel('Shortage Level (%) - Higher = More Difficult', fontweight='bold')
    ax1.set_ylabel('Total Cost (Million DZD)', fontweight='bold')
    ax1.set_title('Cost vs Scenario Difficulty', fontweight='bold')
    ax1.legend(frameon=True, shadow=True)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Right plot: Service level variation with difficulty
    for i, method in enumerate(scenario_1['methods']):
        services = [s['service'][i] for s in all_scenarios]
        ax2.scatter(difficulties, services, s=100, label=method,
                   color=METHOD_COLORS[method], alpha=0.7, edgecolors='black')
    
    ax2.set_xlabel('Shortage Level (%) - Higher = More Difficult', fontweight='bold')
    ax2.set_ylabel('Service Level (%)', fontweight='bold')
    ax2.set_title('Service Level vs Scenario Difficulty', fontweight='bold')
    ax2.legend(frameon=True, shadow=True)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig8_difficulty_analysis.png', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig8_difficulty_analysis.pdf', bbox_inches='tight')
    print("[OK] Generated: fig8_difficulty_analysis")
    plt.close()

# ============================================================================
# FIGURE 9: Performance Summary Table (as image)
# ============================================================================

def create_summary_table():
    """Create a professional summary table"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Calculate average metrics for each method
    table_data = []
    for i, method in enumerate(scenario_1['methods']):
        avg_cost = np.mean([s['cost'][i] for s in all_scenarios]) / 1e6
        avg_service = np.mean([s['service'][i] for s in all_scenarios])
        avg_runtime = np.mean([s['runtime'][i] for s in all_scenarios]) * 1000
        avg_fitness = np.mean([s['fitness'][i] for s in all_scenarios])
        
        # Calculate win rate (how many times this method had best cost)
        wins = sum(1 for s in all_scenarios if s['cost'][i] == min(s['cost']))
        
        table_data.append([
            method,
            f'{avg_cost:.2f}',
            f'{avg_service:.1f}%',
            f'{avg_runtime:.1f}',
            f'{avg_fitness:.4f}',
            f'{wins}/{len(all_scenarios)}'
        ])
    
    table = ax.table(cellText=table_data,
                    colLabels=['Method', 'Avg Cost\n(M DZD)', 'Avg Service\nLevel', 
                              'Avg Runtime\n(ms)', 'Avg Fitness', 'Best Cost\nWins'],
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.25, 0.15, 0.15, 0.15, 0.15, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(6):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style rows with alternating colors
    for i in range(1, len(table_data) + 1):
        color = '#f0f0f0' if i % 2 == 0 else 'white'
        for j in range(6):
            table[(i, j)].set_facecolor(color)
            table[(i, j)].set_edgecolor('gray')
    
    plt.title('Performance Summary Across All Scenarios', 
              fontweight='bold', size=14, pad=20)
    
    plt.savefig(OUTPUT_DIR / 'fig9_summary_table.png', bbox_inches='tight', dpi=300)
    plt.savefig(OUTPUT_DIR / 'fig9_summary_table.pdf', bbox_inches='tight')
    print("[OK] Generated: fig9_summary_table")
    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  GENERATING THESIS FIGURES")
    print("="*60 + "\n")
    
    print("Creating professional figures for master's thesis...")
    print()
    
    create_cost_comparison()
    create_service_level_comparison()
    create_runtime_comparison()
    create_fitness_heatmap()
    create_ilp_savings()
    create_cost_service_tradeoff()
    create_radar_chart()
    create_difficulty_analysis()
    create_summary_table()
    
    print()
    print("="*60)
    print(f"  [SUCCESS] ALL FIGURES GENERATED")
    print(f"  Output directory: {OUTPUT_DIR.absolute()}")
    print(f"  Total figures: 9 (PNG + PDF formats)")
    print("="*60)
    print()
    print("Figures ready for inclusion in your master's thesis!")
    print()
