import time
import pandas as pd
import numpy as np

CITY_DATA = { 'C': 'chicago.csv',
              'N': 'new_york_city.csv',
              'W': 'washington.csv' }
valid_months = ['JAN','FEB','MAR','APR','MAY','JUN']
valid_days = ['MON','TUE','WED','THU','FRI','SAT','SUN','WK','WN']

def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month or month range to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or work week or weekend or "all" to apply no day filter
    """
    # Generic error message on invalid user input:
    message = 'Please attempt your input again with one of the options specified above!'
    month, day = 'ALL','ALL'

    print('Hello! Let\'s explore some US bikeshare data!')
    print('Note that certain cities do not have gender or birth date data available!')
    # Get user input for city and validate that only the first char is entered
    print('Which city would you like to see data for?')
    print('Enter C for Chicago\nEnter N for New York \nEnter W for Washington')
    while True:
        try:
            city = input('-->')
            city = city.strip().capitalize()
            if city in ['C','W','N']:
                break
            else:
                raise Exception
        except:
            print(message)
    # Get user input for additional filter if applicable and validate
    print('Would you like to filter the data by time period?')
    print('Enter M to filter by Month')
    print('Enter D to filter by Day')
    print('Enter N for No additional filter')
    while True:
        try:
            month_filt = input('-->')
            month_filt = month_filt.strip().capitalize()
            if month_filt in ['M','D','N']:
                break
            else:
                raise Exception
        except:
            print(message)
    # Get additional filter for month if requested. Additional month range option!
    if month_filt == 'M':
        print('Enter the month - Jan, Feb, Mar, Apr, May, Jun or alternately:')
        print('To enter a range, separate start and end month by "-" (ex: Jan-Mar)')
        while True:
            try:
                month = input('-->')
                month = month.strip().upper()
                if (month in valid_months or
                (month[0:3] in valid_months and month[3:4] == '-' and month[4:7] in valid_months)):
                    break
                else:
                    raise Exception
            except:
                print(message)

    # Get additional filter for day if requested
    elif month_filt == 'D':
        print('Enter the day - Mon, Tue, Wed, Thu, Fri, Sat, Sun or alternately')
        print('For working week[Mon-Fri] enter WK and for weekends enter WN')
        while True:
            try:
                day = input('-->')
                day = day.strip().upper()
                if day in valid_days:
                    break
                else:
                    raise
            except:
                print(message)
    print('-'*100)
    return city, month, day

def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month or month range to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or work week or weekend or "all" to apply no day filter
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """
    # Load df with the relevant city file (csv)
    df = pd.read_csv(CITY_DATA[city])

    # Convert the Start Time column to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])

    # Extract hour, month and day of week and add as new columns
    df['Hour'] = df['Start Time'].dt.hour
    df['Month'] = df['Start Time'].dt.month
    df['Day_of_week'] = df['Start Time'].dt.weekday

    #Filter the data by user specified month criteria
    if month != 'ALL':
        # Need different behavior for a range like Jan-Mar vs just Jan
        if month.find('-') > 0:
            lower_month, upper_month = month.split('-')
            upper_month = upper_month[0:3]
            month = lower_month + '-' + upper_month
            lower_month_idx = valid_months.index(lower_month)
            upper_month_idx = valid_months.index(upper_month)
            if lower_month_idx <= upper_month_idx:
                month_list = [x+1 for x in range(lower_month_idx, upper_month_idx)]
            else:
                month_list = [x+1 for x in range(upper_month_idx, lower_month_idx)]
            df = df[df['Month'].isin(month_list)]
        else:
            month_idx = valid_months.index(month) + 1
            df = df[df['Month'] == month_idx]

    #Filter the data by user specified day of week criteria
    if day != 'ALL':
        # Similar to month, either we have a single day or M-F or Sat/Sun
        if day == 'WK':
            day_list = [0,1,2,3,4]
            df = df[df['Day_of_week'].isin(day_list)]
        elif day == 'WN':
            day_list = [5,6]
            df = df[df['Day_of_week'].isin(day_list)]
        else:
            day_idx = valid_days.index(day)
            df = df[df['Day_of_week'] == day_idx]
    # Printing parameters of user's filter criteria before printing statistics
    cityname , chars = (CITY_DATA[city]).split('.')
    cityname = cityname.title()
    print('Selection data is for {}, for the month(s): {} and day(s): {}\n'.format(cityname, month, day))

    # Filtering complete, return the sliced data frame per the user's selection
    return df

