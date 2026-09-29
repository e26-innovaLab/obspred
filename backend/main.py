from fastapi import FastAPI

app= FastAPI(title="Observatorio Predictivo API")

@app.get("/")
def root():
    return{"status":"ok","message":"Backend en funcionamiento"}

@app.get("/api/v1/health")
def health():
    return{"status":"healthy"}
