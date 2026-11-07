import random

# Define the percentage of vehicles to convert (0.30 = 30%)
PROB_ELECTRIC_CAR = 0.30   # 30% of cars will be electric
PROB_ELECTRIC_BUS = 0.10   # 10% of buses will be electric


def convert_fleet(config):
    """Convert activity-generated routes using the simulation configuration."""
    input_file = config["route-files"]
    output_file = config["route-mista"]
    rng = random.Random(int(config["seed"]))

    print(f"Processing '{input_file}'...")

    # Counters for reporting
    electric_car_count = 0
    electric_bus_count = 0
    total_vehicles = 0

    # 2. Open input file (read) and output file (write)
    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out:
        
        # 3. Read file line by line
        for line in f_in:
            
            number = rng.random()

            if number <= PROB_ELECTRIC_BUS:
                line = line.replace('type="random"', 'type="ElectricBus" color="255,255,0"')
                electric_bus_count += 1
                total_vehicles += 1

            elif PROB_ELECTRIC_BUS < number <= PROB_ELECTRIC_CAR:
                line = line.replace('type="random"', 'type="evehicle" color="255,255,0"')
                electric_car_count += 1
                total_vehicles += 1

            else:
                total_vehicles += 1
                line = line.replace('type="random"', 'type="random" color="255,255,255"')
            
            f_out.write(line)

    # 5. Print summary
    print("-" * 50)
    print("CONVERSION COMPLETED!")
    print(f"Total vehicles processed: {total_vehicles}")
    print(f"Electric cars created:   {electric_car_count}")
    print(f"Electric buses created:  {electric_bus_count}")
    print(f"Output file saved as:    {output_file}")
    print("-" * 50)
