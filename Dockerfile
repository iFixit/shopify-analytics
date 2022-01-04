FROM python:3.10-alpine

WORKDIR /opt/shopify-analytics
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt
COPY ./get_orders.py ./

ENTRYPOINT python3 get_orders.py
