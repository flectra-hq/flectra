# REST API For Flectra

This module enable REST API in any Flectra applications/modules.


## How to Use


```python
import requests, json, pprint

data = {'username': 'admin', 'password': 'admin', 'db': 'db_flectra_base'}
s = requests.post('http://localhost:7073/api/auth/get_tokens', data=data)
content = json.loads(s.content.decode('utf-8'))
headers = {'access_token': content.get('access_token')}
```

**GET request**
```python
p = requests.get('http://localhost:7073/api/res.partner/', headers=headers,
                 data=json.dumps({'limit': 2}))
# ***Pass optional parameter like this***
# {
#   'limit': 10, 'filters': "[('supplier','=',True),('parent_id','=', False)]",
#   'order': 'name asc', 'offset': 10
# }
print(p.content)
```

**POST request**
```python
p = requests.post('http://localhost:7073/api/res.partner/', headers=headers,
                  data=json.dumps({
    'name':'John',
    'country_id': 105,
    'child_ids': [{'name': 'Contact', 'type':'contact'},
                  {'name': 'Invoice', 'type':'invoice'}],
    'category_id': [{'id':9}, {'id': 10}]
    }
))
print(p.content)
```

**PUT Request**
```python
p = requests.put('http://localhost:7073/api/res.partner/68', headers=headers,
                 data=json.dumps({
    'name':'John Doe',
    'country_id': 107,
    'category_id': [{'id': 10}]
    }
))
print(p.content)
```

**DELETE Request**
```python
p = requests.delete('http://localhost:7073/api/res.partner/68', headers=headers)
print(p.content)
```
