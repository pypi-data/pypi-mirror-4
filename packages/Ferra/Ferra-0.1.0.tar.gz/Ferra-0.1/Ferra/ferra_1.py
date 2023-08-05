import Ferra
import pyglet
import random
window = Ferra.Window(caption="Ferra Test 1")
##sprite = Ferra.sprite.create_sprite("ast.png",
##                      x=window.width//2,
##                      y=window.height//2)
sprite = Ferra.sprite.StaticSprite("ast.png",
                      x=window.width//2,
                      y=window.height//2)
#sprite.scale = 0.1
@window.event
def on_draw():
    r = random.randint(0, 2)
    g = random.randint(0, 2)
    b = random.randint(0, 1)
    a = random.randint(0, 2)
    window.clear(r, g, b, a)
    sprite.draw()
##dx = (random.random() - 0.5) * 100
##dy = (random.random() - 0.5) * 100
def update(dt):
##    sprite.rotate(1)
##    x = sprite.x + dx * dt
##    y = sprite.y + dy * dt
##    sprite.x = Ferra.sprite.wrap_slide(x, 640)
##    sprite.y = Ferra.sprite.wrap_slide(y, 480)
    pass
Ferra.schedule_interval(update, 1/120.)
Ferra.run()
