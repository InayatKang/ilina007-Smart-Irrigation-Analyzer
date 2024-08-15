import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load CSV file with caching
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%y %I:%M:%S %p')
    df.set_index('Time', inplace=True)
    return df

# Use the relative path for your image
st.image("logo.png", use_column_width=True)  # Adjust the path if the image is in a different location

# Analyze data and provide recommendations
def analyze_data(df):
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index, format='%m/%d/%y %I:%M:%S %p')

    df['Time Slot'] = df.index.hour.map(
        lambda x: 'Early Morning' if x < 6 else
                  'Morning' if x < 12 else
                  'Early Afternoon' if x < 15 else
                  'Afternoon' if x < 18 else
                  'Evening'
    )

    daily_stats = df.groupby(df.index.date).agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'light level': 'mean'
    }).reset_index()

    daily_stats.columns = ['Date', 'Mean Temperature (°C)', 'Mean Humidity (%)', 'Mean Light Level (Lux)']
    return daily_stats

# Function to provide irrigation recommendations
def recommend_irrigation(mean_temp, mean_humidity, mean_light):
    if mean_temp > 25 and mean_humidity < 40:
        return ("<b style='color:green;'>Irrigation is recommended early in the morning</b> to minimize evaporation and water wastage. "
                "This helps ensure water reaches the plant roots effectively before temperatures rise.")
    elif mean_temp > 20 and mean_humidity < 50:
        return ("<b style='color:green;'>Irrigation is recommended early in the morning or late afternoon</b>, depending on current temperature and humidity. "
                "This approach balances effective watering with minimizing water loss due to evaporation.")
    else:
        return ("<b style='color:green;'>No irrigation needed</b> based on the current data. Continue to monitor conditions regularly to optimize watering schedules.")

# Streamlit app layout
st.title('Smart Irrigation Analyzer')

# Add links to resources at the top
st.markdown("### Resources")
st.markdown("For more information on irrigation and crop management in Alberta, visit the [Alberta Ministry of Agriculture and Irrigation](https://www.alberta.ca/agriculture-and-irrigation.aspx).")
st.markdown("For weather data and climate information relevant to Calgary, check [Environment Canada](https://www.weather.gc.ca/).")
st.markdown("For further information on optimal irrigation practices in Alberta, visit the [Alberta Irrigation Manual](https://www.alberta.ca/system/files/custom_downloaded_images/af-alberta-irrigation-management-manual.pdf).")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    valid_dates = df.index.normalize().unique()
    if valid_dates.size > 0:
        selected_date = st.sidebar.date_input("Select a date", min_value=valid_dates.min().date(), max_value=valid_dates.max().date())

        if st.sidebar.button("Show hourly data"):
            st.subheader(f"Hourly Data for {selected_date}")
            day_data = df[df.index.date == selected_date]
            if not day_data.empty:
                st.write(day_data)

                mean_temp = day_data['temperature'].mean()
                mean_humidity = day_data['humidity'].mean()
                mean_light = day_data['light level'].mean()

                st.write(f"Mean Temperature: {mean_temp:.2f} °C")
                st.write(f"Mean Humidity: {mean_humidity:.2f} %")
                st.write(f"Mean Light Level (Lux): {mean_light:.2f}")

                recommendation = recommend_irrigation(mean_temp, mean_humidity, mean_light)
                st.markdown(recommendation, unsafe_allow_html=True)

                # Plotting the data
                st.subheader("Data Visualization")
                
                # Creating subplots for each metric in a single row
                fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
                
                ax1.plot(day_data.index, day_data['temperature'], color='red')
                ax1.set_title("Temperature (°C)")
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Temperature (°C)')
                
                ax2.plot(day_data.index, day_data['humidity'], color='blue')
                ax2.set_title("Humidity (%)")
                ax2.set_xlabel('Time')
                ax2.set_ylabel('Humidity (%)')

                ax3.plot(day_data.index, day_data['light level'], color='green')
                ax3.set_title("Light Level (Lux)")
                ax3.set_xlabel('Time')
                ax3.set_ylabel('Light Level (Lux)')

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.write("No data available for the selected date.")
    else:
        st.error("No valid dates available in the data.")

    daily_stats = analyze_data(df)
    if not daily_stats.empty:
        st.subheader("Daily Averages")
        st.write(daily_stats)

        recent_stats = daily_stats.iloc[-1]
        recent_mean_temp = recent_stats['Mean Temperature (°C)']
        recent_mean_humidity = recent_stats['Mean Humidity (%)']
        recent_mean_light = recent_stats['Mean Light Level (Lux)']

        recommendation = recommend_irrigation(recent_mean_temp, recent_mean_humidity, recent_mean_light)
        st.markdown(f"Recent Recommendation: {recommendation}", unsafe_allow_html=True)

    st.write("Note: Recommendations are based on historical data trends and best practices for irrigation timing. They should be used as insights and suggestions rather than strict instructions.")
