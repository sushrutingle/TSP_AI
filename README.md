# AI-Based Route Optimizer

A Tkinter-based desktop application that solves the **Travelling Salesman Problem (TSP)** for Indian cities using the **Hill Climbing** algorithm with 2-opt local search.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-Project-blue.svg)

## Features

- **City Selection**: Choose 2–10 Indian cities from a dropdown list
- **Algorithm Parameters**: Configure random restarts, max iterations, and improvement strategy
- **Hill Climbing Optimization**: Local search with 2-opt neighborhood moves
- **Interactive Map**: Folium-based HTML map showing the optimized route
- **Visualization**: Matplotlib graphs showing route, segment distances, and convergence
- **Dark Theme UI**: Modern styled Tkinter interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RouteOptimizer
```

2. Install dependencies:
```bash
pip install numpy matplotlib folium
```

## Usage

Run the application:
```bash
python main.py
```

### How to Use

1. Select the number of cities (2–10)
2. Choose cities from the dropdown menus (or click "Sample Set" for quick demo)
3. Adjust algorithm parameters:
   - **Random Restarts**: Number of times to restart (1–20)
   - **Max Iterations**: Iterations per restart (500–50000)
   - **Strategy**: First-improvement or Best-improvement
4. Click **Run Optimization**
5. View results in:
   - KPI cards (distance, cities, time, restarts)
   - Route table with segment details
   - **Open Map** button for interactive Folium map
   - **Show Graph** button for Matplotlib visualization

## Project Structure

```
RouteOptimizer/
├── main.py              # Tkinter GUI application
├── algorithm.py         # Hill Climbing optimizer
├── cities_data.py       # Indian cities database (41 cities)
├── distances.py         # Haversine distance calculations
├── map_visualizer.py   # Folium interactive map
├── graph_plotter.py     # Matplotlib visualizations
├── requirements.txt     # Python dependencies
└── output/              # Generated maps and graphs
```

## Algorithm

The application uses **Hill Climbing with 2-opt moves**:

1. Start with a random permutation of cities based on selection
2. Generate neighbors by swapping cities or reversing segments
3. Move to the best neighbor that improves total distance
4. Repeat until no improvement found (local optimum)
5. Restart with new random routes to avoid local optima

## Cities Included

Mumbai, Delhi, Bengaluru, Hyderabad, Ahmedabad, Chennai, Kolkata, Pune, Jaipur, Surat, Lucknow, Kanpur, Nagpur, Indore, Thane, Bhopal, Visakhapatnam, Pimpri-Chinchwad, Patna, Vadodara, Ghaziabad, Ludhiana, Agra, Nashik, Faridabad, Meerut, Rajkot, Varanasi, Srinagar, Aurangabad, Dhanbad, Amritsar, Allahabad, Ranchi, Coimbatore, Mysuru, Kochi, Bhubaneswar, Guwahati, Chandigarh

## License


