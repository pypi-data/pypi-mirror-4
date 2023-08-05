
import ctypes
import infi.cwrap
import infi.wioctl.api
import infi.wioctl.constants
import infi.wioctl.errors

HANDLE = ctypes.c_void_p
EVT_HANDLE = HANDLE
LPCWSTR = ctypes.c_wchar_p
LPWSTR = ctypes.c_wchar_p
DWORD = ctypes.c_ulong
BOOL = ctypes.c_ulong
POINTER = ctypes.POINTER
PDWORD = POINTER(DWORD)
PVOID = ctypes.c_void_p

TRUE = 1
FALSE = 0

MAX_LENGTH = 256
ERROR_NO_MORE_ITEMS = infi.wioctl.constants.ERROR_NO_MORE_ITEMS

WindowsException = infi.wioctl.errors.WindowsException
InvalidHandle = infi.wioctl.errors.InvalidHandle

def errcheck_invalid_handle():
    def errcheck(result, func, args):
        if result in [None, infi.wioctl.constants.INVALID_HANDLE_VALUE]:
            last_error = ctypes.GetLastError()
            raise InvalidHandle(last_error)
        return result
    return errcheck

class EventLogFunction(infi.cwrap.WrappedFunction):
    return_value = ctypes.c_ulong

    @classmethod
    def get_parameters(cls):
        raise NotImplementedError()

    @classmethod
    def get_errcheck(cls):
        # return infi.cwrap.errcheck_zero()
        return infi.cwrap.errcheck_nonzero()

    @classmethod
    def get_library_name(cls):
        return "Wevtapi.dll"


class EvtOpenLog(EventLogFunction):
    return_value = EVT_HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "Session"),
                (LPCWSTR, infi.cwrap.IN, "Path"),
                (DWORD, infi.cwrap.IN, "Flags"),
               )

class EvtClose(EventLogFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return infi.wioctl.api.errcheck_bool()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "Object"),
               )

class EvtOpenChannelEnum(EventLogFunction):
    return_value = EVT_HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "Session"),
                (DWORD, infi.cwrap.IN, "Flags"),
               )

class EvtNextChannelPath(EventLogFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return infi.wioctl.api.errcheck_bool()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "ChannelEnum"),
                (DWORD, infi.cwrap.IN, "ChannelPathBufferSize"),
                (LPWSTR, infi.cwrap.IN_OUT, "ChannelPathBuffer"),
                (PDWORD, infi.cwrap.IN_OUT, "ChannelPathBufferUsed"),
               )

class EvtQuery(EventLogFunction):
    return_value = EVT_HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "Session"),
                (LPCWSTR, infi.cwrap.IN, "Path"),
                (LPCWSTR, infi.cwrap.IN, "Query"),
                (DWORD, infi.cwrap.IN, "Flags"),
               )

class EvtNext(EventLogFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return infi.wioctl.api.errcheck_bool()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "ResultSet"),
                (DWORD, infi.cwrap.IN, "EventArraySize"),
                (POINTER(EVT_HANDLE), infi.cwrap.IN_OUT, "EventArray"),
                (DWORD, infi.cwrap.IN, "Timeout"),
                (DWORD, infi.cwrap.IN, "Flags"),
                (PDWORD, infi.cwrap.IN_OUT, "Returned"),
               )

# class EvtCreateRenderContext(EventLogFunction):
#     return_value = EVT_HANDLE

#     @classmethod
#     def get_errcheck(cls):
#         return errcheck_invalid_handle()

#     @classmethod
#     def get_parameters(cls):
#         return (
#                 (DWORD, infi.cwrap.IN, "ValuePathsCount"),
#                 (POINTER(LPWSTR), infi.cwrap.IN, "ValuePaths"),
#                 (DWORD, infi.cwrap.IN, "Flags"),
#                )

class EvtRender(EventLogFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return infi.wioctl.api.errcheck_bool()

    @classmethod
    def get_parameters(cls):
        return (
                (EVT_HANDLE, infi.cwrap.IN, "Context"),
                (EVT_HANDLE, infi.cwrap.IN, "Fragment"),
                (DWORD, infi.cwrap.IN, "Flags"),
                (DWORD, infi.cwrap.IN, "BufferSize"),
                (PVOID, infi.cwrap.IN, "Buffer"),
                (PDWORD, infi.cwrap.IN_OUT, "BufferUsed"),
                (PDWORD, infi.cwrap.IN_OUT, "PropertyCount"),
               )
