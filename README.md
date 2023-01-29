# Fox Comics
## Capstone 1
---
### Link to Heroku Application
[Fox Comics](https://fox-comics.herokuapp.com/)
---
## About This Application

Fox Comics is an eCommerce site built for a fictional, digital comic book retailer. Users can search by character to discover comic books where the character has appeared. When they find something interesting to read, they can add the comic to their cart and checkout.

Users who sing-up for an account are provided with additional functionality. A registered user can maintain lists of characters and comics they find interesting to return to at a later time.

### The Concept

Create an eCommerce site where users search by character, obtain details about the character, view the comics where that character has appeared, and purchase digital comic books.

### The Plan

1. Build the backend with Flask, Python, SQLAlchemy, and a postgresql server
2. Utilize an HTML template and Jinja for the frontend
3. Retrieve and display data about comic books and characters from the ComicVine API
4. Accept payments with the Stripe API
5. Send an HTML email when users register an account using Flask-Mail

### API Sources

1. ### Stripe - Payments API
[Stripe](https://stripe.com/?ref=apilist.fun)  

Stripe's API is used in this application for the following 

2. ### Comic Vine - Comics API
[ComicVine](https://comicvine.gamespot.com/api/documentation?ref=apilist.fun)

### The Execution
#### A Basic User Flow


1. The application begins by checking for a user id stored in the session and adding the user to Flask global. The user is presented with the homepage, which tells the user about the shop and provides guidance on how to get started. From this page, guest users have the option to sign-in, sign-up, or view the shopping cart. 

2. The user searches for a character name to begin. The search term is passed to the search_characters() function in methods.py where the ComicVine API is called. The response data is returned and then passed to the handle_search_results() function in methods.py. This function loops over the returned data, checks for the expected keys within the api call response data, and either sets the value of each key to the value in the response data or to 'None' if the data is not present. 

During the loop, the values are stored in variables, which are then used to create an instance of the Character object. The character objects created in each iteration are appended to the search_results list. Finally, the search_results list is returned. 

In the /characters view route, the list of characters is passed to the render_template where Jinja is utilized to loop over the character objects and display basic information. Jinja is further utilized to check for a logged-in user. If the user is logged in, they will see the option to save the character. If they are not logged in, they will see an option to login to save characters.

3. When a character in the search results is selected, the character_id is passed to the show_character_details view function. The id is further passed to the find_character_appearances() function in methods.py. This function calls the ComicVine API and returns the response data.

The response data is then passed to the get_and_filter_appearances() function in methods.py. This function iterates over the 'issue_credits' key values and filters out any messy title names. During the loop, each issue credit is added to a dictionary with an 'id' and 'name.' Each dictionary created is appended to a list and the list of comic dictionaries is returned and saved in the variable 'appearances.'

We continue in the show_character_details() view function by checking the local database for the character. If the character exists in the database already, we query the database and pass the character object to the render_template along with the list of appearances.

If the character does not exist in the local database, we pass the character_id to the find_single_character() function in methods.py. This function calls the api and returns one single character. The response data is then returned by this function.

Back in the view function show_character_details(), we extract the necessary values to construct a Character object instance. We then pass the cahracter object and list of appearances to the render_template.

Jinja is utilized in the rendered template to display basic character information. If the user is logged in, they will see a button to add the character to their characters list. The character appearances dictionary is looped over and an unordered list is populated with li's containing anchor tags with each comic name displayed. The id from the dictionary is utilized in the href, which links to the comic details page.

4. The show_comic_details() view function passes the comic_id to the get_comic_issue() function in methods.py. This function calls the ComicVine API and returns the response data about a single comic book issue.

Back in the view function, we extract the data necessary to build a Comic object instance. This object instance is then passed to the render_template. Jinja is utilized to display basic information about the comic issue. If the user is logged in, they will see a button to add the comic to their 'reading list.' All users will have the option to add the comic to their shopping cart on this page.

5. When a comic is added to the cart, we check the local database for the comic. If the comic exists, we query the database for that comic. If the comic does not exist in the database, we call get_comic_issue() from methods.py, create a Comic instance object, and pass the new Comic object to the add_comic_to_db() function in methods.py.

This function simply adds and commits the Comic object to the database, queries the database for the comic, and returns the Comic object.

Next, we check the session the 'cart' key. if a cart is in the session, we check to see if this particular comic in the cart already. If the item is not present, we create a dictionary with key/value pairs == {'id':'comic.id', 'comic.name': 1}. If the comic was already in the cart, we increment the value by 1 where the key == comic.name. If there was no cart in the session, we create one and add the item dictionary as before.

Finally, we redirect the user to the cart page.

6. The show_session_cart() view function iterates over the items in the session cart and queries the local database for each item by id.

For each item, we coerce the quantity and price to a float and use the round() function to format the item subtotal to 2 decimal places. The rounded subtotal is saved in the item_subtotal variable.

Next, we coerce the item quantity to an integer and append the comic object, item quantity, and item_subtotal to the cart_contents list.

Finally, we calculate the subtotal of all items by adding the item_subtotal to the subtotal variable and rounding the result to 2 decimal places. The cart_contents and the subtotal are then passed to the render_template. Jinja is utilized to loop over the cart_contents list and display the items in the cart preview.

Users may change the quantity of items in the cart and select 'update cart.'

When the cart is updated, we call the edit_cart_contents() view function. We get the quantities using request.args and save them to the variable 'args.' We check for args and iterate over the key/value pairs and add them to the 'quantities' dictionary. We then loop over the session cart, query the local database for the comic object, and update the value where key == comic.name, just as before. Finally, we redirect to the cart route.

Users may clear the cart of all items with the 'clear shopping cart' button.

When clicked, we call the clear_cart_contents() view function. This calls the clear_session_cart() function from methods.py. Here, we use a while loop based on the length of the session cart. On each iteration, we simply pop() the dictionary from the session until the session cart contains 0 items.

7. When the user is ready to checkout, we call the create_checkout_session() view function. This function calls the create_line_items() function from methods.py. Here, we call get_all_stripe_products(), which returns a list of products from our Stripe product inventory. We save that list to the variable 'products_list.'

Back in the create_line_items() function, we create an empty dictionary to hold each line item and iterate of the session cart. We query the local database for the matching Comic object. We further iterate over products_list and check for the comic.name in values(). If the item is in our Stripe products list already, we get the value of 'default_price', which is a Stripe price id, and set the value of key 'price' in our items dictionary to the Stripe price id. Finally, we break the loop.

If the product was not in our products_list, we call the create_stripe_product() function, which simply creates a new Stripe Product and returns the new Product object. We then use this Product object to set our 'price' value in our items dictionary.

Finally, we set the value of key 'quantity' in our items dictionary to be the quantity from the session cart and append the item dictionary to items_list. After the loop has completed, we return the items_list.

Back in the create_checkout_session() view function, we call the create_checkout_sess() function from methods.py and pass in the items_list. This function sets the success_url and cancel_url to their respective routes. The success_url will contain the id of the checkout session to be utilized after the checkout session has completed. 

Finaly, we attempt to create a stripe checkout Session object using the items_list. If successful, we return the checkout session.

Back in the view function, we redirect the url returned by the Stripe checkout session.

8. On success, we call the show_checkout_success() view function. We use request.args.get() to grab the session_id from the url and pass the session_id to the function create_new_order() in methods.py.

This function first retrieves the checkout session from Stripe and saves it to the checkout_session variable. Next, we extract the amount_total from checkout_session. Stripe stores the price in cents, so we divide it by 100 and coerce it to a float to make it the proper format for USD, then coerce it to a string. Finally, we save the value to the variable checkout_total.

Next, we extract the necessary information from checkout_session to create a new instance of the Order object. Then we add and commit the new order object to the local database.

We query the new order from the local database, iterate over the session cart, query each Comic object from the local database, and append the Comic objects to order.items.

Finally, we commit and return the order object.

Back in the view function, we check for a logged in user. If the user is logged in, we query them from the local database, append the order to user.orders, and commit. Finally, we call clear_session_cart() and pass the user to the render_template.

The template uses Jinja to display a thank you message that is personalized with the user's first name if the user was logged in.

If the user was a guest, we simply create the order in the database, clear the session cart, and return the render_template. This time, the thank you message displayed will not be personalized.


### Application Flowchart

![app flow chart](https://drive.google.com/uc?id=1j98bpukBpryEVwzo8HwR2nXTtq8YVRE2)

### Database Schema
![app Database Schema](https://drive.google.com/uc?id=1STxh6A2JbaTqaNFwPEHcEwWCQbHdgTqB)


### How Would I Improve This App?

#### Features
1. Order Management
    - Webhook to listen for successful payments from Stripe that would trigger a change to the status of an order from 'processing' to 'complete'
    - Ability for users to request refunds/returns from account dashboard
    - Back-end order management dashboard for the shop owner to approve or deny refund/return requests

2. Recommendation Engine
    - Provide recommendations for comics to the user based on characters and comics they have saved or purchased

#### Performance
1. Reducing Memory Usage
    - Exploring more efficient wasys to handle the necessary data returned from API calls without creating a new object instance when one is not needed (i.e. when simply passing the instance to the render template, rather than adding a new object instance to the local database).