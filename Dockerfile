FROM alpine:latest

RUN apk update && apk add python3 && mkdir -p /opt/shopify-analytics
COPY . /opt/shopify-analytics

WORKDIR /opt/shopify-analytics
RUN cd /opt/shopify-analytics && pip3 install -r requirements.txt

ENTRYPOINT python3 get_orders.py
