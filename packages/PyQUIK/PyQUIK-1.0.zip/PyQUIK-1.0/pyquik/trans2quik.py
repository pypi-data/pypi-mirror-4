""" QUIK TRANS2QUIK API wrapper for Python. """

__author__ = "Denis Kolodin"


from ctypes import WinDLL, c_char, c_long, c_double, POINTER, \
     WINFUNCTYPE, byref, create_string_buffer, pointer, string_at
from ctypes.wintypes import LPCSTR, LPSTR, DWORD, CHAR, PDWORD
from ctypes.util import find_library

c_long_p = POINTER(c_long)
c_double_p = POINTER(c_double)
c_void = None


try:
    TRANS2QUIK = WinDLL("TRANS2QUIK.dll")
except OSError:
    import os
    libpath = os.path.join(os.path.dirname(__file__), "TRANS2QUIK.dll")
    TRANS2QUIK = WinDLL(libpath)


# TRANS2QUIK CONSTANTS
SUCCESS = 0
FAILED = 1
QUIK_TERMINAL_NOT_FOUND = 2
DLL_VERSION_NOT_SUPPORTED = 3
ALREADY_CONNECTED_TO_QUIK = 4
WRONG_SYNTAX = 5
QUIK_NOT_CONNECTED = 6
DLL_NOT_CONNECTED = 7
QUIK_CONNECTED = 8
QUIK_DISCONNECTED = 9
DLL_CONNECTED = 10
DLL_DISCONNECTED = 11
MEMORY_ALLOCATION_ERROR = 12
WRONG_CONNECTION_HANDLE = 13
WRONG_INPUT_PARAMS = 14

RESULTS = {
    SUCCESS: "TRANS2QUIK_SUCCESS",
    FAILED: "TRANS2QUIK_FAILED",
    QUIK_TERMINAL_NOT_FOUND: "TRANS2QUIK_QUIK_TERMINAL_NOT_FOUND",
    DLL_VERSION_NOT_SUPPORTED: "TRANS2QUIK_DLL_VERSION_NOT_SUPPORTED",
    ALREADY_CONNECTED_TO_QUIK: "TRANS2QUIK_ALREADY_CONNECTED_TO_QUIK",
    WRONG_SYNTAX: "TRANS2QUIK_WRONG_SYNTAX",
    QUIK_NOT_CONNECTED: "TRANS2QUIK_QUIK_NOT_CONNECTED",
    DLL_NOT_CONNECTED: "TRANS2QUIK_DLL_NOT_CONNECTED",
    QUIK_CONNECTED: "TRANS2QUIK_QUIK_CONNECTED",
    QUIK_DISCONNECTED: "TRANS2QUIK_QUIK_DISCONNECTED",
    DLL_CONNECTED: "TRANS2QUIK_DLL_CONNECTED",
    DLL_DISCONNECTED: "TRANS2QUIK_DLL_DISCONNECTED",
    MEMORY_ALLOCATION_ERROR: "TRANS2QUIK_MEMORY_ALLOCATION_ERROR",
    WRONG_CONNECTION_HANDLE: "TRANS2QUIK_WRONG_CONNECTION_HANDLE",
    WRONG_INPUT_PARAMS: "TRANS2QUIK_WRONG_INPUT_PARAMS",
}


pnExtendedErrorCode_data = c_long()
pnExtendedErrorCode = byref(pnExtendedErrorCode_data)
pnReplyCode_data = c_long()
pnReplyCode = byref(pnReplyCode_data)
pdOrderNum_data = c_double()
pdOrderNum = byref(pdOrderNum_data)

dwErrorMessageSize = DWORD(200)
dwResultMessageSize = DWORD(200)
lpstrErrorMessage = create_string_buffer(dwErrorMessageSize.value)
lpstrResultMessage = create_string_buffer(dwResultMessageSize.value)



def _declare_extended(func, *args):
    func.restype = c_long
    func.argtypes = args + (c_long_p, LPSTR, DWORD)
    def __caller__(*args):
        args += (
            pnExtendedErrorCode,
            lpstrErrorMessage,
            dwErrorMessageSize
        )
        return func(*args)
    return __caller__


def _declare_method(func, restype, *args):
    func.restype = restype
    func.argtypes = args
    return func


# long TRANS2QUIK_CONNECT(
#     LPCSTR lpcstrConnectionParamsString,
#     _________________________
#     long* pnExtendedErrorCode,
#     LPSTR lpstrErrorMessage,
#     DWORD dwErrorMessageSize
# )
CONNECT = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_CONNECT, LPCSTR
)

