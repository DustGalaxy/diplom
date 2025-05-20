from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_nats import PullBasedJetStreamBroker, NatsBroker


broker2 = PullBasedJetStreamBroker(
    servers=[
        "nats://localhost:4222",
    ],
    queue="track_analisys",
)

broker = NatsBroker(
    servers=[
        "nats://localhost:4222",
    ],
    queue="track_analisys",
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
