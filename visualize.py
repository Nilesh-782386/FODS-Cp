import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import numpy as np
import sys
import os
import time
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.gridspec import GridSpec

class AlgorithmVisualizer:
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.is_playing = False
        self.speed = 1.0
        self.config = {}
        self.theme = 'dark'
        self.show_code = True
        self.comparisons = 0
        self.swaps = 0
        self.input_mode = 'manual'
        
        self.performance_metrics = {
            'comparisons': 0,
            'swaps': 0,
            'accesses': 0,
            'start_time': time.time(),
            'efficiency_score': 0
        }
        
        self.learning_mode = False
        self.current_explanation = ""
        
        self.load_data()
        self.setup_theme()
        
        self.fig = plt.figure(figsize=(20, 12))
        self.fig.patch.set_facecolor(self.colors['bg'])
        
        gs = GridSpec(10, 10, figure=self.fig, hspace=0.4, wspace=0.3,
                     left=0.05, right=0.98, top=0.95, bottom=0.08)
        
        self.ax_main = self.fig.add_subplot(gs[0:5, 0:6])
        self.ax_main.set_facecolor(self.colors['plot_bg'])
        
        self.ax_side = self.fig.add_subplot(gs[0:2, 6:8])
        self.ax_side.set_facecolor(self.colors['panel_bg'])
        
        self.ax_stats = self.fig.add_subplot(gs[2:4, 6:8])
        self.ax_stats.set_facecolor(self.colors['panel_bg'])
        
        self.ax_pattern = self.fig.add_subplot(gs[4:5, 6:8])
        self.ax_pattern.set_facecolor(self.colors['panel_bg'])
        
        self.ax_learn = self.fig.add_subplot(gs[5:7, 0:8])
        self.ax_learn.set_facecolor(self.colors['learn_bg'])
        
        self.ax_code = self.fig.add_subplot(gs[7:9, 0:6])
        self.ax_code.set_facecolor(self.colors['code_bg'])
        
        self.ax_controls = self.fig.add_subplot(gs[9, :])
        self.ax_controls.set_facecolor(self.colors['bg'])
        self.ax_controls.axis('off')
        
        self.setup_ui()
        self.calculate_statistics()
        self.update_visualization()
        
        self.is_playing = True
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=1000/self.speed, 
            repeat=True, blit=False
        )
        
        plt.show()
    
    def setup_theme(self):
        self.colors = {
            'bg': '#1a1a1a',
            'plot_bg': '#2a2a2a',
            'panel_bg': '#1e1e1e',
            'code_bg': '#0d0d0d',
            'learn_bg': '#1a2a3a',
            'text': 'white',
            'accent': '#4CAF50',
            'highlight': '#FFD700',
            'normal': '#3f51b5',
            'compare': '#f44336',
            'found': '#4caf50',
            'pivot': '#ff9800',
            'special': '#9c27b0',
            'sorted': '#00BCD4'
        }
        plt.style.use('dark_background')
    
    def load_data(self):
        try:
            with open('algorithm_steps.json', 'r') as f:
                data = json.load(f)
                self.steps = data['steps']
            
            with open('algorithm_config.json', 'r') as f:
                self.config = json.load(f)
                
            print(f"✓ Loaded {len(self.steps)} steps")
            print(f"✓ Structure: {self.config.get('structure_type', 'unknown')}")
            print(f"✓ Operation: {self.config.get('operation', 'unknown')}")
            
            self.analyze_input_pattern()
            
        except FileNotFoundError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    def analyze_input_pattern(self):
        if not self.steps or not self.steps[0]['data']:
            return
            
        first_step_data = self.steps[0]['data']
        sorted_asc = all(first_step_data[i] <= first_step_data[i+1] for i in range(len(first_step_data)-1))
        sorted_desc = all(first_step_data[i] >= first_step_data[i+1] for i in range(len(first_step_data)-1))
        all_equal = len(set(first_step_data)) == 1
        
        if all_equal:
            self.input_mode = 'All Equal'
        elif sorted_asc:
            self.input_mode = 'Sorted Ascending'
        elif sorted_desc:
            self.input_mode = 'Sorted Descending'
        else:
            self.input_mode = 'Random'
    
    def calculate_statistics(self):
        self.comparisons = 0
        self.swaps = 0
        
        for step in self.steps:
            action = step.get('action', '')
            if 'COMPARE' in action or 'SEARCH' in action:
                self.comparisons += 1
            if 'SWAP' in action:
                self.swaps += 1
        
        total_steps = len(self.steps)
        if total_steps > 0 and self.steps[0]['data']:
            optimal = len(self.steps[0]['data']) * np.log2(max(2, len(self.steps[0]['data'])))
            self.performance_metrics['efficiency_score'] = max(0, min(100, (1 - (total_steps / (optimal * 10))) * 100))
    
    def setup_ui(self):
        button_width = 0.08
        button_height = 0.04
        button_y = 0.02
        start_x = 0.05
        spacing = 0.10
        
        ax_play = plt.axes([start_x, button_y, button_width, button_height])
        self.btn_play = Button(ax_play, 'Play', color=self.colors['accent'])
        self.btn_play.on_clicked(self.toggle_play)
        
        ax_reset = plt.axes([start_x + spacing, button_y, button_width, button_height])
        self.btn_reset = Button(ax_reset, 'Reset', color='#f44336')
        self.btn_reset.on_clicked(self.reset_animation)
        
        ax_back = plt.axes([start_x + spacing*2, button_y, button_width, button_height])
        self.btn_back = Button(ax_back, 'Back', color='#FF9800')
        self.btn_back.on_clicked(self.step_back)
        
        ax_forward = plt.axes([start_x + spacing*3, button_y, button_width, button_height])
        self.btn_forward = Button(ax_forward, 'Next', color='#2196F3')
        self.btn_forward.on_clicked(self.step_forward)
        
        ax_learn = plt.axes([start_x + spacing*4, button_y, button_width*1.2, button_height])
        self.btn_learn = Button(ax_learn, 'Learn', color='#9C27B0')
        self.btn_learn.on_clicked(self.toggle_learning_mode)
        
        ax_speed = plt.axes([0.70, button_y + 0.01, 0.2, 0.025])
        self.slider_speed = Slider(ax_speed, 'Speed', 0.5, 4.0, valinit=1.0, 
                                  facecolor=self.colors['accent'])
        self.slider_speed.on_changed(self.update_speed)
        
        structure_name = self.config.get("structure_type", "").replace("_", " ").title()
        operation_name = self.config.get("operation", "").replace("_", " ").title()
        title = f'{structure_name} - {operation_name}'
        self.fig.suptitle(title, fontsize=18, color=self.colors['highlight'], 
                         y=0.98, fontweight='bold')
    
    def update_side_chart(self, step):
        self.ax_side.clear()
        self.ax_side.set_facecolor(self.colors['panel_bg'])
        
        complexity = step.get('complexity', 'N/A')
        action = step.get('action', 'Unknown')
        
        self.ax_side.text(0.5, 0.95, 'Algorithm Info', ha='center', va='top', 
                         fontsize=11, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        
        progress_pct = int((self.current_step + 1) / len(self.steps) * 100)
        step_info = f"Step {self.current_step + 1}/{len(self.steps)}\n{progress_pct}%"
        self.ax_side.text(0.5, 0.80, step_info, ha='center', va='top',
                         fontsize=9, color='cyan', transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['plot_bg']))
        
        self.ax_side.text(0.1, 0.60, 'Time:', ha='left', va='top',
                         fontsize=9, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        self.ax_side.text(0.1, 0.50, complexity, ha='left', va='top',
                         fontsize=10, color='white', transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.2', facecolor='#4CAF50', alpha=0.8))
        
        space = self.get_space_complexity(action)
        self.ax_side.text(0.1, 0.35, 'Space:', ha='left', va='top',
                         fontsize=9, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        self.ax_side.text(0.1, 0.25, space, ha='left', va='top',
                         fontsize=10, color='white', transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.2', facecolor='#2196F3', alpha=0.8))
        
        progress = (self.current_step + 1) / len(self.steps)
        self.ax_side.barh(0.08, 1, height=0.03, color='#333333', alpha=0.5,
                         transform=self.ax_side.transAxes)
        self.ax_side.barh(0.08, progress, height=0.03, color=self.colors['accent'], 
                         alpha=0.9, transform=self.ax_side.transAxes)
        
        self.ax_side.set_xticks([])
        self.ax_side.set_yticks([])
        for spine in self.ax_side.spines.values():
            spine.set_visible(False)
    
    def update_statistics_dashboard(self, step):
        self.ax_stats.clear()
        self.ax_stats.set_facecolor(self.colors['panel_bg'])
        
        self.ax_stats.text(0.5, 0.95, 'Live Statistics', ha='center', va='top',
                          fontsize=11, fontweight='bold', color=self.colors['highlight'],
                          transform=self.ax_stats.transAxes)
        
        current_comparisons = 0
        current_swaps = 0
        current_accesses = 0
        
        for i in range(self.current_step + 1):
            action = self.steps[i].get('action', '')
            if 'COMPARE' in action or 'SEARCH' in action:
                current_comparisons += 1
            if 'SWAP' in action:
                current_swaps += 1
            current_accesses += 1
        
        y_pos = 0.75
        spacing = 0.18
        
        self.ax_stats.text(0.1, y_pos, 'Comparisons:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'], 
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{current_comparisons}', ha='right', va='center',
                          fontsize=11, fontweight='bold', color='#FFD700',
                          transform=self.ax_stats.transAxes)
        
        y_pos -= spacing
        self.ax_stats.text(0.1, y_pos, 'Swaps:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{current_swaps}', ha='right', va='center',
                          fontsize=11, fontweight='bold', color='#4CAF50',
                          transform=self.ax_stats.transAxes)
        
        y_pos -= spacing
        self.ax_stats.text(0.1, y_pos, 'Accesses:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{current_accesses}', ha='right', va='center',
                          fontsize=11, fontweight='bold', color='#2196F3',
                          transform=self.ax_stats.transAxes)
        
        y_pos -= spacing
        efficiency = self.performance_metrics['efficiency_score']
        eff_color = '#4CAF50' if efficiency > 70 else '#FF9800' if efficiency > 40 else '#f44336'
        
        self.ax_stats.text(0.1, y_pos, 'Efficiency:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{efficiency:.0f}%', ha='right', va='center',
                          fontsize=11, fontweight='bold', color=eff_color,
                          transform=self.ax_stats.transAxes)
        
        self.ax_stats.set_xticks([])
        self.ax_stats.set_yticks([])
        for spine in self.ax_stats.spines.values():
            spine.set_visible(False)
    
    def update_pattern_panel(self):
        self.ax_pattern.clear()
        self.ax_pattern.set_facecolor(self.colors['panel_bg'])
        
        self.ax_pattern.text(0.5, 0.70, 'Input Pattern', ha='center', va='top',
                            fontsize=10, fontweight='bold', color=self.colors['highlight'],
                            transform=self.ax_pattern.transAxes)
        
        self.ax_pattern.text(0.5, 0.40, self.input_mode, ha='center', va='center',
                            fontsize=10, color='cyan', transform=self.ax_pattern.transAxes,
                            bbox=dict(boxstyle='round,pad=0.4', facecolor=self.colors['plot_bg'],
                                    edgecolor=self.colors['accent'], linewidth=2))
        
        self.ax_pattern.set_xticks([])
        self.ax_pattern.set_yticks([])
        for spine in self.ax_pattern.spines.values():
            spine.set_visible(False)
    
    def update_learning_dashboard(self, step):
        self.ax_learn.clear()
        self.ax_learn.set_facecolor(self.colors['learn_bg'])
        
        if not self.learning_mode:
            self.ax_learn.axis('off')
            return
        
        action = step.get('action', '')
        description = step.get('description', '')
        
        self.ax_learn.text(0.02, 0.90, '💡 Learning Mode', 
                         ha='left', va='top', fontsize=12, fontweight='bold', 
                         color=self.colors['highlight'], transform=self.ax_learn.transAxes)
        
        explanation = self.get_step_explanation(action, description)
        wrapped = self.wrap_text(explanation, 100)
        self.ax_learn.text(0.02, 0.75, wrapped, ha='left', va='top',
                         fontsize=9, color=self.colors['text'], transform=self.ax_learn.transAxes,
                         bbox=dict(boxstyle='round,pad=0.4', facecolor='#2a3a4a', alpha=0.8))
        
        insight = self.get_algorithm_insight(action)
        if insight:
            self.ax_learn.text(0.02, 0.40, '🎯 Key Insight:', ha='left', va='top',
                             fontsize=10, fontweight='bold', color='#FFD700',
                             transform=self.ax_learn.transAxes)
            wrapped_insight = self.wrap_text(insight, 90)
            self.ax_learn.text(0.05, 0.28, wrapped_insight, ha='left', va='top',
                             fontsize=8, color='#90CAF9', transform=self.ax_learn.transAxes)
        
        self.ax_learn.set_xticks([])
        self.ax_learn.set_yticks([])
        for spine in self.ax_learn.spines.values():
            spine.set_edgecolor(self.colors['accent'])
            spine.set_linewidth(2)
    
    def update_code_display(self, step):
        self.ax_code.clear()
        self.ax_code.set_facecolor(self.colors['code_bg'])
        
        if not self.show_code:
            self.ax_code.axis('off')
            return
        
        action = step.get('action', '')
        code = self.get_pseudocode(action)
        
        self.ax_code.text(0.02, 0.92, 'Pseudocode:', ha='left', va='top',
                         fontsize=10, fontweight='bold', color=self.colors['highlight'],
                         transform=self.ax_code.transAxes)
        
        highlighted_line = self.get_highlighted_line(action)
        lines = code.split('\n')
        y_pos = 0.78
        line_height = 0.13
        
        for i, line in enumerate(lines[:6]):
            color = '#00FF00' if i == highlighted_line else '#CCCCCC'
            weight = 'bold' if i == highlighted_line else 'normal'
            self.ax_code.text(0.03, y_pos - i * line_height, line, ha='left', va='top',
                            fontsize=7, color=color, family='monospace', fontweight=weight,
                            transform=self.ax_code.transAxes)
        
        self.ax_code.set_xticks([])
        self.ax_code.set_yticks([])
        for spine in self.ax_code.spines.values():
            spine.set_edgecolor(self.colors['accent'])
            spine.set_linewidth(1)
    
    def is_sorting_algorithm(self):
        operation = self.config.get('operation', '').lower()
        sorting_ops = ['bubble_sort', 'selection_sort', 'insertion_sort', 
                      'quick_sort', 'merge_sort', 'sort']
        return any(op in operation for op in sorting_ops)
    
    def visualize_array_sorting(self, step):
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Array Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=16)
            return
        
        max_val = max(data) if data else 1
        min_val = min(data) if data else 0
        value_range = max_val - min_val if max_val != min_val else 1
        
        colors = self.get_colors(highlighted)
        n = len(data)
        
        bar_width = 0.7
        x_positions = np.arange(n)
        
        for i, (value, color, highlight) in enumerate(zip(data, colors, highlighted)):
            normalized_height = (value - min_val) / value_range
            bar_height = normalized_height * 4.5
            
            if highlight == 2:
                bar_color = self.colors['found']
                edge_color = 'lime'
                edge_width = 3
            elif highlight == 1:
                bar_color = self.colors['compare']
                edge_color = 'red'
                edge_width = 3
            elif highlight == 3:
                bar_color = self.colors['pivot']
                edge_color = 'yellow'
                edge_width = 3
            elif highlight == 4:
                bar_color = self.colors['special']
                edge_color = 'purple'
                edge_width = 3
            else:
                bar_color = self.colors['normal']
                edge_color = 'white'
                edge_width = 1.5
            
            rect = Rectangle((i, 0), bar_width, bar_height,
                           facecolor=bar_color, alpha=0.85, 
                           edgecolor=edge_color, linewidth=edge_width, zorder=3)
            self.ax_main.add_patch(rect)
            
            self.ax_main.text(i + bar_width/2, bar_height + 0.15, f'{value}',
                            ha='center', va='bottom', fontsize=10,
                            fontweight='bold', color='white', zorder=4)
            
            self.ax_main.text(i + bar_width/2, -0.25, f'[{i}]',
                            ha='center', va='top', fontsize=8,
                            color=self.colors['text'], alpha=0.7)
        
        pointers = step.get('pointers', [-1] * 10)
        pointer_y = 5.2
        
        if pointers[0] != -1:
            self.ax_main.annotate('L', xy=(pointers[0] + bar_width/2, 0),
                               xytext=(pointers[0] + bar_width/2, pointer_y),
                               arrowprops=dict(arrowstyle='->', color='cyan', lw=2.5),
                               fontsize=11, color='cyan', fontweight='bold',
                               ha='center', bbox=dict(boxstyle='circle', 
                               facecolor='cyan', alpha=0.3))
        
        if pointers[1] != -1:
            self.ax_main.annotate('R', xy=(pointers[1] + bar_width/2, 0),
                               xytext=(pointers[1] + bar_width/2, pointer_y),
                               arrowprops=dict(arrowstyle='->', color='yellow', lw=2.5),
                               fontsize=11, color='yellow', fontweight='bold',
                               ha='center', bbox=dict(boxstyle='circle', 
                               facecolor='yellow', alpha=0.3))
        
        if pointers[2] != -1:
            self.ax_main.annotate('P', xy=(pointers[2] + bar_width/2, 0),
                               xytext=(pointers[2] + bar_width/2, pointer_y),
                               arrowprops=dict(arrowstyle='->', color='magenta', lw=2.5),
                               fontsize=11, color='magenta', fontweight='bold',
                               ha='center', bbox=dict(boxstyle='circle', 
                               facecolor='magenta', alpha=0.3))
        
        self.ax_main.set_xlim(-0.5, n)
        self.ax_main.set_ylim(-0.5, 6.0)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.grid(axis='y', alpha=0.2, linestyle='--', linewidth=0.5)
        
        self.ax_main.set_title(f'{step["description"]}', 
                              fontsize=13, color=self.colors['text'], 
                              pad=15, fontweight='bold')
        
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_array(self, step):
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Array Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=16)
            return
        
        colors = self.get_colors(highlighted)
        x_pos = np.arange(len(data))
        
        for i, (value, color) in enumerate(zip(data, colors)):
            rect = Rectangle((i, 0), 0.85, 0.6, 
                           facecolor=color, alpha=0.85, edgecolor='white', linewidth=2)
            self.ax_main.add_patch(rect)
            self.ax_main.text(i + 0.425, 0.3, f'{value}', 
                            ha='center', va='center', fontsize=11, 
                            fontweight='bold', color='white')
            self.ax_main.text(i + 0.425, -0.15, f'[{i}]', 
                            ha='center', va='top', fontsize=8, color=self.colors['text'])
        
        pointers = step.get('pointers', [-1] * 10)
        if pointers[0] != -1:
            self.ax_main.axvline(x=pointers[0] + 0.425, color='cyan', 
                               linestyle='--', alpha=0.8, linewidth=2, label='Left')
        if pointers[1] != -1:
            self.ax_main.axvline(x=pointers[1] + 0.425, color='yellow', 
                               linestyle='--', alpha=0.8, linewidth=2, label='Right')
        if pointers[2] != -1:
            self.ax_main.axvline(x=pointers[2] + 0.425, color='magenta', 
                               linestyle='--', alpha=0.8, linewidth=2, label='Mid')
        
        self.ax_main.set_xlim(-0.5, len(data) + 0.5)
        self.ax_main.set_ylim(-0.3, 1.0)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(f'{step["description"]}', fontsize=12, 
                              color=self.colors['text'], pad=15, fontweight='bold')
    
    def visualize_stack(self, step):
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Stack Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        element_height = 0.5
        base_y = 0.5
        stack_width = 0.4
        
        base = Rectangle((0.3, base_y - 0.1), stack_width, 0.1,
                        facecolor='#666666', edgecolor='white', linewidth=2)
        self.ax_main.add_patch(base)
        self.ax_main.text(0.5, base_y - 0.25, 'BASE', ha='center', va='top',
                         fontsize=10, color='white', fontweight='bold')
        
        for i, (value, color, highlight) in enumerate(zip(data, colors, highlighted)):
            y_pos = base_y + i * element_height
            
            if highlight == 1:
                edge_color = 'red'
                edge_width = 3
            elif highlight == 2:
                edge_color = 'lime'
                edge_width = 3
            else:
                edge_color = 'white'
                edge_width = 2
            
            rect = Rectangle((0.3, y_pos), stack_width, element_height,
                           facecolor=color, alpha=0.85, edgecolor=edge_color, 
                           linewidth=edge_width)
            self.ax_main.add_patch(rect)
            self.ax_main.text(0.5, y_pos + element_height/2, f'{value}', 
                            ha='center', va='center', fontsize=12, 
                            fontweight='bold', color='white')
        
        if data:
            top_y = base_y + len(data) * element_height
            self.ax_main.annotate('TOP', xy=(0.5, top_y), xytext=(0.8, top_y + 0.3),
                               arrowprops=dict(arrowstyle='->', color='red', lw=3),
                               fontsize=13, color='red', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', 
                                       alpha=0.7, edgecolor='red', linewidth=2))
        
        self.ax_main.text(0.9, 0.9, f'Size: {len(data)}', 
                         transform=self.ax_main.transAxes, ha='right', va='top',
                         fontsize=10, color='cyan', fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['panel_bg']))
        
        self.ax_main.set_xlim(0, 1)
        self.ax_main.set_ylim(0, base_y + len(data) * element_height + 0.8)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(f'{step["description"]}', fontsize=12, 
                              color=self.colors['text'], pad=15, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_queue(self, step):
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Queue Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        element_width = 0.7
        base_x = 0.5
        element_height = 0.5
        
        for i, (value, color, highlight) in enumerate(zip(data, colors, highlighted)):
            x_pos = base_x + i * element_width
            
            if highlight == 1:
                edge_color = 'red'
                edge_width = 3
            elif highlight == 2:
                edge_color = 'lime'
                edge_width = 3
            else:
                edge_color = 'white'
                edge_width = 2
            
            rect = Rectangle((x_pos, 0.3), element_width, element_height,
                           facecolor=color, alpha=0.85, edgecolor=edge_color, 
                           linewidth=edge_width)
            self.ax_main.add_patch(rect)
            self.ax_main.text(x_pos + element_width/2, 0.55, f'{value}', 
                            ha='center', va='center', fontsize=12, 
                            fontweight='bold', color='white')
            self.ax_main.text(x_pos + element_width/2, 0.15, f'{i}',
                            ha='center', va='top', fontsize=8, 
                            color=self.colors['text'], alpha=0.7)
        
        if data:
            front_x = base_x + element_width/2
            self.ax_main.annotate('FRONT', xy=(front_x, 0.85), xytext=(front_x, 1.15),
                               arrowprops=dict(arrowstyle='->', color='red', lw=3),
                               fontsize=12, color='red', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', 
                                       alpha=0.7, edgecolor='red', linewidth=2))
            
            rear_x = base_x + (len(data) - 1) * element_width + element_width/2
            self.ax_main.annotate('REAR', xy=(rear_x, 0.85), xytext=(rear_x, 1.15),
                               arrowprops=dict(arrowstyle='->', color='green', lw=3),
                               fontsize=12, color='green', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', 
                                       alpha=0.7, edgecolor='green', linewidth=2))
        
        self.ax_main.text(0.95, 0.95, f'Size: {len(data)}', 
                         transform=self.ax_main.transAxes, ha='right', va='top',
                         fontsize=10, color='cyan', fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['panel_bg']))
        
        self.ax_main.set_xlim(0, base_x + len(data) * element_width + 0.5)
        self.ax_main.set_ylim(0, 1.5)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(f'{step["description"]}', fontsize=12, 
                              color=self.colors['text'], pad=15, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_linked_list(self, step):
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'List Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        node_width = 0.5
        pointer_length = 0.25
        y_center = 0.5
        node_height = 0.3
        
        for i, (value, color, highlight) in enumerate(zip(data, colors, highlighted)):
            x_center = 0.5 + i * (node_width + pointer_length)
            
            if highlight == 1:
                edge_color = 'red'
                edge_width = 3
            elif highlight == 2:
                edge_color = 'lime'
                edge_width = 3
            else:
                edge_color = 'white'
                edge_width = 2
            
            rect = Rectangle((x_center - node_width/2, y_center - node_height/2),
                           node_width, node_height, facecolor=color, alpha=0.85, 
                           edgecolor=edge_color, linewidth=edge_width)
            self.ax_main.add_patch(rect)
            self.ax_main.text(x_center, y_center, f'{value}', 
                            ha='center', va='center', fontsize=11, 
                            fontweight='bold', color='white')
            
            if i < len(data) - 1:
                arrow = FancyArrowPatch((x_center + node_width/2, y_center),
                                      (x_center + node_width/2 + pointer_length, y_center),
                                      arrowstyle='->', color='cyan', linewidth=2.5, 
                                      mutation_scale=20)
                self.ax_main.add_patch(arrow)
        
        if data:
            head_x = 0.5 - node_width/2
            self.ax_main.annotate('HEAD', xy=(head_x, y_center), 
                               xytext=(head_x - 0.3, y_center + 0.4),
                               arrowprops=dict(arrowstyle='->', color='red', lw=2.5),
                               fontsize=11, color='red', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', 
                                       alpha=0.7, edgecolor='red'))
            
            last_x = 0.5 + (len(data) - 1) * (node_width + pointer_length) + node_width/2
            self.ax_main.text(last_x + 0.15, y_center, 'NULL', 
                            ha='left', va='center', fontsize=9, 
                            color='red', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='black', 
                                    alpha=0.7, edgecolor='red'))
        
        total_width = 0.5 + len(data) * (node_width + pointer_length) + 0.5
        self.ax_main.set_xlim(0, total_width)
        self.ax_main.set_ylim(0, 1)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(f'{step["description"]}', fontsize=12, 
                              color=self.colors['text'], pad=15, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_binary_search_tree(self, step):
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'BST Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        positions = self.calculate_tree_positions(data)
        
        for i in range(1, len(data)):
            if i < len(positions):
                parent_idx = (i - 1) // 2
                if parent_idx < len(positions):
                    x_vals = [positions[parent_idx][0], positions[i][0]]
                    y_vals = [positions[parent_idx][1], positions[i][1]]
                    self.ax_main.plot(x_vals, y_vals, 'cyan', linewidth=2.5, alpha=0.6, zorder=1)
        
        for i, (value, color, highlight) in enumerate(zip(data, colors, highlighted)):
            if i < len(positions):
                x, y = positions[i]
                
                if highlight == 1:
                    edge_color = 'red'
                    edge_width = 3
                elif highlight == 2:
                    edge_color = 'lime'
                    edge_width = 3
                else:
                    edge_color = 'white'
                    edge_width = 2
                
                circle = Circle((x, y), 0.12, facecolor=color, alpha=0.85, 
                              edgecolor=edge_color, linewidth=edge_width, zorder=3)
                self.ax_main.add_patch(circle)
                self.ax_main.text(x, y, f'{value}', ha='center', va='center',
                                fontsize=10, fontweight='bold', color='white', zorder=4)
        
        if positions:
            x_coords = [pos[0] for pos in positions]
            y_coords = [pos[1] for pos in positions]
            x_margin = (max(x_coords) - min(x_coords)) * 0.2 + 0.5
            y_margin = (max(y_coords) - min(y_coords)) * 0.2 + 0.5
            
            self.ax_main.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
            self.ax_main.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
        
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(f'{step["description"]}', fontsize=12, 
                              color=self.colors['text'], pad=15, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def calculate_tree_positions(self, data):
        if not data:
            return []
        
        positions = []
        for i in range(len(data)):
            level = 0
            temp = i + 1
            while temp > 1:
                temp //= 2
                level += 1
            
            level_start = 2 ** level - 1
            pos_in_level = i - level_start
            x = (pos_in_level + 1) * (1.0 / (2 ** level + 1)) - 0.5
            x = x * (2 ** level)
            y = -level * 0.3
            
            positions.append((x, y))
        
        return positions
    
    def get_colors(self, highlighted):
        colors = []
        for h in highlighted:
            if h == 1:
                colors.append(self.colors['compare'])
            elif h == 2:
                colors.append(self.colors['found'])
            elif h == 3:
                colors.append(self.colors['pivot'])
            elif h == 4:
                colors.append(self.colors['special'])
            else:
                colors.append(self.colors['normal'])
        return colors
    
    def get_space_complexity(self, action):
        complexities = {
            'BUBBLE': 'O(1)', 'SELECTION': 'O(1)', 'INSERTION': 'O(1)',
            'MERGE': 'O(n)', 'QUICK': 'O(log n)',
            'LINEAR': 'O(1)', 'BINARY': 'O(1)',
            'PUSH': 'O(1)', 'POP': 'O(1)', 'ENQUEUE': 'O(1)', 'DEQUEUE': 'O(1)'
        }
        for key, val in complexities.items():
            if key in action:
                return val
        return 'O(1)'
    
    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current = []
        
        for word in words:
            if len(' '.join(current + [word])) <= max_chars:
                current.append(word)
            else:
                lines.append(' '.join(current))
                current = [word]
        
        if current:
            lines.append(' '.join(current))
        
        return '\n'.join(lines)
    
    def get_step_explanation(self, action, description):
        explanations = {
            'COMPARE': "Comparing two elements to determine their relative order.",
            'SWAP': "Swapping two elements to correct their positions.",
            'SEARCH': "Searching for a specific element in the data structure.",
            'PIVOT': "Selecting a pivot element for partitioning (Quick Sort).",
            'MERGE': "Merging two sorted subarrays into one sorted array.",
            'PUSH': "Adding element to the top of the stack (LIFO).",
            'POP': "Removing element from the top of the stack (LIFO).",
            'ENQUEUE': "Adding element to the rear of the queue (FIFO).",
            'DEQUEUE': "Removing element from the front of the queue (FIFO).",
            'INSERT': "Inserting an element at the correct position.",
            'BUBBLE': "Bubble Sort compares adjacent elements and swaps if needed.",
            'SELECTION': "Selection Sort finds minimum and places it at beginning.",
            'INSERTION': "Insertion Sort inserts elements in correct position.",
            'BINARY': "Binary Search divides search space in half each step.",
            'LINEAR': "Linear Search checks each element sequentially."
        }
        
        for key, exp in explanations.items():
            if key in action:
                return exp
        return "Processing data structure operation step by step."
    
    def get_algorithm_insight(self, action):
        insights = {
            'QUICK': "Quick Sort efficiency depends on pivot selection - good pivots → O(n log n).",
            'MERGE': "Merge Sort is stable, always O(n log n), but needs O(n) extra space.",
            'BUBBLE': "Bubble Sort is simple but inefficient - best for educational purposes.",
            'INSERTION': "Insertion Sort is efficient for small or nearly sorted datasets.",
            'SELECTION': "Selection Sort always O(n²) - doesn't adapt to input order.",
            'BINARY': "Binary Search is O(log n) - extremely efficient for sorted data.",
            'LINEAR': "Linear Search is O(n) - works on any data but slower.",
            'STACK': "Stack (LIFO) perfect for undo operations and function calls.",
            'QUEUE': "Queue (FIFO) ideal for task scheduling and buffering."
        }
        
        for key, insight in insights.items():
            if key in action:
                return insight
        return ""
    
    def get_pseudocode(self, action):
        codes = {
            'BUBBLE': "for i = 0 to n-1:\n  for j = 0 to n-i-1:\n    if arr[j] > arr[j+1]:\n      swap(arr[j], arr[j+1])",
            'QUICK': "function quickSort(arr, low, high):\n  if low < high:\n    pivot = partition(arr, low, high)\n    quickSort(arr, low, pivot-1)\n    quickSort(arr, pivot+1, high)",
            'MERGE': "function mergeSort(arr):\n  if len(arr) <= 1: return\n  mid = len(arr) // 2\n  mergeSort(arr[:mid])\n  mergeSort(arr[mid:])\n  merge(arr)",
            'SELECTION': "for i = 0 to n-1:\n  min_idx = i\n  for j = i+1 to n:\n    if arr[j] < arr[min_idx]:\n      min_idx = j\n  swap(arr[i], arr[min_idx])",
            'INSERTION': "for i = 1 to n-1:\n  key = arr[i]\n  j = i - 1\n  while j >= 0 and arr[j] > key:\n    arr[j+1] = arr[j]\n    j = j - 1\n  arr[j+1] = key",
            'BINARY_SEARCH': "low = 0, high = n-1\nwhile low <= high:\n  mid = (low + high) // 2\n  if arr[mid] == target:\n    return mid\n  elif arr[mid] < target:\n    low = mid + 1\n  else:\n    high = mid - 1",
            'LINEAR_SEARCH': "for i = 0 to n-1:\n  if arr[i] == target:\n    return i\nreturn -1",
            'PUSH': "if stack.isFull():\n  return overflow\nstack.top++\nstack.arr[top] = element",
            'POP': "if stack.isEmpty():\n  return underflow\nelement = stack.arr[top]\nstack.top--\nreturn element",
            'ENQUEUE': "if queue.isFull():\n  return overflow\nqueue.rear++\nqueue.arr[rear] = element",
            'DEQUEUE': "if queue.isEmpty():\n  return underflow\nelement = queue.arr[front]\nqueue.front++\nreturn element"
        }
        
        for key, code in codes.items():
            if key in action:
                return code
        return "// Algorithm pseudocode\nprocess(data)"
    
    def get_highlighted_line(self, action):
        highlights = {
            'COMPARE': 2, 'SWAP': 3, 'SEARCH': 1, 'PIVOT': 0,
            'MERGE': 4, 'PUSH': 2, 'POP': 1, 'ENQUEUE': 2, 'DEQUEUE': 1
        }
        for key, line in highlights.items():
            if key in action:
                return line
        return 0
    
    def toggle_learning_mode(self, event=None):
        self.learning_mode = not self.learning_mode
        print(f"🎮 Learning Mode: {'ON' if self.learning_mode else 'OFF'}")
        self.update_visualization()
    
    def update_visualization(self):
        if not self.steps:
            return
        
        step = self.steps[self.current_step]
        
        self.update_side_chart(step)
        self.update_statistics_dashboard(step)
        self.update_pattern_panel()
        self.update_learning_dashboard(step)
        self.update_code_display(step)
        
        structure_type = self.config.get('structure_type', 'array')
        
        if self.is_sorting_algorithm():
            self.visualize_array_sorting(step)
        elif structure_type == 'stack' or self.config.get('is_stack', False):
            self.visualize_stack(step)
        elif structure_type == 'queue' or self.config.get('is_queue', False):
            self.visualize_queue(step)
        elif structure_type == 'linked_list' or self.config.get('is_linked_list', False):
            self.visualize_linked_list(step)
        elif structure_type == 'binary_search_tree' or self.config.get('is_binary_search_tree', False):
            self.visualize_binary_search_tree(step)
        else:
            self.visualize_array(step)
        
        plt.draw()
    
    def animate(self, frame):
        if self.is_playing and self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_visualization()
        elif self.current_step >= len(self.steps) - 1:
            self.is_playing = False
            self.btn_play.label.set_text('Restart')
        return []
    
    def toggle_play(self, event):
        if self.current_step >= len(self.steps) - 1:
            self.current_step = 0
            self.is_playing = True
            self.btn_play.label.set_text('Pause')
        else:
            self.is_playing = not self.is_playing
            self.btn_play.label.set_text('Pause' if self.is_playing else 'Play')
    
    def reset_animation(self, event):
        self.current_step = 0
        self.is_playing = False
        self.btn_play.label.set_text('Play')
        self.update_visualization()
    
    def step_back(self, event):
        if self.current_step > 0:
            self.current_step -= 1
            self.is_playing = False
            self.btn_play.label.set_text('Play')
            self.update_visualization()
    
    def step_forward(self, event):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.is_playing = False
            self.btn_play.label.set_text('Play')
            self.update_visualization()
    
    def update_speed(self, val):
        self.speed = val
        if hasattr(self, 'ani'):
            self.ani.event_source.interval = 1000 / self.speed

def main():
    print("=" * 60)
    print("PERFECT ALGORITHM VISUALIZER - v6.0 FINAL")
    print("=" * 60)
    
    if not os.path.exists('algorithm_steps.json'):
        print("Error: algorithm_steps.json not found!")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists('algorithm_config.json'):
        print("Error: algorithm_config.json not found!")
        input("Press Enter to exit...")
        return
    
    try:
        visualizer = AlgorithmVisualizer()
    except KeyboardInterrupt:
        print("\nVisualization interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()