### CUSTOMER - ORDER PROJECT

This project creates a database for Customer and orders in django and using Django Restframework.
We create APIs to perform create, read, update and delete operation on the database.

Every Item must have a customer, and on creation of the order, an SMS is sent to the customer

The user of the database is authenticated using OpenID Connect. User must login using google. 
All end points are protected, hence user must sign in. 
The APIs are designed to be used on the browser, session_id and crsftoken plus Referer in the header



## HOW TO USE END POINTS

### LOGINNING IN TO THE SITE
Visit the homepage which is currently, the user has to login with google page
```
 https://customer-order-project.onrender.com/
```

### VIEWING ALL CUSTOMERS
All customers are displayed accorded to the date of creation, this is paginated.
It show 10 customers at time

Use endpoint
> GET /api/get-customers
```
https://customer-order-project.onrender.com/api/get-customers/
```

### To view a specific customer and all the the orders, customer id is passsed as argument
The id of the customer is passed as an argument
Use Endpoint
> GET /api//view-customer/customer_id
```
https://customer-order-project.onrender.com/api/view-customer/0b811f4f-7116-4502-93d8-30d8fced278c
```

### TO ADD A CUSTOMER TO THE DATABASE 
To add a customer to the database, You pass the name and a phone_number which must start with country code, such as
+254704044033 will be accepted, while 0704044033 will be rejected as invalid.
Each customer must have a unique phone number
> POST /api/add-customer/
```
curl "https://customer-order-project.onrender.com/api/add-customer/" -H "Cookie: csrftoken=MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD; sessionid=rxhvjf48uyi8nmyrajwpht5hqlhdfx9h" -H "X-CSRFToken: MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD" -H "Referer: https://customer-order-project.onrender.com" -H "Content-Type: application/json"  -d '{"name": "boss", "phone_number": "+254701036054"}'
```

Returns 
```
{"id":"252f5004-53f0-4ba3-bbf0-7216322f4cf5","name":"boss","phone_number":"+254701036057"} 

```

### TO UPDATE A CUSTOMER
> PUT /api/update-customer/customer_id
```
curl -X PUT "https://customer-order-project.onrender.com/api/update-customer/252f5004-53f0-4ba3-bbf0-7216322f4cf5/" -H "Cookie: csrftoken=MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD; sessionid=rxhvjf48uyi8nmyrajwpht5hqlhdfx9h" -H "X-CSRFToken: MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD" -H "Referer: https://customer-order-project.onrender.com" -H "Content-Type: application/json"  -d '{"name": "bosslady"}'
```
Returns
```
{"id":"252f5004-53f0-4ba3-bbf0-7216322f4cf5","name":"bosslady","phone_number":"+254701036057"}
```


### TO VIEW ALL ORDERS
> GET api/get-orders/
```
curl  "https://customer-order-project.onrender.com/api/get-orders/" -H "Cookie: csrftoken=MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD; sessionid=rxhvjf48uyi8nmyrajwpht5hqlhdfx9h" -H "X-CSRFToken: MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD" -H "Referer: https://customer-order-project.onrender.com" 
```

Returns

```
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3f3b4d4d-862a-415d-8aaa-1aafb045d9fa",
      "item": "borns",
      "amount": "500.00",
      "created_at": "June 25, 2024, 05:54 PM",
      "customer": {
        "id": "0b811f4f-7116-4502-93d8-30d8fced278c",
        "name": "boss",
        "phone_number": "+254701036054"
      }
    },
    {
      "id": "862a4f4e-e3b7-4228-b0d5-31f164b7adcd",
      "item": "borns",
      "amount": "500.00",
      "created_at": "June 26, 2024, 03:01 AM",
      "customer": {
        "id": "0b811f4f-7116-4502-93d8-30d8fced278c",
        "name": "boss",
        "phone_number": "+254701036054"
      }
    } ...........
  ]
}
```

### TO VIEW A SPECIFIC ORDER
Pass the order id to see all details of a speccific order or customer_id as a query parameter
> GET api/view-order/?order_id=121212121
```
To view a specific order_id, pass the order id is a query parameter
curl  "https://customer-order-project.onrender.com/api/view-order/?order_id=3f3b4d4d-862a-415d-8aaa-1aafb045d9fa"      -H "Coo
kie: csrftoken=MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD; sessionid=rxhvjf48uyi8nmyrajwpht5hqlhdfx9h"      -H "X-CSRFToken: MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD" -H "Referer: https://customer-order-project.onrender.com"
```

Return
``` 
{
  "id": "3f3b4d4d-862a-415d-8aaa-1aafb045d9fa",
  "item": "borns",
  "amount": "500.00",
  "created_at": "June 25, 2024, 05:54 PM",
  "customer": {
    "id": "0b811f4f-7116-4502-93d8-30d8fced278c",
    "name": "boss",
    "phone_number": "+254701036054"
  }
}
```
You can also pass the customer_id to see orders of a specific customer


## TO ADD AN ORDER
You have to pass the customer Id and the data of the order in the payload
> POST api/add-order/
```
curl -X POST "https://customer-order-project.onrender.com/api/add-order/" -H "Content-Type: application/json" -H "Cookie: csrftoken=MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD; sessionid=rxhvjf48uyi8nmyrajwpht5hqlhdfx9h" -H "X-CSRFToken: MduNeLVLgOdbIRAd3u3ftwb1Bso3DOSD" -H "Referer: https://customer-order-project.onrender.com" -d '{    "customer_id": "bdb0aeee-2370-484e-b098-cdf05da9f2df",    "item": "example_item",    "amount": 100}'
```
Returns
```
{
  "id": "71f6965a-8ee1-40c6-aa2b-2ce2b48f115f",
  "item": "example_item",
  "amount": "100.00",
  "created_at": "June 26, 2024, 07:45 AM",
  "customer": {
    "id": "bdb0aeee-2370-484e-b098-cdf05da9f2df",
    "name": "12345sdsds",
    "phone_number": "+254701032023"
  }
}
```
