'''
file: final.py
Osher Shimoni
CS 230 - Professor Frydenberg
Final Project Code
'''

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

filename = "earthquakes.csv"
df = pd.read_csv("earthquakes.csv")
mag = df["mag"]  # Subsets the query keeping only the magnitude column


# Converts input to float
def convertToFloat(num):
    return float(num)


# Display the earthquake with the greatest magnitude
def displayEarthquakeMaxMag(option):
    displayOption = st.sidebar.radio("Display Options", ["Top 100", "Top 10", "Top 1"])

    sortedTable = df.sort_values('mag', ascending=False)
    numRows = int(displayOption[4:])
    st.title(f"Strongest Earthquakes - {displayOption} ")
    st.map(sortedTable.head(numRows))
    st.table(sortedTable.head(numRows)[['time', 'latitude', 'longitude', 'mag', 'place', 'depth']])


# Displays the earthquakes within 10 degrees long/lat to the user's location
def displayNearbyEarthquakes(option):
    st.title(option)

    # User enters their latitude and longitude
    userLatitude = st.sidebar.text_input("Enter your approximate latitude: ")
    userLongitude = st.sidebar.text_input("Enter your approximate longitude: ")

    displayOption = st.sidebar.radio("Display Options", ["Map", "Table", "Both"])

    if userLatitude != "" and userLongitude != "":
        nearbyEarthquakes = pd.DataFrame(df[(df["latitude"] <= convertToFloat(userLatitude) + 5) & (
                df["latitude"] >= convertToFloat(userLatitude) - 5) & (
                                                    df["longitude"] <= convertToFloat(userLongitude) + 5) & (
                                                    df["longitude"] >= convertToFloat(userLongitude) - 5)][
                                             ['time', 'latitude', 'longitude', 'mag', 'depth', 'place']])

        userLocation = pd.DataFrame(
            {'latitude': [convertToFloat(userLatitude)], 'longitude': [convertToFloat(userLongitude)]})

        if nearbyEarthquakes.empty:
            st.write("No earthquakes occurred near you.")
            if displayOption == "Map":
                st.map(userLocation)
        else:
            if displayOption == "Map" or displayOption == "Both":
                st.map(nearbyEarthquakes)
            if displayOption == "Table" or displayOption == "Both":  # If earthquakes within 10 degrees long/lat of user's coords, display map
                st.table(df[(df["latitude"] <= convertToFloat(userLatitude) + 5) & (
                        df["latitude"] >= convertToFloat(userLatitude) - 5) & (
                                    df["longitude"] <= convertToFloat(userLongitude) + 5) & (
                                    df["longitude"] >= convertToFloat(userLongitude) - 5)][
                             ['time', 'latitude', 'longitude', 'mag', 'depth', 'place']])
    else:
        st.map()  # Empty map if not region is selected