def connect(path):
    lpcstrConnectionParamsString = LPCSTR(path.encode())
    return CONNECT(lpcstrConnectionParamsString)

# long TRANS2QUIK_DISCONNECT(
#     _________________________
#     long* pnExtendedErrorCode,
#     LPSTR lpstrErrorMessage,
#     DWORD dwErrorMessageSize
# )
disconnect = DISCONNECT = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_DISCONNECT
)


# long TRANS2QUIK_IS_QUIK_CONNECTED(
#     _________________________
#     long* pnExtendedErrorCode,
#     LPSTR lpstrErrorMessage,
#     DWORD dwErrorMessageSize
# )
is_quik_connected = IS_QUIK_CONNECTED = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_IS_QUIK_CONNECTED
)


# long TRANS2QUIK_IS_DLL_CONNECTED(
#     _________________________
#     long* pnExtendedErrorCode,
#     LPSTR lpstrErrorMessage,
#     DWORD dwErrorMessageSize
# )
is_dll_connected = IS_DLL_CONNECTED = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_IS_DLL_CONNECTED
)


# long TRANS2QUIK_SEND_SYNC_TRANSACTION(
#     LPSTR lpstTransactionString,
#     long* pnReplyCode,
#     PDWORD pdwTransId,
#     double* pdOrderNum,
#     LPSTR lpstrResultMessage,
#     DWORD dwResultMessageSize,
#     _________________________
#     long* pnExtendedErrorCode,
#     LPSTR lpstErrorMessage,
#     DWORD dwErrorMessageSize
# )
SEND_SYNC_TRANSACTION = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_SEND_SYNC_TRANSACTION,
    LPSTR, c_long_p, PDWORD, c_double_p, LPSTR, DWORD
)

#----------------------------------------------------------------------
def send_sync_transaction(transaction, trans_id):
    lpstTransactionString = LPCSTR(transaction.encode())
    dwTransId = DWORD(trans_id)
    pdwTransId = PDWORD(dwTransId)
    return SEND_SYNC_TRANSACTION(
        lpstTransactionString,
        pnReplyCode,
        pdwTransId,
        pdOrderNum,
        lpstrResultMessage,
        dwResultMessageSize,
    )


# void TRANS2QUIK_CONNECTION_STATUS_CALLBACK(
#     long nConnectionEvent,
#     long nExtendedErrorCode,
#     LPSTR lpstrInfoMessage
# )
CONNECTION_STATUS_CALLBACK = \
    WINFUNCTYPE(c_void, c_long, c_long, LPSTR)

# long TRANS2QUIK_SET_CONNECTION_STATUS_CALLBACK(
#     TRANS2QUIK_CONNECTION_STATUS_CALLBACK pfConnectionStatusCallback,
#     _________________________
#     long* pnExtendedErrorCode,
#     LPSTR lpstrErrorMessage,
#     DWORD dwErrorMessageSize
# )

SET_CONNECTION_STATUS_CALLBACK = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_SET_CONNECTION_STATUS_CALLBACK,
    CONNECTION_STATUS_CALLBACK
)

def set_connection_status_callback(callback):
    c = CONNECTION_STATUS_CALLBACK(callback)
    set_connection_status_callback.callback = c  # Keep pointer from gc
    return SET_CONNECTION_STATUS_CALLBACK(c)


# long TRANS2QUIK_SEND_ASYNC_TRANSACTION(
#     LPSTR lpstTransactionString,
#     long* pnExtendedErrorCode,
#     LPSTR lpstErrorMessage,
#     DWORD dwErrorMessageSize
# )
SEND_ASYNC_TRANSACTION = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_SEND_ASYNC_TRANSACTION, LPSTR
)

#----------------------------------------------------------------------
def send_async_transaction(transaction):
    lpstTransactionString = LPCSTR(transaction.encode())
    return SEND_ASYNC_TRANSACTION(lpstTransactionString)


# void TRANS2QUIK_TRANSACTION_REPLY_CALLBACK(
#     long nTransactionResult,
#     long nTransactionExtendedErrorCode,
#     long nTransactionReplyCode,
#     DWORD dwTransId,
#     double dOrderNum,
#     LPSTR lpstrTransactionReplyMessage
# )
TRANSACTION_REPLY_CALLBACK = \
    WINFUNCTYPE(c_void, c_long, c_long, c_long, DWORD, c_double, LPSTR)

