import functools
import time

from solana.rpc.api import Client

from config import cfg


def wait_transaction_finalized(fn):
    @functools.wraps(fn)
    def wrap(self, *args, **kwargs):
        resp = None
        sleep = 5
        for i in range(3):
            try:
                resp = fn(self, *args, **kwargs)
            except Exception:
                time.sleep(sleep)
                sleep += 5
                continue
            if resp.get("error"):
                time.sleep(sleep)
                sleep += 5
                continue

            break

        if resp.get("error"):
            raise Exception("Request limit is reached")

        signature = resp["result"]

        client = Client(cfg.validator)

        while True:
            status_data = client.get_signature_statuses([signature])["result"]["value"][
                0
            ]

            if status_data and status_data["confirmationStatus"] == "finalized":
                break

            time.sleep(1)

        return resp

    return wrap
