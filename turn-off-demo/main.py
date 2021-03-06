import os
import yaml
import base64
from googleapiclient import discovery


# Constants
MSG_TURN_OFF_SERVER = "Turn off"


def turn_off_demo(event, context):
    pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
    if pubsub_message != MSG_TURN_OFF_SERVER:
        return "Not turning off the demo server."

    project = os.environ["GCP_PROJECT"]  # Google Cloud Project ID
    user = event["attributes"]["user"]  # User who creates the PR
    branch = event["attributes"]["branch"]  # The head branch of the PR
    # The latest commit sha of the PR
    commit_sha = event["attributes"]["commit_sha"]
    release_name = "-".join([user, branch]).replace(
        "_", "-").replace("/", "-").lower()[:25]

    service = discovery.build("cloudbuild", "v1", cache_discovery=False)
    with open("cloudbuild.yaml", "r") as stream:
        cloudbuild_yaml = yaml.load(stream, Loader=yaml.SafeLoader)

    build_body = {
        "substitutions": {
            "COMMIT_SHA": commit_sha,
            "_RELEASE_NAME": release_name,
            "_DATABASE_INSTANCE_NAME": os.environ["DATABASE_INSTANCE_NAME"],
        }
    }
    build_body.update(cloudbuild_yaml)

    # Create the build
    print("Starting to create build for commit {}".format(commit_sha))
    service.projects().builds().create(projectId=project, body=build_body).execute()
