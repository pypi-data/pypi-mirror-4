from tenyksclient.client import TenyksClient, run_client


class SwissArmyKnife(TenyksClient):
    irc_message_filters = {
            'website_title': [r'']
    }


def main():
    run_client(SwissArmyKnife)


if __name__=='__main__':
    main()
