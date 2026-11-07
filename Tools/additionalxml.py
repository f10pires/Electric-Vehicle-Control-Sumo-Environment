import json
import xml.etree.ElementTree as ET
from pathlib import Path


class AdditionalXML:

    def additional_fileupdate(self):

        # ==================================================
        # FILE PATHS
        # ==================================================

        ROOT_PATH = Path(__file__).resolve().parent.parent

        JSON_PATH = ROOT_PATH / "data" / "example1" / "additional.json"

        XML_PATH = ROOT_PATH / "data" / "example1" / "xml" / "additionalTest.add.xml"

        # ==================================================
        # READ JSON
        # ==================================================

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            additional = json.load(f)

        # ==================================================
        # AUXILIARY FUNCTION
        # ==================================================

        def add_params(element, params):

            for key, value in params.items():

                value = str(value).lower() if isinstance(value, bool) else str(value)

                ET.SubElement(
                    element,
                    "param",
                    {"key": key, "value": value}
                )

        # ==================================================
        # CREATE XML ROOT
        # ==================================================

        root = ET.Element("additional")

        # ==================================================
        # 1. VEHICLE TYPES
        # ==================================================

        vehicle_names = {
            "EV": "evehicle",
            "BUS": "ElectricBus",
            "TRUCK": "ElectricTruck"
        }

        for vehicle_id, attributes in additional["vTypes"].items():

            routes = ET.SubElement(root, "routes")

            vehicle_attributes = {
                key: str(value)
                for key, value in attributes.items()
                if key != "params"
            }

            vehicle_attributes["id"] = vehicle_names.get(vehicle_id, vehicle_id)

            vehicle = ET.SubElement(routes, "vType", vehicle_attributes)

            if "params" in attributes:
                add_params(vehicle, attributes["params"])

        # ==================================================
        # 2. BUS STOPS
        # ==================================================

        for stop_id, attributes in additional["BUSSTOP"].items():

            stop_attributes = {
                key: str(value)
                for key, value in attributes.items()
                if key != "emptyColor"
            }

            stop_attributes["id"] = stop_id

            bus_stop = ET.SubElement(root, "busStop", stop_attributes)

            if "emptyColor" in attributes:
                add_params(bus_stop, {"emptyColor": attributes["emptyColor"]})

        # ==================================================
        # 3. PLACES
        # ==================================================

        places = additional["PLACES"]

        # Parking
        for parking_id, attributes in places["Parking"].items():

            parking_attributes = {
                key: str(value)
                for key, value in attributes.items()
            }

            parking_attributes["id"] = parking_id

            ET.SubElement(root, "parkingArea", parking_attributes)

        # Bins
        for bin_id, attributes in places["BINS"].items():

            bin_attributes = {
                key: str(value)
                for key, value in attributes.items()
            }

            bin_attributes["id"] = bin_id

            ET.SubElement(root, "parkingArea", bin_attributes)

        # Charging Stations
        for station_id, attributes in places["EVSEs"].items():

            station_attributes = {
                key: str(value)
                for key, value in attributes.items()
            }

            station_attributes["id"] = station_id

            ET.SubElement(root, "chargingStation", station_attributes)

        # ==================================================
        # 4. WRITE XML
        # ==================================================

        tree = ET.ElementTree(root)

        ET.indent(tree, space="    ")

        XML_PATH.parent.mkdir(parents=True, exist_ok=True)

        tree.write(
            XML_PATH,
            encoding="utf-8",
            xml_declaration=True
        )

        print(f"Additional XML updated: {XML_PATH}")

        return str(XML_PATH)