# long TRANS2QUIK_SET_TRANSACTIONS_REPLY_CALLBACK(
#     TRANS2QUIK_TRANSACTION_REPLY_CALLBACK pfTransactionReplyCallback,
#     long* pnExtendedErrorCode,
#     LPSTR lpstrErrorMessage,
#     DWORD dwErrorMessageSize
# )

SET_TRANSACTIONS_REPLY_CALLBACK = _declare_extended(
    TRANS2QUIK.TRANS2QUIK_SET_TRANSACTIONS_REPLY_CALLBACK,
    TRANSACTION_REPLY_CALLBACK
)

def set_transaction_reply_callback(callback):
    c = TRANSACTION_REPLY_CALLBACK(callback)
    set_transaction_reply_callback.callback = c  # Keep pointer from gc
    return SET_TRANSACTIONS_REPLY_CALLBACK(c)


# void TRANS2QUIK_ORDER_STATUS_CALLBACK(
#     long nMode,
#     DWORD dwTransID,
#     double dNumber,
#     LPSTR lpstrClassCode,
#     LPSTR lpstrSecCode,
#     double dPrice,
#     long nBalance,
#     double dValue,
#     long nIsSell,
#     long nStatus,
#     long nOrderDescriptor
# )
ORDER_STATUS_CALLBACK = \
    WINFUNCTYPE(c_void, c_long, DWORD, c_double, LPSTR, LPSTR,
                c_double, c_long, c_double, c_long, c_long, c_long)

# void TRANS2QUIK_START_ORDERS(
#     TRANS2QUIK_ORDER_STATUS_CALLBACK pfnOrderStatusCallback
# )

START_ORDERS = _declare_method(
    TRANS2QUIK.TRANS2QUIK_START_ORDERS, c_void,
    ORDER_STATUS_CALLBACK
)

#----------------------------------------------------------------------
def start_orders(callback):
    c = ORDER_STATUS_CALLBACK(callback)
    start_orders.callback = c
    return START_ORDERS(c)

# long TRANS2QUIK_SUBSCRIBE_ORDERS(
#     LPSTR lpstrClassCode,
#     LPSTR lpstrSeccodes
# )
SUBSCRIBE_ORDERS =  _declare_method(
    TRANS2QUIK.TRANS2QUIK_SUBSCRIBE_ORDERS, c_long, LPSTR, LPSTR
)

#----------------------------------------------------------------------
def subscribe_orders(classcode, seccodes):
    """"""
    lpstrClassCode = LPSTR(classcode.encode())
    lpstrSeccodes = LPSTR(seccodes.encode())
    return SUBSCRIBE_ORDERS(lpstrClassCode, lpstrSeccodes)


# long TRANS2QUIK_UNSUBSCRIBE_ORDERS()
UNSUBSCRIBE_ORDERS = _declare_method(
    TRANS2QUIK.TRANS2QUIK_UNSUBSCRIBE_ORDERS, c_long
)

#----------------------------------------------------------------------
unsubscribe_orders = UNSUBSCRIBE_ORDERS


# void TRANS2QUIK_TRADE_STATUS_CALLBACK(
#     long nMode,
#     double dNumber,
#     double dOrderNum,
#     LPSTR lpstrClassCode,
#     LPSTR lpstrSecCode,
#     double dPrice,
#     long nQty,
#     double dValue,
#     long nIsSell,
#     long nTradeDescriptor
# )
TRADE_STATUS_CALLBACK = \
    WINFUNCTYPE(c_void, c_long, c_double, c_double, LPSTR, LPSTR,
                c_double, c_long, c_double, c_long, c_long)

# void TRANS2QUIK_START_TRADES(
#     TRANS2QUIK_TRADE_STATUS_CALLBACK pfnTradesStatusCallback
# )

START_TRADES = _declare_method(
    TRANS2QUIK.TRANS2QUIK_START_TRADES, c_void,
    TRADE_STATUS_CALLBACK
)

#----------------------------------------------------------------------
def start_trades(callback):
    c = TRADE_STATUS_CALLBACK(callback)
    start_trades.callback = c
    return START_TRADES(c)


# long TRANS2QUIK_SUBSCRIBE_TRADES(
#     LPSTR lpstrClassCode,
#     LPSTR lpstrSeccodes
# )
SUBSCRIBE_TRADES = _declare_method(
    TRANS2QUIK.TRANS2QUIK_SUBSCRIBE_TRADES, c_long, LPSTR, LPSTR
)

#----------------------------------------------------------------------
def subscribe_trades(classcode, seccodes):
    """"""
    lpstrClassCode = LPSTR(classcode.encode())
    lpstrSeccodes = LPSTR(seccodes.encode())
    return SUBSCRIBE_TRADES(lpstrClassCode, lpstrSeccodes)


