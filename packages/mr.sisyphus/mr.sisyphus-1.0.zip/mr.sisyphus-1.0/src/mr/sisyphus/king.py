import os
import argparse
import getpass
import logging
import pkg_resources
from ConfigParser import SafeConfigParser

import github3

logger = logging.getLogger("mr.sisyphus")

def find_base():
    path = os.getcwd()
    while path:
        if os.path.exists(os.path.join(path, 'mr.sisyphus.cfg')):
            break
        old_path = path
        path = os.path.dirname(path)
        if old_path == path:
            path = None
            break
    if path is None:
        raise IOError("mr.sisyphus.cfg not found")
    return path

class King(object):

    def create_token(self):
        gh = github3.GitHub()
        auth = None
        while auth is None:
            username = raw_input("Github Username: ")
            password = getpass.getpass("Github password: ")
            try:
                auth = gh.authorize(username, password, scopes=["user", "repo"], note="Mr. Sisyphus")
            except:
                logger.exception("Couldn't create oauth token")
        return auth
    
    def get_or_update_token_from_config(self):
        config = self.get_configuration()
        if config.has_option("sisyphus", "token"):
            token = config.get("sisyphus", "token", None)
        else:
            token = self.create_token().token
            config.set("sisyphus", "token", token)
            config_file_path = os.path.join(find_base(), "mr.sisyphus.cfg")
            with open(config_file_path, 'wb') as configfile:
                config.write(configfile)
        return token
    
    def get_configuration(self):
        config = os.path.join(find_base(), "mr.sisyphus.cfg")
        parser = SafeConfigParser()
        parser.read(config)
        return parser
    
    def get_team(self, team_id):
        all_teams = self.github.organization(self.org).iter_teams()
        for team in all_teams:
            if team.name == team_id:
                return team
    
    def synchronise_members(self, from_team, to_team):
        from_members = self.get_team(from_team).iter_members()
        from_members = set(member.login for member in from_members)

        to_members = self.get_team(to_team).iter_members()
        to_members = set(member.login for member in to_members)
        
        members_to_add = from_members - to_members
        members_to_remove = to_members - from_members
        
        logger.info("Adding %i members to %s: %s" % (len(members_to_add), to_team, ", ".join(members_to_add)))
        logger.info("Removing %i members from %s: %s" % (len(members_to_remove), to_team, ", ".join(members_to_remove)))
        if not self.dry_run:
            to_team = self.get_team(to_team)
            from_team = self.get_team(from_team)
            for member in members_to_add:
                if not to_team.add_member(member):
                    logger.error("Couldn't add %s" % member)
            for member in members_to_remove:
                if not to_team.remove_member(member):
                    logger.error("Couldn't add %s" % member)
    
    def synchronise_repositories(self, from_team, to_team):
        to_repos = self.get_team(to_team).iter_repos()
        to_repos = set(repo.full_name for repo in to_repos)

        from_repos = self.get_team(from_team).iter_repos()
        from_repos = set(repo.full_name for repo in from_repos)
        
        to_add = to_repos - from_repos
        
        logger.info("Adding %i repositories to %s: %s" % (len(to_add), from_team, ", ".join(to_add)))
        if not self.dry_run:
            to_team = self.get_team(to_team)
            from_team = self.get_team(from_team)
            for repo in to_add:
                if not from_team.add_repo(repo):
                    logger.error("Couldn't add %s" % member)
                else:
                    to_team.remove_repo(repo)
    
    def __call__(self, **kwargs):
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(ch)
        
        self.parser = argparse.ArgumentParser()
        version = pkg_resources.get_distribution("mr.sisyphus").version
        self.parser.add_argument('-v', '--version',
                    action='version',
                    version='mr.sisyphus %s' % version)
        self.parser.add_argument("-n", help="Dry run, just print the calls that would be made", action="store_true")
        
        args = self.parser.parse_args()
        
        config = self.get_configuration()
        self.dry_run = args.n
        self.github = github3.GitHub(token=self.get_or_update_token_from_config())
        self.org = config.get("sisyphus", "organization")
        from_team = config.get("sisyphus", "developer_team")
        to_team = config.get("sisyphus", "stub_team")
        self.synchronise_members(from_team, to_team)
        self.synchronise_repositories(from_team, to_team)
        
king = King()
