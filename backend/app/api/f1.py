from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import f1_data

router = APIRouter()

@router.get("/sessions/{year}/{round_number}/{session_type}/results")
def session_results(
    year: int,
    round_number: int,
    session_type: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get race results from a specific session which requires authentication

    Ex. /api/v1/f1/sessions/2023/1/R/results
    Returns finishing positions, points, and status for all drivers.
    """
    try:
        return f1_data.get_session_results(year, round_number, session_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sessions/{year}/{round_number}/{session_type}/laps/{driver_code}")
def driver_laps(
    year: int,
    round_number: int,
    session_type: str,
    driver_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Gets all the lap times for a specific driver in the session which also requires authentication.

    Ex. /api/v1/f1/sessions/2023/1/R/laps/VER
    Returns the lap times, tyre compound, sector times for every lap
    """

    try:
        #converts the driver code to uppercase 
        return f1_data.get_driver_laps(year, round_number, session_type, driver_code.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sessions/{year}/{round_number}/{session_type}/compare/{driver1}/{driver2}")
def compare_drivers(
    year: int,
    round_number: int,
    session_type: str,
    driver1: str,
    driver2: str,
    current_user: User = Depends(get_current_user),
):
    """
    Compares the two drivers chosen head to head in the same selected session.
    Requires authentication.

    Ex. /api/v1/f1/sessions/2023/1/R/compare/VER/HAM
    Returns fastest lap time, average lap time, and tyre compounds for each of the driver
    """

    try:
        return f1_data.compare_drivers(
            year,
            round_number,
            session_type,
            driver1.upper(),
            driver2.upper(),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sessions/{year}/{round_number}/qualifying")
def qualifying_results(
    year: int,
    round_number: int,
    current_user: User = Depends(get_current_user),
):
    """
    Captures the qualifying results for a race weekend. Requires authentication.

    Ex. /api/v1/f1/sessions/2023/1/qualifying
    Returns Q1, Q2, Q3 times and their final grid positions
    """
    
    try:
        return f1_data.get_qualifying_results(year, round_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sessions/{year}/{round_number}/strategy")
def tyre_strategy(
    year: int,
    round_number: int,
    current_user: User = Depends(get_current_user)
):
    """
    Gets all the tyre strategy for all the drivers in the race. Requires authentication.
    Ex. /api/v1/f1/sessions/2023/1/strategy
    Returns each of the drivers stints - compound, start lap, end lap, stint length.
    """
    try:
        return f1_data.get_tyre_strategy(year, round_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/standings/{year}/{up_to_round}")
def driver_standings(
    year: int,
    up_to_round: int,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the drivers championship standings up to a specific round.
    Requires authentication.

    Ex. /api/v1/f1/standings/2023/5
    Returns drivers sorted by points after the first 5 rounds
    """

    try:
        return f1_data.get_driver_standings(year, up_to_round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))