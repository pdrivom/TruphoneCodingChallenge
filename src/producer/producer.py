import json
import random
from kafka import KafkaProducer
from flask import Flask


app = Flask(__name__)



@app.route('/api/v1/producer/status', methods=['GET'])
def status():
    return {'status': 'OK'}

@app.route('/api/v1/producer/produce', methods=['POST'])
def produce():
    try:
            simcards = [
                "89440001",
                "89440002",
                "89440003",
                "89440004",
                "89440005",
                "89440006",
                "89440007",
                "89440008",
                "89440009",
                "89440010",
                "89440011",
                "89440012",
                "89440013",
                "89440014",
                "89440016",
            ]

            producer = KafkaProducer(
                bootstrap_servers="kafka:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )

            for i in range(28):
                for j in range(24):
                    for z in range(60):
                        simcard = random.choice(simcards)
                        bytes = random.randint(0, 4096)
                        day = str(i).zfill(2)
                        hours = str(j).zfill(2)
                        minutes = str(z).zfill(2)
                        producer.send(
                            "usage",
                            {
                                "sim-card-id": simcard,
                                "bytes-used": bytes,
                                "date": "2020-02-{}T{}:{}:{}Z".format(day, hours, minutes, "00"),
                            },
                        )
            return { 'message': 'data generated!' }, 200
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='kafka-producer', port=5000, debug=True)