from typing import Annotated
from fastapi import FastAPI, Header, Path, Query
from pydantic import BaseModel

app = FastAPI()

class BaseReqBody(BaseModel):
    username: str
    password: str
    client_id: str
    grant_type: str

class Alert(BaseModel):
    uuid: str
    id: int
    name: str
    severity: str
    type: str
    status: str
    sla: str
    description: str
    closure_notes: str
    analysis_recommendation: str
    escalation_path: str
    affected_endpoint: str
    client_uuid: str
    client_name: str
    fc_account_id: int
    fc_client_name: str
    created_date: str
    modified_date: str
    self_fc_account_id: int
    mssp_fc_account_id: int

class tokenResponse(BaseModel):
    access_token: str | None = "v4vkjpAOm9685D6M6MxQBBsw03ss9M"
    expires_in: int | None = 36000
    token_type: str | None = "Bearer"
    scope: str | None = "openid"
    refresh_token: str | None = "CtJcRtF4YeK4poMi94Vew0qjxMrxeb"


@app.post("/api/v1/oauth/token/", response_model=tokenResponse)
async def root(req_body: BaseReqBody) -> tokenResponse:

    resp = tokenResponse()

    return resp

@app.get("/socaasAPI/v1/alert")
async def root(
    Authorization: Annotated[str | None, Header()] = None,
    created_date_from: Annotated[str | None, Query()] = None,
    created_date_to: Annotated[str | None, Query()] = None,
):
    print(f"created_date_from={created_date_from}")
    print(f"created_date_to={created_date_to}")
    
    if Authorization:
        print(Authorization)
        if Authorization.startswith('Bearer'):
            print(Authorization.split('Bearer')[1])
        else:
            print('header starts no Bearer')
    else:
        print('No AUth header')

    alert = Alert (
        uuid="3a90b295-c110-4333-a361-469789cb5b16",
        id=43871,
        name="open api test 0003",
        severity="Medium",
        type="",
        status="Confirmed",
        sla="Met",
        description="open api test 0003",
        closure_notes="",
        analysis_recommendation="",
        escalation_path="",
        affected_endpoint="",
        client_uuid="b25a02ee-8423-42ec-ae15-5ee29ffaf910",
        client_name="fc-socaas-04@master.com",
        fc_account_id=1692344,
        fc_client_name="",
        created_date="1970-01-01T00:00:00Z",
        modified_date="2024-02-28T00:22:32.723408Z",
        self_fc_account_id=1692344,
        mssp_fc_account_id=1692344
    )

    resp = {
        "result": {
            "status": 0,
            "errorArr": [],
            "data": [alert]
        }
    }

    return resp

@app.get("/socaasAPI/v1/alert/{alert_uuid}")
async def root(alert_uuid: Annotated[str, Path()],
               Authorization: Annotated[str | None, Header()]  = None):
    
    if Authorization:
        print(Authorization)
        if Authorization.startswith('Bearer'):
            print(Authorization.split('Bearer')[1])
        else:
            print('header starts no Bearer')
    else:
        print('No AUth header')

    return {alert_uuid: f"{alert_uuid} found."}
