import datetime
import uuid

import yeti_exceptions
import yeti_logging
import yeti_models
import yeti_service_ticket

logger = yeti_logging.get_logger("YetiOrderService")


def create_order(ticket_id, purchase_amount, buyer_id):

    ticket = yeti_service_ticket.get_ticket(ticket_id)
    ticket_version = ticket.ticket_version

    if purchase_amount > ticket.ticket_amount:
        raise yeti_exceptions.YetiApiClientErrorException("Not enough tickets available")

    order = yeti_models.Order.build(order_id=uuid.uuid4(),
                                    order_version=1,
                                    ticket_id=ticket_id,
                                    ticket_version=ticket_version,
                                    purchase_amount=purchase_amount,
                                    order_datetime=datetime.datetime.now().isoformat(),
                                    expiry_datetime=datetime.datetime.now() + datetime.timedelta(minutes=10)
                                    )

    # TODO: insert the order to db


