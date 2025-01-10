# generated by fastapi-codegen:
#   filename:  swagger.yaml
#   timestamp: 2025-01-10T19:28:55+00:00

from __future__ import annotations

import random
import string
from typing import Optional, Union

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .models import (AddWidgetPostRequest, Column, Dashboard, DashboardCreate,
                     DashboardDigest, DataSource, DataSourceTable,
                     DeleteDashboardPostRequest, DeleteDashboardPostResponse,
                     DeleteWidgetPostRequest, Error, GetDashboardPostRequest,
                     GetDashboardsPostRequest, GetDashboardsPostResponse,
                     Histogram, HistogramData, PieChart, PieChartData,
                     PieChartDatum, UpdateDashboardPostRequest, Widget)

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
                    widget_id=0,
                    title="Some Pie Chart",
                    table="HumanResources.Employees",
                    data_column="Gender",
                    data=PieChartData(
                        [
                            PieChartDatum(title="Women", count=1337),
                            PieChartDatum(title="Man", count=999),
                            PieChartDatum(title="Other", count=666),
                        ]
                    ),
                ),
            ),
            Widget(
                Histogram(
                    widget_type="Histogram",
                    widget_id=1,
                    title="Some Histogram",
                    table="HumanResources.Employees",
                    data_column="Age",
                    data=HistogramData([random.random() * 100 - 50 for _ in range(1000)]),
                ),
            ),
        ],
        dataSource=DataSource(
            host="localhost",
            port=5432,
            username="postgres",
            password="postgres",
            database="postgres",
            tables=[
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
            ],
        ),
    )
}


@app.post("/get-dashboards", response_model=GetDashboardsPostResponse)
def post_get_dashboards(body: GetDashboardsPostRequest) -> GetDashboardsPostResponse:
    """
    Retrieve a list of all created dashboards.
    """
    return GetDashboardsPostResponse(
        [DashboardDigest(dashboard_id=dashboard.dashboard_id, title=dashboard.title) for dashboard in dashboards.values()],
    )


@app.post("/get-dashboard", response_model=Dashboard)
def post_get_dashboard(body: GetDashboardPostRequest) -> Dashboard:
    """
    Retrieve details of a specific dashboard by its ID, with optional data recalculation for widgets.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    return dashboards[body.dashboard_id]


@app.post(
    "/create-dashboard",
    response_model=None,
    responses={"201": {"model": Dashboard}, "400": {"model": Error}},
)
def post_create_dashboard(body: DashboardCreate, response: Response) -> Optional[Union[Dashboard, Error]]:
    """
    Create a new dashboard. dashboard_id is replaced with a new one generated by the server.
    """
    if body.title == "test data source error":
        raise HTTPException(status_code=400, detail="Bad data source credentials.")

    dashboard = Dashboard(
        dashboard_id=random.randint(0, 666),
        title=body.title,
        widgets=[],
        dataSource=DataSource(
            host=body.dataSource.host,
            port=body.dataSource.port,
            username=body.dataSource.username,
            password=body.dataSource.password,
            database=body.dataSource.database,
            tables=[
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
            ],
        ),
    )
    dashboards[dashboard.dashboard_id] = dashboard

    response.status_code = 201
    return dashboard


@app.post(
    "/update-dashboard",
    response_model=Dashboard,
    responses={"400": {"model": Error}, "404": {"model": Error}},
)
def post_update_dashboard(body: UpdateDashboardPostRequest) -> Union[Dashboard, Error]:
    """
    Update the dashboard.
    """
    if body.title == "test data source error":
        raise HTTPException(status_code=400, detail="Bad data source credentials.")

    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    dashboards[body.dashboard_id].title = body.title
    dashboards[body.dashboard_id].dataSource.host = body.dataSource.host
    dashboards[body.dashboard_id].dataSource.port = body.dataSource.port
    dashboards[body.dashboard_id].dataSource.username = body.dataSource.username
    dashboards[body.dashboard_id].dataSource.password = body.dataSource.password
    dashboards[body.dashboard_id].dataSource.database = body.dataSource.database

    return dashboards[body.dashboard_id]


@app.post(
    "/delete-dashboard",
    response_model=DeleteDashboardPostResponse,
    responses={"404": {"model": Error}},
)
def post_delete_dashboard(
    body: DeleteDashboardPostRequest,
) -> Union[DeleteDashboardPostResponse, Error]:
    """
    Delete the dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    dashboards.pop(body.dashboard_id)
    return DeleteDashboardPostResponse(
        [DashboardDigest(dashboard_id=dashboard.dashboard_id, title=dashboard.title) for dashboard in dashboards.values()],
    )


@app.post("/add-widget", response_model=Dashboard, responses={"404": {"model": Error}})
def post_add_widget(body: AddWidgetPostRequest) -> Union[Dashboard, Error]:
    """
    Add a new widget to a dashboard, widget_id is replaced with a new one generated by the server.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    if body.widget.root.widget_type == "PieChart":
        widget = Widget(
            PieChart(
                widget_type="PieChart",
                widget_id=random.randint(0, 666),
                title=body.widget.root.title,
                table=body.widget.root.table,
                data_column=body.widget.root.data_column,
                data=PieChartData(
                    [
                        PieChartDatum(title=random.choice(string.ascii_letters), count=random.randint(0, 1000))
                        for _ in range(random.randint(0, 5))
                    ]
                ),
            )
        )
    elif body.widget.root.widget_type == "Histogram":
        widget = Widget(
            Histogram(
                widget_type="Histogram",
                widget_id=random.randint(0, 666),
                title=body.widget.root.title,
                table=body.widget.root.table,
                data_column=body.widget.root.data_column,
                data=HistogramData([random.random() * 100 - 50 for _ in range(1000)]),
            )
        )
    else:
        raise HTTPException(status_code=404, detail="Unknown widget_type")

    dashboards[body.dashboard_id].widgets.append(widget)
    return dashboards[body.dashboard_id]


@app.post("/delete-widget", response_model=Dashboard, responses={"404": {"model": Error}})
def post_delete_widget(body: DeleteWidgetPostRequest) -> Union[Dashboard, Error]:
    """
    Remove a widget from a dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    for i, widget in enumerate(dashboards[body.dashboard_id].widgets):
        if widget.root.widget_id == body.widget_id:
            dashboards[body.dashboard_id].widgets.pop(i)
            return dashboards[body.dashboard_id]

    raise HTTPException(status_code=404, detail="Widget not found.")
