from panda3d.core import DirectionalLight


smiley = loader.load_model("models/smiley")
for i in range(10):
    s = smiley.copy_to(render)
    s.set_y(20+(10-i))
    s.set_x(i)

base.accept("arrow_left",s.set_x,extraArgs=[s,-1])
base.accept("arrow_right",s.set_x,extraArgs=[s,1])

d_light = render.attach_new_node(DirectionalLight("d_light"))
d_light.set_hpr(-25,-25,0)
render.set_light(d_light)

