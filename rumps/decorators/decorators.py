
from ..menu_items import (
    Menu,
    MenuItem,
    SeparatorMenuItem,
    separator,
    SliderMenuItem,
    TextFieldMenuItem,
    ImageMenuItem,
    ListMenuItem,
    ListView,
    CardMenuItem
)
from ..utils.compat import text_type
from ..core.timer import Timer

def timer(interval):
    """Decorator for registering a function as a timer callback."""
    def decorator(f):
        timers = getattr(timer, '*timers', None)
        if timers is None:
            timer.__dict__['*timers'] = []
        timer.__dict__['*timers'].append(Timer(f, interval))
        return f
    return decorator


def clicked(*args, **options):
    """Decorator for registering a function as a menu item callback."""
    def decorator(f):
        if isinstance(args[0], text_type):
            menuitem = MenuItem(args[0], callback=f, **options)
        else:
            menuitem = args[0]
            menuitem.set_callback(f, **options)
        clicked.__dict__[f.__name__] = menuitem
        return f

    if len(args) == 1 and callable(args[0]) and not options:
        f = args[0]
        menuitem = MenuItem(f.__name__.replace('_', ' ').title(), callback=f)
        clicked.__dict__[f.__name__] = menuitem
        return f
    return decorator


def slider(*args, **options):
    """Decorator for creating a slider menu item."""
    def decorator(f):
        options['value'] = options.get('value', 50)
        options['callback'] = f
        menuitem = SliderMenuItem(**options)
        slider.__dict__[f.__name__] = menuitem
        return f

    if not args:
        return decorator
    return decorator


def textfield(*args, **options):
    """Decorator for creating a text field menu item."""
    def decorator(f):
        if isinstance(args[0], TextFieldMenuItem):
            menuitem = args[0]
            menuitem.set_callback(f, **options)
        else:
            options['text'] = args[0] if args else options.get('text', '')
            options['callback'] = f
            menuitem = TextFieldMenuItem(**options)
        textfield.__dict__[f.__name__] = menuitem
        return f

    if not args:
        return decorator
    return decorator


def image(*args, **options):
    """Decorator for creating an image menu item."""
    def decorator(f):
        if isinstance(args[0], ImageMenuItem):
            menuitem = args[0]
            menuitem.set_callback(f, **options)
        else:
            options['image_path'] = args[0] if args else options.get('image_path')
            options['callback'] = f
            menuitem = ImageMenuItem(**options)
        image.__dict__[f.__name__] = menuitem
        return f

    if not args:
        return decorator
    return decorator


def list_menu(*args, **options):
    """Decorator for creating a list menu item."""
    def decorator(f):
        if isinstance(args[0], ListMenuItem):
            menuitem = args[0]
            menuitem.set_callback(f, **options)
        else:
            options['items'] = args[0] if args else options.get('items', [])
            options['callback'] = f
            menuitem = ListMenuItem(**options)
        list_menu.__dict__[f.__name__] = menuitem
        return f

    if not args:
        return decorator
    return decorator


def card(*args, **options):
    """Decorator for creating a card menu item."""
    def decorator(f):
        if isinstance(args[0], CardMenuItem):
            menuitem = args[0]
            menuitem.set_callback(f, **options)
        else:
            options['title'] = args[0] if args else options.get('title', '')
            options['callback'] = f
            menuitem = CardMenuItem(**options)
        card.__dict__[f.__name__] = menuitem
        return f

    if not args:
        return decorator
    return decorator