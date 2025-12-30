import os
from jira import JIRA
import logging

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self):
        self.server = os.getenv("JIRA_SERVER")
        self.user = os.getenv("JIRA_USER")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.jira = None
        
        if self.server and self.user and self.api_token:
            try:
                # Strictly use token_auth (for PAT) as requested
                self.jira = JIRA(server=self.server, token_auth=self.api_token)
                # Test connection to ensure auth works
                self.jira.myself()
                logger.info(f"Connected to Jira at {self.server} (PAT)")
            except Exception as e:
                logger.error(f"Failed to connect to Jira: {e}")
                self.jira = None

        else:
            logger.warning("Jira credentials not fully configured.")

    def get_ticket(self, ticket_number):
        if not self.jira:
            logger.warning("Jira client not initialized.")
            return None
        
        try:
            issue = self.jira.issue(ticket_number)
            return issue
        except Exception as e:
            # check if it is 404
            if "404" in str(e):
                return None # Not found
            logger.error(f"Error fetching ticket {ticket_number}: {e}")
            raise e
