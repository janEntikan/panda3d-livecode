smiley = loader.load_model("models/smiley")
for i in range(10):
    s = smiley.copy_to(render)
    s.set_y(10+i)
    s.set_x(i)
