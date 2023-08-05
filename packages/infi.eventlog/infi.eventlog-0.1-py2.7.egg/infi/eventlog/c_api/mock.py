import os
import ctypes
import infi.cwrap
import textwrap

HANDLE = ctypes.c_void_p
EVT_HANDLE = HANDLE
LPCWSTR = ctypes.c_wchar_p
DWORD = ctypes.c_ulong
BOOL = ctypes.c_ulong
POINTER = ctypes.POINTER
PDWORD = POINTER(DWORD)

TRUE = 1
FALSE = 0

MAX_LENGTH = 256
ERROR_NO_MORE_ITEMS = 259

open_handles = dict()
max_handle_id = 1
available_channel_names = [u"System", u"Application"]

SAMPLE_XML = u"""<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
<System><Provider Name='Service Control Manager' Guid='{555908d1-a6d7-4695-8e1e-2
6931d2012f4}' EventSourceName='Service Control Manager'/><EventID Qualifiers='16
384'>7036</EventID><Version>0</Version><Level>4</Level><Task>0</Task><Opcode>0</
Opcode><Keywords>0x8080000000000000</Keywords><TimeCreated SystemTime='2010-11-2
1T03:31:33.034185300Z'/><EventRecordID>1</EventRecordID><Correlation/><Execution
 ProcessID='484' ThreadID='564'/><Channel>System</Channel><Computer>37L4247F26-2
4</Computer><Security/></System><EventData><Data Name='param1'>User Profile Serv
ice</Data><Data Name='param2'>stopped</Data><Binary>500072006F006600530076006300
2F0031000000</Binary></EventData></Event>""".replace("\n", "")

class WindowsException(Exception):
    def __init__(self, winerror):
        super(WindowsException, self).__init__()
        self.winerror = winerror

InvalidHandle = WindowsException

class Channel(object):
    def __init__(self, name):
        super(Channel, self).__init__()
        self.name = name

class AvailableChannelsEnum(object):
    def __init__(self):
        super(AvailableChannelsEnum, self).__init__()
        self.items = list(available_channel_names)

class Event(object):
    pass

class QueryEnum(object):
    def __init__(self, name):
        super(QueryEnum, self).__init__()
        self.items = [Event() for i in range(10)]

class RenderContext(object):
    pass

def get_new_handle():
    global max_handle_id
    handle = max_handle_id
    max_handle_id +=1 
    return handle

def EvtOpenLog(session, path, flags):
    assert session is None
    assert path in available_channel_names
    handle = get_new_handle()
    open_handles[handle] = Channel(path)
    return handle

def EvtClose(handle):
    assert handle in open_handles
    open_handles.pop(handle)

def EvtOpenChannelEnum(session, flags):
    assert session is None
    handle = get_new_handle()
    open_handles[handle] = AvailableChannelsEnum()
    return handle

def EvtNextChannelPath(handle, buffer_size, buffer, buffer_used_size):
    assert handle in open_handles
    value = open_handles[handle]
    assert isinstance(value, AvailableChannelsEnum)
    if not value.items:
        raise WindowsException(ERROR_NO_MORE_ITEMS)
    buffer.value = value.items.pop()
    return 1

def EvtQuery(session, path, query, flags):
    assert session is None
    if flags & 1:
        assert path in available_channel_names
    elif flags & 2:
        assert os.path.exists(path)
    handle = get_new_handle()
    open_handles[handle] = QueryEnum(path)
    return handle

def EvtNext(result_set, array_size, array, timeout, flags, returned):
    value = open_handles[result_set]
    assert isinstance(value, QueryEnum)
    assert array_size == 1
    assert timeout == 0
    assert flags == 0
    if not value.items:
        raise WindowsException(ERROR_NO_MORE_ITEMS)
    handle = get_new_handle()
    event = value.items.pop()
    open_handles[handle] = event
    array._obj.value = handle
    return 1

# def EvtCreateRenderContext(values_path_count, values_paths, flags):
#     handle = get_new_handle()
#     open_handles[handle] = RenderContext()
#     return handle

def EvtRender(context, fragment, flags, buffer_size, buffer, buffer_used_size, property_count):
    assert context in open_handles.keys() + [None]
    assert fragment.value in open_handles
    buffer._obj.value = unicode(SAMPLE_XML)
    return 1
