from pydantic import BaseModel

class Config(BaseModel):  
    github_database_dir: str = 'github_db.db'
    """
    the path to the sqlite database
    """
    github_token: str = ""
    """
    github tokrn for access github api
    any token either classic or fine-grained access token is accepted
    """
    github_notify_group: dict = {}
    """
    group-to-repo mapping
    format: {group_id: [{repo: str (, commit: bool)(, issue: bool)(, pull_req: bool)(, release: bool)}]}
    """
    github_validate_retries: int = 3
    """
    the max number of retries for validating github token
    """
    github_validate_delay : int = 5
    """
    the delay between each validation retry
    """
    github_del_group_repo : dict = {}
    """
    delete group repo
    format: {group_id: ['repo']}
    """
    github_disable_when_fail : bool = False
    '''
    disable the config when fail to get repo data
    '''
   