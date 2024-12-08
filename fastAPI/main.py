from fastapi import FastAPI
from forecast.routes import router as forecast_router
from scenario.routes import router as scenario_router
from reservoir.routes import router as reservoir_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="FastAPI Model Mediator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000","http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the forecast routes
app.include_router(forecast_router, prefix="/forecast")
app.include_router(scenario_router, prefix="/scenario")
app.include_router(reservoir_router,prefix = "/reservoir")
@app.get("/")
async def root():
    return {"message": "Welcome to the Reservoir Management API"}
