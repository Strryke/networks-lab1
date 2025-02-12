from typing import Union

from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def read_root():
    return {"fuck this shit": "Worlhis is  asfa sdf asu a asdf ssf asfper cool!!"}



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

def main() -> None:
    """Invoke the entrypoint function of the script."""
    uvicorn.run("lab1.main:app", host="0.0.0.0", reload=True)


if __name__ == "__main__":
    main()