# long TRANS2QUIK_UNSUBSCRIBE_TRADES()
UNSUBSCRIBE_TRADES = _declare_method(
    TRANS2QUIK.TRANS2QUIK_UNSUBSCRIBE_TRADES, c_long
)

#----------------------------------------------------------------------
unsubscribe_trades = UNSUBSCRIBE_TRADES




# long TRANS2QUIK_ORDER_QTY(long nOrderDescriptor)
order_qty = ORDER_QTY = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_QTY, c_long, c_long
)


# long TRANS2QUIK_ORDER_DATE(long nOrderDescriptor)
order_date = ORDER_DATE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_DATE, c_long, c_long
)


# long TRANS2QUIK_ORDER_TIME(long nOrderDescriptor)
order_time = ORDER_TIME = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_TIME, c_long, c_long
)


# long TRANS2QUIK_ORDER_ACTIVATION_TIME(long nOrderDescriptor)
order_activation_time = ORDER_ACTIVATION_TIME = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_ACTIVATION_TIME, c_long, c_long
)


# long TRANS2QUIK_ORDER_WITHDRAW_TIME(long nOrderDescriptor)
order_withdraw_time = ORDER_WITHDRAW_TIME = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_WITHDRAW_TIME, c_long, c_long
)

# long TRANS2QUIK_ORDER_EXPIRY(long nOrderDescriptor)
order_expiry = ORDER_EXPIRY = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_EXPIRY, c_long, c_long
)

# double TRANS2QUIK_ORDER_ACCRUED_INT(long nOrderDescriptor)
order_accrued_int = ORDER_ACCRUED_INT = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_ACCRUED_INT, c_double, c_long
)

# double TRANS2QUIK_ORDER_YIELD(long nOrderDescriptor)
order_yield = ORDER_YIELD = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_YIELD, c_double, c_long
)

# LPSTR TRANS2QUIK_ORDER_USERID(long nOrderDescriptor)
order_userid = ORDER_USERID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_USERID, LPSTR, c_long
)

# long TRANS2QUIK_ORDER_UID(long nOrderDescriptor)
order_uid = ORDER_UID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_UID, c_long, c_long
)

# LPSTR TRANS2QUIK_ORDER_ACCOUNT(long nOrderDescriptor)
order_account = ORDER_ACCOUNT = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_ACCOUNT, LPSTR, c_long
)

# LPSTR TRANS2QUIK_ORDER_BROKERREF(long nOrderDescriptor)
order_brokerref = ORDER_BROKERREF = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_BROKERREF, LPSTR, c_long
)

# LPSTR TRANS2QUIK_ORDER_CLIENT_CODE(long nOrderDescriptor)
order_client_code = ORDER_CLIENT_CODE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_CLIENT_CODE, LPSTR, c_long
)

# LPSTR TRANS2QUIK_ORDER_FIRMID(long nOrderDescriptor)
order_firmid = ORDER_FIRMID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_ORDER_FIRMID, LPSTR, c_long
)



# long TRANS2QUIK_TRADE_DATE(long nTradeDescriptor)
trade_date = TRADE_DATE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_DATE, c_long, c_long
)

# long TRANS2QUIK_TRADE_SETTLE_DATE(long nTradeDescriptor)
trade_settle_date = TRADE_SETTLE_DATE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_SETTLE_DATE, c_long, c_long
)

# long TRANS2QUIK_TRADE_TIME(long nTradeDescriptor)
trade_time = TRADE_TIME = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_TIME, c_long, c_long
)

# long TRANS2QUIK_TRADE_IS_MARGINAL(long nTradeDescriptor)
trade_is_marginal = TRADE_IS_MARGINAL = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_IS_MARGINAL, c_long, c_long
)

# LPSTR TRANS2QUIK_TRADE_CURRENCY(long nTradeDescriptor)
trade_currency = TRADE_CURRENCY = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_CURRENCY, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_SETTLE_CURRENCY(long nTradeDescriptor)
trade_settle_currency = TRADE_SETTLE_CURRENCY = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_SETTLE_CURRENCY, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_SETTLE_CODE(long nTradeDescriptor)
trade_settle_code = TRADE_SETTLE_CODE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_SETTLE_CODE, LPSTR, c_long
)

# double TRANS2QUIK_TRADE_ACCRUED_INT(long nTradeDescriptor)
trade_accrued_int = TRADE_ACCRUED_INT = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_ACCRUED_INT, c_double, c_long
)

