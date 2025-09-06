# 🔋 Interactive Battery Analysis Dashboard

An interactive web-based dashboard for analyzing NASA battery dataset performance and aging characteristics.

## ✨ Features

- **Automatic Data Download**: Simple script to download NASA battery dataset from Kaggle
- **Real-time Interactive Dashboard**: No more static images - analyze batteries dynamically
- **Battery Selection Filter**: Choose any battery from the dataset and see results instantly
- **Comprehensive Analysis**: Capacity degradation, impedance analysis, performance metrics
- **Live Charts**: Interactive Plotly charts that update based on selected battery
- **Executive Summary**: Key performance indicators and technical recommendations
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python3 -m pip install -r requirements_v2.txt
```

**Note**: If `pip` command is not found, use `python3 -m pip` instead.

### 2. Download NASA Battery Dataset

```bash
python3 download_nasa_data.py
```

This script will automatically:
- Check if the data already exists
- Download the NASA battery dataset from Kaggle if needed
- Organize the data in the correct directory structure
- Fix any nested directory issues automatically

### 3. Run the Dashboard

```bash
python3 -m streamlit run battery_dashboard_filter_battery_v2.py
```

The dashboard will open in your default web browser. Streamlit will show the exact URL in the terminal (usually `http://localhost:8501`)

## 📊 How to Use

1. **Select a Battery**: Use the sidebar to choose a battery from the dropdown menu
2. **Click "Analyze Selected Battery"**: The dashboard will process the data and display results
3. **Explore Results**: Navigate through different analysis tabs:
   - **Capacity Analysis**: Capacity degradation, SOC/DOD evolution, throughput
   - **Impedance Analysis**: Resistance parameters, aging trends, correlations
   - **Performance Metrics**: Energy efficiency, degradation rates
   - **Executive Summary**: Key metrics and recommendations
4. **Switch Batteries**: Select different batteries to compare performance

## 🔍 Analysis Features

### Capacity Analysis
- **Capacity Degradation**: Track battery capacity over cycles with trend lines
- **SOC/DOD Evolution**: State of Charge and Depth of Discharge analysis
- **Throughput Analysis**: Cumulative energy delivery over battery lifetime

### Impedance Analysis
- **Resistance Parameters**: Electrolyte (Re) and Charge Transfer (Rct) resistance
- **Aging Trends**: Resistance increase over time
- **Performance Correlation**: Capacity vs resistance relationships

### Performance Metrics
- **Energy Efficiency**: Battery performance maintenance over cycles
- **Degradation Rates**: Per-cycle capacity loss analysis
- **End-of-Life Prediction**: Remaining useful life estimates

## 📥 Data Download Script

Simple script to download the NASA battery dataset:

```bash
python3 download_nasa_data.py
```

**Note**: If you get authentication errors, set up Kaggle API credentials at https://www.kaggle.com/account

## 📁 Data Structure

The dashboard expects the following directory structure:
```
cleaned_dataset_battery_NASA/
├── metadata.csv          # Battery metadata and test results
├── data/                 # Individual test data files
│   ├── 06825.csv
│   ├── 01192.csv
│   └── ...
└── extra_infos/          # Additional information files
```

## 🛠️ Technical Details

- **Frontend**: Streamlit web application
- **Charts**: Interactive Plotly visualizations
- **Data Processing**: Pandas and NumPy for analysis
- **Real-time Updates**: Session state management for dynamic content

## 🔧 Customization

You can modify the dashboard by:
- Adding new analysis metrics in the `InteractiveBatteryDashboard` class
- Creating new chart types in the plotting methods
- Customizing the UI layout and styling
- Adding new data sources or analysis algorithms

## 📈 Benefits Over Static Images

- **Instant Analysis**: No waiting for image generation
- **Interactive Exploration**: Zoom, pan, and hover over charts
- **Real-time Comparison**: Switch between batteries instantly
- **Better User Experience**: Modern web interface
- **Shareable**: Access from any device with a web browser

## 🚨 Troubleshooting

- **Data Loading Issues**: Check file paths and CSV format
- **Memory Problems**: Large datasets may require more RAM
- **Browser Compatibility**: Use modern browsers (Chrome, Firefox, Safari, Edge)
- **Streamlit Command Not Found**: Use `python3 -m streamlit` instead of `streamlit`
- **Kaggle Authentication**: Set up Kaggle API credentials if download fails
- **Directory Structure Issues**: The download script automatically fixes nested directories

## 📚 Dependencies

- `streamlit>=1.28.0` - Web application framework
- `plotly>=5.0.0` - Interactive charts
- `pandas>=1.3.0` - Data manipulation
- `numpy>=1.20.0` - Numerical computing
- `matplotlib>=3.3.0` - Plotting (legacy support)
- `seaborn>=0.11.0` - Statistical visualization
- `kagglehub>=0.2.0` - Kaggle dataset downloader

## 🤝 Contributing

Feel free to contribute improvements:
- Add new analysis methods
- Enhance chart interactivity
- Improve UI/UX design
- Add data validation features

## 📄 License

This project is open source and available under the MIT License.
