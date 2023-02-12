# -*- coding: utf-8 -*-
#
# Copyright 2022 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Microservice to bake pizzas

import sys
import json
import time

from utils import set_producer_consumer, delivery_report, get_script_name, log, save_pid


# Global variables
SCRIPT = get_script_name(__file__)
PRODUCE_TOPIC_BAKED = "pizza-baked"
PRODUCE_TOPIC_STATUS = "pizza-status"
CONSUME_TOPICS = ["pizza-assembled"]

# Set producer/consumer objects
producer, consumer = set_producer_consumer(
    sys.argv[1],
    producer_extra_config={
        "on_delivery": delivery_report,
    },
    consumer_extra_config={
        "auto.offset.reset": "earliest",
        "group.id": "pizza_bake",
        "enable.auto.commit": True,
    },
)


def pizza_baked(order_id: str):
    # Produce to kafka topic
    producer.produce(
        PRODUCE_TOPIC_BAKED,
        key=order_id,
    )
    producer.flush()


def update_pizza_status(
    order_id: str,
    status: int,
):
    # Produce to kafka topic
    producer.produce(
        PRODUCE_TOPIC_STATUS,
        key=order_id,
        value=json.dumps(
            {
                "status": status,
            }
        ).encode(),
    )
    producer.flush()


def receive_pizza_assembled():
    consumer.subscribe(CONSUME_TOPICS)
    log(
        "INFO",
        SCRIPT,
        f"Subscribed to topic(s): {', '.join(CONSUME_TOPICS)}",
    )
    while True:
        event = consumer.poll(1.0)
        if event is not None:
            if event.error():
                log(
                    "ERROR",
                    SCRIPT,
                    event.error(),
                )
            else:
                try:
                    order_id = event.key().decode()
                    try:
                        cooking_time = json.loads(event.value().decode()).get(
                            "cooking_time", 0
                        )
                    except Exception as err1:
                        log(
                            "ERROR",
                            SCRIPT,
                            f"Error when processing event.value() {event.value()}: {err1}",
                        )
                    else:
                        # Assemble pizza (blocking point as it is not using asyncio, but that is for demo purposes)
                        log(
                            "INFO",
                            SCRIPT,
                            f"Preparing order {order_id}, baking time is {cooking_time} second(s)",
                        )
                        time.sleep(cooking_time)
                        log(
                            "INFO",
                            SCRIPT,
                            f"Order {order_id} is baked!",
                        )

                        # Update kafka topics
                        pizza_baked(
                            order_id,
                        )
                        update_pizza_status(
                            order_id,
                            300,
                        )
                except Exception as err2:
                    log(
                        "ERROR",
                        SCRIPT,
                        f"Error when processing event.key() {event.key()}: {err2}",
                    )


if __name__ == "__main__":
    # Save PID
    save_pid(SCRIPT)

    receive_pizza_assembled()