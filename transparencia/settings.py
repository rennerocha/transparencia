BOT_NAME = 'transparencia'

SPIDER_MODULES = ['transparencia.spiders']
NEWSPIDER_MODULE = 'transparencia.spiders'

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'

ROBOTSTXT_OBEY = False

RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 403, 404, 408]
