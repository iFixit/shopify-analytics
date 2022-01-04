# Shopify Analytics

Quick and easy tool for pulling order info from a shopify store and storing that
data in Mongo

# Development

This app is dockerized.

```sh
> docker build --no-cache -t shopify-analytics:development .
> cp secrets.env.example secrets.env
> ...
> # Go find the secrets
> ...
> docker run --env-file secrets.env shopify-analytics:development
```

### Stubbing Mongo

Spin up a local mongo container:

- `docker run --rm -p 27017:27017 -d --name mongo-ephemeral mongo`

The provided `secrets.env.example` is already configured to talk to this host:

- `MONGODB_URI=mongodb://mongo:27017`

Inspect the contents of that container via [mongo shell](https://docs.mongodb.com/manual/tutorial/query-documents/):
- `docker run -it --rm --network=host mongo mongosh test`
