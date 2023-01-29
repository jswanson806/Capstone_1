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

### The User Flow

1. The application begins with a homepage telling the user about the shop and provides guidance on how to get started using the site.

2. Users may login or sign-up for an account. Newly registered users are sent an HTML email with a welcome message sent with Flask-Mail. This email has a brief overview of the services they have access to as a registered user and a call to action with a link to the store homepage.

3. The user searches by character name to begin and the ComicVine API is called to retrieve characters with similar names to the search term. The search results page provides a button for registered users to add characters to their "characters list."

4. After selecting a character, the ComicVine API is called to retrieve specific details about that character.

5. The character details page includes a list of comics where the character has appeared, and provides a button for a registered user to add the character to their "character list."

6. The ComicVine API pulls the character appearance data and the application filters out results that are not full comic titles. For example, titles returned as 'TPB/HC' or simply 'Volume' are filtered out of the results.

7. Users select comic books from the list of appearances to view details about that issue. This serves as the product page where users can add the comic to their cart and registered users can add the comic to their "reading list."

8. The database is populated with comics or characters when the user's intent is clear. This occurs at the following moments:

- When a comic is added to the shopping cart
- When a registered user adds a comic to their "reading list"
- When registered users add a character to their "character list"

9. Registered users can view, add and remove comics or characters from their respective lists. From the "reading list", the user can add comics to their cart.

10. The session is used to keep track of the user's cart as they shop. When the user is ready to checkout, they may proceed to the cart page.

11. The cart route takes the information stored in the session cart and queries the postgresql database for each comic. The comic thumbnail image, title, quantity, and item subtotal are provided for each item. The subtotal, delivery option and total are shown below the item preview.

12. Users may adjust the item quantity in the cart in two ways:
- If a duplicate item is added to the cart, the quantity increments by 1
- By using the buttons on the cart preview page and selecting "update cart"

13. When ready, selecting "checkout" will direct the user to the Stripe checkout page to accept payment. This page displays the item names, item subtotals and total. 

14. Stripe is being used in Test mode for this project. Users may use the following information to experince the full checkout process.

- Card number: 4242 4242 4242 4242
- Expiration: Any date in the future
- Security code: Any 3 digit number

15. If checkout succeeds, the user is directed to a page showing a "thank you" message. This is where the database is populated with a new order.

16. If the user is logged in, the "thank you" message is personalized with their first name and the order is linked to the user in the database.

17. Registered users can view the following information about their account:
- User info - with the ability to edit their info
- Order history - with the ability to view the details of each order


### API Sources

1. ### Stripe - Payments API
[Stripe](https://stripe.com/?ref=apilist.fun)  

Stripe's API is used in this application for the following 

2. ### Comic Vine - Comics API
[ComicVine](https://comicvine.gamespot.com/api/documentation?ref=apilist.fun)

### Application Flow

![app flow chart](https://drive.google.com/uc?id=1j98bpukBpryEVwzo8HwR2nXTtq8YVRE2)