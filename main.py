"""
Anonymous Bot: A Slack app that handles anonymous messaging.
Copyright (C) 2025 Paso Robles Vacation Rentals

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/gpl-3.0-standalone.html.
"""

import json
import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Format log messages
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s]: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# Create a logging handler for console output
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


data_path = Path(__file__).resolve().parent / 'data'
if not data_path.exists():
    data_path.mkdir()

# Create directory for logs if it doesn't exist
log_path = data_path / 'logs'
if not log_path.exists():
    log_path.mkdir()

# Create a logging handler for file output
fh = TimedRotatingFileHandler(log_path / 'latest.log', when='midnight', interval=1, backupCount=30)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
fh.suffix = "%Y%m%d.log"  # Custom suffix for rotated log files
fh.extMatch = r'^\d{8}\.log$'  # Regular expression pattern for matching rotated log files
logger.addHandler(fh)

logger.info("""
Anonymous Bot Copyright (C) 2025  Paso Robles Vacation Rentals
This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For details https://www.gnu.org/licenses/gpl-3.0-standalone.html
""")


def save_settings(settings: dict, filename='settings.json'):
    with open(data_path / filename, 'w') as f:
        json.dump(settings, f, indent=4)


def default_settings() -> dict:
    return {
        "Channels": [
            {
                'name': 'Report Box',
                'id': 'C1234567890',
            },
        ],
    }


def load_settings(filename='settings.json') -> dict:
    try:
        with open(data_path / filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f'Settings file not found. Creating new settings file at {data_path / filename}')
        save_settings(default_settings(), filename)
        input('Press Enter to continue...')
        return {}


settings = load_settings()
cd
# Initialize the Slack app
# SLACK_BOT_TOKEN set with environment variable
slack = App()

divider = {
    'type': 'divider'
}


def home_page() -> dict:
    blocks = []
    title = {
        'type': 'header',
        'text': {
            'type': 'plain_text',
            'text': f'Hello!',
            'emoji': True
        }
    }
    report_box = {
        'type': 'actions',
        'elements': [
            {
                'type': 'button',
                'text': {
                    'type': 'plain_text',
                    'text': ':memo: Report Anonymously',
                    'emoji': True
                },
                'action_id': 'home_navigation',
                'value': 'open_report_modal'
            }
        ]
    }
    footer = {
        'type': 'context',
        'elements': [
            {
                'type': 'mrkdwn',
                'text': f'Anonymous Bot Made with :heart: by Anthony DeGarimore\n'
                        f'Review the source code at https://github.com/Paso-Robles-Vacation-Rentals/Anonymous-Bot'
            }
        ]
    }

    blocks.append(title)
    blocks.append(divider)
    blocks.append(report_box)
    blocks.append(divider)
    blocks.append(footer)

    view = {'type': 'home',
            'callback_id': 'home_page',
            'blocks': blocks}
    return view


def _get_report_modal_blocks() -> list[dict]:
    recipient_options = []
    for recipient in settings['Channels']:
        recipient_options.append({
            "text": {
                "type": "plain_text",
                "text": recipient['name'],
                "emoji": True
            },
            "value": recipient['id']
        })

    send_to_block = {
        "type": "input",
        'block_id': 'send_to',
        "label": {
            "type": "plain_text",
            "text": "Send my report to:",
            "emoji": True
        },

        "element": {
            "type": "static_select",
            "action_id": "send_to_select",
            "placeholder": recipient_options[0]['text'],
            "options": recipient_options
        }
    }
    report_text_block = {
        "type": "input",
        'block_id': 'report_text',
        "element": {
            "type": "plain_text_input",
            "multiline": True,
            "action_id": "plain_text_input-action"
        },
        "label": {
            "type": "plain_text",
            "text": "Label",
            "emoji": True
        }
    }

    blocks = [send_to_block, report_text_block]
    return blocks


def get_report_modal() -> dict:
    blocks = _get_report_modal_blocks()
    modal = {
        'type': 'modal',
        'callback_id': 'submit_report',
        'submit': {
            'type': 'plain_text',
            'text': 'Submit',
            'emoji': True
        },
        'close': {
            'type': 'plain_text',
            'text': 'Cancel',
            'emoji': True
        },
        'title': {
            'type': 'plain_text',
            'text': 'Report Anonymously',
            'emoji': True
        },
        'blocks': blocks
    }
    return modal


def get_report_message_blocks(title: str, message: str) -> list[dict]:
    elements = []
    title = {
        "type": "rich_text_section",
        "elements": [
            {
                "type": "text",
                "text": title,
                "style": {
                    "bold": True
                }
            },
            {
                "type": "text",
                "text": "\n"
            }
        ]
    }
    message = {
        "type": "rich_text_quote",
        "elements": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    blocks = [{
        "type": "rich_text",
        "elements": [
            title,
            message
        ]
    }]
    return blocks


@slack.event("app_home_opened")
def update_home_tab(event):
    user_id = event["user"]
    try:
        slack.client.views_publish(
            user_id=user_id,
            view=home_page()
        )
    except SlackApiError as e:
        logger.error(f"Error publishing home view: {e.response['error']}")


@slack.action('home_navigation')
def home_navigation(ack, body, client):
    if body['actions'][0]['value'] == 'open_report_modal':
        try:
            ack()
            client.views_open(
                trigger_id=body["trigger_id"],
                user_id=body['user']['id'],
                view=get_report_modal(),
            )
        except SlackApiError as e:
            logger.error(f"Error opening report modal: {e.response['error']}")


@slack.view('submit_report')
def submit_report(ack, body, client, view):
    recipient = view['state']['values']['send_to']['send_to_select']['selected_option']['value']
    message = view['state']['values']['report_text']['plain_text_input-action']['value']
    try:
        report_blocks = get_report_message_blocks("New Report Recieved", message)
        client.chat_postMessage(channel=recipient, text=message, blocks=report_blocks)
        ack()
        confirmation_blocks = get_report_message_blocks("Report Sent", message)
        client.chat_postMessage(channel=body['user']['id'], text=f"Report Sent:\n{message}", blocks=confirmation_blocks)
    except SlackApiError as e:
        logger.error(f"Error sending message: {e.response['error']}")
        return


if __name__ == "__main__":
    logger.info("Starting Anonymous Bot...")
    # SLACK_APP_TOKEN set with environment variable
    SocketModeHandler(slack, logger=logger).start()
