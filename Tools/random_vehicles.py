from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from sumolib.net import readNet


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "config" / "vehicles.json"
DEFAULT_COUNT = 1
DEFAULT_ENERGY_MAX = 40.0
DEFAULT_MAX_ATTEMPTS = 10_000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate random EV definitions for config/vehicles.json."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the project config file.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path where vehicles.json will be written.",
    )
    parser.add_argument(
        "--count",
        type=positive_int,
        default=DEFAULT_COUNT,
        help="Number of vehicles to generate.",
    )
    parser.add_argument(
        "--vehicle-prefix",
        default="ev",
        help="Prefix used for generated vehicle ids.",
    )
    parser.add_argument(
        "--route-prefix",
        default="Route",
        help="Prefix used for generated route ids.",
    )
    parser.add_argument(
        "--vehicle-type",
        default="evehicle",
        help="SUMO vehicle type assigned to each generated vehicle.",
    )
    parser.add_argument(
        "--vehicle-class",
        default=None,
        help="SUMO permission class used to filter edges. Defaults to passenger, or bus for bus vehicle types.",
    )
    parser.add_argument(
        "--energy-max",
        type=positive_float,
        default=DEFAULT_ENERGY_MAX,
        help="Emax value written for each vehicle.",
    )
    parser.add_argument(
        "--min-route-length",
        type=non_negative_float,
        default=0.0,
        help="Minimum shortest-path length, in meters, between origin and destination.",
    )
    parser.add_argument(
        "--max-attempts",
        type=positive_int,
        default=DEFAULT_MAX_ATTEMPTS,
        help="Maximum random origin/destination attempts before failing.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed. Defaults to config['seed'] when available.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated JSON instead of writing the output file.",
    )
    return parser


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (PROJECT_ROOT / candidate).resolve()


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def seed_from_config(config: dict[str, Any], explicit_seed: int | None) -> int:
    if explicit_seed is not None:
        return explicit_seed

    raw_seed = config.get("seed", 42)
    try:
        return int(raw_seed)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid seed in config: {raw_seed!r}") from exc


def infer_vehicle_class(vehicle_type: str, explicit_class: str | None) -> str:
    if explicit_class:
        return explicit_class

    if "bus" in vehicle_type.lower():
        return "bus"

    return "passenger"


def get_net_path(config: dict[str, Any]) -> Path:
    try:
        return resolve_path(config["net-file"])
    except KeyError as exc:
        raise KeyError("Missing required config key: 'net-file'") from exc


def get_candidate_edges(net: Any, vehicle_class: str) -> list[Any]:
    return [
        edge
        for edge in net.getEdges()
        if not edge.getID().startswith(":")
        and edge.getFunction() in ("", "normal")
        and edge.allows(vehicle_class)
    ]


def route_exists(
    net: Any,
    origin: Any,
    destination: Any,
    vehicle_class: str,
    min_route_length: float,
) -> bool:
    if origin.getID() == destination.getID():
        return False

    path, route_length = net.getShortestPath(
        origin,
        destination,
        vClass=vehicle_class,
    )

    return bool(path) and route_length >= min_route_length


def choose_route(
    net: Any,
    edges: list[Any],
    rng: random.Random,
    vehicle_class: str,
    min_route_length: float,
    max_attempts: int,
) -> tuple[str, str]:
    for _ in range(max_attempts):
        origin, destination = rng.sample(edges, 2)

        if route_exists(net, origin, destination, vehicle_class, min_route_length):
            return origin.getID(), destination.getID()

    raise RuntimeError(
        "Could not find a valid random route. "
        "Try reducing --min-route-length or increasing --max-attempts."
    )


def build_route_id(route_prefix: str, index: int, count: int) -> str:
    if count == 1:
        return route_prefix
    return f"{route_prefix}{index}"


def clean_number(value: float) -> int | float:
    if value.is_integer():
        return int(value)
    return value


def generate_vehicles(
    net_path: Path,
    count: int,
    vehicle_prefix: str,
    route_prefix: str,
    vehicle_type: str,
    vehicle_class: str,
    energy_max: float,
    seed: int,
    min_route_length: float,
    max_attempts: int,
) -> dict[str, dict[str, Any]]:
    net = readNet(str(net_path))
    edges = get_candidate_edges(net, vehicle_class)

    if len(edges) < 2:
        raise RuntimeError(
            f"Need at least two usable edges for vehicle class '{vehicle_class}'. "
            f"Found {len(edges)}."
        )

    rng = random.Random(seed)
    vehicles: dict[str, dict[str, Any]] = {}

    for index in range(1, count + 1):
        vehicle_id = f"{vehicle_prefix}{index}"
        initial_edge, destination_id = choose_route(
            net,
            edges,
            rng,
            vehicle_class,
            min_route_length,
            max_attempts,
        )

        vehicles[vehicle_id] = {
            "type": vehicle_type,
            "Emax": clean_number(energy_max),
            "initial_route": {
                "destination_id": destination_id,
                "route_id": build_route_id(route_prefix, index, count),
                "initial_edge": initial_edge,
            },
        }

    return vehicles


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=4)
        output_file.write("\n")


def main() -> int:
    args = build_parser().parse_args()

    config_path = resolve_path(args.config)
    output_path = resolve_path(args.output)
    config = load_config(config_path)
    seed = seed_from_config(config, args.seed)
    vehicle_class = infer_vehicle_class(args.vehicle_type, args.vehicle_class)

    vehicles = generate_vehicles(
        net_path=get_net_path(config),
        count=args.count,
        vehicle_prefix=args.vehicle_prefix,
        route_prefix=args.route_prefix,
        vehicle_type=args.vehicle_type,
        vehicle_class=vehicle_class,
        energy_max=args.energy_max,
        seed=seed,
        min_route_length=args.min_route_length,
        max_attempts=args.max_attempts,
    )

    if args.dry_run:
        print(json.dumps(vehicles, indent=4))
        return 0

    write_json(output_path, vehicles)

    print("-" * 50)
    print("RANDOM VEHICLES GENERATED")
    print(f"Vehicles        : {len(vehicles)}")
    print(f"Vehicle type    : {args.vehicle_type}")
    print(f"Vehicle class   : {vehicle_class}")
    print(f"Seed            : {seed}")
    print(f"Output file     : {output_path}")
    print("-" * 50)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
