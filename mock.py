from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Models
class DataSource(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database: str


class Widget(BaseModel):
    widget_id: int
    title: str
    table: str
    x: str


class Dashboard(BaseModel):
    dashboard_id: int
    title: str
    widgets: list[Widget]
    dataSource: DataSource | None = None


class TestDataSourceRequest(BaseModel):
    dataSource: DataSource


class TestDataSourceResponse(BaseModel):
    error: str | None = None


class SetDataSourceRequest(BaseModel):
    dashboard_id: int
    dataSource: DataSource


class AddWidgetRequest(BaseModel):
    dashboard_id: int
    widget: Widget


class DeleteWidgetRequest(BaseModel):
    dashboard_id: int
    widget_id: int


class FetchWidgetDataRequest(BaseModel):
    dashboard_id: int
    widget_id: int


class WidgetDataSections(BaseModel):
    title: str
    percentage: float


class WidgetDataBins(BaseModel):
    range: list[float]
    value: int


class FetchWidgetDataResponse(BaseModel):
    sections: list[WidgetDataSections] | None = None
    bins: list[WidgetDataBins] | None = None


# Handlers
@app.post("/get-dashboards")
def get_dashboards() -> list[Dashboard]:
    return [
        Dashboard(
            dashboard_id=1,
            title="Sample Dashboard",
            widgets=[Widget(widget_id=1, title="Sample Widget", table="table1", x="x-axis")],
        ),
        Dashboard(
            dashboard_id=2,
            title="Another Dashboard",
            widgets=[],
        ),
    ]


@app.post("/create-dashboard")
def create_dashboard() -> Dashboard:
    return Dashboard(dashboard_id=2, title="New Dashboard", widgets=[])


@app.post("/update-dashboard")
def update_dashboard(update: Dashboard) -> Dashboard:
    return update


@app.post("/test-data-source-connection")
def test_data_source_connection(data: TestDataSourceRequest) -> TestDataSourceResponse:
    return TestDataSourceResponse(error=None)


@app.post("/set-data-source")
def set_data_source(data: SetDataSourceRequest) -> Dashboard:
    return Dashboard(dashboard_id=data.dashboard_id, title="Updated Dashboard", widgets=[], dataSource=data.dataSource)


@app.post("/add-widget")
def add_widget(data: AddWidgetRequest) -> Dashboard:
    return Dashboard(dashboard_id=data.dashboard_id, title="Dashboard with new widget", widgets=[data.widget], dataSource=None)


@app.post("/delete-widget")
def delete_widget(data: DeleteWidgetRequest) -> Dashboard:
    return Dashboard(dashboard_id=data.dashboard_id, title="Dashboard with widget deleted", widgets=[], dataSource=None)


@app.post("/fetch-widget-data")
def fetch_widget_data(data: FetchWidgetDataRequest) -> FetchWidgetDataResponse:
    return FetchWidgetDataResponse(sections=[WidgetDataSections(title="Section 1", percentage=75.5)], bins=None)
