import random
import pandas as pd
import csv

# Load encounter table
encounter_table = pd.read_csv('tables/Encounter table - Ark 1.csv')
weather_table = pd.read_csv('tables/year900 - Ark 1.csv')
hazard_table = pd.read_csv('tables/hazard - Ark 1.csv')
treasure_table = pd.read_csv('tables/treasure - Ark 1.csv')

# Function to lookup weather based on month and day
def lookup_weather(month, day):
    # Calculate index for the lookup
    index = (month - 1) * 48 + (day - 1)
    
    # Retrieve weather data for the given month and day
    weather_data = weather_table.iloc[index]
    
    # Extract the required weather parameters
    nameOfTheMonth = weather_data['Month']
    temperature = (weather_data['Low °C'] + weather_data['High °C']) / 2 
    precipitation = weather_data['Precipitation']
    clouds = weather_data['Clouds']
    wind = weather_data['Wind']
    
    return nameOfTheMonth, temperature, precipitation, clouds, wind

def get_user_input_str(prompt, default_choice, choices=None):
    """Function returns a string based on input with exception check, so long as the input is one of a few choices."""
    result = None
    while result is None:
        val = input(prompt).lower()
        if val == '':
            result = default_choice
        elif val == 'help':
            print('You need to select one of these {0}'.format(choices,))        
        elif choices and val not in choices:
            print(' Error: must choose one: {0}'.format(choices,))
        else:
            result = val
    return result

def get_user_input_date(prompt, default_choice):
    """Function returns a valid date based on input with exception check."""
    result = None
    while result is None:
        val = input(prompt)
        if val == '':
            result = default_choice
        elif val == 'help':
            print('You need to enter a valid date in the format "month.day" (e.g., 1.15), max month is 10 and max day is 48.')
        else:
            try:
                month, day = map(int, val.split('.'))
                if 1 <= month <= 10 and 1 <= day <= 48:
                    result = val
                else:
                    print('Error: Invalid date. Month must be between 1 and 10, and day must be between 1 and 48.')
            except ValueError:
                print('Error: Invalid date format. Please enter the date in the format "month.day" (e.g., 1.15)')
    return result


# Function to generate encounter
def generate_encounter(biome):
    # Roll for encounter type
    biome = biome.lower()
    encounter = None
    encounter_type = random.choices(['combat', 'hazard', 'treasure'], weights=[0.6, 0.3, 0.1])[0]
    
    if encounter_type == 'combat':
        biome_encounters = encounter_table[encounter_table['Biome'] == biome]
        biome_encounters = biome_encounters.reset_index(drop=True)
        encounter = random.choice(biome_encounters['Encounter'])
    elif encounter_type == 'hazard':
        biome_hazards = hazard_table[hazard_table['Biome'] == biome]
        random_row = biome_hazards.sample(n=1)
        encounter = random_row[['Hazard', 'DC', 'Consequence']].values.tolist()[0]
    else:
        encounter = random.choice(treasure_table['Treasure'])

    return encounter_type, encounter

#format day
def format_day(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        suffix = suffixes.get(day % 10, "th")
    return f"{day}{suffix}"
def increment_day_and_month(date):
    """Function to increment the day and month, handling month boundaries."""
    month, day = map(int, date.split('.'))
    day += 1
    if day == 49:
        month += 1
        day = 1
    return f"{month}.{day}"

# Function to generate day
def generate_day(date, danger, biome):
    # Generate weather
    month, day = map(int, date.split('.'))
    nameOfTheMonth, temperature, precipitation, clouds, wind = lookup_weather(month, day)
    
    # Generate encounters based on danger level
    encounters = []
    available_times = ['early', 'late', 'night']
    if danger == 'low':
        for _ in range(3):
            if random.random() < 0.1:
                print(biome)
                encounter_time = random.choice(available_times)
                available_times.remove(encounter_time)
                encounter_type, encounter, encounter_time = generate_encounter(biome)
                encounters.append((encounter_type, encounter, encounter_time))
    elif danger == 'medium':
        for _ in range(3):
            if random.random() < 0.2:
                encounter_time = random.choice(available_times)
                available_times.remove(encounter_time)
                encounter_type, encounter, encounter_time = generate_encounter(biome)
                encounters.append((encounter_type, encounter, encounter_time))
    elif danger == 'high':
        for _ in range(3):
            if random.random() < 0.3:
                encounter_time = random.choice(available_times)
                available_times.remove(encounter_time)
                encounter_type, encounter = generate_encounter(biome)              
                encounters.append((encounter_type, encounter, encounter_time))
    
    # Print day information
    print(f"Date: {date}")
    print(f"It is the {format_day(day)} of {nameOfTheMonth} ")
    print(f"Weather: Temperature: {temperature}C, Precipitation: {precipitation}, Clouds: {clouds}, Wind: {wind}")
    if encounters:
        print("Encounters:")
        for i, (encounter_type, encounter, encounter_time) in enumerate(encounters):
            print(f"Encounter {i+1}: Type: {encounter_type}, {encounter}, Time of day: {encounter_time}")
    else:
        print("No encounters today.")
    
      # Ask if user wants to generate the next day
    # And checks if the month is over or year is over, and updates the date
    generate_next_day = input("Keep the same biome? (yes)/(type the biome)/(no to exit): ")
    if generate_next_day.lower() in ['no', 'n']:
        print("Good luck on your next adventure!")
        exit()

    # Increment day and month
    date = increment_day_and_month(date)
    if date == "11.1":
        print("The year is over.")
        exit()
    
    # Change biome if needed and generate the next day
    if generate_next_day.lower() in ['forest', 'plain', 'hill', 'mountain', 'swamp']:
        biome = generate_next_day
    generate_day(date, danger, biome)


def get_user_input_all():
    # Get user inputs
    date = get_user_input_date("Enter month and day separated by a dot (e.g., 1.15): ", default_choice='1.1')
    danger = get_user_input_str("Enter the danger level: ", default_choice = 'low', choices=['low', 'medium', 'high'])
    biome = get_user_input_str("Enter the biome: ", default_choice='forest', choices=['forest', 'plain', 'hill', 'mountain', 'swamp'])
    return date, danger, biome




# Main program
if __name__ == "__main__":
    # Get user inputs
    date, danger, biome = get_user_input_all()
    # Generate day
    generate_day(date, danger, biome)