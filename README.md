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
