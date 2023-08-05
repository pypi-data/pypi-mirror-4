========================
Fat Zebra Python Library
========================

This library provides *basic* functionality for the Fat Zebra Payment Gateway.

Currently the only features supported are:

 * Creating Purchases
 * Tokenizing Cards
 * Purchasing with a tokenized card
 * Creating Refunds

Further support for additional functionality will be added as time permits, however if you require this funcitonality and are not able to
add it yourself please contact support@fatzebra.com.au and request the changes.


Usage
=====

Purchases
---------

    import fatzebra

    gw = fatzebra.gateway.Gateway("your username", "your token", True) # The final param indicates whether or not to use the sandbox
    try:
        result = gw.purchase(100, "Jim Smith", "5123456789012346", "05/2014", "123", "122.99.99.111")
        if result.successful:
            print "Purchase approved - ID: " + result.id
        else:
            print "Purchase declined. Message:  " + result.message
    except fatzebra.errors.GatewayError, e:
        print "Gateway error: " + str(e.errors) # <-- e.errors is an array.
    except fatzebra.errors.AuthenticationError:
        print "Authentication error - please check your username and token"

Tokenization
------------

    import fatzebra

    gw = fatzebra.gateway.Gateway("your username", "your token", True) # The final param indicates whether or not to use the sandbox
    try:
        card = gw.tokenize("Jim Smith", "5123456789012346", "05/2014", "123")
        print "Card Tokenized - token: " + card.token
    except fatzebra.errors.GatewayError, e:
        print "Gateway error: " + str(e.errors) # <-- e.errors is an array.
    except fatzebra.errors.AuthenticationError:
        print "Authentication error - please check your username and token"


Purchase with Token
-------------------

    import fatzebra

    gw = fatzebra.gateway.Gateway("your username", "your token", True) # The final param indicates whether or not to use the sandbox
    try:
     token = "abc12345"
     result = gw.purchase(100, token, "122.99.99.111")
     if result.successful:
         print "Purchase approved - ID: " + result.id
     else:
         print "Purchase declined. Message:  " + result.message
    except fatzebra.errors.GatewayError, e:
     print "Gateway error: " + str(e.errors) # <-- e.errors is an array.
    except fatzebra.errors.AuthenticationError:
     print "Authentication error - please check your username and token"


Refund
------

    import fatzebra

    gw = fatzebra.gateway.Gateway("your username", "your token", True) # The final param indicates whether or not to use the sandbox
    try:
        original_transaction = "013-P-ABJU879H"
        result = gw.refund(original_transaction, 100, "my refund reference")
        if result.successful:
            print "Refund approved - ID: " + result.id
        else:
            print "Refund declined. Message:  " + result.message
    except fatzebra.errors.GatewayError, e:
        print "Gateway error: " + str(e.errors) # <-- e.errors is an array.
    except fatzebra.errors.AuthenticationError:
        print "Authentication error - please check your username and token"


Notes
=====

The gateway class utilizes 3 error classes:

 * `fatzebra.errors.GatewayError` - this represents an unsuccessful response from the gateway (invalid card number, expiry etc). Check the `errors` attribute for messages (array)
 * `fatzebra.errors.GatewayUnknownError` - this represents an unknown error. Check the `code` and `response` attributes for details
 * `fatzebra.errors.AuthenticationError` - this indicates your username and token are incorrect. Confirm that you have the right details and you are using the right gateway. Sandbox credentials will begin with **TEST**

Credits
=======

This library was developed by Matthew Savage (Fat Zebra) with the assistance of Simon Meers (Digital Eskimo). It there are any questions or problems with this library
please contact Fat Zebra (support@fatzebra.com.au) or open an `issue <https://github.com/fatzebra/fatzebra-python/issues>`_.