"""Garmin Connect MCP server."""

import logging
from datetime import date, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import GarminClient

logger = logging.getLogger(__name__)

mcp = FastMCP("garmin-connect")

_client: GarminClient | None = None


def _get_client() -> GarminClient:
    global _client
    if _client is None:
        _client = GarminClient()
    return _client


def _today() -> str:
    return date.today().isoformat()


def _days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


# ---------------------------------------------------------------------------
# Health & wellness
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_stats(cdate: str | None = None) -> dict[str, Any]:
    """Get daily stats (steps, calories, distance, floors, etc.) for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(
        f"usersummary-service/usersummary/daily/{display_name}",
        calendarDate=cdate or _today(),
    )


@mcp.tool()
async def get_user_summary(cdate: str | None = None) -> dict[str, Any]:
    """Get user activity summary for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(
        f"usersummary-service/usersummary/daily/{display_name}",
        calendarDate=cdate or _today(),
    )


@mcp.tool()
async def get_steps_data(cdate: str | None = None) -> list[dict[str, Any]]:
    """Get step-by-step data throughout the day.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(
        f"wellness-service/wellness/dailySummaryChart/{display_name}",
        date=cdate or _today(),
    )


@mcp.tool()
async def get_heart_rates(cdate: str | None = None) -> dict[str, Any]:
    """Get heart rate data for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(
        f"wellness-service/wellness/dailyHeartRate/{display_name}",
        date=cdate or _today(),
    )


@mcp.tool()
async def get_sleep_data(cdate: str | None = None) -> dict[str, Any]:
    """Get sleep data for a given date (duration, stages, score).

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(
        f"wellness-service/wellness/dailySleepData/{display_name}",
        date=cdate or _today(),
        nonSleepBufferMinutes=60,
    )


@mcp.tool()
async def get_stress_data(cdate: str | None = None) -> dict[str, Any]:
    """Get stress data throughout a given day.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(
        f"wellness-service/wellness/dailyStress/{cdate or _today()}",
    )


@mcp.tool()
async def get_body_battery(
    startdate: str | None = None,
    enddate: str | None = None,
) -> list[dict[str, Any]]:
    """Get body battery readings over a date range.

    Args:
        startdate: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
        enddate: End date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(
        "wellness-service/wellness/bodyBattery/reports/daily",
        startDate=startdate or _days_ago(7),
        endDate=enddate or _today(),
    )


@mcp.tool()
async def get_hrv_data(cdate: str | None = None) -> dict[str, Any] | None:
    """Get heart rate variability data for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(f"hrv-service/hrv/{cdate or _today()}")


@mcp.tool()
async def get_spo2_data(cdate: str | None = None) -> dict[str, Any]:
    """Get SpO2 (blood oxygen) data for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(
        f"wellness-service/wellness/daily/spo2/{cdate or _today()}",
    )


@mcp.tool()
async def get_respiration_data(cdate: str | None = None) -> dict[str, Any]:
    """Get respiration rate data for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(
        f"wellness-service/wellness/daily/respiration/{cdate or _today()}",
    )


@mcp.tool()
async def get_body_composition(
    startdate: str | None = None,
    enddate: str | None = None,
) -> dict[str, Any]:
    """Get body composition data (weight, BMI, body fat, etc.) over a date range.

    Args:
        startdate: Start date in YYYY-MM-DD format. Defaults to 30 days ago.
        enddate: End date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(
        "weight-service/weight/dateRange",
        startDate=startdate or _days_ago(30),
        endDate=enddate or _today(),
    )


@mcp.tool()
async def get_weigh_ins(
    startdate: str | None = None,
    enddate: str | None = None,
) -> dict[str, Any]:
    """Get weigh-in entries over a date range.

    Args:
        startdate: Start date in YYYY-MM-DD format. Defaults to 30 days ago.
        enddate: End date in YYYY-MM-DD format. Defaults to today.
    """
    return await _get_client().get(
        "weight-service/weight/dateRange",
        startDate=startdate or _days_ago(30),
        endDate=enddate or _today(),
    )


# ---------------------------------------------------------------------------
# Training & fitness
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_training_readiness(cdate: str | None = None) -> dict[str, Any]:
    """Get training readiness score and breakdown for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    d = cdate or _today()
    return await _get_client().get(f"metrics-service/metrics/trainingreadiness/{d}")


