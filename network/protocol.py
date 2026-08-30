import json


BUFFER_SIZE = 4096


def encode_message(message):
    data = json.dumps(message)
    return (
        data.encode("utf-8")
        + b"\n"
    )


def decode_messages(buffer):
    messages = []

    while b"\n" in buffer:
        raw_message, buffer = buffer.split(
            b"\n",
            1
        )

        if not raw_message:
            continue

        try:
            messages.append(
                json.loads(
                    raw_message.decode("utf-8")
                )
            )
        except json.JSONDecodeError:
            continue

    return messages, buffer