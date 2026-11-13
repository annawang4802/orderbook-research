import zlib

def format_decimal(value):
    return str(value).replace(".", "").lstrip("0")

def calculate_checksum(bids, asks):
    top_asks = sorted(asks)[:10]
    top_bids = sorted(bids, reverse=True)[:10]

    checksum_string = ""

    for ask in top_asks:
        ask_decimal = format_decimal(ask)
        checksum_string += ask_decimal
        checksum_string += format_decimal(asks[ask])

    for bid in top_bids:
        checksum_string += format_decimal(bid)
        checksum_string += format_decimal(bids[bid])

    return zlib.crc32(checksum_string.encode("utf-8"))
