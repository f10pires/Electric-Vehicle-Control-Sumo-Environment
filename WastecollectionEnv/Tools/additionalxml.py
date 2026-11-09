import xml.etree.ElementTree as ET
from pathlib import Path


class AdditionalXML:
    def __init__(self, additional: dict, bins: dict, evses: dict, landfills: dict):
        self.additional = additional
        self.bins = bins
        self.evses = evses
        self.landfills = landfills

    def additional_fileupdate(self, xml_path: str | Path):
        """Generate SUMO infrastructure from the loaded scenario data."""
        additional = self.additional

        def add_element(parent, tag, element_id, attributes):
            values = attributes.copy()
            params = values.pop("params", {}).copy()

            if "emptyColor" in values:
                params["emptyColor"] = values.pop("emptyColor")
            if "max_capacity_kg" in values:
                params["max_capacity_kg"] = values.pop("max_capacity_kg")

            values["id"] = element_id
            element = ET.SubElement(
                parent, tag, {key: str(value) for key, value in values.items()}
            )
            for key, value in params.items():
                value = str(value).lower() if isinstance(value, bool) else str(value)
                ET.SubElement(element, "param", {"key": key, "value": value})

        root = ET.Element("additional")
        vehicle_names = {
            "EV": "evehicle",
            "BUS": "ElectricBus",
            "TRUCK": "ElectricTruck",
        }
        for vehicle_id, attributes in additional["vTypes"].items():
            routes = ET.SubElement(root, "routes")
            add_element(
                routes, "vType", vehicle_names.get(vehicle_id, vehicle_id), attributes
            )

        for stop_id, attributes in additional["BUSSTOP"].items():
            add_element(root, "busStop", stop_id, attributes)

        for parking_id, attributes in additional["PLACES"]["Parking"].items():
            add_element(root, "parkingArea", parking_id, attributes)

        place_groups = (
            (self.bins, "parkingArea"),
            (self.evses, "chargingStation"),
            (self.landfills, "parkingArea"),
        )
        for places, tag in place_groups:
            for place_id, attributes in places.items():
                add_element(root, tag, place_id, attributes)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")
        xml_path = Path(xml_path)
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"Additional XML updated: {xml_path}")
        return str(xml_path)
