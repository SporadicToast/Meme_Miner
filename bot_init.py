#import line
import discord
import asyncio
import random as rd
from sql import *
from sql.aggregate import *
from sql.conditionals import *
import sqlite3
import time

#define line
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
#init sql3.py
connection = sqlite3.connect("meme_database.db")
connection.row_factory = dict_factory
cursor = connection.cursor()



#init discord.py
client = discord.Client()
member = discord.Member
user = discord.User
server = discord.Server
game = discord.game
lastedit = "May 17, 2017"
ver = "build 0.04 0x001 - Styrofoam"
prefix = "]"
owner = "SporadicToast"
ownerid = 169064821382316032
clid = 314406318775468033

@client.event
async def on_ready():
    print('Client software ready!')
    print('Bot         {} | {}'.format(client.user.name, client.user.id))
    print('Owner       {} | {}'.format(owner, ownerid))
    print('')
    print('Current command prefix is > {} <'.format(prefix))
    print("{}'s version is {}|{}".format(client.user.name, ver, lastedit))
    print("===============LOGGING===============")
    await client.change_status(game=discord.Game(name='Use {}help'.format(prefix)))
@client.event
async def on_message(message):

    if message.content.startswith('{}'.format(prefix)):
        print('Command recieved - {}|{} - {}'.format(message.author, message.author.id, message.content))
        print(message.channel.name)
        print(message.channel.id)

        current_id = message.author.id
        if 'meme_economy' in message.channel.name:
            sql_command="""INSERT OR IGNORE INTO user_info (user_id) VALUES ({id_user})"""
            cursor.execute(sql_command.format(id_user=message.author.id))
            connection.commit()

            sql_command="""SELECT * FROM user_info WHERE user_id={id_user}"""
            if 'invite' in message.content:
                await client.send_message(message.author, 'https://discordapp.com/oauth2/authorize?client_id=314406318775468033&scope=bot&permissions=0x00218800')
            if "prestige" in message.content:
                if "upgrade max" in message.content:
                    cursor.execute(sql_command.format(id_user=message.author.id))
                    prestige_check = cursor.fetchone()
                    prestige_limiter = [int(prestige_check['mines']) // 10000, int(prestige_check['coolant']) // 10000,
                                        int(prestige_check['mine_size'] // 10000)]
                    prestige_max = int(min(prestige_limiter)) + 1

                    if prestige_max > prestige_check['prestige'] and prestige_max != 1:
                        sql_command = """
                                        UPDATE user_info SET prestige = {new_prestige_level} WHERE user_id = {id_user}"""
                        cursor.execute(sql_command.format(new_prestige_level = prestige_max, id_user = message.author.id))
                        connection.commit()
                        await client.send_message(message.channel,
                                                  "{} congratulations! Your current Prestige level is `{}`!\n`Maximum Mine Output - {}%`\n`Minimum Mine Output - {}%`\n`Cooldown time is now 1/{}`".format(
                                                      message.author.mention, prestige_max, prestige_max * 100,
                                                      prestige_max * 100, prestige_max))
                else:
                    cursor.execute(sql_command.format(id_user=message.author.id))
                    prestige_check = cursor.fetchone()
                    prestige_limiter = [int(prestige_check['mines'])//10000,int(prestige_check['coolant'])//10000,int(prestige_check['mine_size']//10000)]
                    prestige_max = int(min(prestige_limiter))+1

                    if prestige_max > prestige_check['prestige'] and prestige_max != 1 :
                        await client.send_message(message.channel, "{}'s current Prestige level is `{}`.\nYou have reached the pre-requisites of an upgrade! Type `]prestige upgrade max` to upgrade to highest level possible (Prestige Lv.{}).".format(message.author.mention, prestige_check['prestige'], prestige_max))
                    else:
                        message_pres = " "
                        if prestige_limiter[0]<prestige_max:
                            message_pres = "`{}` miners, ".format(10000-(prestige_check['mines']%10000))
                        if prestige_limiter[1]<prestige_max:
                            message_pres = "{}`{}` coolants ".format(message_pres,10000-(prestige_check['coolant']%10000))
                        if prestige_limiter[2]<prestige_max:
                            message_pres = "{}`{}` mine size ".format(message_pres,10000-(prestige_check['mine_size']%10000))
                        await client.send_message(message.channel,"{}'s current Prestige level is `{}`.\nYou need {} to level!".format(message.author.mention, prestige_check['prestige'],message_pres))

            if "portfolio" in message.content:
                cursor.execute(sql_command.format(id_user=message.author.id))
                portfolio_list = cursor.fetchone()
                #print(portfolio_list)
                await client.send_message(message.channel, '{} __**PRESTIGE LEVEL `{}` **__.\nYou have `{}` miners and a mine the size of `{} square meters` and `{}` coolants.\nYou have `{}` dank memes in your treasury.\nMine maximum output `{}`.%\nMine minimum output `{}`%\nCoolant effectiveness ratio `{}x`\nCooldown divider `1/{}`'.format(message.author.mention, portfolio_list['prestige'], portfolio_list['mines'], portfolio_list['mine_size'], portfolio_list['coolant'], portfolio_list['money'], int(portfolio_list['prestige'])*100, int(portfolio_list['prestige'])*100, portfolio_list['prestige'], portfolio_list['prestige']))


            if ']mine' in message.content:
                cursor.execute(sql_command.format(id_user=message.author.id))
                user_ownership = cursor.fetchone()
                #print(user_ownership)
                if int(user_ownership['cooldown']) == 0:
                    #compute cooldown
                    #base 60 seconds, increased by amount of miners by 1 second each
                    #decreases by 3 per coolant
                    cooldown = 5+(int(user_ownership['mines']*1))
                    cooldown = (5+(int(user_ownership['mines']*1)))/int(user_ownership['prestige'])
                    cooldown_decr = (int(user_ownership['coolant'])*3)*user_ownership['prestige']
                    cooldown = cooldown - cooldown_decr
                    if cooldown < 0:
                        cooldown = 3
                    sql_command="""
                    UPDATE user_info SET cooldown = {new_cooldown_val} WHERE user_id = {id_name}
                    """
                    cursor.execute(sql_command.format(new_cooldown_val = cooldown, id_name = message.author.id))
                    connection.commit()
                    rng_mine = rd.uniform(1,1000)
                    if rng_mine < 1001:
                        mine_comment = 'found a undisclosed pile of dank memes! A good mine!'
                    if rng_mine < 800:
                        mine_comment = 'found a nice pile of memes under the earth floor.'
                    if rng_mine < 600:
                        mine_comment = 'had an average meme mine.'
                    if rng_mine < 400:
                        mine_comment = 'noted that were less memes than normal to mine...'
                    if rng_mine < 200:
                        mine_comment = 'barely found any memes in his mine.'
                    if rng_mine < 50:
                        mine_comment = 'picks up a note. "If you see this comment you were given the wost mine in the planet. Theres is only a 5% chance of this message."'
                    rng_storage = rd.uniform(1, 1000)
                    if rng_storage < 1001:
                        store_comment = 'You were able to properly pack up the memes without any of them falling.'
                    if rng_storage < 800:
                        store_comment = 'You dropped a few memes on the way, but it was nothing compared to the amount you have.'
                    if rng_storage < 600:
                        store_comment = 'An unfortunate event and you spent half of your memes on fidget spinners.'
                    if rng_storage < 400:
                        store_comment = 'You landed on a Chance slot and was forced to pay more than half of your collected memes for taxes.'
                    if rng_storage < 200:
                        store_comment = '1/8 of your memes simply dissapeared has you snoozed your way back.'
                    if rng_storage < 50:
                        store_comment = 'Karl Marx seizes your memes of production and distributes it to the normes. You have the worst luck to get this. 5% chance.'
                    to_mine = (int(user_ownership['mines']) * rng_mine)*int(user_ownership['prestige'])
                    # print('To mine value {}'.format(to_mine))
                    max_cap = (int(user_ownership['mine_size']) *rng_storage)*int(user_ownership['prestige'])
                    # print('To max value {}'.format(max_cap))
                    i = 0
                    while int(to_mine) > int(max_cap):
                        to_mine = to_mine - (int(user_ownership['mines']) * rd.randint(1, 1000))
                        i = i + 1
                        # print('Iteration {}'.format(i))

                    result = int(abs(to_mine))
                    await client.send_message(message.channel, '{} {}\n{}\n`{}` dank memes!'.format(message.author.mention, mine_comment, store_comment, result))
                    if rd.randint(1,1000)==rd.randint(1,1000):
                        await client.send_message(message.channel, '{} has a LUCKY HIT! his `{}` dank memes will be multiplied by 1000! Grand total of `{}` dank memes!'.format(message.author.mention, result, result*1000))
                        result = result * 1000
                    new_cash = int(user_ownership['money']) + int(result)
                    sql_command = """
                            UPDATE user_info SET money = {new_cash_value} WHERE user_id = {id_name}"""
                    cursor.execute(sql_command.format(new_cash_value=new_cash, id_name=message.author.id))
                    connection.commit()
                    sql_command = """SELECT cooldown FROM user_info WHERE user_id={id_user}"""
                    cursor.execute(sql_command.format(id_user=message.author.id))
                    cooldown_tock = cursor.fetchone()
                    while int(cooldown_tock['cooldown'])>1:
                        sql_command = """SELECT cooldown FROM user_info WHERE user_id={id_user}"""
                        cursor.execute(sql_command.format(id_user=message.author.id))
                        cooldown_tock = cursor.fetchone()
                        cooldown_change = int(cooldown_tock['cooldown']) - 1
                        connection.commit()
                        sql_command = """UPDATE user_info SET cooldown = {cooldown_new_value} WHERE user_id = {id_name}"""
                        cursor.execute(sql_command.format(cooldown_new_value = cooldown_change, id_name = message.author.id))
                        #print('{} cooldown'.format(cooldown_tock['cooldown']))
                        await asyncio.sleep(1)


                else:
                    cooldown = 60 + (int(user_ownership['mines'] * 1))
                    cooldown_prestige = (60 + (int(user_ownership['mines'] * 1))) / int(user_ownership['prestige'])
                    prestige_d_time = cooldown - cooldown_prestige
                    await client.send_message(message.channel,'{} please wait! Your machines are cooling down. It will complete in `{}` seconds!\n{} coolants decreased it by `{}` seconds! To cool down faster, purchase coolants! (3 second decrease)\nPrestige `Lv.{}` diminished delay time by `{}` seconds!'.format(message.author.mention, user_ownership['cooldown'], user_ownership['coolant'], (int(user_ownership['coolant']*3))*int(user_ownership['prestige']), user_ownership['prestige'], prestige_d_time))


            if "help" in message.content:
                await client.send_message(message.author, "Developed by SporadicToast, the MemeBot simulates a meme tycoon where you buy and sell memes.\nTo start simply type {p}mine.\n```Commands\n{p}help - PMs you this message again\n{p}mine - starts mining memes\n{p}shop - opens shop\n{p}buy_machine ## - buys ## miners\n{p}buy_space ## - increases space by ##```".format(p=prefix))
            if "shop" in message.content:
                # test
                cursor.execute(sql_command.format(id_user=message.author.id))
                user_ownership=cursor.fetchone()
                indiv_miner_cost = 10000 * (int(user_ownership['mines']) // 100)
                if indiv_miner_cost == 0:
                    indiv_miner_cost = 10000
                indiv_space_cost = 5000 * (int(user_ownership['mine_size']) // 100)
                if indiv_space_cost == 0:
                    indiv_space_cost = 5000
                indiv_coolant_cost = 7500 * (int(user_ownership['coolant']) // 100)
                if indiv_coolant_cost == 0:
                    indiv_coolant_cost = 7500

                miner_prompt = "Miners {}dm ea. | Increases minimum output from mining! Each mine adds 2sec cooldown. | ]buy_machine ## or ]buy_machine all".format(indiv_miner_cost)
                space_prompt = "Mine space {}dm/square km. | Increases maximum output from mining! | ]buy_space ## or ]buy_space all".format(indiv_space_cost)
                coolant_prompt = "Coolant {}dm ea. | Decreases cooldown time by 3 seconds! (Does not affect cooldown less than 3 seconds) | ]buy_coolant ## or ]buy_coolant all".format(indiv_coolant_cost)
                await client.send_message(message.channel, "Shop listing for {} || ```{}```\n```{}```\n```{}```".format(message.author.mention, miner_prompt, space_prompt, coolant_prompt))

            if "buy_machine" in message.content:
                cursor.execute(sql_command.format(id_user=message.author.id))
                user_ownership = cursor.fetchone()
                purchase_miner = message.content.strip(']buy_machine ')
                indiv_miner_cost = 10000*(int(user_ownership['mines'])//100)
                if indiv_miner_cost == 0:
                    indiv_miner_cost = 10000
                #print(indiv_miner_cost)

                try:
                    if purchase_miner.isdigit() is True:
                        cost = int(purchase_miner) * indiv_miner_cost
                        if cost < user_ownership['money']:

                            expense = user_ownership['money'] - cost
                            purchased_mines = int(purchase_miner) + user_ownership['mines']
                            await client.send_message(message.channel,
                                                      "{}, Successfully purchased {} miners for {}! Current balance is {}.".format(message.author.mention, purchase_miner, cost, expense))
                            sql_command = """
                                                    UPDATE user_info SET money = {new_cash_value}, mines = {new_mine_value}  WHERE user_id = {id_name}"""
                            cursor.execute(sql_command.format(new_cash_value=expense, new_mine_value=purchased_mines, id_name=message.author.id))
                            connection.commit()
                    else:
                        if 'all' in message.content:
                            autobuy_mine = user_ownership['money'] // indiv_miner_cost
                            cost = autobuy_mine * indiv_miner_cost
                            expense = user_ownership['money'] - cost
                            purchased_mines = int(purchase_miner) + user_ownership['mines']
                            await client.send_message(message.channel,
                                                          "{}, Successfully purchased {} miners for {}! Current balance is {}.".format(
                                                              message.author.mention, autobuy_mine, cost, expense))
                            sql_command = """
                                                            UPDATE user_info SET money = {new_cash_value}, mines = {new_mine_value}  WHERE user_id = {id_name}"""
                            cursor.execute(
                            sql_command.format(new_cash_value=expense, new_mine_value=purchased_mines,
                                                       id_name=message.author.id))
                            connection.commit()
                        else:
                            await client.send_message(message.channel, "{}, Cannot comply purchase. Check if you have enough money".format(message.author.mention))
                except ValueError:
                        if 'all' in message.content:
                            autobuy_mine = user_ownership['money'] // indiv_miner_cost
                            cost = autobuy_mine * indiv_miner_cost
                            expense = user_ownership['money'] - cost
                            purchased_mines = int(autobuy_mine) + user_ownership['mines']
                            await client.send_message(message.channel,
                                                          "{}, Successfully purchased {} miners for {}! Current balance is {}.".format(
                                                              message.author.mention, autobuy_mine, cost, expense))
                            sql_command = """
                                                            UPDATE user_info SET money = {new_cash_value}, mines = {new_mine_value}  WHERE user_id = {id_name}"""
                            cursor.execute(
                            sql_command.format(new_cash_value=expense, new_mine_value=purchased_mines,
                                                       id_name=message.author.id))
                            connection.commit()
                        else:
                            #print('error')
                            print("Invalid command argument on buying")
            if "buy_space" in message.content:
                cursor.execute(sql_command.format(id_user=message.author.id))
                user_ownership = cursor.fetchone()
                purchase_space = message.content.strip(']buy_space ')
                #print(purchase_space)
                indiv_space_cost = 5000 * (int(user_ownership['mine_size']) // 100)
                if indiv_space_cost == 0:
                    indiv_space_cost = 5000
                if purchase_space.isdigit() is True:
                    cost = int(purchase_space) * indiv_space_cost
                    if cost < user_ownership['money']:
                        expense = user_ownership['money'] - cost
                        purchased_space = int(purchase_space) + user_ownership['mine_size']
                        sql_command = """
                        UPDATE user_info SET money = {new_cash_value}, mine_size = {new_minesz_value}  WHERE user_id = {id_name}"""
                        cursor.execute(sql_command.format(new_cash_value=expense, new_minesz_value=purchased_space,
                                                          id_name=message.author.id))
                        await client.send_message(message.channel, "{}, Successfully purchased {} space for {}!".format(message.author.mention, purchase_space, cost))
                        connection.commit()
                else:
                    if 'all' in message.content:
                        autobuy_space = user_ownership['money'] // indiv_space_cost
                        cost = autobuy_space * indiv_space_cost
                        expense = user_ownership['money'] - cost
                        purchased_mines = int(autobuy_space) + user_ownership['mine_size']
                        await client.send_message(message.channel,
                                                  "{}, Successfully purchased {} mine space for {}! Current balance is {}.".format(
                                                      message.author.mention, autobuy_space, cost, expense))
                        sql_command = """
                                                        UPDATE user_info SET money = {new_cash_value}, mine_size = {new_mines_value}  WHERE user_id = {id_name}"""
                        cursor.execute(
                            sql_command.format(new_cash_value=expense, new_mines_value=purchased_mines,
                                               id_name=message.author.id))
                        connection.commit()
                    else:
                        await client.send_message(message.channel,  "{}, Cannot comply purchase. Check if you have enough money".format(message.author.mention))
            if "buy_coolant" in message.content:
                cursor.execute(sql_command.format(id_user=message.author.id))
                user_ownership = cursor.fetchone()
                purchase_coolant= message.content.strip(']buy_coolant ')
                #print(purchase_coolant)
                indiv_coolant_cost = 7500 * (int(user_ownership['coolant']) // 100)
                if indiv_coolant_cost == 0:
                    indiv_coolant_cost = 7500
                if purchase_coolant.isdigit() is True:
                    cost = int(purchase_coolant) * indiv_coolant_cost
                    if cost < user_ownership['money']:
                        expense = user_ownership['money'] - cost
                        purchased_coolant = int(purchase_coolant) + user_ownership['coolant']
                        sql_command = """
                        UPDATE user_info SET money = {new_cash_value}, coolant = {new_coolant_value}  WHERE user_id = {id_name}"""
                        cursor.execute(sql_command.format(new_cash_value=expense, new_coolant_value=purchased_coolant,
                                                          id_name=message.author.id))
                        await client.send_message(message.channel, "{}, Successfully purchased {} coolant for {}!".format(message.author.mention, purchase_coolant, cost))
                        connection.commit()
                    else:
                        await client.send_message(message.channel, "{}, Cannot comply purchase. Check if you have enough money".format(message.author.mention))
                else:
                    if 'all' in message.content:
                        autobuy_coolant = user_ownership['money'] // indiv_coolant_cost
                        cost = autobuy_coolant * indiv_coolant_cost
                        expense = user_ownership['money'] - cost
                        purchased_coolant = int(autobuy_coolant) + user_ownership['coolant']
                        await client.send_message(message.channel,
                                                  "{}, Successfully purchased {} coolant for {}! Current balance is {}.".format(
                                                      message.author.mention, autobuy_coolant, cost, expense))
                        sql_command = """
                                                        UPDATE user_info SET money = {new_cash_value}, coolant = {new_coolant_value}  WHERE user_id = {id_name}"""
                        cursor.execute(
                            sql_command.format(new_cash_value=expense, new_coolant_value=purchased_coolant,
                                               id_name=message.author.id))
                        connection.commit()
                    else:
                        await client.send_message(message.channel,  "{}, Cannot comply purchase. Check if you have enough money".format(message.author.mention))
            if "admin.system_cooldown_override" in message.content:
                #print('detect!')
                if int(message.author.id) == 169064821382316032:
                    sql_command = """UPDATE user_info SET cooldown = 2"""
                    cursor.execute(sql_command)
                    connection.commit()
                    await asyncio.sleep(3)
                    sql_command = """UPDATE user_info SET cooldown = 0"""
                    cursor.execute(sql_command)
                    connection.commit()
                    await client.send_message(message.channel,"{}, admin command reset for cooldown!".format(message.author.mention))

        else:
            await client.send_message(message.channel, 'Sorry {0.author.mention}, I can only interact in the #meme_economy text channel.'.format(message))


client.run(!CHANGE)
os.system("title Meme Stocks - ver {}".format(ver))