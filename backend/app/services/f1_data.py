import fastf1
import pandas as pd
from app.core.config import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
fastf1.Cache.enable_cache(settings.fastf1_cache_path)


def get_session(year: int, round_number: int, session_type: str):
    session = fastf1.get_session(year, round_number, session_type)
    session.load()
    return session


def get_session_results(year: int, round_number: int, session_type: str) -> list[dict]:
    session = get_session(year, round_number, session_type)
    results = session.results
    output = []
    for _, row in results.iterrows():
        output.append({
            "position": int(row.get("Position", 0)) if pd.notna(row.get("Position")) else None,
            "driver_number": str(row.get("DriverNumber", "")),
            "driver_code": str(row.get("Abbreviation", "")),
            "full_name": str(row.get("FullName", "")),
            "team": str(row.get("TeamName", "")),
            "points": float(row.get("Points", 0)) if pd.notna(row.get("Points")) else 0,
            "status": str(row.get("Status", "")),
            "grid_position": int(row.get("GridPosition", 0)) if pd.notna(row.get("GridPosition")) else None,
        })
    return output


def get_driver_laps(year: int, round_number: int, session_type: str, driver_code: str) -> list[dict]:
    session = get_session(year, round_number, session_type)
    laps = session.laps.pick_drivers(driver_code)
    output = []
    for _, lap in laps.iterrows():
        lap_time = lap.get("LapTime")
        lap_time_seconds = lap_time.total_seconds() if pd.notna(lap_time) else None
        output.append({
            "lap_number": int(lap.get("LapNumber", 0)),
            "lap_time_seconds": lap_time_seconds,
            "compound": str(lap.get("Compound", "")),
            "tyre_life": int(lap.get("TyreLife", 0)) if pd.notna(lap.get("TyreLife")) else None,
            "is_personal_best": bool(lap.get("IsPersonalBest", False)),
            "sector_1": lap.get("Sector1Time").total_seconds() if pd.notna(lap.get("Sector1Time")) else None,
            "sector_2": lap.get("Sector2Time").total_seconds() if pd.notna(lap.get("Sector2Time")) else None,
            "sector_3": lap.get("Sector3Time").total_seconds() if pd.notna(lap.get("Sector3Time")) else None,
        })
    return output


def compare_drivers(year: int, round_number: int, session_type: str, driver1: str, driver2: str) -> dict:
    session = get_session(year, round_number, session_type)
    laps1 = session.laps.pick_drivers(driver1).pick_quicklaps()
    laps2 = session.laps.pick_drivers(driver2).pick_quicklaps()

    def summarise(laps, code):
        if laps.empty:
            return {"driver": code, "error": "No clean laps found"}
        fastest = laps.pick_fastest()
        return {
            "driver": code,
            "fastest_lap_seconds": fastest["LapTime"].total_seconds(),
            "average_lap_seconds": laps["LapTime"].dt.total_seconds().mean(),
            "total_laps": len(laps),
            "compounds_used": laps["Compound"].unique().tolist(),
        }

    return {
        "session": f"{year} Round {round_number} {session_type}",
        "driver1": summarise(laps1, driver1),
        "driver2": summarise(laps2, driver2),
    }


def get_qualifying_results(year: int, round_number: int) -> list[dict]:
    session = get_session(year, round_number, "Q")
    results = session.results
    output = []
    for _, row in results.iterrows():
        def safe_time(col):
            val = row.get(col)
            return val.total_seconds() if pd.notna(val) else None

        output.append({
            "position": int(row.get("Position", 0)) if pd.notna(row.get("Position")) else None,
            "driver_code": str(row.get("Abbreviation", "")),
            "full_name": str(row.get("FullName", "")),
            "team": str(row.get("TeamName", "")),
            "q1_time": safe_time("Q1"),
            "q2_time": safe_time("Q2"),
            "q3_time": safe_time("Q3"),
        })
    return output


def get_tyre_strategy(year: int, round_number: int) -> list[dict]:
    session = get_session(year, round_number, "R")
    output = []

    for driver in session.drivers:
        try:
            driver_laps = session.laps.pick_drivers(driver)
            info = session.get_driver(driver)
            driver_code = info["Abbreviation"]
            stints = []
            current_compound = None
            stint_start = None

            for _, lap in driver_laps.iterrows():
                compound = lap.get("Compound")
                lap_num = int(lap.get("LapNumber", 0))
                if compound != current_compound:
                    if current_compound is not None:
                        stints.append({
                            "compound": current_compound,
                            "start_lap": stint_start,
                            "end_lap": lap_num - 1,
                            "length": lap_num - stint_start,
                        })
                    current_compound = compound
                    stint_start = lap_num

            if current_compound is not None:
                stints.append({
                    "compound": current_compound,
                    "start_lap": stint_start,
                    "end_lap": int(driver_laps["LapNumber"].max()),
                    "length": int(driver_laps["LapNumber"].max()) - stint_start + 1,
                })

            output.append({
                "driver_code": driver_code,
                "stints": stints,
                "total_stints": len(stints),
            })
        except Exception:
            continue

    return output

def get_driver_standings(year: int, up_to_round: int) -> list[dict]:
    """
    Calculates drivers championship standings up to a specific round.
    
    Fetches results for rounds 1 through up_to_round and accumulates the points for each driver.

    Uses parallel fetching to speed up the process.

    Args:
        year: Championship year
        up_to_round: Calculate standings after this round number

    Returns:
        List of drivers sorted by total WDC points, from highest to lowest.
    """

    #dictionary to accumulate the points per driver
    #key: driver code, value: dict w/ name, team, points, wins.

    standings = {}

    def fetch_round(round_number):
        #fetches results for a single round and runs in thread.

        try:
            return round_number, get_session_results(year, round_number, "R")
        except Exception:
            #if a round fails to load, skips it rather than crashing everything down hehe
            return round_number, []
        
    #fetch up to 3 rounds simultaneously 
    #fetch more than 3 concurrent FastF1 requests can cause rate limiting.
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(fetch_round, r): r
            for r in range(1, up_to_round + 1)
        }
        
        for future in as_completed(futures):
            round_number, results = future.result()
            for driver in results:
                code = driver["driver_code"]
                if not code:
                    continue
                if code not in standings:
                    standings[code] = {
                        "driver_code": code,
                        "full_name": driver["full_name"],
                        "team": driver["team"],
                        "points": 0.0,
                        "wins": 0,
                        "podiums": 0,
                        "rounds_completed": 0,
                    }
                standings[code]["points"] += driver["points"]
                standings[code]["rounds_completed"] += 1
                if driver["position"] == 1:
                    standings[code]["wins"] += 1
                if driver["position"] is not None and driver["position"] <= 3:
                    standings[code]["podiums"] += 1

    #sort by points descending, then wins as tiebreaker
    sorted_standings = sorted(
        standings.values(),
        key=lambda x: (x["points"], x["wins"]),
        reverse=True,
    )
    
    #add championship position
    for i, driver in enumerate(sorted_standings):
        driver["position"] = i + 1

    return sorted_standings