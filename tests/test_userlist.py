# -*- coding: utf-8 -*-
from irc3 import testing


class TestUserList(testing.BotTestCase):

    def test_userlist(self):
        bot = self.callFTU(nick='foo')
        bot.include('irc3.plugins.core',
                    'irc3.plugins.userlist')
        plugin = bot.get_plugin('irc3.plugins.userlist.Userlist')

        bot.dispatch(':bar!u@b JOIN #foo')
        self.assertIn('bar', plugin.channels['#foo'])
        self.assertNotIn('bar', plugin.channels['#bar'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':bar!u@b JOIN #bar')
        self.assertIn('bar', plugin.channels['#bar'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':gawel!u@h MODE #foo +v-v+v bar bar bar')
        self.assertIn('bar', plugin.channels['#foo'].modes['+'])

        bot.dispatch(':foo!u@b KICK #foo bar :bastard!')
        self.assertNotIn('bar', plugin.channels['#foo'])
        self.assertNotIn('bar', plugin.channels['#foo'].modes['+'])

        bot.dispatch(':gawel!u@h MODE #foo +c')  # coverage
        bot.dispatch(':gawel!u@h MODE gawel')  # coverage

        bot.dispatch(':gawel!u@h MODE #bar +v bar')
        self.assertIn('bar', plugin.channels['#bar'].modes['+'])

        bot.dispatch(':bar!u@b NICK babar')
        self.assertIn('babar', plugin.nicks)
        self.assertIn('babar', plugin.channels['#bar'])
        self.assertIn('babar', plugin.channels['#bar'].modes['+'])
        self.assertNotIn('bar', plugin.channels['#bar'].modes['+'])

        bot.dispatch(':babar!u@b QUIT :lksdlds')
        self.assertNotIn('babar', plugin.nicks)
        self.assertNotIn('babar', plugin.channels['#bar'])

        bot.dispatch(':serv 352 irc3 #chan ~user host serv bar H@ :Blah')
        self.assertIn('bar', plugin.channels['#chan'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':serv 353 irc3 = #chan2 :bar @gawel')
        self.assertIn('bar', plugin.channels['#chan2'])
        self.assertIn('gawel', plugin.channels['#chan2'])
        self.assertIn('gawel', plugin.channels['#chan2'].modes['@'])
        self.assertIn('gawel', plugin.nicks)

        bot.notify('connection_lost')
        self.assertEqual(len(plugin.nicks), 0)
        self.assertEqual(len(plugin.channels), 0)

        bot.dispatch(':serv 353 irc3 = #chan2 :bar @gawel')
        self.assertEqual(len(plugin.nicks), 2)
        self.assertEqual(len(plugin.channels), 1)

        bot.dispatch(':gawel!u@h MODE #chan2 +v bar')
        self.assertIn('bar', plugin.channels['#chan2'].modes['+'])

        bot.dispatch(':bar!u@h PART #chan2')
        self.assertEqual(len(plugin.nicks), 1)
        self.assertNotIn('bar', plugin.channels['#chan2'].modes['+'])

        bot.dispatch(':foo!u@h PART #chan2')
        self.assertNotIn('#chan2', plugin.channels)

        bot.dispatch(':foo!u@h QUIT')
        self.assertEqual(len(plugin.nicks), 0)


class TestServerUserList(testing.ServerTestCase):

    def test_userlist(self):
        s = self.callFTU(clients=0)
        self.assertEqual(len(s.nicks), 0)
        s.add_clients(amount=3)
        self.assertEqual(len(s.nicks), 3)
        s.client1.dispatch('JOIN #irc')
        s.client1.dispatch('JOIN #irc3')
        self.assertEqual(len(s.channels['#irc3']), 1)
        s.client2.dispatch('JOIN #irc3')
        self.assertEqual(len(s.channels['#irc3']), 2)
        self.assertSent(s.client1, ':{mask} JOIN #irc3', s.client2)
        self.assertNotSent(s.client3, ':{mask} JOIN #irc3', s.client2)

        s.client1.dispatch('KICK #irc3 client2 :Lamer!')
        self.assertEqual(len(s.channels['#irc3']), 1)
        self.assertSent(s.client2, ':{mask} KICK #irc3 :Lamer!', s.client1)
        self.assertNotSent(s.client3, ':{mask} KICK #irc3 :Lamer!', s.client1)

        s.client2.dispatch('JOIN #irc3')
        self.assertEqual(len(s.channels['#irc3']), 2)

        s.client1.dispatch('MODE #irc3 +v client2')
        self.assertSent(s.client2, ':{mask} MODE #irc3 +v client2', s.client1)
        self.assertNotSent(
            s.client3, ':{mask} MODE #irc3 +v client2', s.client1)

        s.client1.dispatch('NICK irc3')
        self.assertSent(s.client2, ':client1!uclient1@127.0.0.1 NICK irc3')
        self.assertNotSent(s.client3, ':client1!uclient1@127.0.0.1 NICK irc3')

        s.client3.dispatch('JOIN #irc')
        s.client1.dispatch('NICK client1')
        self.assertSent(s.client2, ':irc3!uclient1@127.0.0.1 NICK client1')
        self.assertSent(s.client3, ':irc3!uclient1@127.0.0.1 NICK client1')

        s.client3.dispatch('PART #irc :Bye')
        self.assertSent(s.client1, ':{mask} PART #irc :Bye', s.client3)
        self.assertNotSent(s.client2, ':{mask} PART #irc :Bye', s.client3)
