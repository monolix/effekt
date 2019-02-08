![effekt-logo](https://i.imgur.com/RgcL6Q1.png)

**Effekt** (`/effe:kt/`) is a **Python Framework** to make Event Driven Programming easier.

With Effekt you can enjoy the power of callbacks without any kind of struggle:
```python
@let.on("/greet")
def saySomething():
    print("Hello World!")

let.emit("/greet")
```
(`let` is just an instance of the Effekt class.)