#!/usr/bin/env python

###############################################################################
# Multi Stage Delta-V Calculator - calculate change in velocity for a multiple stage rocket.
# You can use any units you'd like, as long as you are consistent.
# Copyright(C) 2025 Skylar Grace, under the terms of the 3-clause BSD license.
###############################################################################

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt



class DeltaVCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Multi Stage Delta-V Calculator")

        # Set up our main container
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(padx=10, pady=10)

        # now lets make a list of stages
        self.stages = []

        # frame to display our stages
        self.stages_frame = ttk.Frame(self.main_frame)
        self.stages_frame.pack()

        # Add control buttons for adding stages
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(pady=5)
        ttk.Button(self.controls_frame, text="Add Stage", command=self.add_stage).pack(side=tk.LEFT, padx=5)

        # Calculation and visualization buttons
        ttk.Button(self.main_frame, text="Calculate Delta-V", command=self.calculate_delta_v).pack(pady=5)
        ttk.Button(self.main_frame, text="Plot Stages", command=self.plot_stages).pack(pady=5)

        # Display results of our calculation
        self.result_label = ttk.Label(self.main_frame, text="Total Δv: ")
        self.result_label.pack(pady=5)

        # Add the first stage
        self.add_stage()



    def add_stage(self):
        # Stage input section
        stage_frame = ttk.Frame(self.stages_frame)
        stage_frame.pack(pady=2, fill=tk.X)

        # Stage number label
        stage_num = len(self.stages) + 1
        ttk.Label(stage_frame, text=f"Stage {stage_num}").grid(row=0, column=0, padx=5)

        # Wet mass input
        ttk.Label(stage_frame, text="Wet Mass (kg):").grid(row=0, column=1, padx=5)
        wet_entry = ttk.Entry(stage_frame, width=10)
        wet_entry.grid(row=0, column=2, padx=5)

        # Dry mass input
        ttk.Label(stage_frame, text="Dry Mass (kg):").grid(row=0, column=3, padx=5)
        dry_entry = ttk.Entry(stage_frame, width=10)
        dry_entry.grid(row=0, column=4, padx=5)

        # Specific impulse input
        ttk.Label(stage_frame, text="Isp (s):").grid(row=0, column=5, padx=5)
        isp_entry = ttk.Entry(stage_frame, width=10)
        isp_entry.grid(row=0, column=6, padx=5)

        # Remove button
        ttk.Button(stage_frame, text="Remove", 
                 command=lambda f=stage_frame: self.remove_stage(f)).grid(row=0, column=7, padx=5)

        self.stages.append({
            'frame': stage_frame,
            'wet': wet_entry,
            'dry': dry_entry,
            'isp': isp_entry
        })


    def remove_stage(self, stage_frame):
        # Remove a stage from the interface
        for stage in self.stages:
            if stage['frame'] == stage_frame:
                self.stages.remove(stage)
                stage_frame.destroy()
                break
        self.update_stage_numbers()



    def update_stage_numbers(self):
        # Update displayed stage numbers after removal
        for i, stage in enumerate(self.stages):
            children = stage['frame'].winfo_children()
            children[0].config(text=f"Stage {i+1}")



    def calculate_delta_v(self):
        # Calculate total delta-V and individual stage Delta V
        g0 = 9.80665  # Standard gravity (m/s²)
        stages_data = []
        
        # Validate and collect stage data
        try:
            for i, stage in enumerate(self.stages):
                wet = float(stage['wet'].get())
                dry = float(stage['dry'].get())
                isp = float(stage['isp'].get())
                
                if wet <= dry:
                    raise ValueError(f"Wet mass <= Dry mass in Stage {i+1}")
                if isp <= 0:
                    raise ValueError(f"Invalid Isp in Stage {i+1}")
                
                stages_data.append((wet, dry, isp))
            
            if not stages_data:
                raise ValueError("No stages added")
            
            # Calculate delta-V for each stage
            total_dv = 0.0
            stage_dvs = []
            for i in range(len(stages_data)):
                # Calculate initial and final masses
                initial_mass = sum(s[0] for s in stages_data[i:])
                final_mass = stages_data[i][1] + sum(s[0] for s in stages_data[i+1:])
                
                # Calculate stage delta-V
                dv = stages_data[i][2] * g0 * np.log(initial_mass / final_mass)
                stage_dvs.append(dv)
                total_dv += dv
            
            self.result_label.config(text=f"Total Δv: {total_dv:.2f} m/s")
            self.stage_dvs = stage_dvs
        
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")



    def plot_stages(self):
        # Create a bar chart showing delta-V distribution
        if not hasattr(self, 'stage_dvs') or not self.stage_dvs:
            self.result_label.config(text="Calculate delta-V first!")
            return
        
        # Prepare data for plotting
        stages = [f"Stage {i+1}" for i in range(len(self.stage_dvs))]
        stages.append("Total")
        values = self.stage_dvs.copy()
        values.append(sum(self.stage_dvs))
        
        # Create plot
        plt.figure(figsize=(8, 5))
        bars = plt.bar(stages, values)
        plt.xlabel("Stage")
        plt.ylabel("Delta-V (m/s)")
        plt.title("Delta-V Distribution per Stage")
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}', ha='center', va='bottom')
        
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeltaVCalculator(root)
    root.mainloop()
