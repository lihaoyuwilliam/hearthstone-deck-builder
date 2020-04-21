# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 20:01:04 2020

@author: William
"""
from flask import Flask,request, jsonify,render_template
import requests
import requests_cache
from cassandra.cluster import Cluster


requests_cache.install_cache('crime_api_cache', backend='sqlite', expire_after=36000)

cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()


app = Flask(__name__)

classes = ['Druid','Hunter','Mage','Paladin','Priest','Rogue','Shaman','Warlock','Warrior']
headers = {
    'x-rapidapi-host': "omgvamp-hearthstone-v1.p.rapidapi.com",
    'x-rapidapi-key': "f4ee9eb648msh186aee2d2165672p14d2e4jsn1c8d58287b38"
    }
@app.route('/', methods=['GET'])
def homepage():

    return render_template('home.html')

@app.route('/card-name', methods=['GET','POST'])
def search_by_name():
    card_name = request.form['card_name']
    url = "https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/{}".format(card_name)

    response = requests.request("GET", url, headers=headers)
    
    if not response.ok:
        return "Card '{}' not found!".format(card_name.capitalize()), 404

    return response.json()[0], 200 #ignore cards with the same name

@app.route('/partial-card-name', methods=['GET','POST'])
def search_by_partial_name():
    partial_card_name = request.form['partial_card_name']
    url = "https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/search/{}".format(partial_card_name)

    response = requests.request("GET", url, headers=headers)
    
    if not response.ok:
        return "Card with partial name '{}' not found!".format(partial_card_name.lower()), 404
    
    return response.text, 200


@app.route('/card-class', methods=['GET','POST'])
def search_by_class():
    card_class = request.form['card_class']
    url = "https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/classes/{}".format(card_class)

    response = requests.request("GET", url, headers=headers)
    response = response.text, 200

    return response

@app.route('/new-deck', methods=['GET','POST'])
def new_deck():
    deck_class = request.form['deck_class'].lower()
    deck_name = request.form['deck_name'].lower()
    if deck_name_exists(deck_name):
        response = "deck '{}' already exists!".format(deck_name), 400
    else:
        session.execute('''CREATE TABLE IF NOT EXISTS decks.{} (
                        name text PRIMARY KEY,
                        num int,
                        type text,
                        rarity text,
                        cost int,
                        player_class text ,
                        text text,
                        )
                        '''.format(deck_name,deck_class))
        # add a record to store deck_class to check if added card class is vaild or not          
        session.execute('''INSERT INTO decks.{} (name,num,type,rarity,cost,player_class,text)
                            VALUES('deck_class',0,'','',0,'{}','')'''.format(deck_name,deck_class))
        response = "Deck created successfully! <br/>Deck name: {} <br/>Deck class: {}".format(deck_name.capitalize(),deck_class.capitalize()), 200
        
    return response

@app.route('/delete-deck', methods=['GET','POST','DELETE'])
def delete_deck():
    deck_name = request.form['deck_name'].lower()
    if not deck_name_exists(deck_name):
        response = "Deck '{}' not found!".format(deck_name.capitalize()),400
    else:
        session.execute('''DROP TABLE decks.{} '''.format(deck_name))
        response = "Deck '{}' deleted successfully!".format(deck_name.capitalize()),200
        
    return response

@app.route('/add-card', methods=['GET','POST'])
def add_card():
    deck_name = request.form['deck_name'].lower()
    card_name = request.form['card_name'].lower()
    # check deck name
    if not deck_name_exists(deck_name):
        return "Deck '{}' not found.".format(deck_name.capitalize()), 400
    # check card name
    url = "https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/{}".format(card_name)

    response = requests.request("GET", url, headers=headers)
    
    if not response.ok:
        return "Card '{}' not found!".format(card_name.capitalize()), 404
    else:
        card_info_dict = response.json()[0]
    # check total number of cards
    num_cards = session.execute('''select sum(num) from decks.{}'''.format(deck_name))
    if num_cards.current_rows[0][0] == 30:
        return "Deck '{}' already has 30 cards!<br/>Please delete some cards and try again!".format(deck_name.capitalize()),200
    # check card class
    deck_class = session.execute('''SELECT player_class FROM decks.{} WHERE name='deck_class';'''.format(deck_name))     
    deck_class = deck_class.current_rows[0].player_class
    player_class = card_info_dict['playerClass'].lower()
    if  deck_class != player_class and player_class != 'neutral':
        return "Only '{}' cards and 'neutral' cards can be added!".format(deck_class.capitalize()), 400           
    
    # check cards duplicates in deck
    
    card_info = session.execute('''SELECT * FROM decks.{} where name='{}';'''.format(deck_name,card_name))
    
    # have same card(s) in deck
    if len(card_info.current_rows) != 0: 
        card_info = card_info.current_rows[0]
        # check if this is a legendary card (legendary card should have no duplicates (1 max) in deck)
        if card_info.rarity.lower() == 'legendary':
            return "Legendary card '{}' should not have duplicates in deck!".format(card_name.capitalize()), 400
        # check number of duplicates, non-legendary card 2 max in deck
        if card_info.num == 2:
            return "Non-lengendary card '{}' can only have 2 max in deck! ".format(card_name.capitalize()), 400
        else:
            session.execute('''UPDATE decks.{} set num=2 where name='{}';'''.format(deck_name,card_name))
            return "Card '{}' added successfully, now 2 in deck '{}'.".format(card_name.capitalize(), deck_name.capitalize()),200
    # have no such card in deck
    else:
        name = card_info_dict['name'].lower()
        num = 1
        type_ = card_info_dict['type'].lower()
        rarity = card_info_dict['rarity'].lower()
        cost = int(card_info_dict['cost'])
        text = card_info_dict['text'].lower()
        
        session.execute('''INSERT INTO decks.{} (name,num,type,rarity,cost,player_class,text)
                        VALUES('{}',{},'{}','{}',{},'{}','{}')'''.format(deck_name,name,num,type_,rarity,cost,player_class,text))


    return "Card '{}' added successfully, now 1 in deck '{}'.".format(card_name.capitalize(), deck_name.capitalize()),200

@app.route('/delete-card', methods = ['GET','POST','DELETE'])
def delete_card():
    deck_name = request.form['deck_name'].lower()
    card_name = request.form['card_name'].lower()
    if not deck_name_exists(deck_name):
        resp = "Deck '{}' not found!".format(deck_name.capitalize()), 400
    
    else:
        card_list = []
        rows = session.execute('''SELECT * FROM decks.{};'''.format(deck_name))
        for row in rows:
            card_list.append(row.name)
        if card_name not in card_list:
            resp = "No such card '{}' in deck '{}'.".format(card_name.capitalize(),deck_name.capitalize())
        else:
            card_info = session.execute('''SELECT * FROM decks.{} where name='{}';'''.format(deck_name,card_name))
            card_info = card_info.current_rows[0]
            if card_info.num==2:
                session.execute('''UPDATE decks.{} set num=1 where name='{}';'''.format(deck_name,card_name))
                resp = "Card '{}' deteled successfully, now 1 in deck '{}'!".format(card_name.capitalize(),deck_name.capitalize()),200
            else:
                session.execute('''DELETE FROM decks.{} WHERE name = '{}';'''.format(deck_name,card_name))
                resp = "Card '{}' deteled successfully, now 0 in deck '{}'!".format(card_name.capitalize(),deck_name.capitalize()),200
    
    return resp

@app.route('/show-deck',methods = ['GET','POST'])
def show_deck():
    deck_name = request.form['deck_name']
    if not deck_name_exists(deck_name):
        return "Deck '{}' not found!".format(deck_name.capitalize()), 400
    rows = session.execute('''SELECT name,cost,num,player_class,rarity,type FROM decks.{};'''.format(deck_name))
    string = 'Name|Cost|Num|Class|Rarity|Type<br/><br/>'
    rows = rows.current_rows
    for row in rows:
        for item in row:
            string = string + str(item).capitalize()
            string = string + '|'
        string = string +'<br/>'
    return string, 200

@app.route('/all-decks',methods = ['GET','POST'])
def show_all_decks():
    deck_list=''
    rows = session.execute('''SELECT table_name 
                                          FROM system_schema.tables 
                                          WHERE keyspace_name ='decks';''')
    for row in rows:
        deck_list = deck_list + row.table_name
        deck_list = deck_list + '<br/>'
    return deck_list, 200

def deck_name_exists(deck_name):
    deck_list=[]
    rows = session.execute('''SELECT table_name 
                                          FROM system_schema.tables 
                                          WHERE keyspace_name ='decks';''')
    for row in rows:
        deck_list.append(row.table_name)
    
    if deck_name.lower() in deck_list:
        return True
    
    return False


if __name__=="__main__":
    app.run(host='0.0.0.0',port = 80)
