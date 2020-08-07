```python
data['@id'] # data-tourism id
data['rdfs:label']['fr'][0] # name
data['@type'] # list of categories

### Contact
data['hasContact'][0]['schema:email'] # list
data['hasContact'][0]['schema:telephone'] # list +33 6 72 85 54 30
data['hasContact'][0]['foaf:homepage'] # list website

### Content & Media
'\n\n'.join(data['hasDescription'][0]['shortDescription']['fr']) # description
data['hasMainRepresentation'][0]["ebucore:hasRelatedResource"][0]["ebucore:locator"][0] # main representation
data['hasRepresentation'][0]["ebucore:hasRelatedResource"][0]["ebucore:locator"][0] # orther representations

### Location & Opening Hours
'\n'.join(data['isLocatedAt'][0]["schema:address"][0]["schema:streetAddress"]) # street address
data['isLocatedAt'][0]["schema:address"][0]["schema:postalCode"] # postal Code
data['isLocatedAt'][0]["schema:address"][0]["schema:addressLocality"] # city
data['isLocatedAt'][0]["schema:address"][0]["hasAddressCity"][0]["insee"] # commune code

data['isLocatedAt'][0]['schema:geo']['schema:latitude']
data['isLocatedAt'][0]['schema:geo']['schema:longitude']

data['isLocatedAt'][0]['schema:openingHoursSpecification'] # opening hours
```