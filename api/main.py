import ast
import uuid
from typing import List

import requests
from fastapi import Depends, FastAPI
from starlette.responses import RedirectResponse
from starlette.status import HTTP_201_CREATED

from api.ppd import PPD, PPDFilter, create_ppd, PPDManager

app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})


@app.get("/")
async def root():
    return RedirectResponse(app.docs_url)


@app.post("/populate/{count}", status_code=HTTP_201_CREATED)
def populate(count: int, ppd_manager: PPDManager = Depends(create_ppd)):
    """Populate PPDs based on public available data.

    Arguments:
        count: amount of records that should be added.
        ppd_manager: context manager for processing PPD data.

    Returns:
         List of PPDs.

    """
    response = requests.get(
        "http://prod1.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv", stream=True)
    cnt = 0
    for line in response.iter_lines():
        cnt += 1
        row = ast.literal_eval(line.decode("utf-8"))
        try:
            duration = int(row[7])
        except ValueError:
            continue

        with ppd_manager as ppd:
            ppd.save(
                PPD(
                    id=uuid.UUID(row[0]),
                    price=int(row[1]),
                    date_of_transfer=row[2],
                    postcode=row[3],
                    property_type=row[4],
                    is_residential=row[5],
                    estate_type=row[6],
                    duration=duration,
                    paon=row[8],
                    saon=row[9],
                    street=row[10],
                    locality=row[11],
                    town=row[12],
                    district=row[13],
                    category_type=row[14],
                    record_status=row[15]
                )
            )

        if cnt == count:
            break


@app.get("/get", response_model=List[PPD])
def get(ppd_filter: PPDFilter = Depends(), ppd_manager: PPDManager = Depends(create_ppd)):
    """Extract PPDs.

    Arguments:
        ppd_filter: object that contains all available filters, that user can specify in query parameters.
        ppd_manager: context manager for processing PPD data.

    Returns:
         List of PPDs.

    """
    with ppd_manager as ppd:
        return ppd.get(ppd_filter)


@app.get("/truncate")
def truncate(ppd_manager: PPDManager = Depends(create_ppd)):
    """Truncate all data from PPD table.

        Arguments:
            ppd_manager: context manager for processing PPD data.

        Returns:
             None.

        """
    with ppd_manager as ppd:
        return ppd.clear_table_ppd()