@mcp.tool()
async def get_training_status(cdate: str | None = None) -> dict[str, Any]:
    """Get training status (load, peak training, etc.) for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    d = cdate or _today()
    return await _get_client().get(f"metrics-service/metrics/trainingstatus/aggregated/{d}")


@mcp.tool()
async def get_race_predictions() -> dict[str, Any]:
    """Get predicted race finish times (5k, 10k, half marathon, marathon)."""
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(f"metrics-service/metrics/racepredictions/latest/{display_name}")


@mcp.tool()
async def get_max_metrics(cdate: str | None = None) -> dict[str, Any]:
    """Get VO2 max and other fitness metrics for a given date.

    Args:
        cdate: Date in YYYY-MM-DD format. Defaults to today.
    """
    d = cdate or _today()
    return await _get_client().get(f"metrics-service/metrics/maxmet/daily/{d}/{d}")


@mcp.tool()
async def get_personal_record() -> list[dict[str, Any]]:
    """Get personal records (best times, longest runs, etc.)."""
    client = _get_client()
    display_name = await client.get_display_name()
    return await client.get(f"personalrecord-service/personalrecord/prs/{display_name}")


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_activities(
    start: int = 0,
    limit: int = 20,
    activitytype: str | None = None,
) -> list[dict[str, Any]]:
    """Get a list of recent activities.

    Args:
        start: Offset from most recent activity (0 = most recent).
        limit: Number of activities to return (max 1000).
        activitytype: Optional filter. One of: cycling, running, swimming,
            multi_sport, fitness_equipment, hiking, walking, other.
    """
    params: dict[str, Any] = {"start": start, "limit": limit}
    if activitytype:
        params["activityType"] = activitytype
    return await _get_client().get(
        "activitylist-service/activities/search/activities",
        **params,
    )


@mcp.tool()
async def get_activities_by_date(
    startdate: str | None = None,
    enddate: str | None = None,
    activitytype: str | None = None,
) -> list[dict[str, Any]]:
    """Get activities within a date range.

    Args:
        startdate: Start date in YYYY-MM-DD format. Defaults to 30 days ago.
        enddate: End date in YYYY-MM-DD format. Defaults to today.
        activitytype: Optional filter. One of: cycling, running, swimming,
            multi_sport, fitness_equipment, hiking, walking, other.
    """
    params: dict[str, Any] = {
        "startDate": startdate or _days_ago(30),
        "endDate": enddate or _today(),
    }
    if activitytype:
        params["activityType"] = activitytype
    return await _get_client().get(
        "activitylist-service/activities/search/activities",
        **params,
    )


@mcp.tool()
async def get_last_activity() -> dict[str, Any] | None:
    """Get the most recent activity."""
    result = await _get_client().get(
        "activitylist-service/activities/search/activities",
        start=0,
        limit=1,
    )
    if isinstance(result, list) and result:
        return result[0]
    return None


@mcp.tool()
async def get_activity(activity_id: str) -> dict[str, Any]:
    """Get detailed data for a specific activity.

    Args:
        activity_id: The numeric activity ID.
    """
    return await _get_client().get(f"activity-service/activity/{activity_id}")


@mcp.tool()
async def get_activity_details(activity_id: str) -> dict[str, Any]:
    """Get granular time-series details for a specific activity (GPS, HR, pace, etc.).

    Args:
        activity_id: The numeric activity ID.
    """
    return await _get_client().get(
        f"activity-service/activity/{activity_id}/details",
        maxChartSize=2000,
        maxPolylineSize=4000,
    )


@mcp.tool()
async def get_activity_splits(activity_id: str) -> dict[str, Any]:
    """Get lap/split data for a specific activity.

    Args:
        activity_id: The numeric activity ID.
    """
    return await _get_client().get(f"activity-service/activity/{activity_id}/splits")


@mcp.tool()
async def get_activity_weather(activity_id: str) -> dict[str, Any]:
    """Get weather conditions recorded during a specific activity.

    Args:
        activity_id: The numeric activity ID.
    """
    return await _get_client().get(f"activity-service/activity/{activity_id}/weather")


# ---------------------------------------------------------------------------
# Devices & profile
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_devices() -> list[dict[str, Any]]:
    """Get all registered Garmin devices for the account."""
    return await _get_client().get("device-service/deviceregistration/devices")


@mcp.tool()
async def get_user_profile() -> dict[str, Any]:
    """Get the user's Garmin Connect profile."""
    return await _get_client().get("userprofile-service/socialProfile")


@mcp.tool()
async def get_unit_system() -> dict[str, Any]:
    """Get the user's measurement unit preferences (metric vs imperial)."""
    return await _get_client().get("userprofile-service/userprofile/user-settings")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
