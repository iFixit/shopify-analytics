# Shopify Analytics

Quick and easy tool for pulling order info from a shopify store and storing that
data in Mongo

# Development

This app is dockerized.

```
> docker build --no-cache -t shopify-analytics:development
> cp secrets.env.example secrets.env
> ...
> # Go find the secrets
> ...
> docker run --env-file secrets.env shopify-analytics:development
```

This will attempt to write to the production mongo instance. If you just want to
test order fetching / simply print the data to console. If you need to write to
mongo, stub that out by running your own local mongo container

`docker run --rm -p 27017:27017 -d --name mongo-ephemeral mongo`

Inspect the contents of that container via mongo shell:

`docker run -it --rm --network=host mongo mongosh test`

Update secrets.env to point to your mongo container:

`MONGODB_URI=mongodb://mongo:27017`
