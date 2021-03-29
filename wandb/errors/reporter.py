import json
import os
from typing import Any, Dict, Optional
import uuid

from humbug.consent import HumbugConsent
from humbug.report import Reporter

# TODO: Replace with Bugout tokens
HUMBUG_TOKEN = "f5e24e68-b3d6-4390-b8f9-9a9a438f5c3e"
HUMBUG_KB_ID = "92ba38ef-dce5-431f-818e-cf7974efc41c"

WANDB_REPORT_CONFIG_FILE_NAME = "reporting_config.json"


def get_wandb_repo_dir() -> Optional[str]:
    """
    Return W&B direcotry if exists.
    """
    repo_path = os.path.join(os.getcwd(), "wandb")
    config_file_path = os.path.join(repo_path, "settings")

    if not os.path.isfile(config_file_path):
        return None

    return repo_path


def save_reporting_config(consent: bool, client_id: Optional[str] = None) -> None:
    """
    Allow or disallow W&B reporting.
    """
    reporting_config = {}

    repo_dir = get_wandb_repo_dir()
    if repo_dir is None:
        raise Exception(
            "Config report file not found, use 'wandb init' to initialize a new repository"
        )

    config_report_path = os.path.join(repo_dir, WANDB_REPORT_CONFIG_FILE_NAME)
    if os.path.isfile(config_report_path):
        try:
            with open(config_report_path, "r") as ifp:
                reporting_config = json.load(ifp)
        except Exception:
            pass

    if client_id is not None and reporting_config.get("client_id") is None:
        reporting_config["client_id"] = client_id

    if reporting_config.get("client_id") is None:
        reporting_config["client_id"] = str(uuid.uuid4())

    reporting_config["consent"] = consent

    try:
        with open(config_report_path, "w") as ofp:
            json.dump(reporting_config, ofp)
    except Exception:
        pass


def get_reporting_config() -> Dict[str, Any]:
    reporting_config = {}
    repo_dir = get_wandb_repo_dir()
    if repo_dir is not None:
        config_report_path = os.path.join(repo_dir, WANDB_REPORT_CONFIG_FILE_NAME)
        try:
            if not os.path.exists(config_report_path):
                client_id = str(uuid.uuid4())
                reporting_config["client_id"] = client_id
                save_reporting_config(True, client_id)
            else:
                with open(config_report_path, "r") as ifp:
                    reporting_config = json.load(ifp)
        except Exception:
            pass
    return reporting_config


def wandb_consent_from_reporting_config_file() -> bool:
    reporting_config = get_reporting_config()
    return reporting_config.get("consent", False)


session_id = str(uuid.uuid4())
client_id = get_reporting_config().get("client_id")

wandb_consent = HumbugConsent(wandb_consent_from_reporting_config_file)
wandb_reporter = Reporter(
    name="wandb",
    consent=wandb_consent,
    client_id=client_id,
    session_id=session_id,
    bugout_token=HUMBUG_TOKEN,
    bugout_journal_id=HUMBUG_KB_ID,
)