# double TRANS2QUIK_TRADE_YIELD(long nTradeDescriptor)
trade_yield = TRADE_YIELD = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_YIELD, c_double, c_long
)

# LPSTR TRANS2QUIK_TRADE_USERID(long nTradeDescriptor)
trade_userid = TRADE_USERID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_USERID, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_ACCOUNT(long nTradeDescriptor)
trade_account = TRADE_ACCOUNT = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_ACCOUNT, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_BROKERREF(long nTradeDescriptor)
trade_brokerref = TRADE_BROKERREF = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_BROKERREF, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_CLIENT_CODE(long nTradeDescriptor)
trade_client_code = TRADE_CLIENT_CODE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_CLIENT_CODE, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_FIRMID(long nTradeDescriptor)
trade_firmid = TRADE_FIRMID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_FIRMID, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_PARTNER_FIRMID(long nTradeDescriptor)
trade_partner_firmid = TRADE_PARTNER_FIRMID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_PARTNER_FIRMID, LPSTR, c_long
)

# double TRANS2QUIK_TRADE_TS_COMMISSION(long nTradeDescriptor)
trade_ts_comission = TRADE_TS_COMMISSION = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_TS_COMMISSION, c_double, c_long
)

# double TRANS2QUIK_TRADE_CLEARING_CENTER_COMMISSION(long nTradeDescriptor)
trade_clearing_center_comission = \
    TRADE_CLEARING_CENTER_COMMISSION = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_CLEARING_CENTER_COMMISSION, c_double, c_long
)

# double TRANS2QUIK_TRADE_EXCHANGE_COMMISSION(long nTradeDescriptor)
trade_exchange_comission = TRADE_EXCHANGE_COMMISSION = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_EXCHANGE_COMMISSION, c_double, c_long
)

# double TRANS2QUIK_TRADE_TRADING_SYSTEM_COMMISSION(long nTradeDescriptor)
trade_trading_system_commission = \
    TRADE_TRADING_SYSTEM_COMMISSION = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_TRADING_SYSTEM_COMMISSION, c_double, c_long
)

# double TRANS2QUIK_TRADE_PRICE2(long nTradeDescriptor)
trade_price2 = TRADE_PRICE2 = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_PRICE2, c_double, c_long
)

# double TRANS2QUIK_TRADE_REPO_RATE(long nTradeDescriptor)
trade_repo_rate = TRADE_REPO_RATE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_REPO_RATE, c_double, c_long
)

# double TRANS2QUIK_TRADE_REPO_VALUE(long nTradeDescriptor)
trade_repo_rate = TRADE_REPO_RATE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_REPO_RATE, c_double, c_long
)

# double TRANS2QUIK_TRADE_REPO2_VALUE(long nTradeDescriptor)
trade_repo2_value = TRADE_REPO2_VALUE = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_REPO2_VALUE, c_double, c_long
)

# double TRANS2QUIK_TRADE_ACCRUED_INT2(long nTradeDescriptor)
trade_accrued_int2 = TRADE_ACCRUED_INT2 = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_ACCRUED_INT2, c_double, c_long
)

# long TRANS2QUIK_TRADE_REPO_TERM(long nTradeDescriptor)
trade_repo_term = TRADE_REPO_TERM = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_REPO_TERM, c_long, c_long
)

# double TRANS2QUIK_TRADE_START_DISCOUNT(long nTradeDescriptor)
trade_start_discount = TRADE_START_DISCOUNT = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_START_DISCOUNT, c_double, c_long
)

# double TRANS2QUIK_TRADE_LOWER_DISCOUNT(long nTradeDescriptor)
trade_lower_discount = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_LOWER_DISCOUNT, c_double, c_long
)

# double TRANS2QUIK_TRADE_UPPER_DISCOUNT(long nTradeDescriptor)
trade_upper_discount = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_UPPER_DISCOUNT, c_double, c_long
)

# LPSTR TRANS2QUIK_TRADE_EXCHANGE_CODE(long nTradeDescriptor)
trade_exchange_code = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_EXCHANGE_CODE, LPSTR, c_long
)

# LPSTR TRANS2QUIK_TRADE_STATION_ID(long nTradeDescriptor)
trade_station_id = TRADE_STATION_ID = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_STATION_ID, LPSTR, c_long
)

# long TRANS2QUIK_TRADE_BLOCK_SECURITIES(long nTradeDescriptor)
trade_block_securities = TRADE_BLOCK_SECURITIES = _declare_method(
    TRANS2QUIK.TRANS2QUIK_TRADE_BLOCK_SECURITIES, c_long, c_long
)

