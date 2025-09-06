#!/usr/bin/env python3
"""
Interactive Battery Analysis Dashboard - NASA Dataset
Real-time interactive dashboard with battery selection filter
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')

# Professional styling
plt.style.use('default')
sns.set_palette("husl")

class InteractiveBatteryDashboard:
    def __init__(self, metadata_path, data_dir):
        """Initialize the interactive battery dashboard"""
        self.metadata_path = metadata_path
        self.data_dir = data_dir
        self.metadata = None
        self.battery_data = {}
        self.available_batteries = []
        
    def load_and_clean_data(self):
        """Load and clean battery data with robust error handling"""
        with st.spinner("📊 Loading and cleaning battery data..."):
            try:
                # Load metadata
                self.metadata = pd.read_csv(self.metadata_path)
                st.success(f"Raw data loaded: {len(self.metadata)} records")
                
                # Handle different column formats
                if len(self.metadata.columns) >= 10:
                    self.metadata.columns = ['type', 'start_time', 'ambient_temperature', 
                                           'battery_id', 'test_id', 'uid', 'filename', 
                                           'Capacity', 'Re', 'Rct']
                else:
                    st.warning("Unexpected column format, using first 10 columns")
                    self.metadata.columns = list(self.metadata.columns[:10]) + ['extra'] * max(0, 10 - len(self.metadata.columns))
                
                # Clean data more carefully
                with st.spinner("Cleaning data types..."):
                    # Convert Capacity column
                    self.metadata['Capacity'] = pd.to_numeric(self.metadata['Capacity'], errors='coerce')
                    
                    # Convert Re column (handle cases where it's split across columns)
                    if 'Re' in self.metadata.columns:
                        self.metadata['Re'] = pd.to_numeric(self.metadata['Re'], errors='coerce')
                    else:
                        self.metadata['Re'] = np.nan
                        
                    # Convert Rct column
                    if 'Rct' in self.metadata.columns:
                        self.metadata['Rct'] = pd.to_numeric(self.metadata['Rct'], errors='coerce')
                    else:
                        self.metadata['Rct'] = np.nan
                    
                    # Clean start_time - handle multiple formats
                    self.metadata['start_time'] = pd.to_datetime(self.metadata['start_time'], errors='coerce')
                    
                    # Remove completely invalid rows but keep partial data
                    initial_count = len(self.metadata)
                    self.metadata = self.metadata.dropna(subset=['type', 'battery_id'])
                    
                    # Get list of available batteries (excluding problematic ones)
                    all_batteries = sorted(self.metadata['battery_id'].unique())
                    problematic_batteries = ['B0038', 'B0039', 'B0040', 'B0041', 'B0042', 'B0043', 'B0044', 'B0050', 'B0052']
                    self.available_batteries = [b for b in all_batteries if b not in problematic_batteries]
                    
                    st.success(f"✅ Data cleaned: {len(self.metadata)} valid records (from {initial_count})")
                    st.info(f"🔋 Available batteries: {len(self.available_batteries)} (excluded 9 problematic batteries: B0038, B0039, B0040, B0041, B0042, B0043, B0044, B0050, B0052)")
                    
                    # Show data quality summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Records with Capacity", self.metadata['Capacity'].notna().sum())
                    with col2:
                        st.metric("Records with Re", self.metadata['Re'].notna().sum())
                    with col3:
                        st.metric("Records with Rct", self.metadata['Rct'].notna().sum())
                    with col4:
                        st.metric("Records with valid time", self.metadata['start_time'].notna().sum())
                    
            except Exception as e:
                st.error(f"❌ Error loading data: {e}")
                return False
                
            return True
        
    def calculate_battery_metrics(self, battery_id):
        """Calculate battery metrics for a specific battery"""
        with st.spinner(f"🧮 Calculating metrics for {battery_id}..."):
            # Clear previous battery data
            self.battery_data = {}
            
            try:
                # Get battery data
                battery_meta = self.metadata[self.metadata['battery_id'] == battery_id]
                if len(battery_meta) == 0:
                    st.error(f"❌ No data for {battery_id}")
                    return False
                
                # Separate by type
                discharge = battery_meta[battery_meta['type'] == 'discharge'].copy()
                charge = battery_meta[battery_meta['type'] == 'charge'].copy()
                impedance = battery_meta[battery_meta['type'] == 'impedance'].copy()
                
                # Process discharge cycles
                if len(discharge) > 0:
                    discharge = discharge.sort_values('test_id').reset_index(drop=True)
                    discharge = discharge[discharge['Capacity'].notna()].copy()
                    
                    if len(discharge) > 0:
                        # Use first 30 rows to find peak capacity (avoid calibration issues)
                        first_30_rows = discharge.head(30)
                        peak_capacity = first_30_rows['Capacity'].max()
                        
                        discharge['EFC'] = range(len(discharge))
                        discharge['SOC'] = (discharge['Capacity'] / peak_capacity) * 100
                        discharge['DOD'] = 100 - discharge['SOC']
                        discharge['Capacity_Fade'] = ((peak_capacity - discharge['Capacity']) / peak_capacity) * 100
                        discharge['Throughput'] = discharge['Capacity'].cumsum()
                        self.battery_data['discharge'] = discharge
                
                # Process impedance
                if len(impedance) > 0:
                    impedance = impedance[impedance['Re'].notna() & impedance['Rct'].notna()].copy()
                    if len(impedance) > 0:
                        impedance = impedance.sort_values('test_id').reset_index(drop=True)
                        impedance['Total_Resistance'] = impedance['Re'] + impedance['Rct']
                        impedance['Resistance_Increase'] = ((impedance['Total_Resistance'] - impedance['Total_Resistance'].iloc[0]) / impedance['Total_Resistance'].iloc[0]) * 100
                        self.battery_data['impedance'] = impedance
                
                # Store charge cycles
                if len(charge) > 0:
                    self.battery_data['charge'] = charge
                
                return True
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                return False
    
    def load_individual_csv_files(self, battery_id, test_type='discharge'):
        """Load individual CSV files for detailed analysis"""
        try:
            # Get filenames for this battery and test type
            battery_meta = self.metadata[self.metadata['battery_id'] == battery_id]
            test_meta = battery_meta[battery_meta['type'] == test_type]
            
            if len(test_meta) == 0:
                return None
            
            # Load individual CSV files
            detailed_data = []
            for _, row in test_meta.iterrows():
                filename = row['filename']
                filepath = f"{self.data_dir}/{filename}"
                
                try:
                    # Load CSV file
                    df = pd.read_csv(filepath)
                    df['test_id'] = row['test_id']
                    df['uid'] = row['uid']
                    df['filename'] = filename
                    detailed_data.append(df)
                except Exception as e:
                    st.warning(f"⚠️ Could not load {filename}: {e}")
                    continue
            
            if detailed_data:
                return pd.concat(detailed_data, ignore_index=True)
            else:
                return None
                
        except Exception as e:
            st.error(f"❌ Error loading individual files: {e}")
            return None
    
    def plot_iv_curves(self, battery_id):
        """Plot I-V curves for different cycles"""
        with st.spinner(f"📊 Loading detailed discharge data for {battery_id}..."):
            # Load detailed discharge data
            detailed_data = self.load_individual_csv_files(battery_id, 'discharge')
            
            if detailed_data is None or len(detailed_data) == 0:
                st.warning("No detailed discharge data available for I-V analysis")
                return
            
            # Check required columns
            required_cols = ['Voltage_measured', 'Current_measured', 'uid']
            missing_cols = [col for col in required_cols if col not in detailed_data.columns]
            
            if missing_cols:
                st.warning(f"Missing required columns: {missing_cols}")
                return
            
            # Get unique test cycles (limit to first 5 for clarity)
            unique_tests = sorted(detailed_data['uid'].unique())[:5]
            
            fig = go.Figure()
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            
            for i, test_id in enumerate(unique_tests):
                test_data = detailed_data[detailed_data['uid'] == test_id].copy()
                
                # Clean data
                test_data = test_data.dropna(subset=['Voltage_measured', 'Current_measured'])
                test_data = test_data[test_data['Current_measured'] < 0]  # Only discharge current
                
                if len(test_data) > 10:  # Need enough points for meaningful curve
                    fig.add_trace(go.Scatter(
                        x=abs(test_data['Current_measured']),  # Use absolute value
                        y=test_data['Voltage_measured'],
                        mode='lines',
                        name=f'Cycle {test_id}',
                        line=dict(color=colors[i % len(colors)], width=2),
                        hovertemplate='Current: %{x:.3f}A<br>Voltage: %{y:.3f}V<br>Cycle: ' + str(test_id)
                    ))
            
            fig.update_layout(
                title=f'I-V Curves (Voltage vs Current) - {battery_id}',
                xaxis_title='Current (A)',
                yaxis_title='Voltage (V)',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis
            st.info("**ANALYSIS:** I-V curves show how voltage drops as current increases. Steeper curves indicate higher internal resistance and battery aging.")
    
    def plot_real_energy_efficiency(self, battery_id):
        """Plot real energy efficiency using detailed data"""
        with st.spinner(f"⚡ Calculating real energy efficiency for {battery_id}..."):
            # Load detailed discharge data
            detailed_data = self.load_individual_csv_files(battery_id, 'discharge')
            
            if detailed_data is None or len(detailed_data) == 0:
                st.warning("No detailed discharge data available for energy efficiency calculation")
                return
            
            # Check required columns
            required_cols = ['Voltage_measured', 'Current_measured', 'Voltage_load', 'Current_load', 'Time', 'uid']
            missing_cols = [col for col in required_cols if col not in detailed_data.columns]
            
            if missing_cols:
                st.warning(f"Missing required columns: {missing_cols}")
                return
            
            # Calculate efficiency for each test
            test_efficiencies = []
            test_numbers = []
            
            for test_id in sorted(detailed_data['uid'].unique()):
                test_data = detailed_data[detailed_data['uid'] == test_id].copy()
                
                # Sort by time and calculate time differences
                test_data = test_data.sort_values('Time').reset_index(drop=True)
                test_data['dt'] = test_data['Time'].diff().fillna(0)
                test_data = test_data[test_data['dt'] > 0].copy()
                
                if len(test_data) == 0:
                    continue
                
                # Calculate energies
                energy_supplied = (test_data['Voltage_load'] * test_data['Current_load'] * test_data['dt']).sum()
                energy_received = (test_data['Voltage_measured'] * abs(test_data['Current_measured']) * test_data['dt']).sum()
                
                # Calculate efficiency
                if energy_received > 0 and energy_supplied > 0:
                    efficiency = (energy_supplied / energy_received) * 100
                    if 0 <= efficiency <= 200:  # Reasonable range
                        test_efficiencies.append(efficiency)
                        test_numbers.append(test_id)
            
            if not test_efficiencies:
                st.warning("Could not calculate energy efficiency - no valid tests found")
                return
            
            # Create plot
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=test_numbers,
                y=test_efficiencies,
                mode='lines+markers',
                line=dict(color='purple', width=3),
                marker=dict(size=8),
                name='Real Energy Efficiency'
            ))
            
            # Add 100% reference line
            fig.add_hline(y=100, line_dash="dash", line_color="green", 
                         annotation_text="100% Efficiency")
            
            fig.update_layout(
                title=f'Real Energy Efficiency - {battery_id}',
                xaxis_title='Test Cycle',
                yaxis_title='Energy Efficiency (%)',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis with calculation explanation
            avg_efficiency = sum(test_efficiencies) / len(test_efficiencies)
            final_efficiency = test_efficiencies[-1]
            
            st.info(f"**ANALYSIS:** Average efficiency: {avg_efficiency:.1f}%, Final efficiency: {final_efficiency:.1f}%.")
            
            # Calculation explanation
            with st.expander("📖 How is Real Energy Efficiency Calculated?"):
                st.markdown("""
                **Real Energy Efficiency Formula:**
                ```
                Efficiency = (Energy Supplied / Energy Received) × 100%
                ```
                
                **Where:**
                - **Energy Supplied** = ∫(Voltage_load × Current_load × dt)
                - **Energy Received** = ∫(Voltage_measured × |Current_measured| × dt)
                
                **Why this matters:**
                - Shows actual energy losses during operation
                - Accounts for internal resistance and heat generation
                - More accurate than simple capacity retention
                - Helps optimize charge/discharge protocols
                
                **Typical values:**
                - New batteries: 90-95%
                - Aged batteries: 80-90%
                - End-of-life: <80%
                """)
    
    def plot_thermal_analysis(self, battery_id):
        """Plot thermal analysis with detailed temperature data"""
        with st.spinner(f"🌡️ Analyzing thermal behavior for {battery_id}..."):
            # Load detailed discharge data
            detailed_data = self.load_individual_csv_files(battery_id, 'discharge')
            
            if detailed_data is None or len(detailed_data) == 0:
                st.warning("No detailed discharge data available for thermal analysis")
                return
            
            # Check for temperature data
            if 'Temperature_measured' not in detailed_data.columns:
                st.warning("No temperature data available in detailed files")
                return
            
            # Clean temperature data
            temp_data = detailed_data.dropna(subset=['Temperature_measured', 'Voltage_measured', 'Current_measured']).copy()
            
            if len(temp_data) == 0:
                st.warning("No valid temperature data found")
                return
            
            # Create two separate plots side by side
            col1, col2 = st.columns(2)
            
            with col1:
                # Plot 1: Temperature vs Time
                fig1 = go.Figure()
                fig1.add_trace(
                    go.Scatter(
                        x=temp_data['Time'],
                        y=temp_data['Temperature_measured'],
                        mode='lines',
                        name='Temperature',
                        line=dict(color='red', width=2)
                    )
                )
                fig1.update_layout(
                    title=f'Temperature vs Time - {battery_id}',
                    xaxis_title="Time (s)",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Plot 2: Temperature vs Voltage
                fig2 = go.Figure()
                fig2.add_trace(
                    go.Scatter(
                        x=temp_data['Voltage_measured'],
                        y=temp_data['Temperature_measured'],
                        mode='markers',
                        name='T vs V',
                        marker=dict(color='blue', size=4, opacity=0.6)
                    )
                )
                fig2.update_layout(
                    title=f'Temperature vs Voltage - {battery_id}',
                    xaxis_title="Voltage (V)",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Calculate thermal statistics
            avg_temp = temp_data['Temperature_measured'].mean()
            min_temp = temp_data['Temperature_measured'].min()
            max_temp = temp_data['Temperature_measured'].max()
            temp_range = max_temp - min_temp
            
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
            with col2:
                st.metric("Temp Range", f"{temp_range:.1f}°C")
            with col3:
                st.metric("Min Temp", f"{min_temp:.1f}°C")
            with col4:
                st.metric("Max Temp", f"{max_temp:.1f}°C")
            
            # Simplified thermal analysis conclusions
            if temp_range < 5:
                stability = "Excellent thermal stability"
            elif temp_range < 10:
                stability = "Good thermal stability"
            elif temp_range < 20:
                stability = "Moderate thermal variation"
            else:
                stability = "High thermal variation - monitor closely"
            
            st.info(f"**THERMAL ANALYSIS:** {stability} (range: {temp_range:.1f}°C). Temperature monitoring helps identify thermal stress and aging patterns.")
        
    def plot_capacity_degradation(self, battery_id):
        """Plot capacity degradation with Plotly"""
        if 'discharge' not in self.battery_data or len(self.battery_data['discharge']) == 0:
            st.warning("No discharge data available")
            return
            
        discharge_data = self.battery_data['discharge']
        
        fig = go.Figure()
        
        # Add measured capacity
        fig.add_trace(go.Scatter(
            x=discharge_data['EFC'],
            y=discharge_data['Capacity'],
            mode='lines+markers',
            name='Measured Capacity',
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ))
        
        # Add trend line
        try:
            z = np.polyfit(discharge_data['EFC'], discharge_data['Capacity'], 2)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=discharge_data['EFC'],
                y=p(discharge_data['EFC']),
                mode='lines',
                name='Trend Line',
                line=dict(color='red', width=2, dash='dash')
            ))
        except:
            pass
        
        fig.update_layout(
            title=f'Capacity Degradation - {battery_id}',
            xaxis_title='Equivalent Full Cycles (EFC)',
            yaxis_title='Capacity (Ah)',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add conclusion
        first_30_rows = discharge_data.head(30)
        peak_capacity = first_30_rows['Capacity'].max()
        final_cap = discharge_data['Capacity'].iloc[-1]
        capacity_fade = ((peak_capacity - final_cap) / peak_capacity) * 100
        
        st.info(f"**CONCLUSION:** Battery shows capacity decline from peak {peak_capacity:.3f}Ah to {final_cap:.3f}Ah over {len(discharge_data)} cycles ({capacity_fade:.1f}% degradation).")
    
    def plot_soc_dod_evolution(self, battery_id):
        """Plot SOC and DOD evolution"""
        if 'discharge' not in self.battery_data or len(self.battery_data['discharge']) == 0:
            st.warning("No discharge data available")
            return
            
        discharge_data = self.battery_data['discharge']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=discharge_data['EFC'],
            y=discharge_data['SOC'],
            mode='lines+markers',
            name='SOC (%)',
            line=dict(color='green', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=discharge_data['EFC'],
            y=discharge_data['DOD'],
            mode='lines+markers',
            name='DOD (%)',
            line=dict(color='orange', width=3)
        ))
        
        fig.update_layout(
            title=f'SOC & DOD Evolution - {battery_id}',
            xaxis_title='Equivalent Full Cycles (EFC)',
            yaxis_title='Percentage (%)',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add conclusion
        initial_soc = discharge_data['SOC'].iloc[0]
        final_soc = discharge_data['SOC'].iloc[-1]
        final_dod = discharge_data['DOD'].iloc[-1]
        st.info(f"**CONCLUSION:** SOC decreases from {initial_soc:.1f}% to {final_soc:.1f}% while DOD increases to {final_dod:.1f}%. This shows the battery is losing its ability to maintain charge over cycles.")
    
    def plot_throughput_analysis(self, battery_id):
        """Plot cumulative throughput"""
        if 'discharge' not in self.battery_data or len(self.battery_data['discharge']) == 0:
            st.warning("No discharge data available")
            return
            
        discharge_data = self.battery_data['discharge']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=discharge_data['EFC'],
            y=discharge_data['Throughput'],
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f'Cumulative Throughput - {battery_id}',
            xaxis_title='Equivalent Full Cycles (EFC)',
            yaxis_title='Cumulative Throughput (Ah)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add conclusion
        total_throughput = discharge_data['Throughput'].iloc[-1]
        avg_throughput = total_throughput / len(discharge_data)
        st.info(f"**CONCLUSION:** Total energy delivered reaches {total_throughput:.2f}Ah over {len(discharge_data)} cycles. Average throughput per cycle: {avg_throughput:.3f}Ah.")
    
    def plot_impedance_parameters(self, battery_id):
        """Plot impedance parameters"""
        if 'impedance' not in self.battery_data or len(self.battery_data['impedance']) == 0:
            st.warning("No impedance data available")
            return
            
        impedance_data = self.battery_data['impedance']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=impedance_data.index,
            y=impedance_data['Re'],
            mode='lines+markers',
            name='Re (Electrolyte)',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=impedance_data.index,
            y=impedance_data['Rct'],
            mode='lines+markers',
            name='Rct (Charge Transfer)',
            line=dict(color='red', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=impedance_data.index,
            y=impedance_data['Total_Resistance'],
            mode='lines+markers',
            name='Total',
            line=dict(color='green', width=3)
        ))
        
        fig.update_layout(
            title=f'Impedance Parameters - {battery_id}',
            xaxis_title='Impedance Measurements',
            yaxis_title='Resistance (Ω)',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add conclusion
        initial_res = impedance_data['Total_Resistance'].iloc[0]
        final_res = impedance_data['Total_Resistance'].iloc[-1]
        res_increase = ((final_res - initial_res) / initial_res) * 100
        st.info(f"**CONCLUSION:** Total resistance increases from {initial_res:.3f}Ω to {final_res:.3f}Ω ({res_increase:+.1f}%). Both Re and Rct show trends indicating electrochemical aging.")
    
    def plot_resistance_increase(self, battery_id):
        """Plot resistance increase over time"""
        if 'impedance' not in self.battery_data or len(self.battery_data['impedance']) == 0:
            st.warning("No impedance data available")
            return
            
        impedance_data = self.battery_data['impedance']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=impedance_data.index,
            y=impedance_data['Resistance_Increase'],
            mode='lines+markers',
            line=dict(color='red', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f'Cumulative Resistance Increase - {battery_id}',
            xaxis_title='Impedance Measurements',
            yaxis_title='Resistance Increase (%)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add conclusion
        max_increase = impedance_data['Resistance_Increase'].max()
        st.info(f"**CONCLUSION:** Resistance increase reaches {max_increase:.1f}% over time. This trend suggests the battery is experiencing electrochemical aging.")
    
    def plot_capacity_vs_resistance(self, battery_id):
        """Plot capacity vs resistance correlation"""
        if ('discharge' not in self.battery_data or 'impedance' not in self.battery_data or 
            len(self.battery_data['discharge']) == 0 or len(self.battery_data['impedance']) == 0):
            st.warning("Insufficient data for correlation")
            return
            
        discharge_data = self.battery_data['discharge']
        impedance_data = self.battery_data['impedance']
        
        # Interpolate impedance values for discharge cycles
        impedance_interp = np.interp(discharge_data['EFC'], 
                                   range(len(impedance_data)), 
                                   impedance_data['Total_Resistance'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=impedance_interp,
            y=discharge_data['Capacity'],
            mode='markers',
            marker=dict(size=8, color='purple', opacity=0.7),
            name='Capacity vs Resistance'
        ))
        
        # Add trend line
        try:
            z = np.polyfit(impedance_interp, discharge_data['Capacity'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=impedance_interp,
                y=p(impedance_interp),
                mode='lines',
                line=dict(color='red', width=2, dash='dash'),
                name='Trend Line'
            ))
            
            # Correlation coefficient
            corr = np.corrcoef(impedance_interp, discharge_data['Capacity'])[0,1]
            fig.add_annotation(
                x=0.05, y=0.95,
                xref='paper', yref='paper',
                text=f'R² = {corr**2:.3f}',
                showarrow=False,
                bgcolor='white',
                bordercolor='black',
                borderwidth=1
            )
            
            st.info(f"**CONCLUSION:** Correlation (R² = {corr**2:.3f}) between resistance and capacity. Higher resistance = lower capacity.")
        except:
            st.info("**CONCLUSION:** Correlation analysis shows relationship between resistance increase and capacity degradation.")
        
        fig.update_layout(
            title=f'Capacity vs Resistance - {battery_id}',
            xaxis_title='Total Resistance (Ω)',
            yaxis_title='Capacity (Ah)',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_energy_efficiency(self, battery_id):
        """Plot energy efficiency (capacity retention)"""
        if 'discharge' not in self.battery_data or len(self.battery_data['discharge']) == 0:
            st.warning("No discharge data available")
            return
            
        discharge_data = self.battery_data['discharge']
        
        # Use first 30 rows to find peak capacity (avoid calibration issues)
        first_30_rows = discharge_data.head(30)
        peak_capacity = first_30_rows['Capacity'].max()
        
        # Calculate capacity retention using peak capacity as reference
        energy_efficiency = (discharge_data['Capacity'] / peak_capacity) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=discharge_data['EFC'],
            y=energy_efficiency,
            mode='lines+markers',
            line=dict(color='orange', width=3),
            marker=dict(size=6),
            name='Energy Efficiency'
        ))
        
        # Add EOL threshold
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="EOL Threshold (70%)")
        
        fig.update_layout(
            title=f'Capacity Retention - {battery_id} (Peak: {peak_capacity:.2f} Ah)',
            xaxis_title='Equivalent Full Cycles (EFC)',
            yaxis_title='Capacity Retention (%)',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add conclusion
        final_efficiency = energy_efficiency.iloc[-1]
        if final_efficiency < 70:
            status = "END-OF-LIFE - Replace immediately"
            st.error(f"**CONCLUSION:** Capacity retention drops to {final_efficiency:.1f}% (from peak {peak_capacity:.2f} Ah). Status: {status}")
        elif final_efficiency < 80:
            status = "Advanced aging - Monitor closely"
            st.warning(f"**CONCLUSION:** Capacity retention drops to {final_efficiency:.1f}% (from peak {peak_capacity:.2f} Ah). Status: {status}")
        else:
            status = "Good performance - Continue monitoring"
            st.success(f"**CONCLUSION:** Capacity retention remains at {final_efficiency:.1f}% (from peak {peak_capacity:.2f} Ah). Status: {status}")
    
    def plot_degradation_rate(self, battery_id):
        """Plot degradation rate"""
        if ('discharge' not in self.battery_data or len(self.battery_data['discharge']) < 2):
            st.warning("Insufficient data for degradation rate")
            return
            
        discharge_data = self.battery_data['discharge']
        
        # Calculate degradation rate correctly
        capacity_values = discharge_data['Capacity'].values
        efc_values = discharge_data['EFC'].values
        
        # Calculate percentage change between consecutive cycles
        degradation_rates = []
        efc_for_rates = []
        
        for i in range(1, len(capacity_values)):
            rate = ((capacity_values[i-1] - capacity_values[i]) / capacity_values[i-1]) * 100
            degradation_rates.append(rate)
            efc_for_rates.append(efc_values[i])
        
        if len(degradation_rates) > 0:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=efc_for_rates,
                y=degradation_rates,
                mode='lines+markers',
                line=dict(color='red', width=3),
                marker=dict(size=6)
            ))
            
            fig.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.5)
            
            fig.update_layout(
                title=f'Per-Cycle Degradation Rate - {battery_id}',
                xaxis_title='Equivalent Full Cycles (EFC)',
                yaxis_title='Degradation Rate (%/cycle)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add conclusion
            avg_rate = np.mean(degradation_rates)
            st.info(f"**CONCLUSION:** Average degradation rate: {avg_rate:.2f}% per cycle. Rate varies between cycles, indicating non-uniform aging.")
        else:
            st.warning("Insufficient data for degradation rate")
    
    def generate_executive_summary(self, battery_id):
        """Generate executive summary for a specific battery"""
        st.subheader(f"🔋 EXECUTIVE SUMMARY - {battery_id}")
        
        if 'discharge' not in self.battery_data or len(self.battery_data['discharge']) == 0:
            st.error(f"No discharge data available for {battery_id}")
            return
            
        discharge_data = self.battery_data['discharge']
        
        # Key metrics
        initial_capacity = discharge_data['Capacity'].iloc[0]
        final_capacity = discharge_data['Capacity'].iloc[-1]
        total_cycles = len(discharge_data)
        capacity_fade = ((initial_capacity - final_capacity) / initial_capacity) * 100
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Initial Capacity", f"{initial_capacity:.3f} Ah")
        with col2:
            st.metric("Final Capacity", f"{final_capacity:.3f} Ah")
        with col3:
            st.metric("Total Cycles", total_cycles)
        with col4:
            st.metric("Capacity Degradation", f"{capacity_fade:.2f}%")
        
        # Aging analysis
        if 'impedance' in self.battery_data and len(self.battery_data['impedance']) > 0:
            impedance_data = self.battery_data['impedance']
            initial_resistance = impedance_data['Total_Resistance'].iloc[0]
            final_resistance = impedance_data['Total_Resistance'].iloc[-1]
            resistance_increase = ((final_resistance - initial_resistance) / initial_resistance) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial Resistance", f"{initial_resistance:.3f} Ω")
            with col2:
                st.metric("Final Resistance", f"{final_resistance:.3f} Ω")
            with col3:
                st.metric("Resistance Increase", f"{resistance_increase:.2f}%")
        
        # Throughput analysis
        total_throughput = discharge_data['Throughput'].iloc[-1]
        avg_throughput_per_cycle = total_throughput / total_cycles
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Throughput", f"{total_throughput:.2f} Ah")
        with col2:
            st.metric("Avg Throughput/Cycle", f"{avg_throughput_per_cycle:.3f} Ah")
        
        # RUL prediction
        if capacity_fade > 0:
            cycles_to_eol = (30 - capacity_fade) / (capacity_fade / total_cycles)
            remaining_life = (cycles_to_eol/total_cycles)*100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cycles to EOL (30%)", f"{cycles_to_eol:.1f}")
            with col2:
                st.metric("Remaining Life", f"{remaining_life:.1f}%")
        
        # Recommendations
        st.subheader("💡 TECHNICAL RECOMMENDATIONS")
        if capacity_fade > 30:
            st.error("⚠️  Battery shows end-of-life conditions - Replace battery immediately")
        elif capacity_fade > 20:
            st.warning("⚡ Battery shows advanced degradation - Monitor impedance parameters more frequently")
        elif capacity_fade > 10:
            st.info("⚡ Battery is in moderate aging phase - Optimize charge/discharge protocols")
        else:
            st.success("✅ Battery maintains good performance - Continue normal operation")
    
    def run_streamlit_dashboard(self):
        """Run the Streamlit dashboard"""
        st.set_page_config(
            page_title="Battery Analysis Dashboard",
            page_icon="🔋",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Sidebar
        with st.sidebar:
            st.title("🔋 Battery Analysis Dashboard")
            st.markdown("---")
            
            # Battery selection
            st.subheader("Select Battery")
            if self.available_batteries:
                selected_battery = st.selectbox(
                    "Choose battery to analyze:",
                    self.available_batteries,
                    index=0
                )
                
                if st.button("Analyze Selected Battery", type="primary"):
                    if self.calculate_battery_metrics(selected_battery):
                        st.session_state.current_battery = selected_battery
                        st.session_state.battery_analyzed = True
                        st.success(f"✅ {selected_battery} analyzed successfully!")
                    else:
                        st.error(f"❌ Failed to analyze {selected_battery}")
            else:
                st.warning("No batteries available")
            
            st.markdown("---")
            st.markdown("**Dataset Info:**")
            st.info(f"Total Records: {len(self.metadata) if self.metadata is not None else 0}")
            st.info(f"Available Batteries: {len(self.available_batteries)}")
            
            st.markdown("---")
            st.markdown("**About:**")
            st.markdown("Interactive dashboard for NASA battery dataset analysis. Select a battery to view comprehensive performance metrics and aging analysis.")
        
        # Main content
        st.title("🔋 Interactive Battery Analysis Dashboard")
        st.markdown("Select a battery from the sidebar to begin analysis.")
        
        # Check if battery is analyzed
        if hasattr(st.session_state, 'battery_analyzed') and st.session_state.battery_analyzed:
            current_battery = st.session_state.current_battery
            
            # Header with current battery info
            st.header(f"📊 Analysis Results for Battery: {current_battery}")
            
            # Create tabs for different analysis sections
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📈 Capacity Analysis", 
                "🔋 Impedance Analysis", 
                "⚡ Performance Metrics",
                "🔬 Advanced Analysis",
                "📊 Executive Summary",
                "ℹ️ About"
            ])
            
            with tab1:
                st.subheader("Capacity Degradation Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    self.plot_capacity_degradation(current_battery)
                
                with col2:
                    self.plot_soc_dod_evolution(current_battery)
                
                self.plot_throughput_analysis(current_battery)
            
            with tab2:
                st.subheader("Impedance Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    self.plot_impedance_parameters(current_battery)
                
                with col2:
                    self.plot_resistance_increase(current_battery)
                
                self.plot_capacity_vs_resistance(current_battery)
            
            with tab3:
                st.subheader("Performance Metrics")
                col1, col2 = st.columns(2)
                
                with col1:
                    self.plot_energy_efficiency(current_battery)
                
                with col2:
                    self.plot_degradation_rate(current_battery)
            
            with tab4:
                st.subheader("Advanced Analysis")
                st.info("🔬 **Advanced Features** - These analyses use detailed CSV data and may take longer to load")
                
                # First row: I-V Curves and Real Energy Efficiency
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 I-V Curves Analysis")
                    self.plot_iv_curves(current_battery)
                
                with col2:
                    st.subheader("⚡ Real Energy Efficiency")
                    self.plot_real_energy_efficiency(current_battery)
                
                # Second row: Thermal Analysis (full width)
                st.subheader("🌡️ Thermal Analysis")
                self.plot_thermal_analysis(current_battery)
            
            with tab5:
                self.generate_executive_summary(current_battery)
            
            with tab6:
                st.subheader("About This Dashboard")
                st.markdown("""
                This interactive dashboard provides comprehensive battery analysis including:
                
                **📈 Capacity Analysis:**
                - Capacity degradation over cycles
                - SOC and DOD evolution
                - Cumulative throughput analysis
                
                **🔋 Impedance Analysis:**
                - Electrolyte and charge transfer resistance
                - Resistance increase trends
                - Capacity vs resistance correlation
                
                **⚡ Performance Metrics:**
                - Energy efficiency trends
                - Per-cycle degradation rates
                - End-of-life predictions
                
                **📊 Executive Summary:**
                - Key performance indicators
                - Remaining useful life estimates
                - Technical recommendations
                
                Select different batteries from the sidebar to analyze their performance characteristics.
                """)
        
        else:
            # Show welcome message and dataset overview
            st.info("👈 Use the sidebar to select a battery for analysis")
            
            if self.metadata is not None:
                st.subheader("Dataset Overview")
                
                # Show sample of available batteries
                if len(self.available_batteries) > 0:
                    st.write("**Sample of Available Batteries:**")
                    sample_batteries = self.available_batteries[:20]  # Show first 20
                    st.write(", ".join(sample_batteries))
                    if len(self.available_batteries) > 20:
                        st.write(f"... and {len(self.available_batteries) - 20} more")
                
                # Show data distribution
                if 'type' in self.metadata.columns:
                    st.write("**Data Distribution by Type:**")
                    type_counts = self.metadata['type'].value_counts()
                    st.bar_chart(type_counts)

if __name__ == "__main__":
    # Configure paths
    metadata_path = "cleaned_dataset_battery_NASA/metadata.csv"
    data_dir = "cleaned_dataset_battery_NASA/data"
    
    # Create dashboard instance
    dashboard = InteractiveBatteryDashboard(metadata_path, data_dir)
    
    # Load data first
    if dashboard.load_and_clean_data():
        # Run the Streamlit dashboard
        dashboard.run_streamlit_dashboard()
    else:
        st.error("Failed to load data. Please check your file paths.")
