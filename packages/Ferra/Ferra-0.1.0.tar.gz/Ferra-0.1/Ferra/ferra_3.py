import Ferra

window = Ferra.Window(width=900, height=200, caption="Rotating Sprites")
spritebatch = Ferra.Batch()
sprites = []
for i in range(5):
    i = i + 1
    bubbleimage = Ferra.resource.load_image("bubble%d.png" % i)
    sprite = Ferra.sprite.RotatingSprite(img=bubbleimage,
                                         x=i*150,
                                         y=100,
                                         rotate_speed=180.,
                                         batch=spritebatch)
    sprites.append(sprite)
@window.event
def on_draw():
    window.clear()
    spritebatch.draw()
def update(dt):
    for sprite in sprites:
        sprite.update(dt)
Ferra.schedule_interval(update, 1/60.)
Ferra.run()
