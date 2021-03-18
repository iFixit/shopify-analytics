FROM python:3-alpine

RUN mkdir -p /opt/
WORKDIR /opt/shopify-analytics
COPY ./requirements.txt /opt/shopify-analytics
RUN cd /opt/shopify-analytics && pip3 install -r requirements.txt
COPY ./get_orders.py /opt/shopify-analytics/

ENTRYPOINT python3 get_orders.py
