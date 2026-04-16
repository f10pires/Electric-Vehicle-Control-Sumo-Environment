from pathlib import Path
import csv

class Register :
    def __init__(self,id : str):
        self.id = id
        self.registration_init()
        return
    
    def registration_init(self) :   
        base_dir = Path(__file__).resolve().parent.parent 
        self.pasta_results = base_dir / "sumo" / "results"
        self.pasta_results.mkdir(parents=True, exist_ok=True) 
        
        self.arquivo_csv = self.pasta_results / f"{self.id}.csv"

        self.setup_results_and_headers()
        
        self.buffer = []
        return
    

    def setup_results_and_headers(self):

        # Remove only this EV's CSV file (if it exists)
        if self.arquivo_csv.exists():
            self.arquivo_csv.unlink()

        cabecalho = [
            "== ID ==",
            "== Velocity (km/h) ==",
            "== Current route ==",
            "== Distance traveled (m) ==",
            "== Destination ==",
            "== Distance to destination (m) ==",
            "== Type ==",
            "== Battery level (%) ==",
            "== Timestamp =="
        ]

        # Create file and write header
        with open(self.arquivo_csv, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(cabecalho)
        
        return
    

    def accumulate_information(self, informations: dict,TIME):

        self.buffer.append([
            self.id,
            informations.get("speedKm"),
            informations.get("edge"),
            informations.get("total_dist"),
            informations.get("dest"),
            informations.get("dist_to_dest"),
            informations.get("vType"),
            informations.get("soc"),
            TIME
        ])

        if len(self.buffer) >= 100:
            self.register()
        
        return
    
    def register(self):

        with open(self.arquivo_csv, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(self.buffer)
        self.buffer = []
        return
    
    def close(self):
        if self.buffer:
            self.register()