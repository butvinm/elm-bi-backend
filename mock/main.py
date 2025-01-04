# generated by fastapi-codegen:
#   filename:  swagger.yaml
#   timestamp: 2025-01-03T22:55:45+00:00

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .models import (
    AddWidgetPostRequest,
    Bin,
    Column,
    Dashboard,
    DataSource,
    DataSourceTable,
    DeleteWidgetPostRequest,
    GetDashboardPostRequest,
    GetDashboardsPostResponse,
    GetDataSourceTablesPostRequest,
    GetDataSourceTablesPostResponse,
    Histogram,
    PieChart,
    Range,
    Section,
    SetDataSourcePostRequest,
    Widget,
)

app = FastAPI(
    title="Elm-BI API",
    version="1.0.1",
    description="API for a simplified business intelligence (BI) system.",
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
        dataSource=None,
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


@app.post("/create-dashboard", response_model=Dashboard)
def post_create_dashboard() -> Dashboard:
    """
    Create a new dashboard and return its details.
    """
    dashboard_id = max(dashboards) + 1
    dashboard = Dashboard(
        dashboard_id=dashboard_id,
        title=f"Untitled {dashboard_id}",
        widgets=[],
        dataSource=None,
    )
    dashboards[dashboard_id] = dashboard
    return dashboard


@app.post("/add-widget", response_model=Dashboard)
def post_add_widget(body: AddWidgetPostRequest) -> Dashboard:
    """
    Add a new widget to a dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    dashboards[body.dashboard_id].widgets.append(body.widget)
    return dashboards[body.dashboard_id]


@app.post("/delete-widget", response_model=Dashboard)
def post_delete_widget(body: DeleteWidgetPostRequest) -> Dashboard:
    """
    Remove a widget from a dashboard.
    """
    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    if body.widget_id < 0 or body.widget_id >= len(dashboards[body.dashboard_id].widgets):
        raise HTTPException(status_code=404, detail="Widget not found.")

    dashboards[body.dashboard_id].widgets.pop(body.widget_id)
    return dashboards[body.dashboard_id]


@app.post("/get-data-source-tables", response_model=GetDataSourceTablesPostResponse)
def post_get_data_source_tables(
    body: GetDataSourceTablesPostRequest,
) -> GetDataSourceTablesPostResponse:
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


@app.post("/set-data-source", response_model=Dashboard)
def post_set_data_source(body: SetDataSourcePostRequest) -> Dashboard:
    """
    Configure the data source connection for a specific dashboard.
    """
    if body.dashboard_id == 69:
        raise HTTPException(status_code=400, detail="Password is incorrect")

    if body.dashboard_id == 42:
        raise HTTPException(status_code=400, detail="Not such database")

    if body.dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found.")

    dashboards[body.dashboard_id].dataSource = body.dataSource
    return dashboards[body.dashboard_id]
