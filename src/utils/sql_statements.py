STATEMENT = \
{
    "CREATE_ENDPOINT_CONFIG" :
        "CREATE TABLE \
            ENDPOINT_CONFIG( \
                ENDPOINT TEXT, \
                METHOD TEXT, \
                LOG BOOLEAN, \
                MESSAGE TEXT, \
                REDIRECT_URL TEXT, \
                REDIRECT_WAIT INTEGER, \
                WEBHOOK_URL TEXT, \
                WEBHOOK_METHOD TEXT, \
                WEBHOOK_BODY TEXT, \
                PRIMARY KEY ( ENDPOINT, METHOD ) \
            )",
    "CREATE_LOG" :
        "CREATE TABLE \
            LOG( \
                ENDPOINT TEXT, \
                METHOD TEXT, \
                TIMESTAMP DATETIME, \
                HOST TEXT, \
                REMOTE_IP TEXT, \
                USER_AGENT TEXT \
            )",
    "GET_ALL_ENDPOINTS" :
        "SELECT * FROM ENDPOINT_CONFIG",
    "GET_ENDPOINT" :
        "SELECT * FROM ENDPOINT_CONFIG WHERE ENDPOINT = ? AND METHOD = ?",
    "INSERT_ENDPOINT_CONFIG" :
        "INSERT INTO \
            ENDPOINT_CONFIG( \
                ENDPOINT, \
                METHOD, \
                LOG, \
                MESSAGE, \
                REDIRECT_URL, \
                REDIRECT_WAIT, \
                WEBHOOK_URL, \
                WEBHOOK_METHOD, \
                WEBHOOK_BODY \
            ) \
            VALUES( \
                :endpoint, \
                :method, \
                :log, \
                :message, \
                :redirectUrl, \
                :redirectWait, \
                :webhookUrl, \
                :webhookMethod, \
                :webhookBody \
            )",
    "INSERT_LOG_ENTRY" :
        "INSERT INTO \
            LOG(  \
                ENDPOINT, \
                METHOD, \
                TIMESTAMP, \
                HOST, \
                REMOTE_IP, \
                USER_AGENT \
            ) \
            VALUES( \
                :endpoint, \
                :method, \
                :timestamp, \
                :host, \
                :remoteIp, \
                :userAgent \
            )"
}