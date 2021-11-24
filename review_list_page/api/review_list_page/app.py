import time

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from indico.filters import Filter
from indico import IndicoClient, IndicoConfig
from virga.types import User
from virga.plugins.noct import get_current_user

# from graphene import Schema
# from virga.plugins.graphql import GraphQLRoute
# from .gql import RootQuery

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import async_session
from .database.models.submission_meta import SubmissionMeta, StatusEnum
from .submissions import format_submission, ListSubmissions, CheckPermissions

from .settings import Settings, settings

client = IndicoClient(
    config=IndicoConfig(
        host=settings().indico_host, api_token=settings().indico_api_token
    )
)


class SubmissionFilter(Filter):
    """
    Create a Filter when querying for WorkflowSubmissions.
    Args:
        input_filename (str): submissions with input file names containing this string
        status (str): submissions in this status. Options:
            [PROCESSING, PENDING_REVIEW, PENDING_ADMIN_REVIEW, COMPLETE, FAILED]
        retrieved(bool): Filter submissions on the retrieved flag
    Returns:
        dict containing query filter parameters
    """

    __options__ = ("input_filename", "status", "retrieved")

    def __init__(
        self, input_filename: str = None, status: str = None, retrieved: bool = None
    ):
        kwargs = {
            "inputFilename": input_filename,
            "status": status.upper() if status else status,
            "retrieved": retrieved,
        }

        super().__init__(**kwargs)


PENDING_REVIEW_FILTER = SubmissionFilter(status="PENDING_REVIEW", retrieved=False)

app = FastAPI(root_path="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Origin",
        "Authorization",
        "X-Requested-With",
        "x-xsrftoken",
    ],
)

# I WA
@app.get("/submission/{id}/{status}")
async def submission_update(
    id: int,
    status: str,
    session: AsyncSession = Depends(async_session),
):
    try:
        await session.merge(SubmissionMeta(id=id, status=status))
        await session.commit()
        return {"success": True}
    except:
        return {"success": False}
    finally:
        await session.close()


@app.get("/ping")
def pong():
    """
    Returns HTTP 200 OK when the application is live and ready to receive requests. This
    can be used as a healthcheck endpoint in deployment configurations.
    """
    return True


@app.get("/list")
async def list(
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(settings),
    session: AsyncSession = Depends(async_session),
    q: str = "",
    statusFilter: str = "",
):
    # TODO: remove me once we're properly plugged into app.indico.io
    # current_user.id = 7
    print(current_user)
    perm_check = client.call(CheckPermissions(workflow_ids=settings.workflow_ids))
    permitted_workflow_ids = []
    for workflow in perm_check["workflows"]["workflows"]:
        for user in workflow["dataset"]["users"]:
            if (
                # TODO: remove hard coded value here
                user["userId"] == 7  # current_user.id
                and "add_review" in user["permissions"]
            ):
                permitted_workflow_ids.append(workflow["id"])

    if not q.strip():
        filter = PENDING_REVIEW_FILTER
    else:
        filter = SubmissionFilter(
            status="PENDING_REVIEW", retrieved=False, input_filename=q
        )

    start = time.time()
    submissions = client.call(
        ListSubmissions(
            # workflow_ids=settings.workflow_ids,
            # TODO: sort out why filter by workflow ID is so slow
            filters=filter,
        )
    )
    end = time.time()
    print(f"Time to list submissions: {end - start}")
    submission_by_id = {submission["id"]: submission for submission in submissions}
    results = await session.execute(
        select(SubmissionMeta).filter(
            SubmissionMeta.id.in_(tuple(submission_by_id.keys()))
        )
    )
    for result in results:
        result = result["SubmissionMeta"]
        submission_by_id[result.id]["blocked"] = result.status

    await session.close()

    results = [
        format_submission(submission, settings.indico_host)
        for submission in submission_by_id.values()
    ]

    # Filter by status
    if statusFilter.strip():
        print(set([s["blocked"] for s in results]))
        results = [s for s in results if s["blocked"] == statusFilter]

    return results


@app.get("/")
async def home(settings: Settings = Depends(settings)):
    return {settings.app_name: "Hello World!"}


# Makes use of Noct middleware to fetch the current authenticated user.
@app.get("/user")
async def user_home(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.email}!"}


# # Mounts a Graphene executor with schema to '/graphql'. POST requests to
# # the route get executed while GET requests will render GraphiQL.
# # GraphQLRoute accepts any Graphene Schema object.
# #
# # Read more: https://docs.graphene-python.org/en/stable/types/schema/
# app.add_route("/graphql", GraphQLRoute(schema=Schema(query=RootQuery)))
