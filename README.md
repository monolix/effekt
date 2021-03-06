![effekt-logo](https://i.imgur.com/f0KGccz.png)

**Effekt** (`/effe:kt/`) is a **Python Framework** to make Event Driven Programming easier.

## Summary
 * [Installing](#installing)
 * [Support](#support)
 * [Contributing](#contributing)

With Effekt you can enjoy the power of callbacks without any kind of struggle.
```python
from effekt import Router

router = Router()

@router.on("/greet")
def saySomething():
    print("Hello World!")

router.fire("/greet")
```

> Note: although URL patterns and names such as "router" come up really often, it has nothing related to the HTTP protocol, it's just a convention.

Pretty unsatisfied? Watch this:
```python
from effekt import Router

router = Router()

@router.on("/welcome/main", pr=1)
def welcome_message():
    print("Welcome user!")

@router.on("/welcome/main", pr=2)
def ask_name():
    print("What's your name? ")
    name = input()
    router.fire("/welcome/name", name=name)

@router.on("/welcome/name")
def beautiful_name(name):
    print("Oh {}! You've got such a beautiful name!".format(name))

router.fire("/welcome/main")
```

> Ok, I see, isn't this just calling functions under the hood?

Yes it is. But Effekt offers the possibity to create **Extensions**, such as the official `Clock` one.
```python
from effekt import Router
from effekt.ext.clock import Clock
from dmotd import DMOTD

router = Router()
clock = Clock(router)
dmotd = DMOTD("https://monolix.github.io/motd")

@router.on("/fetch")
def fetch_motd():
    motd = dmotd.raw()
    router.fire("/save", motd=motd)

@router.on("/save")
def save_to_file(motd):
    with open("motd.txt", "w") as f:
        f.write(motd)

@router.on("/save")
def save_to_remote_server(motd):
    # SSH stuff...

clock.tick("/fetch", relax=3600)
```
This script fetches the [DMOTD](https://github.com/monolix/dmotd) every hour and saves it locally and onto another remote server.
You can broadcast a message only by assigning different functions to the same event listener.

## Installing
To install it, just clone the repo and add it to the local packages with
```bash
git clone https://github.com/monolix/effekt # Clone the repository
cd effekt/src # Change working directory
python setup.py install # Install the package
```

If you want to install it in a virtual environment, just run before installing

```bash
source <envdir>/bin/activate
```

## Support
If you want some (moral) support or just help, you can rely on the [gitter](https://gitter.im/effekt-framework) chat.

## Contributing
If you want to contribute to this open source project, you're free to pull-request us! We'll check your submission as soon as we can.