def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel based on start times...\n')
    start_time = time.time()

    # Calculate the most common month, day of week and start hour and associated trip counts
    common_month = df['Month'].mode()[0] - 1
    common_month_count = df['Month'].value_counts().iloc[0]
    common_day = df['Day_of_week'].mode()[0]
    common_day_count = df['Day_of_week'].value_counts().iloc[0]
    common_hour = df['Hour'].mode()[0]
    common_hour_count = df['Hour'].value_counts().iloc[0]

    # Display the calculated mode values
    print("The most common month with {} rides was:\t\t{}".format(common_month_count , valid_months[common_month]))
    print("The most common day of week with {} rides was:\t{}".format(common_day_count , valid_days[common_day]))
    print("The most common start hour for {} rides was:\t{}:00".format(common_hour_count , common_hour))
    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*100)

def station_stats(df):
    """Displays statistics on the most popular stations and associated trip counts."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # Determine most common start and end stations with ride counts and combo trip
    # Need to modify the df projection to add a combined field for Origin/Dest
    df['Start_End_Stations'] = (df['Start Station'] + '%' + df['End Station'])
    common_start = df['Start Station'].mode()[0]
    common_start_count = df['Start Station'].value_counts().iloc[0]
    common_end = df['End Station'].mode()[0]
    common_end_count = df['End Station'].value_counts().iloc[0]
    common_trip = df['Start_End_Stations'].mode()[0]
    common_trip_count = df['Start_End_Stations'].value_counts().iloc[0]
    common_trip_l = common_trip.split('%')

    # Display the calculated values for most popular stations
    print("The most common start station with {} rides was:\t{}".format(common_start_count , common_start))
    print("The most common end station with {} rides was:\t{}".format(common_end_count , common_end))
    print("The most common trip stations with {} rides were b/w:\t{} AND {}".format(common_trip_count , common_trip_l[0] , common_trip_l[1]))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*100)

def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # Compute the total travel time and mean travel durations
    total_duration_sec = df['Trip Duration'].sum()
    # Function call for calculating seconds in days and HH:MM:SS
    total_duration = convert_time_seconds(total_duration_sec)
    total_trips = df.count()[0]
    mean_duration_sec = df['Trip Duration'].mean()
    mean_duration = time.strftime("%H:%M:%S", time.gmtime(mean_duration_sec))

    # Display total travel time and mean travel time
    print("The total travel time [Days HH:MM:SS] for {} rides was:\t{}".format(total_trips , total_duration))
    print("The average travel time [HH:MM:SS] for {} rides was:\t{}".format(total_trips , mean_duration))


    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*100)

def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...')
    start_time = time.time()

    # Some of the city sheets may not have all these columns, so a check is always performed
    # Computing counts of user types and gender
    user_type_stats(df, 'User Type')
    user_type_stats(df, 'Gender')

    # Display earliest, most recent, and most common year of birth
    if 'Birth Year' in df.columns:
        print("\nThe earliest year of birth was:\t\t{}".format(int(df['Birth Year'].min())))
        print("The most recent year of birth was:\t{}".format(int(df['Birth Year'].max())))
        print("The most common year of birth was:\t{}".format(int(df['Birth Year'].mode()[0])))
    else:
        print("\n**NOTE: No data available for Birth Year")

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*100)

def convert_time_seconds(input_time):
    """Takes an input time in seconds and returns days, hours, mins, seconds."""

    if input_time == 0:
        return 0
    else:
        num_days = input_time // 86400
        if num_days > 0:
            rem_seconds = input_time - (num_days * 86400)
            duration = time.strftime("%H:%M:%S", time.gmtime(rem_seconds))
            duration = str(num_days) + ' Days ' + duration
        else:
            duration = time.strftime("%H:%M:%S", time.gmtime(rem_seconds))
        return duration

def user_type_stats(df , column_name):
    """Checks if the column exists in the df, if so prints its value counts."""

    if column_name in df.columns:
        print("\nThe different {} counts are:".format(column_name))
        print(df[column_name].value_counts())
    else:
        print("\n**NOTE: No data available for {}".format(column_name))

def rawdata_chunker(df, size):
    """Yield successive chunks from df of length size."""
    for i in range(0, len(df), size):
        yield df[i:i + size]

def main():
    """Main function"""

    while True:
        # Get inputs from user on filters to apply
        city, month, day = get_filters()

        # Read the user specified city file and apply filters and logic
        df = load_data(city, month, day)

        # Invoke functions to calculate the respective statistic groups
        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)

        # Check if user wants to see raw data in batches of 5, if so print in chunks of 5
        print('\nWould you like to see raw data? Enter yes or no:')
        input_chunk = input('-->')
        if input_chunk.lower() == 'yes':
            for chunk in rawdata_chunker(df, 5):
                element_list = [chunk.iloc[i,:9] for i in range(0, len(chunk))]
                print(element_list, '\n')
                chunk_continue = input('\nContinue to see raw data? Enter yes or no.\n-->')
                if chunk_continue.lower() != 'yes':
                    break

        # Check if the user would like to restart selection
        print('\nWould you like to restart with a new selection? Enter yes or no:')
        restart = input('-->')
        if restart.lower() != 'yes':
            break

if __name__ == "__main__":
	main()