def displayEarthquakesByRegion(option):
    regionList = list(df.locationSource.unique())  # Display region options
    regionListMenu = list(df.locationSource.unique())
    regionListMenu.insert(0, "")

    regionSelect = st.sidebar.selectbox("Select a Region", regionListMenu)  # User selects region
    st.title(f"Earthquakes by Region {regionSelect.upper()}")
    displayOption = st.sidebar.radio("Display Options", ["Map of Regional Earthquakes", "Chart Region Data",
                                                         "Strongest Earthquake in Region",
                                                         "Detailed Regional Earthquake Table"])

    if displayOption == "Map of Regional Earthquakes":
        if regionSelect == "":
            st.write("Select a region from the drop down menu")
            st.map()
        else:
            regionSubsetWithCoords = pd.DataFrame(df[(df["locationSource"] == regionSelect)][["time", "mag", "latitude",
                                                                                              'longitude']])  # Subset dataframe by selected region including lat/long
            st.map(regionSubsetWithCoords)

    elif displayOption == "Chart Region Data":
        regionSubsetGroupByDate = pd.DataFrame(df[(df["locationSource"] == regionSelect)][["time",
                                                                                           "mag"]])  # Subset dataframe by selected region
        regionSubsetGroupByDate['time'] = pd.to_datetime(
            regionSubsetGroupByDate['time']).dt.date  # Changes time column to datetime datatype

        regionSubsetGroupByRegion = pd.DataFrame(df["locationSource"])

        graphType = st.selectbox("Choose a Graph", ["", "Total Earthquakes by Day", "Average Magnitude by Day",
                                                    "Pie Chart of Earthquakes by Region"])
        if graphType == "":
            st.write("Select a graph to display from the drop down menu above.")
        # Option 1
        elif graphType == "Total Earthquakes by Day":
            if regionSelect == "":
                st.write("Select a region from the drop down menu")
            else:
                plt.plot(regionSubsetGroupByDate.groupby(["time"]).size())  # Plots num of earthquakes by day
                plt.title(f"Number of Earthquakes per Day in {regionSelect.upper()}")
                plt.xlabel("Date")
                plt.ylabel("Number of Earthquakes")
                plt.xticks(rotation='vertical')
                st.pyplot(plt)  # Show plot
        # Option 2
        elif graphType == "Average Magnitude by Day":
            if regionSelect == "":
                st.write("Select a region from the drop down menu")
            else:
                plt.plot(regionSubsetGroupByDate.groupby(["time"]).mean())  # Plots avg magnitude  by day
                plt.title(f"Average Magnitude by Day in {regionSelect.upper()}")
                plt.xlabel("Date")
                plt.ylabel("Magnitude")
                plt.xticks(rotation='vertical')
                st.pyplot(plt)
        # Option 3
        elif graphType == "Pie Chart of Earthquakes by Region":
            sorted(regionList)
            pieType = st.radio("Select an Option", ["Selected Region", "All Regions"])
            if pieType == "Selected Region":
                # Count of earthquakes by region
                regionEarthquakeCount = regionSubsetGroupByRegion.groupby(["locationSource"]).size()

                # List of region's proportions
                regionProportions = []
                for i in range(len(regionEarthquakeCount)):
                    regionProportions.append((regionEarthquakeCount[i] / regionSubsetGroupByRegion.count()) * 100)

                # If no region is selected, display full pie chart
                if regionSelect == "":
                    plt.pie(regionEarthquakeCount, labels=sorted(regionList), radius=.70)
                    plt.legend(loc="best", prop={'size': 6},
                               labels=['%s, %1.1f %%' % (l, s) for l, s in zip(sorted(regionList), regionProportions)])
                    plt.title("Proportions of Total Earthquakes by Region")
                    plt.tight_layout()
                    st.pyplot(plt)
                else:  # Display pie chart proportions exploding selected region
                    explode = []
                    for i in range(len(regionList)):
                        explode.append(0.0)
                    explode[sorted(regionList).index(
                        regionSelect)] = 0.125  # Finds index of selected region and explodes that value

                    plt.pie(regionEarthquakeCount, labels=sorted(regionList), explode=explode, radius=.70)
                    plt.legend(loc="best", prop={'size': 6},
                               labels=['%s, %1.1f %%' % (l, s) for l, s in zip(sorted(regionList), regionProportions)])
                    plt.title("Proportions of Total Earthquakes by Region")
                    plt.tight_layout()
                    st.pyplot(plt)
            else:
                # Filter by non-us, then get mag value, then filter by mag value
                regionSubsetGroupByRegionAndMag = pd.DataFrame(
                    df[(df["locationSource"] != "us")][["locationSource", "mag"]])
                magValue = st.slider("Filter by Magnitude", min_value=regionSubsetGroupByRegionAndMag["mag"].min(),
                                     max_value=regionSubsetGroupByRegionAndMag["mag"].max(), value=0.00, step=0.01)
                regionSubsetGroupByRegionAndMag = pd.DataFrame(
                    regionSubsetGroupByRegionAndMag[(regionSubsetGroupByRegionAndMag["mag"] >= magValue)][
                        "locationSource"])

                # Count the earthquakes per region filtered by mag
                regionEarthquakeCountWithMag = regionSubsetGroupByRegionAndMag.groupby(
                    ["locationSource"]).size()
                # List regions that are greater than or equal to current magnitude filter
                regionListWithFilter = list(regionSubsetGroupByRegionAndMag.locationSource.unique())

                # Count the proprtions of total per region earthquakes filtered by mag
                regionProportionsWithMag = []
                for i in range(len(regionEarthquakeCountWithMag)):
                    regionProportionsWithMag.append(
                        (regionEarthquakeCountWithMag[
                             i] / regionSubsetGroupByRegionAndMag.count()) * 100)

                # Plot
                plt.pie(regionEarthquakeCountWithMag, labels=sorted(regionListWithFilter), radius=.70)
                plt.legend(loc="best", prop={'size': 6}, labels=['%s, %1.1f %%' % (l, s) for l, s in
                                                                 zip(sorted(regionListWithFilter),
                                                                     regionProportionsWithMag)])
                plt.title("Proportions of Total Earthquakes by Region")
                plt.tight_layout()
                st.pyplot(plt)

    elif displayOption == "Detailed Regional Earthquake Table":
        if regionSelect == "":
            st.write("Select a region from the drop down menu")
        else:
            regionSubsetTable = pd.DataFrame(df[(df["locationSource"] == regionSelect)])  # Subset dataframe by region
            st.subheader(f"Earthquakes Recorded in {regionSelect.upper()}")
            st.write(
                regionSubsetTable.drop(['locationSource', 'net', 'magSource', 'type', 'magType', 'status'], axis=1))
    elif displayOption == "Strongest Earthquake in Region":
        # Subset dataframe by selected region
        regionSubset = pd.DataFrame(
            df[(df["locationSource"] == regionSelect)][["time", "mag", "latitude", 'longitude', 'place']])
        # Sort descending by magnitude
        sortedRegionTable = regionSubset.sort_values('mag', ascending=False)

        st.map(sortedRegionTable.head(1))  # map
        st.table(sortedRegionTable.head(1))  # table


def learn(option):
    st.title(option)
    st.video("https://www.youtube.com/watch?v=_r_nFT2m-Vg")


def main():
    st.write("Created by Osher Shimoni")
    st.sidebar.title("USA Earthquake Data")
    st.sidebar.subheader("Sept. 30th to Nov. 23rd, 2020")

    # User chooses what they want to do
    option = st.sidebar.selectbox("Select an Option", (
        "Home", "Earthquakes by Region", "Strongest Earthquakes", "Earthquakes Near Me",
        "Learn About Earthquakes"))
    if option == "Home":
        st.title("Home")
        st.subheader("USA Earthquakes Map")
        st.map(df)  # Homepage is USA earthquakes map
    # User chose display earthquake highest mag
    if option == "Earthquakes by Region":
        displayEarthquakesByRegion(option)
    # User chose strongest earthquakes
    elif option == "Strongest Earthquakes":
        displayEarthquakeMaxMag(option)
    # User chose display earthquakes near you
    elif option == "Earthquakes Near Me":
        displayNearbyEarthquakes(option)
    # User chose learn about earthquakes
    elif option == "Learn About Earthquakes":
        learn(option)


main()
