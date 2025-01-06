# generated by fastapi-codegen:
#   filename:  swagger.yaml
#   timestamp: 2025-01-04T18:03:51+00:00

from __future__ import annotations

from typing import Union

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    AddWidgetPostRequest,
    Bin,
    Column,
    Dashboard,
    DataSource,
    DataSourceTable,
    DeleteWidgetPostRequest,
    Error,
    GetDashboardPostRequest,
    GetDashboardsPostResponse,
    GetDataSourceTablesPostRequest,
    GetDataSourceTablesPostResponse,
    Histogram,
    PieChart,
    Range,
    Section,
    Widget,
)

app = FastAPI(
    title="Elm-BI API",
    version="1.0.1",
    description="API for a simplified business intelligence (BI) system.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


dashboards = {
    0: Dashboard(
        dashboard_id=0,
        title="Sample Dashboard",
        widgets=[
            Widget(
                PieChart(
                    widget_type="PieChart",
                    title="Some Pie Chart",
                    table="HumanResources.Employees",
                    x_column="Gender",
                    sections=[
                        Section(title="Man", percentage=89),
                        Section(title="Woman", percentage=10),
                        Section(title="Other", percentage=1),
                    ],
                ),
            ),
            Widget(
                Histogram(
                    widget_type="Histogram",
                    title="Some Histogram",
                    table="HumanResources.Employees",
                    x_column="Age",
                    bins=[Bin(range=Range(left=23, right=30), value=80), Bin(range=Range(left=31, right=None), value=20)],
                ),
            ),
        ],
        dataSource=DataSource(
            host="localhost",
            port=5432,
            username="postgres",
            password="postgres",
            database="postgres",
        ),
    )
}


@app.post("/get-dashboards", response_model=GetDashboardsPostResponse)
def post_get_dashboards() -> GetDashboardsPostResponse:
    """
    Retrieve a list of all created dashboards.
    """
    return GetDashboardsPostResponse(list(dashboards.values()))


@app.post("/get-dashboard", response_model=Dashboard)
def post_get_dashboard(body: GetDashboardPostRequest) -> Dashboard:
    """
    Retrieve details of a specific dashboard by its ID, with optional data recalculation for widgets.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    return dashboards[body.dashboard_id]


@app.post(
    "/create-or-update-dashboard",
    response_model=Dashboard,
    responses={
        "201": {"model": Dashboard},
        "400": {"model": Error},
    },
)
def post_create_or_update_dashboard(body: Dashboard, response: Response) -> Union[Dashboard, Error]:
    """
    Updates the specified dashboard if dashboard_id exists; otherwise, creates a new one. Use dashboard_id=-1 to explicitly create a new dashboard.
    """
    if body.dashboard_id == 69:
        raise HTTPException(status_code=400, detail="Bad data source credentials.")
    elif body.dashboard_id in dashboards:
        dashboards[body.dashboard_id] = body
        response.status_code = 200
    else:
        dashboard_id = max(dashboards.keys()) + 1
        body.dashboard_id = dashboard_id
        dashboards[body.dashboard_id] = body
        response.status_code = 201

    return body


@app.post("/add-widget", response_model=Dashboard, responses={"404": {"model": Error}})
def post_add_widget(body: AddWidgetPostRequest) -> Union[Dashboard, Error]:
    """
    Add a new widget to a dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    dashboards[body.dashboard_id].widgets.append(body.widget)
    return dashboards[body.dashboard_id]


@app.post("/delete-widget", response_model=Dashboard, responses={"404": {"model": Error}})
def post_delete_widget(body: DeleteWidgetPostRequest) -> Union[Dashboard, Error]:
    """
    Remove a widget from a dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    if body.widget_id < 0 or body.widget_id >= len(dashboards[body.dashboard_id].widgets):
        raise HTTPException(status_code=404, detail="Widget not found.")

    dashboards[body.dashboard_id].widgets.pop(body.widget_id)
    return dashboards[body.dashboard_id]


@app.post(
    "/get-data-source-tables",
    response_model=GetDataSourceTablesPostResponse,
    responses={"400": {"model": Error}, "404": {"model": Error}},
)
def post_get_data_source_tables(
    body: GetDataSourceTablesPostRequest,
) -> Union[GetDataSourceTablesPostResponse, Error]:
    """
    Retrieve the list of tables and their columns from the data source linked to a dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    return GetDataSourceTablesPostResponse(
        [
            DataSourceTable(
                name="HumanResources.Employees",
                columns=[
                    Column(name="Age", dataType="int"),
                    Column(name="Gender", dataType="string"),
                ],
            ),
            DataSourceTable(
                name="HumanResources.Candidates",
                columns=[
                    Column(name="Age", dataType="int"),
                    Column(name="Department", dataType="string"),
                ],
            ),
        ]
    )
