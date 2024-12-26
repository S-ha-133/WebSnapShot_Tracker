## Overview
The WebSnapShot_Tracker is a specialized tool designed for capturing and analyzing changes on web pages. This application not only saves web-related data in JSON format but also captures screenshots in PNG format, allowing users to compare historical and current data snapshots to identify changes effectively. It can capture data and images from a specified URL and any accessible links found on the initial page.

You will need to set up an OpenAI API key and an Assistant ID in the `Web_Change_Analyzer.py` script to use the comparison features. Replace the placeholders in the script with your actual API key and Assistant ID.

## Features
- **Capture Web Data**: Automatically saves snapshots of web pages as JSON files and PNG images. It captures data from the specified URL and all navigable links from that URL.
- **Compare Snapshots**: Compares different versions of web data in JSON format to highlight changes and updates. Note: This feature does not compare images but focuses on JSON data comparisons.

## Running the Application
To launch the WebSnapShot_Tracker application, navigate to the project directory and execute the following command in your terminal:
```
streamlit run WebSnapShot_Tracker.py
```



