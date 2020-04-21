# **ECS781P Cloud Computing Mini Project**

# **Hearthstone Deck Builder**

### Student Name: Haoyu Li

### Student ID: 190751931

The application is a deck builder for the popular card game Hearthstone. It allows users to search cards by name or class using dynamic RESTful APIs, which is based on an external RESTful service: https://rapidapi.com/omgvamp/api/hearthstone. The RESTful API responses conform to REST standards.

By making use of a Cloud Database in Cassandra, users can build there own decks through adding and deleting cards in the deck. The deck will follow the constraint rules in Hearthstone, so users do not need to think much about that.  Additionally, users can view their decks in the browser. See details below.

## **Homepage:**

URL:

```python
@app.route('/', methods=['GET'])
```

Description:

Direct users to the homepage which enables the users to access to all the APIs of the application, e. g., searching card and building decks,  via a friendly user interface. Users can access to the APIs by filling the forms and clicking the buttons easily in the home page.



## **Searching Card**

### Searching single card by full name:

URL:

```python
@app.route('/card-name', methods=['GET','POST'])
```

Description:

Search card with full name. Case differences do not matters.  Only one card will returned, the other cards with same name are ignored.

### Searching cards by partial name:

URL:

```python
@app.route('/partial-card-name', methods=['GET','POST'])
```

Description:

Search cards with partial name. Case differences do not matters.  All the cards that meet the requirements will return as a list of JSON data.

### Searching cards by class:

URL:

```python
@app.route('/card-class', methods=['GET','POST'])
```

Description:

Search cards with class. All the cards that meet the conditions will return as a list of JSON data.



## Build deck

### Create a new deck:

URL:

```python
@app.route('/new-deck', methods=['GET','POST'])
```

Description:

Create a new deck in Cassandra database. Card name, quantity, cost, type, rarity, class and description will be stored. Deck name is case insensitive.



### Delete a deck:

URL:

```python
@app.route('/delete-deck', methods=['GET','POST','DELETE'])
```

Description:

Delete an exist deck in Cassandra database. 

### Show deck:

URL:

```python
@app.route('/show-deck',methods = ['GET','POST'])
```

Description:

Show an exist deck in Cassandra database. All card information except description will be shown in the browser. The entry 'class_deck' is to tell which class the deck belongs to.



### Add a card:

URL:

```python
@app.route('/add-card', methods=['GET','POST'])
```

Description:

Add a card to an exist deck in Cassandra database. There are some constraint rules:

1. A deck can only have up to 30 cards;

2. Only cards of the same deck class or 'neutral' cards can be added;

3. Each non-legendary card can only have 2  in a deck;

4. Each legendary card can only have 1 in a deck.

   

   

### Delete a card:

URL:

```python
@app.route('/delete-card', methods = ['GET','POST','DELETE'])
```

Description:

Delete a card to an exist deck in Cassandra database. If there are two same cards  in a deck, only one card will be deleted once.









