import time 

# def get_nanosecond_timestamp() -> int:
#     return int(time.time() * 1e9)

# def get_microsecond_timestamp() -> int:
#     return int(time.time() * 1e6)

# def get_millisecond_timestamp() -> int:
#     return int(time.time() * 1e3) 

# do*NOT* use time.time_ns() - it will return repeat values...
start_time = time.perf_counter_ns() 

def get_nanosecond_timestamp() -> int:
    return time.perf_counter_ns() - start_time

def get_microsecond_timestamp() -> int:
    return int(get_nanosecond_timestamp() // 1e3)

def get_millisecond_timestamp() -> int:
    return int(get_nanosecond_timestamp() // 1e6)
