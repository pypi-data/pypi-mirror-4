from tenyksclient.client import Client, run_client


class TenyksSearch(Client):

    message_filters = {
        'search': r'^search (.*)$',
    }
    direct_only = True

    def handle(self, data, match, filter_name):
        query = match.groups()[0]
        self.send('{nick_from}: You will be able to search for "{query}" later.'.format(
                    nick_from=data['nick_from'], query=query), data=data)

if __name__ == '__main__':
    search = TenyksSearch()
    run_client(search)
