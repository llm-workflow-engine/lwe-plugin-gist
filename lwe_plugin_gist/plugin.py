import os
import json
import requests
import urllib.parse
from lwe.core.plugin import Plugin

VISIBILITY_MAP = {
    "public": True,
    "secret": False,
}


class Gist(Plugin):
    """
    Post content to a GitHub Gist.
    """

    def default_config(self):
        return {
            "defaults": {
                "file_extension": "md",
                "visibility": "public",
            },
            "include_raw_link": False,
            "exclude_system_messages": False,
        }

    def setup(self):
        self.log.info(f"Setting up Gist plugin, running with backend: {self.backend.name}")
        self.github_token = os.environ.get("GITHUB_GIST_ACCESS_TOKEN")
        self.default_file_extension = self.config.get("plugins.gist.defaults.file_extension")
        self.default_visibility = self.config.get("plugins.gist.defaults.visibility")
        self.include_raw_link = self.config.get("plugins.gist.include_raw_link")
        self.exclude_system_messages = self.config.get("plugins.gist.exclude_system_messages")

    def content_from_conversation(self, conversation):
        content_parts = []
        for message in conversation["messages"]:
            if self.exclude_system_messages and message["role"] == "system":
                continue
            role = message["role"].upper()
            message_content = message["message"]
            if isinstance(message_content, dict):
                message_content = f"```json\n{json.dumps(message_content, indent=2)}\n```"
            section = f"## {role}\n\n{message_content}"
            content_parts.append(section)
        return "\n\n---\n\n".join(content_parts)

    def create_gist(self, content, description, file_name, visibility):
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "description": description,
            "public": visibility,
            "files": {
                file_name: {
                    "content": content
                }
            }
        }
        response = requests.post('https://api.github.com/gists', headers=headers, json=data)
        if response.status_code == 201:
            return response.json()['html_url'], response.json()['id']
        else:
            raise ValueError(f"GitHub API error: {response.status_code} {response.json().get('message')}")

    def build_raw_url(self, gist_id, file_name):
        escaped_file_name = urllib.parse.quote(file_name)
        return f"https://gist.githubusercontent.com/raw/{gist_id}/{escaped_file_name}"

    def parse_args(self, conversation_data, args):
        visibility = self.default_visibility
        file_extension = self.default_file_extension
        description = conversation_data["conversation"]["title"]
        try:
            visibility, file_extension, description = args.split(maxsplit=2)
        except ValueError:
            try:
                visibility, file_extension = args.split()
            except ValueError:
                if args:
                    visibility = args
        return visibility, file_extension, description

    def command_gist(self, args):
        """
        Post a conversation to https://gist.github.com

        Arguments:
            visibility: Optional, one of: public, secret (default: public)
            extension: Optional, extension of the file (default: md)
            title: Optional, custom title, if not provided, conversation title will be used.

        Examples:
            # Use the defaults.
            {COMMAND}
            # An secret gist.
            {COMMAND} secret
            # Custom everything
            {COMMAND} public yaml My custom title
        """
        success, conversation_data, user_message = self.backend.get_conversation()
        if not success:
            return success, conversation_data, user_message
        if not conversation_data:
            return False, None, "No current conversation"
        visibility, file_extension, description = self.parse_args(conversation_data, args)
        if visibility in VISIBILITY_MAP:
            visibility = VISIBILITY_MAP[visibility]
        else:
            return False, None, f"Invalid visibility: {visibility}"
        file_name = f"{description}.{file_extension}"
        content = self.content_from_conversation(conversation_data)
        try:
            gist_url, gist_id = self.create_gist(content, description, file_name, visibility)
        except Exception as e:
            return False, None, str(e)

        user_message_parts = [f"Gist URL: {gist_url}"]
        if self.include_raw_link:
            raw_url = self.build_raw_url(gist_id, file_name)
            user_message_parts.append(f"Raw URL: {raw_url}")

        return True, gist_url, "\n".join(user_message_parts)
