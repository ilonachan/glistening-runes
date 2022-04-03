import kagaconf

# top-level defaults
kagaconf.from_dict({
    'db': {
        'main': {
            'location': 'sqlite:///runic.sqlite'
        }
    }
})

# read user config directory
kagaconf.from_path('config')
kagaconf.from_path('config/deploy')

# read environment variables
kagaconf.from_env_mapping({
    'discord': {
        'bot_token': 'BOT_TOKEN',
        'sync_slash': 'SYNC_SLASH'
    },
    'db': {
        'main': {
            'location': 'DB_LOCATION'
        }
    }
})
