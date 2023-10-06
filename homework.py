from http import HTTPStatus
from json import JSONDecodeError
import logging
import os
import requests
import sys
import time
from typing import Any, Union

from dotenv import load_dotenv

import telegram

from exceptions import (
    DoNotSendToBotException,
    EndpointResponseException,
)


load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


# Dict of possible homework\s statuses.
# Unable to translate because of tests:(
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> list[str]:
    """
    Checking if any of the required tokens is absent.
    Return list of absent tokens (or empty if it's ok).
    """
    # Simple dict to get varnames to each critical token.
    tokens = dict(
        PRACTICUM_TOKEN=PRACTICUM_TOKEN,
        TELEGRAM_TOKEN=TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID,
    )

    failed_list = []
    for token_name, token in tokens.items():
        if not token or token is None:
            failed_list.append(token_name)

    return failed_list


def send_message(bot: telegram.Bot, message: str) -> None:
    """
    Try to send message via bot.
    Either raise exception or log in case of success.
    """
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

    except telegram.TelegramError as error:
        raise DoNotSendToBotException(f'Unable to send message: {error}')

    else:
        logging.debug(msg='Bot has sent message.')


def get_api_answer(timestamp: int) -> dict[str, Any]:
    """
    Send request to endpoint, returns dict made from json.
    Keys:
        - current_date: int -> time of response (since unix era);
        - homeworks: list[dict[str, str]] -> data structure of all homeworks
          from chosen date forward.
    """
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=dict(from_date=timestamp))
        # Check if endpoint returns not OK.
        if response.status_code != HTTPStatus.OK:
            raise EndpointResponseException(
                'Endpoint response returned wrong status: '
                + f'{response.status_code}',
            )
        # Get json from response.
        response_json = response.json()
        # Convert it into dictionary
        resulting_dict = dict(
            homeworks=response_json.get('homeworks'),
            current_date=response_json.get('current_date'),
        )
        return resulting_dict

    except EndpointResponseException as error:
        raise error

    except requests.RequestException as error:
        raise Exception(f'Unexpected request error: {error}')

    except JSONDecodeError:
        raise Exception('No valid json found in response.')

    except Exception as error:
        raise Exception(f'Unexpected error: {error}')


def check_response(response: dict[str, Any]) -> bool:
    """
    Check if response is in correct form.
    Expected dictionary with:
        - key 'current_date' -> int,
        - key 'homeworks' -> list (possibly empty).
    """
    try:
        if not isinstance(response, dict):
            raise TypeError('Response recieved should be dict '
                            + f'not {type(response)}')

        if not ('current_date' in response.keys()
                and 'homeworks' in response.keys()):
            raise KeyError(
                'One or more of expected keys are absent in API '
                + f'response. Keys recieved: {response.keys()}',
            )

        if (date_type := type(response.get('current_date'))) is not int:
            raise TypeError('Unexpected type of date in response: '
                            + f'{date_type.__name__}. '
                            + 'int expected.')

        if type(response.get('homeworks')) is not list:
            raise TypeError('Cannot get list of homeworks.')

        return True

    except (TypeError, KeyError) as error:
        raise error

    except Exception as error:
        raise Exception(f'Unexpected error: {error}')


def parse_status(homework: dict) -> Union[str, None]:
    """
    Format messsage string from json's dict.
    Uses 2 keys: homework_name and status.
    If either of keys is absent or status differs
    from preordained returns None.
    """
    if not ('homework_name' in homework.keys()
            and 'status' in homework.keys()):
        raise KeyError('One or more keys is missing'
                       + 'in homework\'s dictionary.')

    homework_name = homework.get('homework_name')
    verdict = homework.get('status')

    if verdict not in HOMEWORK_VERDICTS.keys():
        raise ValueError(f'Unexpected status of homework: {verdict}')

    verdict = HOMEWORK_VERDICTS.get(verdict)
    # Another untranslateable line:(
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """
    Basic bot logic.
    Check for required tokens, interrupt if at least one is absent.
    Run bot in perma-loop, every RETRY_PERIOD sec ask API for an update.
    """
    if len(tokens := check_tokens()) > 0:
        logging.critical(msg=f'Environment var not found: {tokens}')
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0

    # We don't want to send one after another identical errors.
    last_error_sent = None

    while True:
        try:
            if (response := get_api_answer(timestamp)) is None:
                continue

            check_response(response)

            homeworks = response.get('homeworks')
            if len(homeworks) == 0:
                logger.debug('No updates in homeworks\' statuses.')

            for homework in homeworks:
                verdict = parse_status(homework)
                send_message(bot, verdict)

            timestamp = response.get('current_date')

        # Most likely cannot send feedback about bot\'s errors.
        # Nevertheless can log them.
        except DoNotSendToBotException as error:
            logging.error(f'TError: {error}')

        # These errors can be logged as well as sent via bot message.
        except Exception as error:
            logger.error(f'An error has occured: {type(error).__name__}')
            if error != last_error_sent:
                # Don't want to send same error again and again.
                last_error_sent = error
                send_message(bot, error)

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
