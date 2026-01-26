import re


def cascade_all_eq(l: list):
    l = [x for x in l if x]
    if not all(x == l[0] for x in l):
        # print("oops, contradictory information", l)
        return
    
    for x in l:
        if x:
            return x


def infer_speed(gen: str, speed: int):
    BANDWIDTHS = {
        'DDR': (1600, 2100, 2700, 3200),
        'DDR2': (3200, 4200, 5300, 6400, 8500),
        'DDR3': (6400, 8500, 10600, 10666, 12800, 14900, 17000),
        'DDR4': (12800, 14900, 17000, 19200, 21300, 23400, 25600, 28800),
        'DDR5': (32000, 35200, 38400, 41600, 44800, 48000, 49600,
              51200, 54400, 57600, 60800, 64000, 65600, 67200, 70400)
    }

    CONVERTIONS = {1600: 200, 2100: 266, 2700: 333, 3200: 400,
                   4200: 533, 5300: 667, 6400: 800, 8500: 1066,
                   10600: 1333, 10666: 1333, 12800: 1600, 14900: 1866, 17000: 2133,
                   19200: 2400, 21300: 2666, 23400: 2933, 25600: 3200, 28800: 3600, 32000: 4000,
                   35200: 4400, 38400: 4800, 41600: 5200, 44800: 5600, 48000: 6000,
                   49600: 6200, 51200: 6400, 54400: 6800, 57600: 7200, 60800: 7600,
                   64000: 8000, 65600: 8200, 67200: 8400, 70400: 8800}

    if speed in BANDWIDTHS[gen]:
        return CONVERTIONS[speed]
    if speed in CONVERTIONS.values():
        return speed
    
    # print(f"I don't know speed {speed} for gen {gen}")


def extract_gen_and_speed(text: str):
    # good for 90%
    GEN_RE = re.compile(r"(?:pc|ddr)[-\s]?(?=\d)(?:(\d)l?(?:\D|$))?(?:[\s-]*(\d{3,5}))?", re.I)

    matches = GEN_RE.findall(text)
    
    gens = []
    speeds = []
    for m in matches:
        gen, speed = m
        gen = gen or ''
        gen = '' if gen == '1' else gen
        gen = "DDR" + gen
        if speed:
            speed = infer_speed(gen, int(speed))
        gens.append(gen)
        speeds.append(speed)
        
    return cascade_all_eq(gens), cascade_all_eq(speeds)


def extract_speed(text: str):
    SPEED_RE = re.compile(r"(\d{3,4})\s*(?:mhz|mt/?s)", re.I)
    matches = SPEED_RE.findall(text)
    speeds = []
    for m in matches:
        speed = int(m.replace('.', ''))

        speeds.append(speed)

    return cascade_all_eq(speeds)


def extract_speed_backup(gen: str, text: str):
    SPEED_RE = re.compile(r"(\d{4,5})", re.I)
    matches = SPEED_RE.findall(text)
    speeds = []
    for m in matches:
        speed = int(m.replace('.', ''))
        if gen:
            speed = infer_speed(gen, speed)
        speeds.append(speed)

    return cascade_all_eq(speeds)
    

def extract_ram_type(text: str):
    SERVER_RE = re.compile(r'(server|ecc|registered)', re.I)
    LAPTOP_RE = re.compile(r'(so[-\s]?dimm|laptop)', re.I)

    if SERVER_RE.search(text):
        return 'server'
    elif LAPTOP_RE.search(text):
        return 'laptop'
    return 'desktop'


def extract_latency(text: str):
    LATENCY_RE = re.compile(r'[^a-z]cl?(\d{1,2})')
    latency = cascade_all_eq(LATENCY_RE.findall(text))
    if latency:
        return int(latency)


def extract_gb(text: str):
    get_size = lambda a, t: int(a) / 1024 if t and t.lower() == 'mb' else int(a)

    TOTAL_RE = re.compile(r'(\d{1,3})\s*(gb|mb)', re.I)
    STICKS_RE = re.compile(r'(\d{1,2})\s*x\s*(\d{1,2})\s*(gb|mb)?', re.I)

    m = STICKS_RE.search(text)
    if m:
        amount = int(m.group(1))
        size = get_size(m.group(2), m.group(3))
        return amount, size, amount * size

    sizes = []
    for size, type in TOTAL_RE.findall(text):
        sizes.append(get_size(size, type))
    if not sizes:
        return None, None, None
    
    total = max(sizes)

    return 1, total, total


def extract_ram_info(text: str):
    gen, speed = extract_gen_and_speed(text)

    if not speed:
        speed = extract_speed(text)

    if gen and not speed:
        speed = extract_speed_backup(gen, text)

    ram_type = extract_ram_type(text)
    
    latency = extract_latency(text)

    amount, size, total = extract_gb(text)

    return {
        'type': ram_type,
        'ddr gen': gen,
        'speed (mt/s)': speed,
        'latency (cycles)': latency,
        'sticks': amount,
        'stick size (gb)': size,
        'total (gb)': total
    }
