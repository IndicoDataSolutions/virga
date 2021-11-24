import enum
from typing import List, Dict, Union
from indico.client.request import PagedRequest, GraphQLRequest
from indico.filters import SubmissionFilter


class CheckPermissions(GraphQLRequest):
    query = """
    query CheckWorkflowPermissions(
        $workflowIds: [Int]
    )
    {
        workflows(workflowIds: $workflowIds){
            workflows {
                id  
                dataset {
                    users {
                        userId
                        permissions
                    }
                }
            }
        }
    }
    """

    def __init__(
        self,
        *,
        workflow_ids: List[int] = None,
    ):
        super().__init__(
            self.query,
            variables={
                "workflowIds": workflow_ids,
            },
        )

    def process_response(self, response):
        return super().process_response(response)


class ListSubmissions(PagedRequest):
    """
    List all Submissions visible to the authenticated user by most recent.
    Supports pagination (limit becomes page_size)
    Options:
        submission_ids (List[int]): Submission ids to filter by
        workflow_ids (List[int]): Workflow ids to filter by
        filters (SubmissionFilter or Dict): Submission attributes to filter by
        limit (int, default=1000): Maximum number of Submissions to return
        orderBy (str, default="ID"): Submission attribute to filter by
        desc: (bool, default=True): List in descending order
    Returns:
        List[Submission]: All the found Submission objects
        If paginated, yields results one at a time
    """

    query = """
        query ListSubmissions(
            $submissionIds: [Int],
            $workflowIds: [Int],
            $filters: SubmissionFilter,
            $limit: Int,
            $orderBy: SUBMISSION_COLUMN_ENUM,
            $desc: Boolean,
            $after: Int
        ){
            submissions(
                submissionIds: $submissionIds,
                workflowIds: $workflowIds,
                filters: $filters,
                limit: $limit
                orderBy: $orderBy,
                desc: $desc,
                after: $after
            ){
                submissions {
                    id
                    datasetId
                    workflowId
                    status
                    inputFile
                    inputFilename
                    resultFile
                    deleted
                    retrieved
                    errors
                    createdAt
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    """

    def __init__(
        self,
        *,
        submission_ids: List[int] = None,
        workflow_ids: List[int] = None,
        filters: Union[Dict, SubmissionFilter] = None,
        limit: int = 1000,
        order_by: str = "ID",
        desc: bool = True,
    ):
        super().__init__(
            self.query,
            variables={
                "submissionIds": submission_ids,
                "workflowIds": workflow_ids,
                "filters": filters,
                "limit": limit,
                "orderBy": order_by,
                "desc": desc,
            },
        )

    def process_response(self, response):
        return [
            s for s in super().process_response(response)["submissions"]["submissions"]
        ]


def format_submission(submission, host):
    submission[
        "review_link"
    ] = f"https://{host}/review/queues/{submission['workflowId']}/submission/{submission['id']}"
    submission["blocked"] = submission.get("blocked", "UNBLOCKED")

    if isinstance(submission["blocked"], enum.Enum):
        submission["blocked"] = submission["blocked"].value

    return submission
