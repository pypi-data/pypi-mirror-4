from mtj.f3u1.factory import UnitGroup

_plurals = {
    'day': 'days',
    'hour': 'hours',
    'minute': 'minutes',
    'second': 'seconds',
    'mile': 'miles',
    'yard': 'yards',
    'foot': 'feet',
    'inch': 'inches',
    'ton': 'tons',
    'stone': 'stones',
    'pound': 'pounds',
    'ounce': 'ounces',
}

Time = UnitGroup(base_unit='second', plurals=_plurals, ratios={
    'day': 86400,
    'hour': 3600,
    'minute': 60,
})

ImperialLength = UnitGroup(base_unit='inch', plurals=_plurals, ratios={
    'mile': 63360,
    'yard': 36,
    'foot': 12,
})

ImperialWeight = UnitGroup(base_unit='ounce', plurals=_plurals, ratios={
    'ton': 35840,
    'stone': 224,
    'pound': 16,
})
